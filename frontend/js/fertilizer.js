/**
 * Smart Crop Advisory - Fertilizer & Nutrient Management Controller
 */

const Fertilizer = {
  async init() {
    this.bindEvents();
    this.refreshRecommendation();
  },

  bindEvents() {
    const calcBtn = document.getElementById('btn-recalc-fertilizer');
    if (calcBtn) {
      calcBtn.addEventListener('click', () => this.calculateCustom());
    }
  },

  async refreshRecommendation() {
    try {
      const res = await fetch('/api/fertilizer/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_id: App.currentFieldId })
      });
      const json = await res.json();
      if (json.status === 'success') {
        this.renderResult(json.data);
      }
    } catch (e) {
      console.error(e);
    }
  },

  async calculateCustom() {
    const n = parseFloat(document.getElementById('fert-input-n')?.value || 138);
    const p = parseFloat(document.getElementById('fert-input-p')?.value || 24);
    const k = parseFloat(document.getElementById('fert-input-k')?.value || 180);
    const ph = parseFloat(document.getElementById('fert-input-ph')?.value || 7.3);

    try {
      const res = await fetch('/api/fertilizer/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          nitrogen_ppm: n,
          phosphorus_ppm: p,
          potassium_ppm: k,
          ph: ph
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        this.renderResult(json.data);
        App.showToast("Fertilizer prescription generated based on soil test inputs.", "success");
      }
    } catch (e) {
      App.showToast("Calculation error", "error");
    }
  },

  renderResult(data) {
    const list = document.getElementById('fertilizer-recs-list');
    const totCostEl = document.getElementById('fert-total-cost');
    const statusEl = document.getElementById('fert-status-badge');

    if (totCostEl) totCostEl.textContent = `₹${data.total_estimated_cost_inr.toLocaleString()}`;
    if (statusEl) {
      const isDef = data.status === 'DEFICIENCY_DETECTED';
      statusEl.className = `badge ${isDef ? 'badge-warning' : 'badge-success'}`;
      statusEl.textContent = isDef ? 'Deficiency Detected' : 'Nutrient Profile Balanced';
    }

    if (!list) return;

    list.innerHTML = data.recommendations.map(r => `
      <div class="card" style="margin-bottom: 14px; border-left: 4px solid var(--primary-light);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <div>
            <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main);">${r.recommended_fertilizer}</h4>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">Target: <b>${r.nutrient}</b> (${r.current_value})</div>
          </div>
          <div class="badge ${r.deficiency_severity === 'HIGH' ? 'badge-danger' : r.deficiency_severity === 'MODERATE' ? 'badge-warning' : 'badge-success'}">
            ${r.deficiency_severity} SEVERITY
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; background: var(--bg-muted); padding: 10px; border-radius: var(--radius-sm); margin: 10px 0; font-size: 0.82rem;">
          <div>
            <span class="text-muted">Dosage Rate:</span>
            <div class="font-bold">${r.rate_kg_ha} kg/Hectare</div>
          </div>
          <div>
            <span class="text-muted">Total Needed:</span>
            <div class="font-bold">${r.total_quantity_kg} kg (${r.bags_needed} Bags)</div>
          </div>
          <div>
            <span class="text-muted">Estimated Cost:</span>
            <div class="font-bold" style="color: var(--primary-light);">₹${r.estimated_cost_inr.toLocaleString()}</div>
          </div>
        </div>

        <p style="font-size: 0.84rem; color: var(--text-main); margin-bottom: 8px;"><b>Application Timing:</b> ${r.application_timing}</p>
        <p style="font-size: 0.8rem; color: var(--text-muted);">${r.explanation}</p>

        ${r.rate_kg_ha > 0 ? `
          <div style="margin-top: 12px; text-align: right;">
            <button class="btn btn-secondary btn-sm" onclick="Fertilizer.applyFertilizer('${r.recommended_fertilizer}', ${r.total_quantity_kg}, ${r.estimated_cost_inr})">
              Mark Applied & Log Expense
            </button>
          </div>
        ` : ''}
      </div>
    `).join('');
  },

  async applyFertilizer(name, qty, cost) {
    try {
      const res = await fetch('/api/fertilizer/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          fertilizer_name: name,
          quantity_kg: qty,
          cost_inr: cost
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast(`Applied ${name}. Recorded in expenses and audit trail.`, "success");
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Failed to apply fertilizer", "error");
    }
  }
};
