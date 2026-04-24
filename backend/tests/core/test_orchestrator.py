import pytest

from app.core.orchestrator import PortoDingOrchestrator
from app.core.security import SecurityManager


class RecordingTicketService:
    def __init__(self) -> None:
        self.recorded_calls: list[dict] = []

    async def create_new_ticket(
        self,
        document_id: int,
        extracted_intent: str,
        requires_manager_approval: bool,
        database_session,
    ) -> dict:
        recorded_call = {
            "document_id": document_id,
            "extracted_intent": extracted_intent,
            "requires_manager_approval": requires_manager_approval,
            "database_session": database_session,
        }
        self.recorded_calls.append(recorded_call)
        return {
            "id": 501,
            "doc_id": document_id,
            "intent_category": extracted_intent,
            "status": "PENDING_APPROVAL" if requires_manager_approval else "NEW",
            "assigned_to": None,
        }


class RecordingRagService:
    def __init__(self) -> None:
        self.recorded_queries: list[dict] = []

    async def search_memory_tool(self, query: str, client_id: str, user_role: str) -> str:
        self.recorded_queries.append(
            {"query": query, "client_id": client_id, "user_role": user_role}
        )
        return "relevant memory context"


@pytest.mark.asyncio
async def test_process_request_scrubs_ic_number_and_creates_ticket_requiring_manager_approval() -> None:
    recording_ticket_service = RecordingTicketService()

    async def classifier_with_sensitive_data(scrubbed_request_text: str) -> dict:
        assert "950101-14-5566" not in scrubbed_request_text
        assert "5566" in scrubbed_request_text
        return {
            "intent_category": "ORDER_PLACEMENT",
            "formal_summary": scrubbed_request_text,
            "security_flags": {
                "pii_detected": True,
                "pii_types": ["IC_NUMBER"],
            },
        }

    orchestrator = PortoDingOrchestrator(
        ticket_service=recording_ticket_service,
        security_manager=SecurityManager(),
        rag_service=None,
        classifier=classifier_with_sensitive_data,
    )

    orchestrator_result = await orchestrator.process_request(
        raw_request_text="Customer IC is 950101-14-5566 and wants to place an order for flour.",
        user_role="STAFF",
        source_document_id=999,
        database_session=object(),
    )

    assert orchestrator_result["ticket"]["id"] == 501
    assert orchestrator_result["ticket"]["intent_category"] == "ORDER_PLACEMENT"
    assert orchestrator_result["requires_manager_approval"] is True
    assert "950101-14-5566" not in orchestrator_result["scrubbed_request_text"]
    assert recording_ticket_service.recorded_calls[0]["requires_manager_approval"] is True


@pytest.mark.asyncio
async def test_process_request_normalizes_classifier_intent_and_uses_real_ticket_enum_values() -> None:
    recording_ticket_service = RecordingTicketService()

    async def classifier_with_alias_intent(scrubbed_request_text: str) -> dict:
        return {
            "intent": "procurement",
            "formal_summary": scrubbed_request_text,
            "security_flags": {},
        }

    orchestrator = PortoDingOrchestrator(
        ticket_service=recording_ticket_service,
        classifier=classifier_with_alias_intent,
        rag_service=None,
    )

    orchestrator_result = await orchestrator.process_request(
        raw_request_text="Need supplier procurement for packaging stock.",
        user_role="MANAGER",
        source_document_id=321,
        database_session=object(),
    )

    assert orchestrator_result["ticket"]["intent_category"] == "STOCK_PROCUREMENT"
    assert orchestrator_result["requires_manager_approval"] is False
    assert recording_ticket_service.recorded_calls[0]["extracted_intent"] == "STOCK_PROCUREMENT"


@pytest.mark.asyncio
async def test_process_request_attaches_memory_context_when_query_and_rag_service_are_available() -> None:
    recording_ticket_service = RecordingTicketService()
    recording_rag_service = RecordingRagService()

    async def classifier_with_query(scrubbed_request_text: str) -> dict:
        return {
            "intent_category": "REFUND",
            "formal_summary": scrubbed_request_text,
            "query": "recent refund precedents",
            "security_flags": {},
        }

    orchestrator = PortoDingOrchestrator(
        ticket_service=recording_ticket_service,
        rag_service=recording_rag_service,
        classifier=classifier_with_query,
    )

    orchestrator_result = await orchestrator.process_request(
        raw_request_text="Customer wants a refund after damaged delivery.",
        user_role="MANAGER",
        source_document_id=654,
        database_session=object(),
    )

    assert orchestrator_result["ticket"]["intent_category"] == "REFUND"
    assert orchestrator_result["memory_context"] == "relevant memory context"
    assert recording_rag_service.recorded_queries[0]["client_id"] == "654"
