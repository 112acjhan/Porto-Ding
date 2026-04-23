import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "Alex_SME_2026")
        raw_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        # Clean Token
        self.access_token = raw_token.encode('ascii', 'ignore').decode('ascii').strip()
        self.save_dir = "downloaded_media"

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def save_to_log(self, text: str):
        with open("whatsapp_history.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"📝 Logged text: {text}")

    def download_media(self, media_id: str, filename: str):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        
        try:
            # Step 1: Get download URL
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            download_url = res.json().get('url')
            
            if download_url:
                # Step 2: Download file
                file_res = requests.get(download_url, headers=headers)
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(file_res.content)
                print(f"📁 Media saved: {file_path}")
                return file_path
        except Exception as e:
            print(f"❌ Media download error: {e}")
            return None