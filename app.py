import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mengambil kredensial dari Environment Variables (Lebih Aman)
APP_ID = os.getenv("APP_ID", "NjEyMjQ5ODgwMDU4")
APP_SECRET = os.getenv("APP_SECRET", "u9c5SX-_wSRWobgBQte27t1k9F1ZBP-")

def get_access_token():
    url = "https://openapi.seatalk.io/auth/app_access_token"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    try:
        res = requests.post(url, json=payload, timeout=10).json()
        return res.get("app_access_token")
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

# Web Server - Tampilan Dashboard Web Sederhana
@app.route("/")
def home():
    return """
    <html>
        <head><title>SeaTalk Bot Server</title></head>
        <body style="font-family: Arial; text-align: center; padding-top: 50px;">
            <h1>🚀 SeaTalk Bot Status: ACTIVE</h1>
            <p>Server web dan Webhook SeaTalk berjalan normal.</p>
        </body>
    </html>
    """

# Endpoint Callback Webhook SeaTalk
@app.route("/seatalk-webhook", methods=["POST"])
def seatalk_webhook():
    data = request.json
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    # 1. Verifikasi URL awal dari Developer Portal SeaTalk
    if data.get("event_type") == "event_subscription_verification":
        return jsonify({"challenge": data.get("event", {}).get("challenge")})
    
    # 2. Respon pesan masuk dari pengguna di SeaTalk
    if data.get("event_type") == "message_from_single_chat":
        event = data.get("event", {})
        chat_id = event.get("message", {}).get("chat_id")
        text_received = event.get("message", {}).get("text", {}).get("content", "")
        
        token = get_access_token()
        if token and chat_id:
            send_url = "https://openapi.seatalk.io/messaging/v2/single_chat"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {
                "chat_id": chat_id,
                "message_type": "text",
                "text": {"content": f"Bot Menerima Pesan: '{text_received}'"}
            }
            requests.post(send_url, json=payload, headers=headers, timeout=10)
            
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)