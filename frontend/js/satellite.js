/**
 * Smart Crop Advisory - Satellite & Disaster Risk Controller
 */

const Satellite = {
  data: null,

  async init() {
    this.refreshData();
  },

  async refreshData() {
    try {
      const res = await fetch(`/api/satellite/${App.currentFieldId}`);
      const json = await res.json();
      if (json.status === 'success') {
        this.data = json.data;
        this.renderAssessment();
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderAssessment() {
    if (!this.data) return;
    const s = this.data;

    const disasterEl = document.getElementById('sat-disaster-type');
    const sevBadge = document.getElementById('sat-severity-badge');
    const baseNdviEl = document.getElementById('sat-base-ndvi');
    const curNdviEl = document.getElementById('sat-cur-ndvi');
    const anomEl = document.getElementById('sat-anomaly-pct');
    const affEl = document.getElementById('sat-affected-area');
    const lossEl = document.getElementById('sat-yield-loss');
    const finEl = document.getElementById('sat-fin-loss');

    if (disasterEl) disasterEl.textContent = s.disaster_type;
    if (sevBadge) {
      const isSevere = s.severity === 'HIGH' || s.severity === 'SEVERE' || s.severity === 'CRITICAL';
      sevBadge.className = `badge ${isSevere ? 'badge-danger' : 'badge-success'}`;
      sevBadge.textContent = `${s.severity} RISK`;
    }

    if (baseNdviEl) baseNdviEl.textContent = s.baseline_ndvi.toFixed(2);
    if (curNdviEl) curNdviEl.textContent = s.current_ndvi.toFixed(2);
    if (anomEl) {
      anomEl.textContent = `${s.ndvi_anomaly_pct > 0 ? '+' : ''}${s.ndvi_anomaly_pct.toFixed(1)}%`;
      anomEl.style.color = s.ndvi_anomaly_pct < -15 ? 'var(--danger)' : 'var(--text-main)';
    }

    if (affEl) affEl.textContent = `${s.affected_acreage} Hectares`;
    if (lossEl) lossEl.textContent = `${s.estimated_yield_loss_pct}%`;
    if (finEl) finEl.textContent = `₹${s.estimated_financial_loss_inr.toLocaleString()}`;

    // Render interactive NDVI spectrum graphic
    const spectrum = document.getElementById('ndvi-spectrum-bar');
    if (spectrum) {
      const markerPos = Math.max(0, Math.min(100, s.current_ndvi * 100));
      spectrum.innerHTML = `
        <div style="position: relative; height: 16px; background: linear-gradient(to right, #dc2626, #f59e0b, #eab308, #22c55e, #15803d); border-radius: 8px;">
          <div style="position: absolute; left: ${markerPos}%; top: -4px; width: 4px; height: 24px; background: #ffffff; border: 2px solid #000000; border-radius: 2px; transform: translateX(-50%);">
            <span style="position: absolute; top: 26px; left: 50%; transform: translateX(-50%); font-size: 0.72rem; font-weight: bold; white-space: nowrap; color: var(--text-main);">Current: ${s.current_ndvi}</span>
          </div>
        </div>
      `;
    }
  }
};
