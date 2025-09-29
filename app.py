import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# Variables d'environnement
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mon_token_secret")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Bot Facebook est en ligne 🚀"

# Vérification du Webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token invalide", 403
    return "Erreur", 400

# Réception des messages
@app.route("/webhook", methods=["POST"])
def handle_messages():
    body = request.get_json()

    if "entry" in body:
        for entry in body["entry"]:
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"].get("text")

                    if user_message:
                        bot_response = ask_openai(user_message)
                        send_message(sender_id, bot_response)

    return "EVENT_RECEIVED", 200

# Fonction OpenAI
def ask_openai(question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant amical sur Messenger."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur API: {str(e)}"

# Fonction d’envoi de message à Messenger
def send_message(user_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
