from enum import Enum
from typing import Any
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, MetaData, Table, String, Text, DateTime,
    insert, select, update,
)
from sqlalchemy.dialects.postgresql import ENUM as PostgreSqlEnum
from sqlalchemy.ext.asyncio import AsyncSession

# --- Enums ---
class TicketIntent(str, Enum):
    ORDER_PLACEMENT = "ORDER_PLACEMENT"
    STOCK_PROCUREMENT = "STOCK_PROCUREMENT"
    REFUND = "REFUND"

class TicketStatus(str, Enum):
    NEW = "NEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

metadata = MetaData()

# --- New Tables from Claude Architecture ---
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(128), unique=True, nullable=False),
    # Changed from PostgreSqlEnum to String
    Column("role", String(50), nullable=False), 
    Column("password_hash", String(256), nullable=False),
)

external_entities_table = Table(
    "external_entities",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("identifier", String(128), unique=True, nullable=False),   
    Column("display_name", String(256), nullable=True),
    # Changed from PostgreSqlEnum to String
    Column("entity_type", String(50), nullable=False),
    Column("full_ic_no", String(20), nullable=True),
    Column("full_bank_acc", String(20), nullable=True),
)

documents_table = Table(
    "documents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("unique_hash", String(64), unique=True, nullable=False),
    Column("gcs_url", Text, nullable=True),
    Column("uploader_id", Integer, nullable=True),
    Column("entity_id", Integer, nullable=True),
    # Changed from PostgreSqlEnum to String
    Column("source_platform", String(50), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=True),
)

audit_logs_table = Table(
    "audit_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=True),
    Column("action", String(128), nullable=False),
    Column("target_id", Integer, nullable=True),
    Column("timestamp", DateTime(timezone=True), nullable=True),
)

tickets_table = Table(
    "tickets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("doc_id", Integer, nullable=True),
    # Changed from PostgreSqlEnum to String
    Column("intent_category", String(50), nullable=False),
    # Changed from PostgreSqlEnum to String
    Column("status", String(50), nullable=False),
    Column("deadline", Integer, nullable=True),
    Column("assigned_to", Integer, nullable=True),
)

class TicketService:
    # Existing methods remain the same, ensuring they use AsyncSession
    async def create_new_ticket(self, document_id: int, extracted_intent: str, requires_manager_approval: bool, database_session: AsyncSession) -> dict:
        initial_ticket_status = TicketStatus.PENDING_APPROVAL if requires_manager_approval else TicketStatus.NEW
        create_ticket_statement = (
            insert(tickets_table).values(
                doc_id=document_id,
                intent_category=extracted_intent,
                status=initial_ticket_status.value,
            ).returning(*tickets_table.c)
        )
        result = await database_session.execute(create_ticket_statement)
        created_ticket = result.mappings().one()
        await database_session.commit()
        return dict(created_ticket)
    
    async def claim_ticket(self, ticket_id: int, staff_id: int, database_session: AsyncSession) -> dict:
        stmt = (
            update(tickets_table)
            .where(tickets_table.c.id == ticket_id, tickets_table.c.status == TicketStatus.NEW.value)
            .values(status=TicketStatus.IN_PROGRESS.value, assigned_to=staff_id)
            .returning(*tickets_table.c)
        )
        res = await database_session.execute(stmt)
        await database_session.commit()
        return dict(res.mappings().one())

    async def get_all_active_tickets(self, database_session: AsyncSession) -> list[dict]:
        # Gets everything that isn't finished yet
        stmt = select(tickets_table).where(tickets_table.c.status != TicketStatus.COMPLETED.value)
        result = await database_session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def get_pending_approval_tickets(self, database_session: AsyncSession) -> list[dict]:
        stmt = select(tickets_table).where(tickets_table.c.status == TicketStatus.PENDING_APPROVAL.value)
        result = await database_session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

    async def grant_manager_approval(self, ticket_id: int, approving_manager_id: int, database_session: AsyncSession) -> dict:
        stmt = (
            update(tickets_table)
            .where(tickets_table.c.id == ticket_id, tickets_table.c.status == TicketStatus.PENDING_APPROVAL.value)
            .values(status=TicketStatus.NEW.value, assigned_to=approving_manager_id)
            .returning(*tickets_table.c)
        )
        result = await database_session.execute(stmt)
        record = result.mappings().one_or_none()
        if not record: raise ValueError("Ticket not found or already approved")
        await database_session.commit()
        return dict(record)
    
    async def get_or_create_external_entity(
        self, 
        identifier: str, 
        entity_type: str, 
        display_name: str | None,
        ic_no: str | None,
        bank_acc: str | None,
        database_session: AsyncSession
    ) -> int:
        """Checks if an entity exists. If not, creates them. If yes, updates missing details."""
        
        # 1. Search for the entity
        stmt = select(external_entities_table).where(external_entities_table.c.identifier == identifier)
        result = await database_session.execute(stmt)
        existing_entity = result.mappings().one_or_none()

        if existing_entity:
            entity_id = existing_entity["id"]
            
            update_data = {}
            if display_name and not existing_entity["display_name"]: update_data["display_name"] = display_name
            if ic_no and not existing_entity["full_ic_no"]: update_data["full_ic_no"] = ic_no
            if bank_acc and not existing_entity["full_bank_acc"]: update_data["full_bank_acc"] = bank_acc
            
            if update_data:
                upd_stmt = update(external_entities_table).where(external_entities_table.c.id == entity_id).values(**update_data)
                await database_session.execute(upd_stmt)
                
            return entity_id

        # 2. If they don't exist, insert them with ALL data
        insert_stmt = (
            insert(external_entities_table)
            .values(
                identifier=identifier, 
                entity_type=entity_type,
                display_name=display_name,
                full_ic_no=ic_no,
                full_bank_acc=bank_acc
            )
            .returning(external_entities_table.c.id)
        )
        result = await database_session.execute(insert_stmt)
        return result.scalar()

    async def mark_ticket_as_completed(
        self,
        ticket_id: int,
        database_session: AsyncSession,
    ) -> dict:
        complete_ticket_statement = (
            update(tickets_table)
            .where(
                tickets_table.c.id == ticket_id,
                tickets_table.c.status == TicketStatus.IN_PROGRESS.value,
            )
            .values(
                status=TicketStatus.COMPLETED.value,
            )
            .returning(*tickets_table.c)
        )

        completed_ticket_result = await database_session.execute(complete_ticket_statement)
        completed_ticket = completed_ticket_result.mappings().one_or_none()

        if completed_ticket is None:
            # Check if ticket exists to give a better error message
            await self._get_ticket_by_id(ticket_id, database_session)
            raise ValueError("Only tickets with IN_PROGRESS status can be marked as completed.")

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
        return dict(ticket_record)