import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Vérification du webhook (Facebook appelle cette URL pour vérifier ton bot)
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Invalid verification token", 403


# ✅ Réception des messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry.get("messaging", []):
                sender_id = messaging["sender"]["id"]

                if "message" in messaging and "text" in messaging["message"]:
                    user_message = messaging["message"]["text"]

                    # Réponse avec OpenAI
                    reply = ask_openai(user_message)

                    # Envoyer la réponse à Messenger
                    send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200


# ✅ Fonction pour appeler l’API OpenAI
def ask_openai(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "Désolé, je n'ai pas pu répondre."


# ✅ Fonction pour envoyer un message sur Messenger
def send_message(recipient_id, message):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, headers=headers, json=payload)


@app.route('/')
def index():
    return "✅ Bot is running on Render!"


if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
