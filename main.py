import os
import requests
from flask import Flask, request, jsonify
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
SOLSCAN_KEY = os.getenv('SOLSCAN_API_KEY')
bot = TeleBot(TOKEN)
app = Flask(__name__)

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ACTIVE*\nInstitutional Grade Solana Tracking Ready.", parse_mode='Markdown')

@bot.message_handler(commands=['scan'])
def scan_wallet(message):
    address = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not address:
        return bot.reply_to(message, "Usage: /scan [address]")

    bot.send_message(message.chat.id, f"🔍 Scanning Solana Mainnet for `{address}`...", parse_mode='Markdown')

    try:
        url = f"https://pro-api.solscan.io/v2/account/tokens?address={address}"
        headers = {"token": SOLSCAN_KEY}
        res = requests.get(url, headers=headers).json()

        tokens = res.get('data', [])[:5] # Show top 5
        report = f"📊 *Wallet Report:* `{address[:6]}...`\n\n"
        for t in tokens:
            report += f"• *{t['tokenSymbol']}:* {round(t['tokenAmount']['uiAmount'], 2)}\n"

        bot.send_message(message.chat.id, report, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Scan failed. Verify API Key.")

# --- HELIUS WEBHOOK ENDPOINT ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    for tx in data:
        msg = f"🚀 *WHALE MOVE DETECTED*\n\nAction: {tx.get('description')}\n[View on Solscan](https://solscan.io/tx/{tx.get('signature')})"
        bot.send_message(ADMIN_ID, msg, parse_mode='Markdown')
    return "OK", 200

# --- RUNNER ---
if __name__ == "__main__":
    # Start Telegram Polling in background
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    # Start Webserver for Render/Helius
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

