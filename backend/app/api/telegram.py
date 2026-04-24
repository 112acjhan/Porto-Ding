from fastapi import APIRouter, Request, Response
from app.services.tele_service import TelegramService

router = APIRouter(prefix="/webhook/telegram", tags=["Telegram"])
tele_service = TelegramService()

@tele_service.bot.message_handler(content_types=['text'])
def handle_text(message):
    user_name = message.from_user.first_name
    tele_service.log_text(user_name, message.text)

@tele_service.bot.message_handler(content_types=['document', 'photo'])
def handle_docs(message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_name = f"{file_id}.jpg"
    else:
        file_id = message.document.file_id
        file_name = message.document.file_name
    
    tele_service.download_tele_file(file_id, file_name)

@router.post("/")
async def telegram_webhook(request: Request):
    """Entry point for Telegram's POST request."""
    json_data = await request.json()
    tele_service.process_update(json_data)
    return Response(content="OK", status_code=200)