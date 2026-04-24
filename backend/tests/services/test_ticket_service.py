from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.services.ticket_service import (
    TicketIntent,
    TicketService,
    TicketStatus,
    metadata,
    tickets_table,
)


@pytest_asyncio.fixture
async def isolated_ticket_database_session() -> AsyncGenerator[AsyncSession, None]:
    sqlite_database_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )

    original_intent_category_column_type = tickets_table.c.intent_category.type
    original_status_column_type = tickets_table.c.status.type
    tickets_table.c.intent_category.type = SqlAlchemyEnum(
        *(ticket_intent.value for ticket_intent in TicketIntent),
        name="ticket_intent",
        native_enum=False,
    )
    tickets_table.c.status.type = SqlAlchemyEnum(
        *(ticket_status.value for ticket_status in TicketStatus),
        name="ticket_status",
        native_enum=False,
    )

    try:
        async with sqlite_database_engine.begin() as database_connection:
            await database_connection.run_sync(metadata.create_all)

        sqlite_session_factory = async_sessionmaker(
            bind=sqlite_database_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with sqlite_session_factory() as isolated_database_session:
            yield isolated_database_session
    finally:
        async with sqlite_database_engine.begin() as database_connection:
            await database_connection.run_sync(metadata.drop_all)

        tickets_table.c.intent_category.type = original_intent_category_column_type
        tickets_table.c.status.type = original_status_column_type
        await sqlite_database_engine.dispose()


@pytest.mark.asyncio
async def test_create_ticket_with_manager_approval_sets_pending_approval_status(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_ticket = await ticket_service.create_new_ticket(
        document_id=101,
        extracted_intent=TicketIntent.ORDER_PLACEMENT.value,
        requires_manager_approval=True,
        database_session=isolated_ticket_database_session,
    )

    assert created_ticket["doc_id"] == 101
    assert created_ticket["intent_category"] == TicketIntent.ORDER_PLACEMENT.value
    assert created_ticket["status"] == TicketStatus.PENDING_APPROVAL.value
    assert created_ticket["assigned_to"] is None


@pytest.mark.asyncio
async def test_create_ticket_without_manager_approval_sets_new_status(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_ticket = await ticket_service.create_new_ticket(
        document_id=202,
        extracted_intent=TicketIntent.REFUND.value,
        requires_manager_approval=False,
        database_session=isolated_ticket_database_session,
    )

    assert created_ticket["doc_id"] == 202
    assert created_ticket["intent_category"] == TicketIntent.REFUND.value
    assert created_ticket["status"] == TicketStatus.NEW.value
    assert created_ticket["assigned_to"] is None


@pytest.mark.asyncio
async def test_grant_manager_approval_moves_pending_ticket_to_new_status(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_ticket_requiring_approval = await ticket_service.create_new_ticket(
        document_id=303,
        extracted_intent=TicketIntent.STOCK_PROCUREMENT.value,
        requires_manager_approval=True,
        database_session=isolated_ticket_database_session,
    )

    approved_ticket = await ticket_service.grant_manager_approval(
        ticket_id=created_ticket_requiring_approval["id"],
        approving_manager_id=77,
        database_session=isolated_ticket_database_session,
    )

    assert approved_ticket["id"] == created_ticket_requiring_approval["id"]
    assert approved_ticket["status"] == TicketStatus.NEW.value
    assert approved_ticket["assigned_to"] == 77


@pytest.mark.asyncio
async def test_grant_manager_approval_raises_value_error_when_ticket_is_not_pending_approval(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_ticket_not_requiring_approval = await ticket_service.create_new_ticket(
        document_id=404,
        extracted_intent=TicketIntent.REFUND.value,
        requires_manager_approval=False,
        database_session=isolated_ticket_database_session,
    )

    with pytest.raises(
        ValueError,
        match="Only tickets with PENDING_APPROVAL status can receive manager approval.",
    ):
        await ticket_service.grant_manager_approval(
            ticket_id=created_ticket_not_requiring_approval["id"],
            approving_manager_id=88,
            database_session=isolated_ticket_database_session,
        )


@pytest.mark.asyncio
async def test_mark_ticket_as_completed_moves_new_ticket_to_completed_status(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_new_ticket = await ticket_service.create_new_ticket(
        document_id=505,
        extracted_intent=TicketIntent.ORDER_PLACEMENT.value,
        requires_manager_approval=False,
        database_session=isolated_ticket_database_session,
    )

    completed_ticket = await ticket_service.mark_ticket_as_completed(
        ticket_id=created_new_ticket["id"],
        database_session=isolated_ticket_database_session,
    )

    assert completed_ticket["id"] == created_new_ticket["id"]
    assert completed_ticket["status"] == TicketStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_mark_ticket_as_completed_raises_value_error_when_ticket_is_not_new(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    created_pending_approval_ticket = await ticket_service.create_new_ticket(
        document_id=606,
        extracted_intent=TicketIntent.STOCK_PROCUREMENT.value,
        requires_manager_approval=True,
        database_session=isolated_ticket_database_session,
    )

    with pytest.raises(
        ValueError,
        match="Only tickets with NEW status can be marked as completed.",
    ):
        await ticket_service.mark_ticket_as_completed(
            ticket_id=created_pending_approval_ticket["id"],
            database_session=isolated_ticket_database_session,
        )


@pytest.mark.asyncio
async def test_get_pending_approval_tickets_returns_only_pending_approval_records(
    isolated_ticket_database_session: AsyncSession,
) -> None:
    ticket_service = TicketService()

    first_pending_approval_ticket = await ticket_service.create_new_ticket(
        document_id=707,
        extracted_intent=TicketIntent.ORDER_PLACEMENT.value,
        requires_manager_approval=True,
        database_session=isolated_ticket_database_session,
    )
    await ticket_service.create_new_ticket(
        document_id=808,
        extracted_intent=TicketIntent.REFUND.value,
        requires_manager_approval=False,
        database_session=isolated_ticket_database_session,
    )
    second_pending_approval_ticket = await ticket_service.create_new_ticket(
        document_id=909,
        extracted_intent=TicketIntent.STOCK_PROCUREMENT.value,
        requires_manager_approval=True,
        database_session=isolated_ticket_database_session,
    )

    pending_approval_tickets = await ticket_service.get_pending_approval_tickets(
        isolated_ticket_database_session
    )

    pending_approval_ticket_ids = {
        pending_approval_ticket["id"]
        for pending_approval_ticket in pending_approval_tickets
    }

    assert pending_approval_ticket_ids == {
        first_pending_approval_ticket["id"],
        second_pending_approval_ticket["id"],
    }
    assert all(
        pending_approval_ticket["status"] == TicketStatus.PENDING_APPROVAL.value
        for pending_approval_ticket in pending_approval_tickets
    )

    persisted_tickets_result = await isolated_ticket_database_session.execute(
        select(tickets_table)
    )
    persisted_tickets = persisted_tickets_result.mappings().all()
    assert len(persisted_tickets) == 3
