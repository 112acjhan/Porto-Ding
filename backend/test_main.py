import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import tickets
from app.api.tickets import database_engine, get_database_session, ticket_service
from app.core.orchestrator import PortoDingOrchestrator
from app.services.ticket_service import metadata

app = FastAPI(title="SME Ops Orchestrator Ticket Test App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
orchestrator = PortoDingOrchestrator(ticket_service=ticket_service)


class ProcessMessageDebugRequest(BaseModel):
    raw_request_text: str
    user_role: str = "STAFF"
    source_document_id: int = 999


@app.on_event("startup")
async def startup() -> None:
    async with database_engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "Server is running and healthy"}


@app.post("/api/debug/create-ticket", tags=["Debug"])
async def debug_create_ticket(
    extracted_intent: str = "ORDER_PLACEMENT",
    requires_manager_approval: bool = True,
    database_session: AsyncSession = Depends(get_database_session),
) -> dict:
    return await ticket_service.create_new_ticket(
        document_id=999,
        extracted_intent=extracted_intent,
        requires_manager_approval=requires_manager_approval,
        database_session=database_session,
    )


@app.post("/api/debug/process-message", tags=["Debug"])
async def debug_process_message(
    process_message_request: ProcessMessageDebugRequest,
    database_session: AsyncSession = Depends(get_database_session),
) -> dict:
    return await orchestrator.process_request(
        raw_request_text=process_message_request.raw_request_text,
        user_role=process_message_request.user_role,
        source_document_id=process_message_request.source_document_id,
        database_session=database_session,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
