import time
import os
import requests
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# Load environment variables
load_dotenv()
telegram_token = os.getenv("telegram_token")
chat_id = os.getenv("chat_id")

# Set timezone
IST = pytz.timezone("Asia/Kolkata")

# === Flask app ===
app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Bot is running!", 200

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
        res = requests.get("https://dev-fitsquad.onrender.com/send_notifications")
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

# === Background Scheduler Thread ===
def run_scheduler():
    while True:
        now = datetime.now(IST)
        current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

        if now.hour == 19 and now.minute == 45:
            if send_notification():
                telegram_bot_send(f"✅ Notification sent at {current_time_str}")
            else:
                telegram_bot_send(f"❌ Notification failed at {current_time_str}")
            sleep_until_next_7am()
        else:
            time.sleep(60)

# === Start background thread ===
if __name__ == '__main__':
    Thread(target=run_scheduler, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
