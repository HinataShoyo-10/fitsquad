import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

notifications = [
    {"title": "Yo, Beast!", "message": "Did you crush the gym today or what?"},
    {"title": "Reps or Regrets?", "message": "Only one belongs in your log. 👀"},
    {"title": "Sweat Check!", "message": "Logged your grind yet? Don't skip!"},
    {"title": "Gym Called 📞", "message": "It’s wondering where you are!"},
    {"title": "Leg Day or Nah?", "message": "C’mon, your squat log misses you."},
    {"title": "Grind Time 🕒", "message": "Did you lift today or just lift snacks?"},
    {"title": "Beast Mode Pending…", "message": "Time to log those gains!"},
    {"title": "Push It Real Good 🎶", "message": "Did you push today? Log it!"},
    {"title": "You Flexin’ Yet?", "message": "If yes, it better be in the app!"},
    {"title": "Gym Rat Check-in 🐀", "message": "You in or you hiding today?"},
    {"title": "Tiny Pump Reminder 💥", "message": "Get in, get sweaty, get logged!"},
    {"title": "Hey Hulk!", "message": "Did you smash or snooze?"},
    {"title": "Workout Wizard 🧙‍♂️", "message": "Cast a log spell today yet?"},
    {"title": "DOMS Incoming 🚨", "message": "But first—log that burn!"},
    {"title": "You Lift, You Log", "message": "That’s the rule. Did you follow?"},
    {"title": "Iron Doesn’t Lift Itself!", "message": "But you do. Let’s log it!"},
    {"title": "Mirror Misses You!", "message": "So does your logbook."},
    {"title": "Training Tuesday?", "message": "Or nap-tastic Tuesday? Log the truth!"},
    {"title": "Swipe Up, Bulk Up", "message": "Log those lifts, legend."},
    {"title": "That Gym Glow Tho ✨", "message": "Let’s get that energy logged!"},
    {"title": "Benched or Beastin’?", "message": "Either way, log it like a boss."},
    {"title": "Hey, Fit Machine 🏋️", "message": "Done sweating? Let the log know!"},
    {"title": "Shred Season?", "message": "Only if it’s logged, buddy!"},
    {"title": "Work Out Loud 💬", "message": "Your log’s waiting. Brag a little."},
    {"title": "Crushed It Today?", "message": "Drop those stats in the app 💪"},
    {"title": "Still Sore?", "message": "Must’ve been a good one. Log it!"},
    {"title": "No Gains Without Logs!", "message": "You know it. Go update it!"},
    {"title": "Spotted You… Not Logging", "message": "Come back and finish strong!"},
    {"title": "Reps or Netflix?", "message": "Hope you picked right. Log the truth!"},
    {"title": "That Post-Pump High 🔥", "message": "Capture it in your log before it fades!"},

    {"title": "Did You Hit the Gym?", "message": "No better time than now—go log it!"},
    {"title": "Workout Complete?", "message": "Mark it down and flex with pride."},
    {"title": "Training Logged?", "message": "Because those gains deserve recognition."},
    {"title": "Gym Session Done?", "message": "Then seal it in the app."},
    {"title": "Lifted Today?", "message": "Let your log do the talking."},
    {"title": "Moved or Snoozed?", "message": "Either way, time to check in."},
    {"title": "Finished Your Sets?", "message": "End strong—log stronger."},
    {"title": "Daily Grind Done?", "message": "Drop the data, champ!"},
    {"title": "Workout Tracked Yet?", "message": "Let’s not let it slip."},
    {"title": "Earn That Rest!", "message": "Just make sure it’s logged first."}
]



def send_PushNotification():
    try:
        selected = random.choice(notifications)
        title=selected["title"]
        message = selected["message"]
        Target_URL = "https://fitsquad.onrender.com/"
            
        headers = {
            'webpushrKey': os.getenv("webpushrKey"),
            'webpushrAuthToken': os.getenv("webpushrAuthToken"),
            'Content-Type': 'application/json',
        }

        data = f'{{"title": "{title}", "message": "{message}", "target_url": "{Target_URL}"}}'

        response = requests.post('https://api.webpushr.com/v1/notification/send/all', headers=headers, data=data)
        print(response)

        return response.status_code

    except Exception as error:
        print(error)


