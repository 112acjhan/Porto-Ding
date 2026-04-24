import os
import telebot
from dotenv import load_dotenv

load_dotenv()

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = telebot.TeleBot(self.bot_token, threaded=False)
        self.save_dir = "downloaded_media_tele"
        self.log_file = "tele_history.txt"

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def log_text(self, user_name: str, text: str):
        log_entry = f"Tele User {user_name}: {text}"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        print(f" Tele message logged: {log_entry}")

    def download_tele_file(self, file_id: str, file_name: str):
        try:
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            
            save_path = os.path.join(self.save_dir, file_name)
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            print(f" Tele file saved: {save_path}")
            return save_path
        except Exception as e:
            print(f" Tele download failed: {e}")
            return None

    def process_update(self, json_data: dict):
        """Processes raw JSON from the FastAPI webhook."""
        update = telebot.types.Update.de_json(json_data)
        self.bot.process_new_updates([update])