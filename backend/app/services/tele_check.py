import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SAVE_DIR = "downloaded_media_tele"
LOG_FILE = "tele_history.txt"

bot = telebot.TeleBot(BOT_TOKEN)

# Ensure the media directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 1. Handle and log text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_name = message.from_user.first_name
    text = message.text
    log_entry = f"Tele User {user_name}: {text}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    print(f"📝 Tele message logged: {log_entry}")

# 2. Handle and download files (Document/Photo)
@bot.message_handler(content_types=['document', 'photo'])
def handle_docs(message):
    try:
        # Get file_id (For photos, pick the highest quality)
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_name = f"{file_id}.jpg"
        else:
            file_id = message.document.file_id
            file_name = message.document.file_name

        # Request file path from Telegram
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save to local directory
        save_path = os.path.join(SAVE_DIR, file_name)
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        print(f"📁 Tele file saved successfully: {save_path}")
    except Exception as e:
        print(f"❌ Tele download failed: {e}")

if __name__ == "__main__":
    print("🚀 Telegram monitor started (Polling mode)...")
    bot.polling()