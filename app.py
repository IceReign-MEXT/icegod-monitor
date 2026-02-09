import os
import requests
import threading
import time
from flask import Flask, request, render_template, jsonify
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
VIP_CHANNEL = os.getenv('VIP_CHANNEL_ID')
SOLSCAN_KEY = os.getenv('SOLSCAN_API_KEY')

bot = TeleBot(TOKEN)
app = Flask(__name__)

# --- DASHBOARD & UPTIME ---
@app.route('/')
def home():
    print("🛰️ UPTIME PING: System Awake.")
    return "<h1>ICEGOD MONITOR ONLINE</h1><p>System is listening...</p>"

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
        except Exception as e:
            print(f"❌ Webhook Error: {e}")
    return "OK", 200

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ONLINE*\nListening for whale activity...")

@bot.message_handler(commands=['p', 'price'])
def get_price(message):
    try:
        query = message.text.split()[1]
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={query}").json()
        pair = res['pairs'][0]
        mcap = pair.get('fdv', 0)
        mcap_str = f"${mcap/1e6:.1f}M" if mcap >= 1e6 else f"${mcap/1e3:.1f}K"
        msg = f"📊 *{pair['baseToken']['symbol']}*\nPrice: `${pair['priceUsd']}`\nMCap: `{mcap_str}`\n[Chart]({pair['url']})"
        bot.reply_to(message, msg, parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Use: `/p SOL` or check token name.")

# --- ENGINE ---
def run_bot():
    print("🤖 SYSTEM: Starting Telegram Bot Thread...")
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"⚠️ Bot Restarting: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Start bot thread
    threading.Thread(target=run_bot, daemon=True).start()
    # Run Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

