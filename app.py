import os
import requests
import threading
from flask import Flask, request, render_template, jsonify
from telebot import TeleBot
from dotenv import load_dotenv

# Load keys from .env or Render Environment Variables
load_dotenv()

# --- CONFIGURATION ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
VIP_CHANNEL = os.getenv('VIP_CHANNEL_ID')
SOLSCAN_KEY = os.getenv('SOLSCAN_API_KEY')
RPC_URL = os.getenv('ALCHEMY_RPC_URL')

# Initialize the Bot and Flask app
# Flask needs to know where your HTML and CSS/JS folders are
bot = TeleBot(TOKEN)
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- DASHBOARD ROUTES ---
@app.route('/')
def home():
    """Serves the main dashboard HTML."""
    return render_template('index.html')

@app.route('/api/scan/<address>')
def scan_api(address):
    """API endpoint used by the dashboard's script.js."""
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
        desc = event.get('description', 'No description available')

        # Build the alert message
        alert = (
            f"🚀 *WHALE MOVE DETECTED*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{desc}\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🔗 [View on Solscan](https://solscan.io/tx/{signature})"
        )

        # Send to Admin and Channel
        try:
            bot.send_message(ADMIN_ID, alert, parse_mode='Markdown', disable_web_page_preview=False)
            if VIP_CHANNEL:
                bot.send_message(VIP_CHANNEL, alert, parse_mode='Markdown')
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    return "OK", 200

# --- TELEGRAM BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "🧊 *ICEGOD MONITOR ONLINE*\nListening for institutional moves...")

@bot.message_handler(commands=['scan'])
def bot_scan(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "Usage: `/scan [wallet_address]`")

        address = parts[1]
        bot.send_message(message.chat.id, f"🔍 Scanning: `{address}`...", parse_mode='Markdown')

        # Reusing the Solscan logic for the bot
        url = f"https://pro-api.solscan.io/v2/account/tokens?address={address}"
        headers = {"token": SOLSCAN_KEY}
        data = requests.get(url, headers=headers).json()

        tokens = data.get('data', [])[:5] # Show top 5
        report = f"📊 *Wallet Report:*\n"
        for t in tokens:
            report += f"• *{t['tokenSymbol']}:* {round(t['tokenAmount']['uiAmount'], 2)}\n"

        bot.send_message(message.chat.id, report, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, "❌ Scan failed. Verify your Solscan Pro Key.")

# --- ENGINE RUNNER ---
def run_bot():
    """Keeps the bot listening in a separate thread."""
    bot.infinity_polling()

if __name__ == "__main__":
    # Start the Telegram bot thread (Polling)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # Start the Flask Web Server (Render uses the PORT environment variable)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

