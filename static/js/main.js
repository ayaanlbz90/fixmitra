document.addEventListener('DOMContentLoaded', () => {
    const deviceSelect = document.getElementById('wizard-device');
    const problemSelect = document.getElementById('wizard-problem');
    const priceDisplay = document.getElementById('estimated-price-display');

    async function fetchEstimate() {
        if (!deviceSelect || !problemSelect || !priceDisplay) return;

        const device = deviceSelect.value;
        const problem = problemSelect.value;

        try {
            const res = await fetch('/estimate-price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device, problem })
            });
            const data = await res.json();
            priceDisplay.innerText = data.estimate;
            
            const hiddenEstimateInput = document.getElementById('hidden-estimate');
            if(hiddenEstimateInput) hiddenEstimateInput.value = data.estimate;
        } catch (err) {
            console.error("Error fetching estimation:", err);
        }
    }

    if (deviceSelect && problemSelect) {
        deviceSelect.addEventListener('change', fetchEstimate);
        problemSelect.addEventListener('change', fetchEstimate);
    }
});