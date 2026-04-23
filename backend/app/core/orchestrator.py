from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityManager
from app.services.rag_service import RAGService
from app.services.ticket_service import TicketService

class PortoDingOrchestrator:
    def __init__(self):
        self.rag = RAGService()
        self.security = SecurityManager()
        self.ticket_service = TicketService()

    async def process_request(
        self,
        raw_request_text: str,
        user_role: str,
        source_document_id: int,
        database_session: AsyncSession,
    ):
        # 1. THE PRE-PROCESS (The Regex PII Layer you insisted on)
        safe_text = self.security.regex_scrub(raw_request_text)
        
        # 2. THE REASONING (Calling Z.AI GLM)
        # We ask the AI: "Based on this text, what is the intent and what data is inside?"
        extraction = await self.call_glm(safe_text)
        
        # 3. THE TOOL DISPATCHER (The Agentic Logic)
        extracted_intent = extraction.get("intent") or extraction.get("intent_category") or "UNKNOWN"
        requires_manager_approval = self._extraction_requires_manager_approval(extraction)

        created_ticket = await self.ticket_service.create_new_ticket(
            document_id=source_document_id,
            extracted_intent=extracted_intent,
            requires_manager_approval=requires_manager_approval,
            database_session=database_session,
        )

        await self._send_whatsapp_confirmation(
            recipient_identifier=str(source_document_id),
            message_text=(
                "Ticket created and waiting for manager approval."
                if requires_manager_approval
                else "Ticket created and ready for processing."
            ),
            ticket_id=created_ticket["id"],
        )
        
        if extracted_intent == "ORDER_PLACEMENT":
            return created_ticket

        if extracted_intent == "INQUIRY":
            # Call Tool: Search Qdrant for past prices/info
            context = self.rag.search_memory_tool(extraction["query"])
            return self.generate_answer(context)

        return created_ticket

    def _extraction_requires_manager_approval(self, extraction: dict[str, Any]) -> bool:
        security_flags = extraction.get("security_flags") or {}

        if security_flags.get("pii_detected") is True:
            return True

        if security_flags.get("sensitive_data_detected") is True:
            return True

        sensitive_data_fields = (
            "pii_types",
            "sensitive_fields",
            "restricted_fields",
        )
        return any(bool(security_flags.get(field_name)) for field_name in sensitive_data_fields)

    async def _send_whatsapp_confirmation(
        self,
        recipient_identifier: str,
        message_text: str,
        ticket_id: int,
    ) -> dict:
        # TODO: REPLACE WITH ACTUAL SECRETS LATER.
        dummy_whatsapp_api_key = "DUMMY_API_KEY_REPLACE_ME"
        dummy_whatsapp_api_url = "https://dummy-whatsapp-provider.example/messages"

        dummy_whatsapp_api_response = {
            "api_url": dummy_whatsapp_api_url,
            "api_key": dummy_whatsapp_api_key,
            "recipient_identifier": recipient_identifier,
            "message_text": message_text,
            "ticket_id": ticket_id,
            "status": "mocked",
        }

        return dummy_whatsapp_api_response
