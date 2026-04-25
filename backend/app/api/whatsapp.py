from fastapi import APIRouter, Request, Query, HTTPException, Depends
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.services.wa_service import WhatsAppService
from app.api.intake import orchestrator # Import your brain!
from app.api.tickets import DatabaseSessionFactory # Import the DB generator

router = APIRouter(prefix="/webhook/whatsapp", tags=["WhatsApp"])
wa_service = WhatsAppService()

@router.get("/", response_class=PlainTextResponse)
async def verify(mode: str = Query(None, alias="hub.mode"), token: str = Query(None, alias="hub.verify_token"), challenge: str = Query(None, alias="hub.challenge")):
    if mode == "subscribe" and token == wa_service.verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/")
async def handle_messages(request: Request):
    data = await request.json()

    if data.get('entry'):
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        msg_type = message['type']
                        
                        # Open a database session for the Orchestrator
                        async with DatabaseSessionFactory() as db:
                            
                            # 1. TEXT MESSAGES
                            if msg_type == 'text':
                                text = message['text']['body']
                                # Send to the AI Brain!
                                await orchestrator.process_text_input(
                                    raw_text=text,
                                    sender_id=sender,
                                    user_role="SYSTEM", # Bots act as SYSTEM
                                    source_platform="WHATSAPP",
                                    database_session=db
                                )
                            
                            # 2. MEDIA MESSAGES (Images/PDFs)
                            elif msg_type in ['image', 'document']:
                                media_id = message[msg_type]['id']
                                ext = "jpg" if msg_type == "image" else "pdf"
                                filename = f"{sender}_{media_id}.{ext}"
                                
                                # Download it locally
                                file_path = await wa_service.download_media(media_id, filename)
                                
                                if file_path:
                                    # Read bytes and send to Orchestrator Document pipeline!
                                    with open(file_path, "rb") as f:
                                        file_bytes = f.read()
                                        
                                    await orchestrator.process_document_input(
                                        file_bytes=file_bytes,
                                        file_name=filename,
                                        sender_id=sender,
                                        user_role="SYSTEM",
                                        source_platform="WHATSAPP",
                                        uploader_id=None,
                                        database_session=db
                                    )
                                    # Clean up local file after processing
                                    os.remove(file_path)

    return Response(content="OK", status_code=200)