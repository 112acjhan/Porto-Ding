import uvicorn
from fastapi import FastAPI, Request, Response
from app.services.wa_service import WhatsAppService
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
wa_service = WhatsAppService()

# 1. 处理 Meta 的验证 (GET)
@app.get("/webhook/whatsapp")
async def verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    if mode == "subscribe" and token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        print("✅ Webhook Verified!")
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)

# 2. 处理 WhatsApp 消息 (POST)
@app.post("/webhook/whatsapp")
async def webhook(request: Request):
    data = await request.json()
    print("📩 Received Data:", data)
    
    # 提取号码
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message['from']
            
            # --- 这一部分是 Leader 的逻辑 ---
            if message['type'] == 'text':
                wa_service.save_to_log(f"User {sender}: {message['text']['body']}")
            
            # --- 这一部分是你的 Plan B 自动回复 ---
            # 只要收到消息，就触发你的欢迎语
            print(f"🚀 Triggering Plan B reply to: {sender}")
            wa_service.send_onboarding_text(sender)
            
    except Exception as e:
        print(f"Error: {e}")

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)