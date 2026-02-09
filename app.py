import os
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- ROUTES ---
@app.route('/')
def dashboard():
    return render_template('index.html')

# --- API FOR SCANNER (The Brain) ---
@app.route('/api/scan')
def scan_wallet():
    wallet = request.args.get('wallet')

    # SIMULATED SCAN (Connect Helius here later for Real Data)
    # This makes the dashboard look alive immediately

    total = random.randint(10000, 500000)

    tokens = [
        {"symbol": "SOL", "balance": random.randint(50, 1000), "price": 145.20},
        {"symbol": "JUP", "balance": random.randint(1000, 50000), "price": 1.20},
        {"symbol": "BONK", "balance": random.randint(1000000, 10000000), "price": 0.000024},
        {"symbol": "USDC", "balance": random.randint(5000, 20000), "price": 1.00}
    ]

    # Calculate values
    token_data = []
    for t in tokens:
        val = t['balance'] * t['price']
        token_data.append({
            "symbol": t['symbol'],
            "balance": t['balance'],
            "price": t['price'],
            "value": round(val, 2)
        })

    return jsonify({
        "status": "success",
        "total_value": total,
        "tokens": token_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
