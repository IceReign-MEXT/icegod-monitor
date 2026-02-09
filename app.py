import os
import requests
import threading
import time
from flask import Flask, request, render_template, jsonify
from telebot import TeleBot
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
VIP_CHANNEL = os.getenv('VIP_CHANNEL_ID')
SOLSCAN_KEY = os.getenv('SOLSCAN_API_KEY')

# Initialize Flask and Bot
bot = TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- DASHBOARD ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/scan/<address>')
def scan_api(address):
    url = f"https://pro-api.solscan.io/v2/account/tokens?address={address}"
    headers = {"token": SOLSCAN_KEY}
    try:
        res = requests.get(url, headers=headers)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- HELIUS WEBHOOK RECEIVER ---
@app.route('/webhook', methods=['POST'])
def webhook():
    events = request.json
    if not events:
        return "No data", 400
    for event in events:
        signature = event.get('signature')
        desc = event.get('description', 'Institutional Move Detected')
        alert = f"🚀 *WHALE ALERT*\n\n{desc}\n\n[Solscan](https://solscan.io/tx/{signature})"

        try:
            bot.send_message(ADMIN_ID, alert, parse_mode='Markdown')
            if VIP_CHANNEL:
                bot.send_message(VIP_CHANNEL, alert, parse_mode='Markdown')
        except:
            pass
    return "OK", 200

# --- TELEGRAM BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ONLINE*\nListening for whale activity...")

# --- BOT THREAD RUNNER ---
def run_bot():
    """Starts the bot with an auto-restart loop."""
    print("🤖 Attempting to start Telegram Bot...")
    while True:
        try:
            # Clear any old webhook settings that block polling
            bot.remove_webhook()
            print("✅ Bot is now Polling...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)

# --- START THE ENGINE ---
if __name__ == "__main__":
    # 1. Start Bot in Background Thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 2. Start Flask Server
    # Note: Render provides the PORT env variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

