import os
import threading
import random
import telebot
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Apps
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# ===========================
# 🌐 WEBSITE LOGIC (DASHBOARD)
# ===========================

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/health')
def health():
    return "ICEGOD MONITOR ONLINE", 200

@app.route('/api/scan')
def scan_wallet_api():
    wallet = request.args.get('wallet')
    # Simulated Data for the Website Visuals
    total = random.randint(10000, 500000)
    tokens = [
        {"symbol": "SOL", "balance": random.randint(50, 1000), "price": 145.20},
        {"symbol": "JUP", "balance": random.randint(1000, 50000), "price": 1.20},
        {"symbol": "BONK", "balance": random.randint(1000000, 10000000), "price": 0.000024}
    ]

    token_data = []
    for t in tokens:
        val = t['balance'] * t['price']
        token_data.append({
            "symbol": t['symbol'],
            "balance": t['balance'],
            "price": t['price'],
            "value": round(val, 2)
        })

    return jsonify({"status": "success", "total_value": total, "tokens": token_data})

def run_flask():
    # Render assigns the port automatically
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ===========================
# 🤖 BOT LOGIC (TELEGRAM)
# ===========================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message,
        "🛡️ **ICEGOD MONITOR V1**\n\n"
        "The High-Speed Wallet Intelligence Engine.\n\n"
        "🌐 **Live Dashboard:**\n"
        "https://icegod-monitor.onrender.com\n\n"
        "👇 **Commands:**\n"
        "`/scan <WALLET>` - Scan a Solana Address\n"
        "`/status` - Check System Health",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['scan'])
def scan_cmd(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ **Usage:** `/scan <WALLET_ADDRESS>`", parse_mode="Markdown")
            return

        wallet = parts[1]
        msg = bot.reply_to(message, f"🛰 **Scanning {wallet[:6]}...**")

        # Simulate Scan Result
        time.sleep(1)
        net_worth = random.randint(5000, 100000)
        bot.edit_message_text(
            f"✅ **SCAN COMPLETE**\n\n"
            f"💼 **Wallet:** `{wallet}`\n"
            f"💰 **Net Worth:** ${net_worth:,.2f}\n"
            f"📈 **Top Holding:** $SOL\n\n"
            f"🔗 [View Full Dashboard](https://icegod-monitor.onrender.com)",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    bot.reply_to(message, "🟢 **SYSTEM ONLINE**\nDashboard: Active\nBot: Active")

# ===========================
# 🚀 MAIN LAUNCHER
# ===========================
if __name__ == "__main__":
    print("🚀 STARTING HYBRID ENGINE...")

    # Start Website in Background Thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # Start Bot in Main Thread (Polling)
    try:
        print("🤖 Bot Polling Started...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Bot Crash: {e}")
