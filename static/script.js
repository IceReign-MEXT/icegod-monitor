async function trackWallet() {
    const address = document.getElementById('walletInput').value;
    const loader = document.getElementById('loader');

    if (address.length < 10) { alert("Invalid Solana Address"); return; }

    // UI Updates
    loader.style.display = 'block';
    document.getElementById('tokenTableBody').innerHTML = '';

    try {
        // Call Python Backend
        const response = await fetch(`/api/scan?wallet=${address}`);
        const data = await response.json();

        // Update Total Value
        document.getElementById('totalPortfolioValue').innerText = "$" + data.total_value.toLocaleString();

        // Populate Tokens
        const tbody = document.getElementById('tokenTableBody');
        data.tokens.forEach(token => {
            const row = `<tr>
                <td><b style="color:#fff">${token.symbol}</b></td>
                <td>${token.balance.toLocaleString()}</td>
                <td>$${token.price}</td>
                <td style="color:#0aff0a; font-weight:bold">$${token.value.toLocaleString()}</td>
            </tr>`;
            tbody.innerHTML += row;
        });

    } catch (error) {
        alert("Scan Failed. Check Wallet Address.");
    } finally {
        loader.style.display = 'none';
    }
}

function quickTrack(name) {
    // Demo Whale Addresses for instant show
    const whales = {
        'Ansem': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1',
        'Legend': '8dtuyskTtsB78DFDPWZszarvDpedwftKYCoMdZwjHbxy'
    };
    document.getElementById('walletInput').value = whales[name];
    trackWallet();
}
