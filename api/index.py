from flask import Flask, request
import os
import requests
from mistralai import Mistral

app = Flask(__name__)

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

@app.route('/', methods=['POST'])
def groupme_webhook():
    data = request.get_json()
    text = data.get('text', '')

    if text.startswith('!#') and data.get('sender_type') != 'bot':
        user_message = text[2:].strip()

        try:
            chat_response = client.chat.complete(
                 model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant who is happy to answer any questions. Be consise."},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_response = chat_response.choices[0].message.content
            
        except Exception as e:
            if "429" in str(e):
                bot_response = "Mistral is thinking too fast! Wait a few seconds."
            else:
                bot_response = f"Mistral error: {str(e)[:50]}..."

        post_data = {
            "bot_id": os.getenv("GROUPME_BOT_ID"),
            "text": bot_response
        }
        requests.post("https://api.groupme.com/v3/bots/post", json=post_data)

    return "OK", 200
