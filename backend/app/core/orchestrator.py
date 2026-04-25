import hashlib
import json
import logging
import os
import tempfile
import time
import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, desc

from app.core.security import SecurityManager
from app.services.glm_service import GLMService
from app.services.wa_service import WhatsAppService
from app.services.google_sheets import GoogleSheetsService
from app.services.rag_service import RAGService
from app.services.ticket_service import (
    TicketIntent, TicketService, documents_table, audit_logs_table
)
from app.models.schemas import Order, Customer
from app.services.gdrive_service import GoogleDriveService

logger = logging.getLogger("PortoDingOrchestrator")
# Add your company name here!
MY_COMPANY_NAME = "PortoDing Sdn Bhd" 

# Notice the 'f' at the beginning of the string to allow variable injection
MASTER_JSON_SYSTEM_PROMPT = f"""
You are the AI operations manager for "{MY_COMPANY_NAME}", a Malaysian SME.
Analyse the input (which has already been PII-scrubbed) and return ONLY a valid JSON object — no markdown, no prose.

CRITICAL INSTRUCTION: 
When extracting the "client_name", DO NOT extract our own name ("{MY_COMPANY_NAME}"). 
You must extract the name of the EXTERNAL customer, vendor, or supplier we are doing business with.

Required output schema:
{{
  "metadata": {{
    "unique_hash": "<will be filled by system>",
    "timestamp": "<ISO-8601 UTC>",
    "detected_language": "<IETF tag, e.g. ms-MY or en-MY>",
    "confidence_score": 0.9,
    "source_type": "<WhatsApp_Text | WhatsApp_Image_OCR | Web_Upload | ...>",
    "source_url": "<will be filled by system>"
  }},
  "classification": {{
    "intent_category": "<ORDER_PLACEMENT | STOCK_PROCUREMENT | REFUND | UNKNOWN>",
    "urgency_level": 3,
    "formal_summary": "<professional one-sentence summary in English>"
  }},
  "extracted_entities": {{
    "client_name": "<string or null>",
    "items": [{{"item_name": "<str>", "quantity": 1, "unit": "<str>"}}],
    "location": "<string or null>",
    "deadline": "<YYYY-MM-DD or null>"
  }},
  "security_flags": {{
    "pii_detected": false,
    "pii_types": ["<IC_NUMBER|BANK_ACCOUNT|PHONE_NUMBER|...>"],
    "requires_manager_approval": false
  }}
}}
"""

class PortoDingOrchestrator:
    def __init__(
        self,
        ticket_service: TicketService | None = None,
        security_manager: SecurityManager | None = None,
        rag_service: RAGService | None = None,
        glm_service: GLMService | None = None,
        sheets_service: GoogleSheetsService | None = None,
        wa_service: WhatsAppService | None = None,
    ) -> None:
        self.ticket_service = ticket_service or TicketService()
        self.security = security_manager or SecurityManager()
        self.glm = glm_service or GLMService()
        self.rag = rag_service or RAGService()
        self.wa_service = wa_service or WhatsAppService()
        
        try:
            self.drive_service = GoogleDriveService()
        except Exception:
            self.drive_service = None
            
        try:
            self.sheets = sheets_service or GoogleSheetsService()
        except Exception:
            self.sheets = None

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
        
    def _hash_file_bytes(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    async def _semantic_dedup_check(self, text: str, client_id: str, role: str) -> str | None:
        if not self.rag: return None
        try:
            context = await self.rag.search_memory_tool(query=text, client_id=client_id, user_role=role)
            if context and context != "No relevant memory found.":
                return f"⚠️ Warning: A similar request was found in memory for client {client_id}."
        except Exception as e:
            logger.warning(f"Semantic dedup check failed: {e}")
        return None

    # ─── PIPELINE 1: TEXT ──────────────────────────────────────────────────
    async def process_text_input(self, raw_text: str, sender_id: str, user_role: str, source_platform: str, database_session: AsyncSession) -> dict:
        unique_hash = self._hash_text(raw_text)
        await self._audit(database_session, user_role, "TEXT_INTAKE", None)
        
        # 1. Binary Dedup
        existing = await self._find_document_by_hash(unique_hash, database_session)
        if existing:
            return {"status": "DUPLICATE", "message": "Message already processed.", "existing_id": existing["id"]}
        
        raw_pii = self.security.extract_raw_pii(raw_text)

        # 2. PII Scrub & Semantic Dedup
        scrubbed_text = self.security.regex_scrub(raw_text)
        pii_was_scrubbed = scrubbed_text != raw_text
        semantic_warning = await self._semantic_dedup_check(scrubbed_text, sender_id, user_role)
        
        # 3. AI Classification
        master_json = await self._call_glm_for_master_json(scrubbed_text, unique_hash, "", f"{source_platform}_Text")
        
        intent = master_json.get("classification", {}).get("intent_category")
        valid_intents = [
            TicketIntent.ORDER_PLACEMENT.value, 
            TicketIntent.STOCK_PROCUREMENT.value, 
            TicketIntent.REFUND.value
        ]

        if not intent or intent not in valid_intents:
            print("[ORCHESTRATOR] Document is IRRELEVANT")
            return {"status": "IRRELEVANT", "message": "This document is irrelevant."}
        
        if pii_was_scrubbed:
            master_json["security_flags"]["pii_detected"] = True

        if intent == TicketIntent.STOCK_PROCUREMENT.value:
            entity_type = "SUPPLIER"
        else:
            entity_type = "CUSTOMER"

        extracted_client = master_json.get("extracted_entities", {}).get("client_name")
        
        if source_platform.upper() == "WHATSAPP":
            client_identifier = sender_id
        else:
            client_identifier = raw_pii.get("phone_number") or extracted_client or f"Unknown_Entity_{unique_hash[:8]}"

        entity_id = await self.ticket_service.get_or_create_external_entity(
            identifier=client_identifier,
            entity_type=entity_type,
            display_name=extracted_client,
            ic_no=raw_pii.get("ic_number"),
            bank_acc=raw_pii.get("bank_account"),
            database_session=database_session
        )
        # 4. Save Doc
        doc_record = await self._save_document_record(unique_hash, None, source_platform, None, entity_id, database_session)

        master_json["metadata"]["raw_text"] = scrubbed_text
        
        # 5. Ingest to RAG
        await self._ingest_to_qdrant(master_json, sender_id)

        # 6. Auto-Update Sheets
        sheets_result = None
        if master_json["classification"]["intent_category"] == TicketIntent.ORDER_PLACEMENT.value and not master_json["security_flags"]["pii_detected"]:
            sheets_result = self._push_order_to_sheets(master_json, doc_record["id"])

        # 7. Create Ticket
        requires_approval = self._needs_approval(master_json, user_role, pii_was_scrubbed)
        ticket = await self.ticket_service.create_new_ticket(
            document_id=doc_record["id"],
            extracted_intent=master_json["classification"]["intent_category"],
            requires_manager_approval=requires_approval,
            database_session=database_session
        )

        # 8. Notify
        msg = "Ticket awaiting manager approval." if requires_approval else "Ticket ready for processing."
        await self.whatsapp_send(sender_id, msg, ticket["id"])
        await self._audit(database_session, user_role, "TEXT_INTAKE_COMPLETE", ticket["id"])

        return {
            "status": "OK",
            "ticket": ticket,
            "master_json": self.security.apply_role_based_censorship(master_json, user_role),
            "semantic_warning": semantic_warning,
            "sheets_update": sheets_result
        }

    # ─── PIPELINE 2: DOCUMENTS ──────────────────────────────────────────────
    async def process_document_input(self, file_bytes: bytes, file_name: str, sender_id: str, user_role: str, source_platform: str, uploader_id: int, database_session: AsyncSession) -> dict:
        unique_hash = self._hash_file_bytes(file_bytes)
        await self._audit(database_session, user_role, "DOC_INTAKE", None)

        existing = await self._find_document_by_hash(unique_hash, database_session)
        if existing:
            print(f"🛑 [ORCHESTRATOR] DUPLICATE FOUND! This file was already saved as Document ID: {existing['id']}")
            return {"status": "DUPLICATE", "message": "File already processed.", "existing_id": existing["id"]}

        # Parse Document (PDF, Word, Excel, etc.)
        raw_text = self._parse_document(file_bytes, file_name)
        raw_pii = self.security.extract_raw_pii(raw_text)

        scrubbed_text = self.security.regex_scrub(raw_text)
        pii_was_scrubbed = scrubbed_text != raw_text
        semantic_warning = await self._semantic_dedup_check(scrubbed_text, sender_id, user_role)

        ext = file_name.rsplit(".", 1)[-1].upper() if "." in file_name else "BIN"
        safe_file_name = f"{unique_hash[:8]}_{file_name}"

        temp_url = f"pending_upload/{safe_file_name}"
        master_json = await self._call_glm_for_master_json(scrubbed_text, unique_hash, temp_url, f"{source_platform}_{ext}_Upload")
        
        intent = master_json.get("classification", {}).get("intent_category")
        valid_intents = [
            TicketIntent.ORDER_PLACEMENT.value, 
            TicketIntent.STOCK_PROCUREMENT.value, 
            TicketIntent.REFUND.value
        ]

        if not intent or intent not in valid_intents:
            print("[ORCHESTRATOR] Document is IRRELEVANT. Dumping it. Nothing uploaded or saved.")
            return {"status": "IRRELEVANT", "message": "This document is irrelevant."}
        
        if self.drive_service:
            try:
                print(f"☁️ Uploading {safe_file_name} to Google Drive...")
                source_url = self.drive_service.upload_file(safe_file_name, file_bytes)
            except Exception as e:
                print(f"🚨 Drive Upload Failed: {e}")
                source_url = f"local_storage/{safe_file_name}"
        else:
            source_url = f"local_storage/{safe_file_name}"
            
        master_json["metadata"]["source_url"] = source_url

        if pii_was_scrubbed:
            master_json["security_flags"]["pii_detected"] = True

        if intent == TicketIntent.STOCK_PROCUREMENT.value:
            entity_type = "SUPPLIER"
        else:
            entity_type = "CUSTOMER"

        extracted_client = master_json.get("extracted_entities", {}).get("client_name")

        if source_platform.upper() == "WHATSAPP":
            client_identifier = sender_id
        else:
            client_identifier = raw_pii.get("phone_number") or extracted_client or f"Unknown_Entity_{unique_hash[:8]}"

        entity_id = await self.ticket_service.get_or_create_external_entity(
            identifier=client_identifier,
            entity_type=entity_type,
            display_name=extracted_client,
            ic_no=raw_pii.get("ic_number"),
            bank_acc=raw_pii.get("bank_account"),
            database_session=database_session
        )

        doc_record = await self._save_document_record(unique_hash, source_url, source_platform, uploader_id, entity_id, database_session)
        
        master_json["metadata"]["raw_text"] = scrubbed_text
        
        await self._ingest_to_qdrant(master_json, sender_id)

        sheets_result = None
        if self.sheets and not master_json["security_flags"]["pii_detected"]:
            try:
                # Auto-Create Customer if they are missing
                customers = self.sheets.get_all_customers()
                if not any(str(c.get("customer_id")) == str(client_identifier) for c in customers):
                    new_cust = Customer(
                        customer_id=client_identifier,
                        contact_person=extracted_client or "Unknown",
                        masked_bank_details=self.security.mask_value(raw_pii.get("bank_account") or "", "BANK_ACCOUNT"),
                        masked_ic_number=self.security.mask_value(raw_pii.get("ic_number") or "", "IC_NUMBER")
                    )
                    self.sheets.add_customer_row(new_cust)

                # Auto-Create Order for BOTH Intents
                if intent in [TicketIntent.ORDER_PLACEMENT.value, TicketIntent.STOCK_PROCUREMENT.value]:
                    sheets_result = self._push_order_to_sheets(master_json, doc_record["id"], intent)
            except Exception as e:
                print(f"🚨 Sheets Sync Error: {e}")
                

        requires_approval = self._needs_approval(master_json, user_role, pii_was_scrubbed)
        ticket = await self.ticket_service.create_new_ticket(
            document_id=doc_record["id"],
            extracted_intent=master_json["classification"]["intent_category"],
            requires_manager_approval=requires_approval,
            database_session=database_session
        )

        msg = "Document Ticket awaiting manager approval." if requires_approval else "Document Ticket ready for processing."
        await self.whatsapp_send(sender_id, msg, ticket["id"])
        await self._audit(database_session, user_role, "DOC_INTAKE_COMPLETE", ticket["id"])

        return {
            "status": "OK",
            "ticket": ticket,
            "master_json": self.security.apply_role_based_censorship(master_json, user_role),
            "semantic_warning": semantic_warning,
            "sheets_update": sheets_result
        }

    # ─── HELPERS ──────────────────────────────────────────────────────────
    def _parse_document(self, file_bytes: bytes, file_name: str) -> str:
        from app.services.parser import extract_from_excel, extract_from_pdf, extract_from_ppt, extract_from_word
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        suffix = f".{ext}" if ext else ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            if ext in ("pdf",): return extract_from_pdf(tmp_path)
            elif ext in ("docx", "doc"): return extract_from_word(tmp_path)
            elif ext in ("pptx", "ppt"): return extract_from_ppt(tmp_path)
            elif ext in ("xlsx", "xls", "csv"): return extract_from_excel(tmp_path)
            else: return file_bytes.decode("utf-8", errors="replace")
        finally:
            os.unlink(tmp_path)

    async def _call_glm_for_master_json(self, text: str, unique_hash: str, source_url: str, source_type: str) -> dict:
        try:
            response = self.glm.client.chat.completions.create(
                model=self.glm.model,
                messages=[
                    {"role": "system", "content": MASTER_JSON_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            parsed = json.loads(response.choices[0].message.content)
        except Exception as exc:
            logger.warning(f"GLM failed: {exc}")
            parsed = {"classification": {"intent_category": "UNKNOWN", "formal_summary": text[:100]}}
            
        parsed.setdefault("metadata", {})
        parsed["metadata"]["unique_hash"] = unique_hash
        parsed["metadata"]["source_url"] = source_url
        parsed["metadata"]["source_type"] = source_type
        parsed.setdefault("security_flags", {"pii_detected": False})
        return parsed

    async def _save_document_record(self, unique_hash: str, gcs_url: str | None, source_platform: str, uploader_id: int | None, entity_id: int | None, db: AsyncSession) -> dict:
        stmt = insert(documents_table).values(
            unique_hash=unique_hash, 
            gcs_url=gcs_url, 
            source_platform=source_platform, 
            uploader_id=uploader_id, 
            entity_id=entity_id,
            created_at=datetime.now(timezone.utc)
        ).returning(*documents_table.c)
        res = await db.execute(stmt)
        await db.commit()
        return dict(res.mappings().one())

    async def _find_document_by_hash(self, unique_hash: str, db: AsyncSession) -> dict | None:
        res = await db.execute(select(documents_table).where(documents_table.c.unique_hash == unique_hash))
        row = res.mappings().one_or_none()
        return dict(row) if row else None

    async def _ingest_to_qdrant(self, master_json: dict, client_id: str) -> None:
        if self.rag:
            try:
                extracted_client = master_json.get("extracted_entities", {}).get("client_name")
                actual_client = extracted_client if extracted_client else client_id

                master_json.setdefault("payload_extras", {})["client"] = actual_client
                await self.rag.ingest_document(master_json)
            except Exception as exc:
                print(f"🚨 [QDRANT ERROR] Failed to ingest document: {exc}")

    def _push_order_to_sheets(self, master_json: dict, doc_id: int, intent: str) -> dict | None:
        if not self.sheets: return None
        try:
            # Calculate total items
            total = sum(float(i.get("quantity", 0)) for i in master_json.get("extracted_entities", {}).get("items", []))
            
            # Procurement is a negative hit to cashflow
            if intent == TicketIntent.STOCK_PROCUREMENT.value:
                total = -abs(total)
            else:
                total = abs(total)
                
            order = Order(
                order_id=f"ORD-{doc_id}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                customer_name=master_json.get("extracted_entities", {}).get("client_name") or "Unknown",
                total_amount=total,
                status="Pending"
            )
            self.sheets.add_order_row(order)
            return {"status": "written", "order_id": order.order_id}
        except Exception as e: 
            logger.error(f"Sheet push error: {e}")
            return None

    def _needs_approval(self, master_json: dict, user_role: str, pii_was_scrubbed: bool) -> bool:
        if pii_was_scrubbed or user_role.upper() == "STAFF": return True
        return master_json.get("security_flags", {}).get("pii_detected", False)

    async def _audit(self, session: AsyncSession, user_id: str, action: str, target_id: int | None) -> None:
        try:
            stmt = insert(audit_logs_table).values(
                action=f"{action}|role={user_id}", 
                target_id=target_id, 
                timestamp=datetime.now(timezone.utc)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"Audit failed: {e}")

    async def whatsapp_send(self, recipient: str, message: str, ticket_id: int = 0):
        return await self.wa_service.send_custom_text(recipient, message)

    async def process_request(self, raw_request_text: str, user_role: str, source_document_id: int, database_session: AsyncSession) -> dict:
        return await self.process_text_input(raw_request_text, str(source_document_id), user_role, "WEB", database_session)