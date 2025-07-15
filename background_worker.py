import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
telegram_token = os.getenv("telegram_token")
chat_id = os.getenv("chat_id")

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
        return True

    except Exception as error:
        print(error)
        telegram_bot_send(f"⚠️ Error triggering notification: {error}")
        return False


# === Start background thread ===
if __name__ == '__main__':
    if(send_notification()):
        telegram_bot_send("Notifications Triggered Succesfully")
    else:
        telegram_bot_send("Error Triggering Notifications")