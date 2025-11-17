import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 🔹 Load environment variables
load_dotenv()

app = Flask(__name__)

# 🔐 Meta (WhatsApp Cloud API) credentials
ACCESS_TOKEN = "EAA9n4jLNxPgBP088W2ykzo6HgvQICEnajrXKxzk8VcTxohISoJCQM5mQhikopS4nqvRZAMFkgZBaA9XrrDxhZAkEiuPRXBfWUjQ6Khw2EHCgwLCzqm6ZCWGR97VXTqqsUu4wE9oy5JgFze1cOZBZBycqHxbhGcZBVa77qFUUZAZC0g9A6r0ZBc6c6h0t0JjLJ4WSaNZAZAWXv3KdBwC88RtVh1cEXWH8OjEmnZAD0ZBPqVZA4j2cPcx4yPvAIlpE1OffQdQrKpF0M4spImZAoWUB8suuGprEOLOxAwZDZD"
PHONE_NUMBER_ID = "865001720029861"
VERIFY_TOKEN = "971662"

# 🔑 OpenAI setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ✅ Webhook verification (Meta setup)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification token mismatch", 403


# 📩 Handle incoming messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)

    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            from_number = message["from"]
            msg_body = message.get("text", {}).get("body", "").lower()

            print(f"👤 From: {from_number}\n💬 Message: {msg_body}")

            # If user says hi, show buttons
            if msg_body in ["hi", "hello", "hey"]:
                send_interactive_buttons(from_number)
            else:
                # Use AI for intelligent replies
                ai_reply = get_ai_response(msg_body)
                send_text_message(from_number, ai_reply)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ Error processing message:", e)
        return jsonify({"error": str(e)}), 200


# 💬 Send text message
def send_text_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent text message:", response.status_code, response.text)


# 🧩 Send interactive message with 3 buttons
def send_interactive_buttons(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "👋 Welcome to Clothing Assistant! What would you like to explore today?"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "polo_btn", "title": "Polo Shirts 👕"}},
                    {"type": "reply", "reply": {"id": "jeans_btn", "title": "Jeans 👖"}},
                    {"type": "reply", "reply": {"id": "help_btn", "title": "Need Help 💬"}}
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent interactive message:", response.status_code, response.text)


# 🧠 Generate smart reply using OpenAI
def get_ai_response(user_message):
    try:
        prompt = f"""
        You are a friendly WhatsApp clothing shopping assistant that understands both English and Nigerian Pidgin.
        Help users find clothes (like jeans, polo shirts, gowns, native wear, etc.).
        Respond briefly, naturally, and politely.
        User: {user_message}
        Assistant:
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly clothing shop assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        ai_text = response.choices[0].message.content.strip()
        return ai_text

    except Exception as e:
        print("❌ OpenAI error:", e)
        return "Sorry, I get small network issue. Try again, abeg 😅"


# 🚀 Run Flask server
if __name__ == '__main__':
    app.run(port=5000, debug=True)

