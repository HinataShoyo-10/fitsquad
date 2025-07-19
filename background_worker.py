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
def send_notification(env):
    try:
        messages = []

        if env in ["dev", "both"]:
            dev_res = requests.get("https://dev-fitsquad.onrender.com/send_notifications")
            messages.append(f" Dev: {dev_res.status_code} ")

        if env in ["prod", "both"]:
            prod_res = requests.get("https://fitsquad.onrender.com/send_notifications")
            messages.append(f"Prod: {prod_res.status_code} ")

        print("\n".join(messages))
        return True, "\n".join(messages)

    except Exception as error:
        print(f"❌ Error: {error}")
        return False, f"⚠️ Error triggering notification: {error}"


# === Start background thread ===
if __name__ == '__main__':
    success, msg = send_notification(env="both")  # Change to "prod" or "dev" if needed

    if success:
        telegram_bot_send(f"📢 Notifications Triggered Successfully\n\n{msg}")
    else:
        telegram_bot_send(msg)