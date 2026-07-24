/* ==========================================================================
   Plata Emi & Uli - Interactive JS & Dynamic Split Calculator
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initModals();
    initSplitCalculator();
    initDolarConverter();
});

function initModals() {
    const openBtns = document.querySelectorAll('[data-open-modal]');
    const closeBtns = document.querySelectorAll('[data-close-modal]');

    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = btn.getAttribute('data-open-modal');
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.add('active');
        });
    });

    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal-overlay');
            if (modal) modal.classList.remove('active');
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.classList.remove('active');
        }
    });
}

function initSplitCalculator() {
    const totalInput = document.getElementById('input-monto-total');
    const splitTypeSelect = document.getElementById('select-tipo-division');
    
    const calcBox = document.getElementById('split-calc-box');
    const exactGroup = document.getElementById('group-exact-split');
    const pctGroup = document.getElementById('group-pct-split');

    const emiMontoInput = document.getElementById('input-monto-emi');
    const uliMontoInput = document.getElementById('input-monto-uli');
    const emiPctInput = document.getElementById('input-pct-emi');

    const previewEmiText = document.getElementById('preview-split-emi');
    const previewUliText = document.getElementById('preview-split-uli');

    if (!totalInput || !splitTypeSelect) return;

    function updateSplitPreview() {
        const total = parseFloat(totalInput.value) || 0;
        const type = splitTypeSelect.value;

        exactGroup.style.display = 'none';
        pctGroup.style.display = 'none';

        let emiShare = 0;
        let uliShare = 0;

        if (type === '50_50') {
            emiShare = total / 2;
            uliShare = total / 2;
        } else if (type === 'EXACT') {
            exactGroup.style.display = 'grid';
            emiShare = parseFloat(emiMontoInput.value) || 0;
            uliShare = parseFloat(uliMontoInput.value) || 0;
        } else if (type === 'PERCENT') {
            pctGroup.style.display = 'block';
            const pctEmi = parseFloat(emiPctInput.value) || 50;
            emiShare = (total * pctEmi) / 100;
            uliShare = total - emiShare;
        } else if (type === 'FOR_OTHER') {
            const payerId = document.getElementById('select-pagado-por')?.value;
            // Payer pays for other, so responsibility is 100% on receiver
            if (payerId === '1') { // Assuming Emi is ID 1 or slug
                emiShare = 0;
                uliShare = total;
            } else {
                emiShare = total;
                uliShare = 0;
            }
        } else if (type === 'PERSONAL') {
            const payerId = document.getElementById('select-pagado-por')?.value;
            if (payerId === '1') {
                emiShare = total;
                uliShare = 0;
            } else {
                emiShare = 0;
                uliShare = total;
            }
        }

        if (previewEmiText) previewEmiText.textContent = `$${emiShare.toFixed(2)}`;
        if (previewUliText) previewUliText.textContent = `$${uliShare.toFixed(2)}`;
    }

    totalInput.addEventListener('input', updateSplitPreview);
    splitTypeSelect.addEventListener('change', updateSplitPreview);
    if (emiMontoInput) emiMontoInput.addEventListener('input', updateSplitPreview);
    if (uliMontoInput) uliMontoInput.addEventListener('input', updateSplitPreview);
    if (emiPctInput) emiPctInput.addEventListener('input', updateSplitPreview);
    const payerSelect = document.getElementById('select-pagado-por');
    if (payerSelect) payerSelect.addEventListener('change', updateSplitPreview);

    updateSplitPreview();
}

function initDolarConverter() {
    const arsInput = document.getElementById('calc-ars-input');
    const rateSelect = document.getElementById('calc-rate-select');
    const usdResult = document.getElementById('calc-usd-result');

    if (!arsInput || !rateSelect || !usdResult) return;

    function convert() {
        const ars = parseFloat(arsInput.value) || 0;
        const rate = parseFloat(rateSelect.value) || 1400;
        const res = ars / rate;
        usdResult.textContent = `US$ ${res.toFixed(2)}`;
    }

    arsInput.addEventListener('input', convert);
    rateSelect.addEventListener('change', convert);
    convert();
}
