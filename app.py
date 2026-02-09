import os
import requests
import threading
import time
import re
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
    """Serves the dashboard and acts as the Uptime Robot target."""
    print("🛰️ UPTIME PING: Keeping the 'IceGod' awake.")
    return render_template('index.html')

@app.route('/api/scan/<address>')
def scan_api(address):
    """API for the dashboard's wallet scanner."""
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
    """Receives real-time whale alerts from Helius."""
    events = request.json
    if not events:
        return "No data", 400

    for event in events:
        signature = event.get('signature')
        desc = event.get('description', 'Institutional Move Detected')

        # Build the Telegram Alert
        alert = (
            f"🚀 *WHALE ALERT*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{desc}\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔗 [Solscan](https://solscan.io/tx/{signature})"
        )

        try:
            bot.send_message(ADMIN_ID, alert, parse_mode='Markdown')
            if VIP_CHANNEL:
                bot.send_message(VIP_CHANNEL, alert, parse_mode='Markdown')
        except Exception as e:
            print(f"❌ Webhook Error: {e}")

    return "OK", 200

# --- TELEGRAM BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ONLINE*\n\n"
                          "Monitoring whale moves 24/7.\n"
                          "Use `/p [ticker]` for instant prices.")

@bot.message_handler(commands=['p', 'price'])
def get_price(message):
    """Fetches real-time price and mcap from DexScreener."""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "💡 Usage: `/p [ticker]` (e.g. `/p SOL`)")

        query = parts[1]
        bot.send_chat_action(message.chat.id, 'typing')

        # DexScreener API (Free, No Key Required)
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
        res = requests.get(url).json()

        pairs = res.get('pairs', [])
        if not pairs:
            return bot.reply_to(message, "❌ No pairs found for that token.")

        # Get highest liquidity pair
        top_pair = pairs[0]
        symbol = top_pair.get('baseToken', {}).get('symbol', '???')
        price = top_pair.get('priceUsd', '0.00')
        mcap = top_pair.get('fdv', 0)
        h1 = top_pair.get('priceChange', {}).get('h1', 0)
        link = top_pair.get('url')

        mcap_formatted = f"${mcap/1_000_000:.1f}M" if mcap >= 1_000_000 else f"${mcap/1_000:.1f}K"
        change_emoji = "🟢" if float(h1) >= 0 else "🔴"

        response = (
            f"📊 *{symbol} Data*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 *Price:* `${price}`\n"
            f"💎 *MCap:* `{mcap_formatted}`\n"
            f"{change_emoji} *1h Change:* `{h1}%`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 [Chart/Trade]({link})"
        )
        bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        print(f"Price Error: {e}")
        bot.reply_to(message, "❌ Error fetching price.")

# --- ENGINE RUNNER ---
def run_bot():
    """Starts the bot in a background thread."""
    while True:
        try:
            bot.remove_webhook()
            bot_info = bot.get_me()
            print(f"✅ SYSTEM: Bot @{bot_info.username} is listening!")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"⚠️ SYSTEM: Bot reconnecting... ({e})")
            time.sleep(5)

if __name__ == "__main__":
    # 1. Start Bot Thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 2. Start Web Server
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

