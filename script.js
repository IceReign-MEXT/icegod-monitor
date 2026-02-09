async function trackWallet() {
    const address = document.getElementById("walletInput").value.trim();
    if (!address) return alert("Please enter a Solana address.");

    const loader = document.getElementById("loader");
    const tokenBody = document.getElementById("tokenTableBody");
    const txBody = document.getElementById("txTableBody");
    const totalDisplay = document.getElementById("totalPortfolioValue");

    loader.style.display = "block";
    tokenBody.innerHTML = "";
    txBody.innerHTML = "";
    totalDisplay.innerText = "SCANNING...";

    try {
        // Fetch Holdings and Transactions in parallel
        const [tokenRes, txRes] = await Promise.all([
            fetch(`http://localhost:8080/api/scan/${address}`),
            fetch(`http://localhost:8080/api/tx/${address}`)
        ]);

        const tokenData = await tokenRes.json();
        const txData = await txRes.json();

        loader.style.display = "none";

        // 1. Render Holdings
        let grandTotal = 0;
        const tokens = tokenData.data || [];

        if (tokens.length === 0) {
            tokenBody.innerHTML = "<tr><td colspan='4'>No assets found.</td></tr>";
        }

        tokens.forEach(t => {
            const amount = t.tokenAmount?.uiAmount || 0;
            const price = t.priceUsdt || 0;
            const value = amount * price;
            grandTotal += value;

            tokenBody.innerHTML += `
                <tr>
                    <td><strong>${t.tokenSymbol || 'SPL'}</strong></td>
                    <td>${amount.toLocaleString(undefined, {maximumFractionDigits: 2})}</td>
                    <td>$${price < 1 ? price.toFixed(6) : price.toFixed(2)}</td>
                    <td style="color: #00f2ff; font-weight: bold;">$${value.toFixed(2)}</td>
                </tr>`;
        });

        totalDisplay.innerText = `$${grandTotal.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

        // 2. Render Transactions
        const transactions = txData.data || [];
        transactions.forEach(tx => {
            const time = new Date(tx.block_time * 1000).toLocaleTimeString();
            txBody.innerHTML += `
                <tr>
                    <td><small>${tx.tx_hash.substring(0, 16)}...</small></td>
                    <td>${time}</td>
                    <td><span class="status-tag">${tx.status === 1 ? '✅ SUCCESS' : '❌ FAILED'}</span></td>
                </tr>`;
        });

    } catch (err) {
        console.error(err);
        loader.innerText = "Backend Connection Error.";
    }
}

function quickTrack(name) {
    const whales = {
        'Ansem': '4ACfpUFoaSD9bfPdeu6DBt89gB6ENTeHBXCAi87NhDEE',
        'Legend': 'D2L6yPZ2FmmmTKPgzaMKdhu6EWZcTpLy1Vhx8uvZe7NZ'
    };
    document.getElementById("walletInput").value = whales[name] || name;
    trackWallet();
}

