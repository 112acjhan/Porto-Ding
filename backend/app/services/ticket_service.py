from enum import Enum
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import ENUM as PostgreSqlEnum
from sqlalchemy.ext.asyncio import AsyncSession


class TicketStatus(str, Enum):
    NEW = "NEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


metadata = MetaData()

tickets_table = Table(
    "tickets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("document_id", Integer, nullable=False),
    Column("extracted_intent", String, nullable=False),
    Column(
        "status",
        PostgreSqlEnum(
            TicketStatus.NEW.value,
            TicketStatus.PENDING_APPROVAL.value,
            TicketStatus.COMPLETED.value,
            TicketStatus.FAILED.value,
            name="ticket_status",
            create_type=False,
        ),
        nullable=False,
    ),
    Column("approving_manager_id", Integer, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)


class TicketService:
    async def create_new_ticket(
        self,
        document_id: int,
        extracted_intent: str,
        requires_manager_approval: bool,
        database_session: AsyncSession,
    ) -> dict:
        initial_ticket_status = (
            TicketStatus.PENDING_APPROVAL
            if requires_manager_approval
            else TicketStatus.NEW
        )

        create_ticket_statement = (
            insert(tickets_table)
            .values(
                document_id=document_id,
                extracted_intent=extracted_intent,
                status=initial_ticket_status.value,
            )
            .returning(*tickets_table.c)
        )

        created_ticket_result = await database_session.execute(create_ticket_statement)
        created_ticket = created_ticket_result.mappings().one()
        await database_session.commit()

        return self._format_ticket_response(created_ticket)

    async def get_pending_approval_tickets(
        self,
        database_session: AsyncSession,
    ) -> list[dict]:
        get_pending_tickets_statement = select(tickets_table).where(
            tickets_table.c.status == TicketStatus.PENDING_APPROVAL.value
        )
        pending_tickets_result = await database_session.execute(get_pending_tickets_statement)
        pending_tickets = pending_tickets_result.mappings().all()

        return [
            self._format_ticket_response(pending_ticket)
            for pending_ticket in pending_tickets
        ]

    async def grant_manager_approval(
        self,
        ticket_id: int,
        approving_manager_id: int,
        database_session: AsyncSession,
    ) -> dict:
        approve_ticket_statement = (
            update(tickets_table)
            .where(
                tickets_table.c.id == ticket_id,
                tickets_table.c.status == TicketStatus.PENDING_APPROVAL.value,
            )
            .values(
                status=TicketStatus.NEW.value,
                approving_manager_id=approving_manager_id,
                updated_at=func.now(),
            )
            .returning(*tickets_table.c)
        )

        approved_ticket_result = await database_session.execute(approve_ticket_statement)
        approved_ticket = approved_ticket_result.mappings().one_or_none()

        if approved_ticket is None:
            await self._get_ticket_by_id(ticket_id, database_session)
            raise ValueError("Only tickets with PENDING_APPROVAL status can receive manager approval.")

        await database_session.commit()

        return self._format_ticket_response(approved_ticket)

    async def mark_ticket_as_completed(
        self,
        ticket_id: int,
        database_session: AsyncSession,
    ) -> dict:
        complete_ticket_statement = (
            update(tickets_table)
            .where(
                tickets_table.c.id == ticket_id,
                tickets_table.c.status == TicketStatus.NEW.value,
            )
            .values(
                status=TicketStatus.COMPLETED.value,
                updated_at=func.now(),
            )
            .returning(*tickets_table.c)
        )

        completed_ticket_result = await database_session.execute(complete_ticket_statement)
        completed_ticket = completed_ticket_result.mappings().one_or_none()

        if completed_ticket is None:
            await self._get_ticket_by_id(ticket_id, database_session)
            raise ValueError("Only tickets with NEW status can be marked as completed.")

        await database_session.commit()

        return self._format_ticket_response(completed_ticket)

    async def _get_ticket_by_id(
        self,
        ticket_id: int,
        database_session: AsyncSession,
    ) -> dict:
        get_ticket_statement = select(tickets_table).where(tickets_table.c.id == ticket_id)
        ticket_result = await database_session.execute(get_ticket_statement)
        ticket = ticket_result.mappings().one_or_none()

        if ticket is None:
            raise ValueError(f"Ticket with id {ticket_id} was not found.")

        return self._format_ticket_response(ticket)

    def _format_ticket_response(self, ticket_record: Any) -> dict:
        ticket_dictionary = dict(ticket_record)

        for date_field_name in ("created_at", "updated_at"):
            date_field_value = ticket_dictionary.get(date_field_name)
            if date_field_value is not None:
                ticket_dictionary[date_field_name] = date_field_value.isoformat()

        return ticket_dictionary
