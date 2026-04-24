from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityManager
from app.services.glm_service import GLMService
from app.services.ticket_service import TicketIntent, TicketService


ClassifierCallable = Callable[[str], Awaitable[dict[str, Any]]]
NotificationCallable = Callable[[str, str, int], Awaitable[dict[str, Any]]]


class PortoDingOrchestrator:
    def __init__(
        self,
        ticket_service: TicketService | None = None,
        security_manager: SecurityManager | None = None,
        rag_service: Any | None = None,
        classifier: ClassifierCallable | None = None,
        notification_sender: NotificationCallable | None = None,
    ) -> None:
        self.ticket_service = ticket_service or TicketService()
        self.security = security_manager or SecurityManager()
        self.rag = rag_service
        self.classifier = classifier
        self.notification_sender = notification_sender or self._send_whatsapp_confirmation
        self.glm_service = GLMService()

        if self.rag is None:
            self.rag = self._build_rag_service_if_available()

    async def process_request(
        self,
        raw_request_text: str,
        user_role: str,
        source_document_id: int,
        database_session: AsyncSession,
    ) -> dict[str, Any]:
        scrubbed_request_text = self.security.regex_scrub(raw_request_text)
        scrubbed_content_was_detected = scrubbed_request_text != raw_request_text

        self.security.log_audit_event(
            user_id=user_role,
            action="SCRUB_AND_CLASSIFY_REQUEST",
            doc_id=str(source_document_id),
            status="STARTED",
        )

        extraction = await self.call_glm(scrubbed_request_text)
        normalized_intent_category = self._normalize_intent_category(extraction)
        requires_manager_approval = self._requires_manager_approval(
            extraction=extraction,
            user_role=user_role,
            scrubbed_content_was_detected=scrubbed_content_was_detected,
        )

        created_ticket = await self.ticket_service.create_new_ticket(
            document_id=source_document_id,
            extracted_intent=normalized_intent_category,
            requires_manager_approval=requires_manager_approval,
            database_session=database_session,
        )

        notification_result = await self.notification_sender(
            str(source_document_id),
            (
                "Ticket created and waiting for manager approval."
                if requires_manager_approval
                else "Ticket created and ready for processing."
            ),
            created_ticket["id"],
        )

        response_payload: dict[str, Any] = {
            "ticket": created_ticket,
            "classification": extraction,
            "scrubbed_request_text": scrubbed_request_text,
            "requires_manager_approval": requires_manager_approval,
            "notification": notification_result,
        }

        if extraction.get("query") and self.rag is not None:
            response_payload["memory_context"] = await self._search_memory_context(
                query=str(extraction["query"]),
                client_id=str(source_document_id),
                user_role=user_role,
            )

        self.security.log_audit_event(
            user_id=user_role,
            action="SCRUB_AND_CLASSIFY_REQUEST",
            doc_id=str(source_document_id),
            status="SUCCESS",
        )

        return response_payload

    async def call_glm(self, scrubbed_request_text: str) -> dict[str, Any]:
        if self.classifier is not None:
            classifier_result = await self.classifier(scrubbed_request_text)
            return self._coerce_extraction_payload(classifier_result, scrubbed_request_text)

        if self.glm_service.is_configured():
            try:
                classifier_result = await self.glm_service.classify_message(scrubbed_request_text)
                return self._coerce_extraction_payload(classifier_result, scrubbed_request_text)
            except Exception:
                pass

        return self._build_fallback_extraction(scrubbed_request_text)

    def _coerce_extraction_payload(
        self,
        classifier_result: dict[str, Any],
        scrubbed_request_text: str,
    ) -> dict[str, Any]:
        if not isinstance(classifier_result, dict):
            classifier_result = {}

        security_flags = classifier_result.get("security_flags")
        if not isinstance(security_flags, dict):
            security_flags = {}

        coerced_payload = dict(classifier_result)
        coerced_payload["formal_summary"] = str(
            classifier_result.get("formal_summary") or scrubbed_request_text.strip()
        )
        coerced_payload["security_flags"] = security_flags
        coerced_payload.setdefault("query", scrubbed_request_text.strip())
        return coerced_payload

    def _build_fallback_extraction(self, scrubbed_request_text: str) -> dict[str, Any]:
        lowered_request_text = scrubbed_request_text.lower()

        if any(keyword in lowered_request_text for keyword in ("order", "purchase", "buy")):
            fallback_intent_category = TicketIntent.ORDER_PLACEMENT.value
        elif any(keyword in lowered_request_text for keyword in ("stock", "procurement", "supplier", "inventory")):
            fallback_intent_category = TicketIntent.STOCK_PROCUREMENT.value
        else:
            fallback_intent_category = TicketIntent.REFUND.value

        pii_was_detected = "[REDACTED]" in scrubbed_request_text or "XXXX" in scrubbed_request_text

        return {
            "intent_category": fallback_intent_category,
            "formal_summary": scrubbed_request_text.strip(),
            "query": scrubbed_request_text.strip(),
            "security_flags": {
                "pii_detected": pii_was_detected,
                "pii_types": ["IC_NUMBER"] if pii_was_detected else [],
            },
        }

    def _normalize_intent_category(self, extraction: dict[str, Any]) -> str:
        raw_intent_category = extraction.get("intent") or extraction.get("intent_category")
        normalized_key = str(raw_intent_category or "").strip().upper().replace(" ", "_")

        intent_aliases = {
            "ORDER": TicketIntent.ORDER_PLACEMENT.value,
            "ORDER_PLACEMENT": TicketIntent.ORDER_PLACEMENT.value,
            "PLACE_ORDER": TicketIntent.ORDER_PLACEMENT.value,
            "PURCHASE_ORDER": TicketIntent.ORDER_PLACEMENT.value,
            "STOCK_PROCUREMENT": TicketIntent.STOCK_PROCUREMENT.value,
            "PROCUREMENT": TicketIntent.STOCK_PROCUREMENT.value,
            "INVENTORY_REQUEST": TicketIntent.STOCK_PROCUREMENT.value,
            "SUPPLIER_PROCUREMENT": TicketIntent.STOCK_PROCUREMENT.value,
            "REFUND": TicketIntent.REFUND.value,
            "REFUND_REQUEST": TicketIntent.REFUND.value,
            "RETURN": TicketIntent.REFUND.value,
        }

        return intent_aliases.get(normalized_key, TicketIntent.REFUND.value)

    def _requires_manager_approval(
        self,
        extraction: dict[str, Any],
        user_role: str,
        scrubbed_content_was_detected: bool,
    ) -> bool:
        if scrubbed_content_was_detected:
            return True

        if user_role.upper() == "STAFF":
            return True

        return self._extraction_requires_manager_approval(extraction)

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

    async def _search_memory_context(
        self,
        query: str,
        client_id: str,
        user_role: str,
    ) -> str | None:
        if self.rag is None or not hasattr(self.rag, "search_memory_tool"):
            return None

        return await self.rag.search_memory_tool(
            query=query,
            client_id=client_id,
            user_role=user_role,
        )

    def _build_rag_service_if_available(self) -> Any | None:
        try:
            from app.services.rag_service import RAGService
        except Exception:
            return None

        try:
            return RAGService()
        except Exception:
            return None

    async def _send_whatsapp_confirmation(
        self,
        recipient_identifier: str,
        message_text: str,
        ticket_id: int,
    ) -> dict[str, Any]:
        dummy_whatsapp_api_key = "DUMMY_API_KEY_REPLACE_ME"
        dummy_whatsapp_api_url = "https://dummy-whatsapp-provider.example/messages"

        return {
            "api_url": dummy_whatsapp_api_url,
            "api_key": dummy_whatsapp_api_key,
            "recipient_identifier": recipient_identifier,
            "message_text": message_text,
            "ticket_id": ticket_id,
            "status": "mocked",
        }
