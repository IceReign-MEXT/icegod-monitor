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

# --- DASHBOARD & UPTIME ROUTES ---
@app.route('/')
def home():
    print("🛰️ UPTIME PING: System Awake.")
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
        desc = event.get('description', 'Whale Activity Detected')
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
    print(f"📥 Bot received /start from {message.chat.id}")
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ONLINE*\nListening for whale activity...")

@bot.message_handler(commands=['p', 'price'])
def get_price(message):
    try:
        parts = message.text.split()
        if len(parts) < 2: return bot.reply_to(message, "Usage: `/p [ticker]`")
        query = parts[1]
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
        res = requests.get(url).json()
        pairs = res.get('pairs', [])
        if not pairs: return bot.reply_to(message, "❌ No pairs found.")

        top = pairs[0]
        symbol = top.get('baseToken', {}).get('symbol', '???')
        price = top.get('priceUsd', '0.00')
        mcap = top.get('fdv', 0)
        link = top.get('url')

        mcap_str = f"${mcap/1_000_000:.1f}M" if mcap >= 1_000_000 else f"${mcap/1_000:.1f}K"
        bot.reply_to(message, f"📊 *{symbol}*\nPrice: `${price}`\nMCap: `{mcap_str}`\n[Chart]({link})", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Price Error")

# --- BOT THREAD RUNNER ---
def run_bot():
    """Starts the bot with a cleanup to prevent conflicts."""
    print("🤖 SYSTEM: Bot thread starting...")
    while True:
        try:
            bot.remove_webhook() # Clear old connections
            bot_info = bot.get_me()
            print(f"✅ SYSTEM: Bot @{bot_info.username} is ACTIVE!")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"⚠️ SYSTEM: Bot reconnecting... ({e})")
            time.sleep(5)

# --- START THE ENGINE ---
if __name__ == "__main__":
    # Start bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Run Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

