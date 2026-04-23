from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, Response
from services.wa_service import WhatsAppService

router = APIRouter(prefix="/webhook/whatsapp", tags=["WhatsApp"])
wa_service = WhatsAppService()

@router.get("/", response_class=PlainTextResponse)
async def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    # Verification logic using the service's token
    if mode == "subscribe" and token == wa_service.verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/")
async def handle_messages(request: Request):
    data = await request.json()

    # Process Meta's nested JSON structure
    if data.get('entry'):
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        msg_type = message['type']
                        
                        # 1. Logic for Text
                        if msg_type == 'text':
                            text = message['text']['body']
                            wa_service.save_to_log(f"User {sender}: {text}")
                        
                        # 2. Logic for Media
                        elif msg_type in ['image', 'document', 'video']:
                            media_id = message[msg_type]['id']
                            ext = "jpg" if msg_type == "image" else "pdf"
                            filename = f"{sender}_{media_id}.{ext}"
                            wa_service.download_media(media_id, filename)

    return Response(content="OK", status_code=200)