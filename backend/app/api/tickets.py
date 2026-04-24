import os
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.services.ticket_service import TicketService


dummy_database_url = "postgresql+asyncpg://admin:zai_PortoDing@localhost:5433/zai_vault"

database_url = os.getenv("DATABASE_URL", dummy_database_url)
database_engine = create_async_engine(database_url, future=True)
DatabaseSessionFactory = async_sessionmaker(
    bind=database_engine,
    expire_on_commit=False,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
ticket_service = TicketService()


class ManagerApprovalRequest(BaseModel):
    approving_manager_id: int


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    async with DatabaseSessionFactory() as database_session:
        yield database_session


@router.get("/pending")
async def get_pending_tickets(
    database_session: AsyncSession = Depends(get_database_session),
) -> list[dict]:
    return await ticket_service.get_pending_approval_tickets(database_session)


@router.post("/{ticket_id}/approve")
async def approve_ticket(
    ticket_id: int,
    manager_approval_request: ManagerApprovalRequest,
    database_session: AsyncSession = Depends(get_database_session),
) -> dict:
    try:
        approved_ticket = await ticket_service.grant_manager_approval(
            ticket_id=ticket_id,
            approving_manager_id=manager_approval_request.approving_manager_id,
            database_session=database_session,
        )

        await send_whatsapp_approval_confirmation(
            ticket_id=approved_ticket["id"],
            approving_manager_id=manager_approval_request.approving_manager_id,
        )

        return approved_ticket
    except ValueError as approval_error:
        raise HTTPException(status_code=400, detail=str(approval_error)) from approval_error


@router.post("/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: int,
    database_session: AsyncSession = Depends(get_database_session),
) -> dict:
    try:
        return await ticket_service.mark_ticket_as_completed(
            ticket_id=ticket_id,
            database_session=database_session,
        )
    except ValueError as completion_error:
        raise HTTPException(status_code=400, detail=str(completion_error)) from completion_error


async def send_whatsapp_approval_confirmation(
    ticket_id: int,
    approving_manager_id: int,
) -> dict:
    # TODO: REPLACE WITH ACTUAL SECRETS LATER.
    dummy_whatsapp_api_key = "DUMMY_API_KEY_REPLACE_ME"
    dummy_whatsapp_api_url = "https://dummy-whatsapp-provider.example/messages"

    dummy_whatsapp_api_response = {
        "api_url": dummy_whatsapp_api_url,
        "api_key": dummy_whatsapp_api_key,
        "message_text": "Ticket approved by manager and ready for processing.",
        "ticket_id": ticket_id,
        "approving_manager_id": approving_manager_id,
        "status": "mocked",
    }

    return dummy_whatsapp_api_response
