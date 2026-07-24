/* ==========================================================================
   Plata Emi & Uli - Interactive JS, Edit Modals & Dynamic Split Calculator
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initModals();
    initSplitCalculator();
    initDetailModal();
    initEditModals();
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

        if (exactGroup) exactGroup.style.display = 'none';
        if (pctGroup) pctGroup.style.display = 'none';

        let emiShare = 0;
        let uliShare = 0;

        if (type === '50_50') {
            emiShare = total / 2;
            uliShare = total / 2;
        } else if (type === 'EMI') {
            emiShare = total;
            uliShare = 0;
        } else if (type === 'ULI') {
            emiShare = 0;
            uliShare = total;
        } else if (type === 'EXACT') {
            if (exactGroup) exactGroup.style.display = 'grid';
            emiShare = parseFloat(emiMontoInput.value) || 0;
            uliShare = parseFloat(uliMontoInput.value) || 0;
        } else if (type === 'PERCENT') {
            if (pctGroup) pctGroup.style.display = 'block';
            const pctEmi = parseFloat(emiPctInput.value) || 50;
            emiShare = (total * pctEmi) / 100;
            uliShare = total - emiShare;
        }

        if (previewEmiText) previewEmiText.textContent = `$${emiShare.toLocaleString('es-AR', {minimumFractionDigits: 2})}`;
        if (previewUliText) previewUliText.textContent = `$${uliShare.toLocaleString('es-AR', {minimumFractionDigits: 2})}`;
    }

    totalInput.addEventListener('input', updateSplitPreview);
    splitTypeSelect.addEventListener('change', updateSplitPreview);
    if (emiMontoInput) emiMontoInput.addEventListener('input', updateSplitPreview);
    if (uliMontoInput) uliMontoInput.addEventListener('input', updateSplitPreview);
    if (emiPctInput) emiPctInput.addEventListener('input', updateSplitPreview);

    updateSplitPreview();
}

function initDetailModal() {
    const detailTriggers = document.querySelectorAll('[data-gasto-detail]');
    const modal = document.getElementById('modal-detalle-gasto');

    if (!modal) return;

    detailTriggers.forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            const id = el.getAttribute('data-id') || '';
            const desc = el.getAttribute('data-desc') || '';
            const monto = el.getAttribute('data-monto') || '0';
            const fecha = el.getAttribute('data-fecha') || '';
            const division = el.getAttribute('data-division') || '';
            const emi = el.getAttribute('data-emi') || '0';
            const uli = el.getAttribute('data-uli') || '0';
            const notas = el.getAttribute('data-notas') || '';

            document.getElementById('detail-desc').textContent = desc;
            document.getElementById('detail-monto').textContent = `$${monto}`;
            document.getElementById('detail-fecha').textContent = fecha;
            document.getElementById('detail-division').textContent = division;
            document.getElementById('detail-emi').textContent = `$${emi}`;
            document.getElementById('detail-uli').textContent = `$${uli}`;
            document.getElementById('detail-notas').textContent = notas ? notas : 'Sin descripción o notas adicionales.';

            // Pass ID to detail modal edit button
            const detailEditBtn = document.getElementById('detail-btn-edit');
            if (detailEditBtn) {
                detailEditBtn.setAttribute('data-id', id);
                detailEditBtn.setAttribute('data-desc', desc);
                detailEditBtn.setAttribute('data-monto-raw', el.getAttribute('data-monto-raw') || '');
                detailEditBtn.setAttribute('data-fecha-raw', el.getAttribute('data-fecha-raw') || '');
                detailEditBtn.setAttribute('data-division-raw', el.getAttribute('data-division-raw') || '');
                detailEditBtn.setAttribute('data-notas', notas);
            }

            modal.classList.add('active');
        });
    });
}

function initEditModals() {
    // 1. Edit Gasto Modal
    const editGastoTriggers = document.querySelectorAll('[data-edit-gasto]');
    const modalEditGasto = document.getElementById('modal-editar-gasto');
    const formEditGasto = document.getElementById('form-editar-gasto');

    if (modalEditGasto && formEditGasto) {
        editGastoTriggers.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const id = btn.getAttribute('data-id');
                const desc = btn.getAttribute('data-desc') || '';
                const monto = btn.getAttribute('data-monto-raw') || '0';
                const fecha = btn.getAttribute('data-fecha-raw') || '';
                const division = btn.getAttribute('data-division-raw') || '50_50';
                const notas = btn.getAttribute('data-notas') || '';

                formEditGasto.action = `/editar/${id}/`;
                document.getElementById('edit-gasto-desc').value = desc;
                document.getElementById('edit-gasto-monto').value = monto;
                document.getElementById('edit-gasto-fecha').value = fecha;
                document.getElementById('edit-gasto-division').value = division;
                document.getElementById('edit-gasto-notas').value = notas;

                // Close detail modal if open
                const detailModal = document.getElementById('modal-detalle-gasto');
                if (detailModal) detailModal.classList.remove('active');

                modalEditGasto.classList.add('active');
            });
        });
    }

    // 2. Edit Gasto Fijo Modal
    const editGfTriggers = document.querySelectorAll('[data-edit-gf]');
    const modalEditGf = document.getElementById('modal-editar-gasto-fijo');
    const formEditGf = document.getElementById('form-editar-gasto-fijo');

    if (modalEditGf && formEditGf) {
        editGfTriggers.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                const id = btn.getAttribute('data-id');
                const nombre = btn.getAttribute('data-nombre') || '';
                const monto = btn.getAttribute('data-monto-raw') || '0';
                const dia = btn.getAttribute('data-dia') || '1';
                const resp = btn.getAttribute('data-resp') || 'COMPARTIDO';
                const esCuota = btn.getAttribute('data-es-cuota') === 'true';
                const cTotales = btn.getAttribute('data-cuotas-totales') || '';
                const cRestantes = btn.getAttribute('data-cuotas-restantes') || '';
                const fechaFin = btn.getAttribute('data-fecha-fin') || '';

                formEditGf.action = `/gastos-fijos/editar/${id}/`;
                document.getElementById('edit-gf-nombre').value = nombre;
                document.getElementById('edit-gf-monto').value = monto;
                document.getElementById('edit-gf-dia').value = dia;
                document.getElementById('edit-gf-responsable').value = resp;

                const checkCuota = document.getElementById('edit-gf-check-cuota');
                const boxCuotas = document.getElementById('edit-gf-box-cuotas');
                if (checkCuota) {
                    checkCuota.checked = esCuota;
                    if (boxCuotas) boxCuotas.style.display = esCuota ? 'block' : 'none';
                }

                document.getElementById('edit-gf-cuotas-totales').value = cTotales;
                document.getElementById('edit-gf-cuotas-restantes').value = cRestantes;
                document.getElementById('edit-gf-fecha-fin').value = fechaFin;

                modalEditGf.classList.add('active');
            });
        });
    }
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
