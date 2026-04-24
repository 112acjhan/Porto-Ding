from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from test_main import app, database_engine


@pytest_asyncio.fixture
async def ticket_api_client() -> AsyncGenerator[AsyncClient, None]:
    try:
        async with database_engine.begin() as database_connection:
            await database_connection.execute(
                text(
                    """
                    INSERT INTO users (id, username, role, password_hash)
                    VALUES (99, 'integration_manager', 'MANAGER', 'integration-test-password-hash')
                    ON CONFLICT (id) DO NOTHING;
                    """
                )
            )
            await database_connection.execute(
                text(
                    """
                    INSERT INTO documents (id, unique_hash, gcs_url, source_platform)
                    VALUES (999, 'integration-test-document-999', 'gs://integration-tests/document-999', 'WEB')
                    ON CONFLICT (id) DO NOTHING;
                    """
                )
            )
    except (OSError, SQLAlchemyError) as database_error:
        await database_engine.dispose()
        pytest.skip(
            f"PostgreSQL integration database is not available for API tests: {database_error}"
        )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as integration_test_client:
        yield integration_test_client

    await database_engine.dispose()


@pytest.mark.asyncio
async def test_system_can_create_new_ticket_via_debug_endpoint(
    ticket_api_client: AsyncClient,
) -> None:
    create_ticket_response = await ticket_api_client.post("/api/debug/create-ticket")

    assert create_ticket_response.status_code == 200

    created_ticket = create_ticket_response.json()
    assert isinstance(created_ticket["id"], int)
    assert created_ticket["doc_id"] == 999
    assert created_ticket["intent_category"] == "ORDER_PLACEMENT"
    assert created_ticket["status"] == "PENDING_APPROVAL"


@pytest.mark.asyncio
async def test_dashboard_retrieves_pending_tickets(
    ticket_api_client: AsyncClient,
) -> None:
    create_ticket_response = await ticket_api_client.post("/api/debug/create-ticket")
    created_ticket = create_ticket_response.json()

    pending_tickets_response = await ticket_api_client.get("/tickets/pending")

    assert pending_tickets_response.status_code == 200

    pending_tickets = pending_tickets_response.json()
    pending_ticket_ids = {
        pending_ticket["id"]
        for pending_ticket in pending_tickets
    }

    assert created_ticket["id"] in pending_ticket_ids


@pytest.mark.asyncio
async def test_manager_approval_updates_ticket_status(
    ticket_api_client: AsyncClient,
) -> None:
    create_ticket_response = await ticket_api_client.post("/api/debug/create-ticket")
    created_ticket = create_ticket_response.json()
    created_ticket_id = created_ticket["id"]

    approve_ticket_response = await ticket_api_client.post(
        f"/tickets/{created_ticket_id}/approve",
        json={"approving_manager_id": 99},
    )

    assert approve_ticket_response.status_code == 200

    approved_ticket = approve_ticket_response.json()
    assert approved_ticket["id"] == created_ticket_id
    assert approved_ticket["status"] == "NEW"
    assert approved_ticket["assigned_to"] == 99


@pytest.mark.asyncio
async def test_completed_fulfillment_updates_ticket_status(
    ticket_api_client: AsyncClient,
) -> None:
    create_ticket_response = await ticket_api_client.post("/api/debug/create-ticket")
    created_ticket = create_ticket_response.json()
    created_ticket_id = created_ticket["id"]

    approve_ticket_response = await ticket_api_client.post(
        f"/tickets/{created_ticket_id}/approve",
        json={"approving_manager_id": 99},
    )
    assert approve_ticket_response.status_code == 200

    complete_ticket_response = await ticket_api_client.post(
        f"/tickets/{created_ticket_id}/complete"
    )

    assert complete_ticket_response.status_code == 200

    completed_ticket = complete_ticket_response.json()
    assert completed_ticket["id"] == created_ticket_id
    assert completed_ticket["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_system_can_process_raw_message_into_tracked_ticket(
    ticket_api_client: AsyncClient,
) -> None:
    process_message_response = await ticket_api_client.post(
        "/api/debug/process-message",
        json={
            "raw_request_text": "Customer IC 950101-14-5566 wants to place an order for cooking oil.",
            "user_role": "STAFF",
            "source_document_id": 999,
        },
    )

    assert process_message_response.status_code == 200

    orchestrator_result = process_message_response.json()
    created_ticket = orchestrator_result["ticket"]
    assert created_ticket["doc_id"] == 999
    assert created_ticket["intent_category"] == "ORDER_PLACEMENT"
    assert created_ticket["status"] == "PENDING_APPROVAL"
    assert orchestrator_result["requires_manager_approval"] is True
    assert "950101-14-5566" not in orchestrator_result["scrubbed_request_text"]
