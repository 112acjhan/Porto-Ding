import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Configuration from Environment Variables ---
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "Alex_SME_2026")
RAW_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")

# Core: Clean Token to prevent encoding errors (e.g., latin-1)
ACCESS_TOKEN = RAW_ACCESS_TOKEN.encode('ascii', 'ignore').decode('ascii').strip()

SAVE_DIR = "downloaded_media"

# Ensure the media directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route("/webhook/whatsapp", methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook/whatsapp", methods=['POST'])
def handle_messages():
    data = request.get_json()
    
    if data.get('entry'):
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for message in value['messages']:
                        sender = message['from']
                        msg_type = message['type']
                        
                        # 1. Handle text messages
                        if msg_type == 'text':
                            text = message['text']['body']
                            log_msg = f"User {sender}: {text}"
                            save_to_log(log_msg)
                        
                        # 2. Handle media files (image, document, video)
                        elif msg_type in ['image', 'document', 'video']:
                            media_id = message[msg_type]['id']
                            # Determine file extension
                            ext = "jpg" if msg_type == "image" else "pdf"
                            filename = f"{sender}_{media_id}.{ext}"
                            download_and_save_media(media_id, filename)

    return "OK", 200, {'ngrok-skip-browser-warning': 'true'}

def save_to_log(text):
    with open("whatsapp_history.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"📝 Logged text: {text}")

def download_and_save_media(media_id, filename):
    # Step 1: Request download URL from Meta
    auth_header = f"Bearer {ACCESS_TOKEN}"
    headers = {"Authorization": auth_header}
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    
    try:
        res = requests.get(url, headers=headers)
        res_data = res.json()
        download_url = res_data.get('url')
        
        if download_url:
            # Step 2: Download the actual file
            file_res = requests.get(download_url, headers=headers)
            file_path = os.path.join(SAVE_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(file_res.content)
            print(f"📁 Media saved successfully: {file_path}")
        else:
            print(f"⚠️ Meta Error (Check if Token is expired): {res_data}")
    except Exception as e:
        print(f"❌ Error during media download: {e}")

if __name__ == "__main__":
    if not ACCESS_TOKEN:
        print("❌ Warning: WHATSAPP_ACCESS_TOKEN not found in .env!")
    else:
        print(f"✅ Token loaded (Length: {len(ACCESS_TOKEN)}). Server Ready...")
    app.run(port=5000)