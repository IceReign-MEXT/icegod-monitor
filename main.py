import os
import requests
from flask import Flask, request, render_template
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()

# Config
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
VIP_CHANNEL = os.getenv('VIP_CHANNEL_ID')
SOLSCAN_KEY = os.getenv('SOLSCAN_API_KEY')

# Initialize
bot = TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- ROUTES FOR DASHBOARD ---
@app.route('/')
def dashboard():
    return render_template('index.html')

# --- WEBHOOK FOR WHALE ALERTS ---
@app.route('/webhook', methods=['POST'])
def webhook():
    events = request.json
    for event in events:
        msg = f"🚀 *WHALE ALERT*\n{event.get('description')}\n[Solscan](https://solscan.io/tx/{event.get('signature')})"
        bot.send_message(ADMIN_ID, msg, parse_mode='Markdown')
        bot.send_message(VIP_CHANNEL, msg, parse_mode='Markdown')
    return "OK", 200

# API for Dashboard to Scan
@app.route('/api/scan/<address>')
def api_scan(address):
    url = f"https://pro-api.solscan.io/v2/account/tokens?address={address}"
    headers = {"token": SOLSCAN_KEY}
    return requests.get(url, headers=headers).json()

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

