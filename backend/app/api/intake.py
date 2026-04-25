import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from app.api.tickets import get_database_session, ticket_service
from app.core.orchestrator import PortoDingOrchestrator
from app.services.ticket_service import audit_logs_table, documents_table, tickets_table, external_entities_table

router = APIRouter(prefix="/api/intake", tags=["Intake"])
orchestrator = PortoDingOrchestrator(ticket_service=ticket_service)

@router.post("/text")
async def intake_text(
    raw_text: str = Form(...),
    sender_id: str = Form(...),
    user_role: str = Form("STAFF"),
    source_platform: str = Form("WEB"),
    db: AsyncSession = Depends(get_database_session),
):
    return await orchestrator.process_text_input(
        raw_text=raw_text,
        sender_id=sender_id,
        user_role=user_role,
        source_platform=source_platform,
        database_session=db,
    )

@router.post("/document")
async def intake_document(
    file: UploadFile = File(...),
    sender_id: str = Form(...),
    user_role: str = Form("STAFF"),
    source_platform: str = Form("WEB"),
    uploader_id: int | None = Form(None),
    db: AsyncSession = Depends(get_database_session),
):
    # This now correctly reads the file and parses it (PDF/OCR/Excel)
    file_bytes = await file.read()
    return await orchestrator.process_document_input(
        file_bytes=file_bytes,
        file_name=file.filename or "upload.bin",
        sender_id=sender_id,
        user_role=user_role,
        source_platform=source_platform,
        uploader_id=uploader_id,
        database_session=db
    )

@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50, db: AsyncSession = Depends(get_database_session)):
    try:
        result = await db.execute(select(audit_logs_table).order_by(desc(audit_logs_table.c.id)).limit(limit))
        return [dict(row) for row in result.mappings().all()]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/documents")
async def list_documents(
    limit: int = 50, 
    user_role: str = "STAFF",
    user_id: int | None = None,
    db: AsyncSession = Depends(get_database_session)
):
    try:
        # 1. Join documents table with tickets table so we can read the ticket status
        stmt = select(documents_table).select_from(
            documents_table.outerjoin(tickets_table, documents_table.c.id == tickets_table.c.doc_id)
        )

        # 2. Apply Security Filters for Staff
        if user_role.upper() != "MANAGER":
            # Staff can see it IF it is NOT pending approval, OR if they uploaded it
            safe_conditions = [
                tickets_table.c.status != "PENDING_APPROVAL",
                tickets_table.c.status.is_(None) # Fallback if document has no ticket yet
            ]
            
            if user_id:
                # Allow staff to see their own pending documents
                safe_conditions.append(documents_table.c.uploader_id == user_id)
                
            stmt = stmt.where(or_(*safe_conditions))

        # 3. Order by newest
        stmt = stmt.order_by(desc(documents_table.c.created_at)).limit(limit)
        result = await db.execute(stmt)
        
        # 4. Censor the direct download links for staff (Double Security)
        docs = []
        for row in result.mappings().all():
            doc = dict(row)
            if user_role.upper() != "MANAGER":
                doc["gcs_url"] = "[RESTRICTED - View via Extraction Only]"
            docs.append(doc)
            
        return docs

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/documents/{document_id}")
async def get_document(document_id: int, user_role: str = "STAFF", db: AsyncSession = Depends(get_database_session)):
    
    # 1. SQL JOIN: Merge Documents, External Entities, and Tickets
    query = (
        select(
            documents_table,
            external_entities_table.c.display_name,
            external_entities_table.c.identifier,
            tickets_table.c.deadline
        )
        .select_from(
            documents_table
            .outerjoin(external_entities_table, documents_table.c.entity_id == external_entities_table.c.id)
            .outerjoin(tickets_table, documents_table.c.id == tickets_table.c.doc_id)
        )
        .where(documents_table.c.id == document_id)
    )
    
    result = await db.execute(query)
    row = result.mappings().one_or_none()
    
    if not row: 
        raise HTTPException(status_code=404, detail="Document not found.")
        
    doc = dict(row)
    
    if user_role.upper() != "MANAGER":
        doc["gcs_url"] = "[RESTRICTED — Manager access required]"

    # 2. VECTOR DB FETCH: Grab formal_summary and raw_text from Qdrant
    if orchestrator.rag:
        try:
            # Qdrant uses UUIDs. Recreate the UUID from your unique_hash
            try:
                point_id = str(uuid.UUID(doc["unique_hash"]))
            except ValueError:
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc["unique_hash"]))
                
            # Retrieve the payload
            points = orchestrator.rag.vector_db.client.retrieve(
                collection_name=orchestrator.rag.vector_db.collection_name,
                ids=[point_id]
            )
            
            if points:
                payload = points[0].payload
                doc["formal_summary"] = payload.get("text_to_search", "")
                doc["raw_text"] = payload.get("raw_text", "")
        except Exception as e:
            print(f"🚨 [QDRANT FETCH ERROR]: Failed to retrieve extraction text: {e}")
            
    return doc