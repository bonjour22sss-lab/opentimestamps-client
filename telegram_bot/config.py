import os
from dotenv import load_dotenv

load_dotenv()

def get_telegram_token():
    return os.getenv("TELEGRAM_BOT_TOKEN")
