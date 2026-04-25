import os
from typing import AsyncGenerator
from app.models.schemas import InventoryUpdate, InventoryItem
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from app.services.ticket_service import TicketService, tickets_table, metadata, documents_table, external_entities_table
from app.core.config import settings
from app.services.wa_service import WhatsAppService


database_engine = create_async_engine(settings.DATABASE_URL)
DatabaseSessionFactory = async_sessionmaker(
    bind=database_engine,
    expire_on_commit=False,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
ticket_service = TicketService()
wa_service = WhatsAppService()


class ManagerApprovalRequest(BaseModel):
    approving_manager_id: int


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    async with DatabaseSessionFactory() as database_session:
        yield database_session

@router.get("/active")
async def get_active_tickets(db: AsyncSession = Depends(get_database_session)):
    return await ticket_service.get_all_active_tickets(db)

@router.post("/{ticket_id}/claim")
async def claim_ticket(ticket_id: int, staff_id: int, db: AsyncSession = Depends(get_database_session)):
    try:
        ticket = await ticket_service.claim_ticket(ticket_id, staff_id, db)
        await sync_ticket_status_to_rag(ticket_id, "IN_PROGRESS", db)
        return ticket
    except Exception as e:
        raise HTTPException(status_code=400, detail="Ticket already claimed or unavailable")

@router.get("/pending")
async def get_pending_tickets(
    database_session: AsyncSession = Depends(get_database_session),
) -> list[dict]:
    return await ticket_service.get_pending_approval_tickets(database_session)


@router.post("/{ticket_id}/approve")
async def approve_ticket(ticket_id: int, manager_approval_request: ManagerApprovalRequest, database_session: AsyncSession = Depends(get_database_session)) -> dict:
    try:
        # Check intent BEFORE changing status
        get_stmt = select(tickets_table).where(tickets_table.c.id == ticket_id)
        res = await database_session.execute(get_stmt)
        ticket_row = res.mappings().one_or_none()
        
        # 1. Normal approval process (sets to NEW for Staff to see)
        approved_ticket = await ticket_service.grant_manager_approval(ticket_id, manager_approval_request.approving_manager_id, database_session)
        await sync_ticket_status_to_rag(ticket_id, "NEW", database_session)
        
        # 2. IF IT IS A RESTOCK REQUEST, MANAGER APPROVAL IMMEDIATELY FULFILLS IT
        if ticket_row and ticket_row["intent_category"] == "STOCK_PROCUREMENT":
            from sqlalchemy import update
            stmt = update(tickets_table).where(tickets_table.c.id == ticket_id).values(status="COMPLETED").returning(*tickets_table.c)
            res = await database_session.execute(stmt)
            approved_ticket = dict(res.mappings().one())
            await database_session.commit()
            
            await sync_ticket_status_to_rag(ticket_id, "COMPLETED", database_session)
            await update_inventory_and_orders(ticket_id, is_addition=True, db=database_session)

        # 3. WhatsApp Notification logic
        query = (select(external_entities_table.c.identifier).select_from(documents_table.join(external_entities_table, documents_table.c.entity_id == external_entities_table.c.id)).where(documents_table.c.id == approved_ticket["doc_id"]))
        doc_result = await database_session.execute(query)
        recipient_phone = doc_result.scalar()

        if recipient_phone and any(char.isdigit() for char in recipient_phone):
            await send_whatsapp_approval_confirmation(ticket_id, manager_approval_request.approving_manager_id, recipient_phone)

        return approved_ticket
    except ValueError as approval_error:
        raise HTTPException(status_code=400, detail=str(approval_error)) from approval_error


@router.post("/{ticket_id}/complete")
async def complete_ticket(ticket_id: int, database_session: AsyncSession = Depends(get_database_session)) -> dict:
    try:
        get_stmt = select(tickets_table).where(tickets_table.c.id == ticket_id)
        res = await database_session.execute(get_stmt)
        ticket_row = res.mappings().one_or_none()
        
        ticket = await ticket_service.mark_ticket_as_completed(ticket_id, database_session)
        await sync_ticket_status_to_rag(ticket_id, "COMPLETED", database_session)
        
        # WHEN STAFF COMPLETES A CUSTOMER ORDER, DEDUCT INVENTORY
        if ticket_row and ticket_row["intent_category"] == "ORDER_PLACEMENT":
            await update_inventory_and_orders(ticket_id, is_addition=False, db=database_session)
            
        return ticket
    except ValueError as completion_error:
        raise HTTPException(status_code=400, detail=str(completion_error)) from completion_error


async def send_whatsapp_approval_confirmation(
    ticket_id: int,
    approving_manager_id: int,
    recipient_phone: str
) -> dict:
    
    message = (
        f"✅ *Ticket Approved*\n\n"
        f"Ticket ID: #{ticket_id}\n"
        f"Approved By Manager: {approving_manager_id}\n"
        f"Status: Ready for processing."
    )

    response = await wa_service.send_custom_text(recipient_phone, message)

    return {
        "status": "success" if response else "failed",
        "ticket_id": ticket_id,
        "response_data": response
    }

async def sync_ticket_status_to_rag(ticket_id: int, new_status: str, db: AsyncSession):
    """Fetches the document hash and triggers a Qdrant payload update."""
    from app.api.intake import orchestrator
    
    if not orchestrator.rag: 
        return

    # SQL JOIN: Find the unique_hash for this ticket
    query = (
        select(documents_table.c.unique_hash)
        .select_from(
            tickets_table.join(documents_table, tickets_table.c.doc_id == documents_table.c.id)
        )
        .where(tickets_table.c.id == ticket_id)
    )
    result = await db.execute(query)
    unique_hash = result.scalar()

    if unique_hash:
        await orchestrator.rag.update_document_status(unique_hash, new_status)

async def update_inventory_and_orders(ticket_id: int, is_addition: bool, db: AsyncSession):
    from app.api.intake import orchestrator
    if not orchestrator.sheets or not orchestrator.rag: return
    
    # Grab doc_id & hash from database
    query = (
        select(documents_table.c.unique_hash, documents_table.c.id)
        .select_from(tickets_table.join(documents_table, tickets_table.c.doc_id == documents_table.c.id))
        .where(tickets_table.c.id == ticket_id)
    )
    res = await db.execute(query)
    row = res.mappings().one_or_none()
    if not row: return
    
    # Extract Items from RAG
    import uuid
    try:
        point_id = str(uuid.UUID(row["unique_hash"]))
    except ValueError:
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, row["unique_hash"]))
        
    points = orchestrator.rag.vector_db.client.retrieve(
        collection_name=orchestrator.rag.vector_db.collection_name, ids=[point_id]
    )
    items = points[0].payload.get("extracted_entities", {}).get("items", []) if points else []

    # Update Order Status to Fulfilled
    orchestrator.sheets.update_order_status_row(f"ORD-{row['id']}", "Fulfilled")
    
    # Process Inventory Math
    records = orchestrator.sheets.get_all_inventory()
    import time
    for item in items:
        item_name = item.get("item_name") or item.get("item", "Unknown")
        qty = float(item.get("quantity", 0))
        
        found = False
        for inv_row in records:
            if str(inv_row.get("item_name", "")).lower() == item_name.lower():
                found = True
                item_id = str(inv_row.get("item_id"))
                current_stock = float(inv_row.get("stock_level", 0))
                
                # Math based on context (Supplier increases stock, Customer decreases stock)
                new_stock = current_stock + qty if is_addition else current_stock - qty
                orchestrator.sheets.update_inventory_row(item_id, InventoryUpdate(stock_level=new_stock))
                break
                
        # If procuring a brand new item, dynamically create it!
        if not found and is_addition:
            new_item = InventoryItem(
                item_id=f"ITEM-{int(time.time())}",
                item_name=item_name,
                stock_level=qty,
                reorder_point=10.0,
                unit_price=0.0
            )
            orchestrator.sheets.add_inventory_row(new_item)
            
    # Check for Low Stock Audits
    from datetime import datetime, timezone
    from sqlalchemy import insert
    from app.services.ticket_service import audit_logs_table
    
    updated_records = orchestrator.sheets.get_all_inventory()
    for inv_row in updated_records:
        stock = float(inv_row.get("stock_level", 0))
        reorder = float(inv_row.get("reorder_point", 0))
        
        if stock < reorder:
            stmt = insert(audit_logs_table).values(
                action=f"LOW_STOCK_ALERT|{inv_row.get('item_name', 'Unknown')}",
                target_id=None,
                timestamp=datetime.now(timezone.utc)
            )
            await db.execute(stmt)
    await db.commit()