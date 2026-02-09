require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8080;
const SOLSCAN_API_KEY = process.env.SOLSCAN_API_KEY;
const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ADMIN_ID = process.env.ADMIN_ID;

// Helper: Send Alert to your Telegram
const notifyAdmin = async (msg) => {
    try {
        await axios.post(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
            chat_id: ADMIN_ID,
            text: `🧊 *ICEGOD MONITOR*\n${msg}`,
            parse_mode: 'Markdown'
        });
    } catch (e) { console.log("TG Alert Error"); }
};

// Endpoint: Fetch Token Holdings
app.get('/api/scan/:address', async (req, res) => {
    try {
        const response = await axios.get(`https://pro-api.solscan.io/v2/account/tokens?address=${req.params.address}`, {
            headers: { 'token': SOLSCAN_API_KEY }
        });
        notifyAdmin(`🔍 Wallet Scanned: \`${req.params.address}\``);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "Solscan Fetch Failed" });
    }
});

// Endpoint: Fetch Transaction History
app.get('/api/tx/:address', async (req, res) => {
    try {
        const response = await axios.get(`https://pro-api.solscan.io/v2/account/transactions?address=${req.params.address}&limit=10`, {
            headers: { 'token': SOLSCAN_API_KEY }
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "TX Fetch Failed" });
    }
});

app.listen(PORT, () => {
    console.log(`ICEGOD Engine Active on Port ${PORT}`);
});

