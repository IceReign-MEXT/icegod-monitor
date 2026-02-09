async function trackWallet() {
    const address = document.getElementById("walletInput").value.trim();
    if (!address) return alert("Please enter a Solana address.");

    const loader = document.getElementById("loader");
    const tokenBody = document.getElementById("tokenTableBody");
    const totalDisplay = document.getElementById("totalPortfolioValue");

    loader.style.display = "block";
    tokenBody.innerHTML = "";
    totalDisplay.innerText = "SYNCING...";

    try {
        // Calling your Python API endpoint
        const response = await fetch(`/api/scan/${address}`);
        const result = await response.json();

        loader.style.display = "none";
        let grandTotal = 0;

        if (!result.data || result.data.length === 0) {
            tokenBody.innerHTML = "<tr><td colspan='4' style='text-align:center'>No assets found in this wallet.</td></tr>";
            totalDisplay.innerText = "$0.00";
            return;
        }

        result.data.forEach(t => {
            const amount = t.tokenAmount.uiAmount || 0;
            const price = t.priceUsdt || 0;
            const val = amount * price;
            grandTotal += val;

            tokenBody.innerHTML += `
                <tr>
                    <td><strong>${t.tokenSymbol || 'SPL'}</strong></td>
                    <td>${amount.toLocaleString(undefined, {maximumFractionDigits: 2})}</td>
                    <td>$${price.toFixed(4)}</td>
                    <td style="color:#00f2ff; font-weight:bold">$${val.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                </tr>`;
        });

        totalDisplay.innerText = `$${grandTotal.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

    } catch (err) {
        console.error(err);
        loader.innerText = "CONNECTION ERROR: Check backend status.";
    }
}

function quickTrack(name) {
    const map = {
        'Ansem': '4ACfpUFoaSD9bfPdeu6DBt89gB6ENTeHBXCAi87NhDEE',
        'Legend': 'D2L6yPZ2FmmmTKPgzaMKdhu6EWZcTpLy1Vhx8uvZe7NZ'
    };
    document.getElementById("walletInput").value = map[name] || name;
    trackWallet();
}

