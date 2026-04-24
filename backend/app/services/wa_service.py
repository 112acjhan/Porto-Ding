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
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.save_dir = "downloaded_media"
        self.seen_users_file = "seen_users.txt"

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def save_to_log(self, text: str):   
        with open("whatsapp_history.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f" Logged text: {text}")

    
    def send_onboarding_text(self, to_number: str):
        if not self.phone_number_id:
            print(" Error: WHATSAPP_PHONE_NUMBER_ID is not set in .env")
            return
            
        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": (
                    "Welcome to our *SME Assistant!* 🌟\n\n"
                    "To help us process your request, please reply with the following details in *ONE* message:\n\n"
                    "1️⃣ *Full Name:*\n"
                    "2️⃣ *IC Number:*\n"
                    "3️⃣ *Purpose:* (Complaint / Inquiry / Booking)\n"
                    "4️⃣ *Detailed Description:*\n\n"
                    "Thank you for your cooperation!"
                )
            }
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            print(f" Text reply status: {res.json()}")
            return res.json()
        except Exception as e:
            print(f" Failed to send text: {e}")
            return None

    # identified new user
    def is_new_user(self, phone_number: str):
        if not os.path.exists(self.seen_users_file):
            return True
        with open(self.seen_users_file, "r") as f:
            seen_users = f.read().splitlines()
        return phone_number not in seen_users

    def mark_user_as_seen(self, phone_number: str):
        with open(self.seen_users_file, "a") as f:
            f.write(phone_number + "\n")

    def download_media(self, media_id: str, filename: str):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            download_url = res.json().get('url')
            if download_url:
                file_res = requests.get(download_url, headers=headers)
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(file_res.content)
                print(f" Media saved: {file_path}")
                return file_path
        except Exception as e:
            print(f" Media download error: {e}")
            return None