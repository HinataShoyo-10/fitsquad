import time
import os
import requests
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()
telegram_token = os.getenv("telegram_token")
chat_id = os.getenv("chat_id")

IST = pytz.timezone("Asia/Kolkata")

# === Telegram Bot Function ===
def telegram_bot_send(message):
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.get(url, params=payload)
        return response.status_code == 200

    except Exception as error:
        print(f"Telegram Error: {error}")
        return False

# === Notification Trigger ===
def send_notification():
    try:
        res = requests.get("https://dev-fitsquad.onrender.com/trigger_notifications")
        print(res)
        return res.status_code == 200

    except Exception as error:
        telegram_bot_send(f"⚠️ Error triggering notification: {error}")
        return False

# === Sleep Logic ===
def sleep_until_next_7am():
    now = datetime.now(IST)
    tomorrow_8am = (now + timedelta(days=1)).replace(hour=8, minute=25, second=0, microsecond=0)
    seconds = (tomorrow_8am - now).total_seconds()
    telegram_bot_send(f"😴 Notifications -- sleep Mode activated")
    time.sleep(seconds)

# === Main Scheduler ===
while True:
    now = datetime.now(IST)
    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    if now.hour == 19 and now.minute == 15:
        if send_notification():
            telegram_bot_send(f"✅ Notification sent at {current_time_str}")
        else:
            telegram_bot_send(f"❌ Notification failed at {current_time_str}")
        
        sleep_until_next_7am()
    else:
        time.sleep(60)