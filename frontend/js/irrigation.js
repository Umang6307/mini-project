/**
 * Smart Crop Advisory - Irrigation Decision Engine UI Controller
 */

const Irrigation = {
  async init() {
    this.bindEvents();
    this.refreshRecommendation();
  },

  bindEvents() {
    const slider = document.getElementById('irrig-moisture-slider');
    const valDisplay = document.getElementById('irrig-slider-val');
    if (slider && valDisplay) {
      slider.addEventListener('input', (e) => {
        valDisplay.textContent = `${e.target.value}%`;
      });
      slider.addEventListener('change', () => {
        this.calculateCustom();
      });
    }

    const calcBtn = document.getElementById('btn-recalculate-irrig');
    if (calcBtn) {
      calcBtn.addEventListener('click', () => this.calculateCustom());
    }

    const applyBtn = document.getElementById('btn-apply-irrigation');
    if (applyBtn) {
      applyBtn.addEventListener('click', () => this.applyIrrigation());
    }
  },

  async refreshRecommendation() {
    try {
      const res = await fetch('/api/irrigation/recommend', {
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
    const slider = document.getElementById('irrig-moisture-slider');
    const soilType = document.getElementById('irrig-soil-type')?.value || 'Alluvial Clay Loam';
    const moisture = slider ? parseFloat(slider.value) : 28.0;

    try {
      const res = await fetch('/api/irrigation/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          soil_moisture: moisture,
          soil_type: soilType
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        this.renderResult(json.data);
        App.showToast(`Updated irrigation advice for ${moisture}% moisture`, "info");
      }
    } catch (e) {
      App.showToast("Calculation error", "error");
    }
  },

  renderResult(rec) {
    const statusBadge = document.getElementById('irrig-status-badge');
    const depthEl = document.getElementById('irrig-water-depth');
    const volEl = document.getElementById('irrig-water-volume');
    const durEl = document.getElementById('irrig-pump-duration');
    const urgEl = document.getElementById('irrig-urgency');
    const expEl = document.getElementById('irrig-explanation');

    if (statusBadge) {
      const st = rec.status;
      statusBadge.className = `badge badge-${st.toLowerCase()}`;
      statusBadge.textContent = st;
    }

    if (depthEl) depthEl.textContent = `${rec.water_depth_mm} mm`;
    if (volEl) volEl.textContent = `${rec.water_volume_m3.toLocaleString()} m³`;
    if (durEl) durEl.textContent = `${rec.duration_hours} Hours`;
    if (urgEl) urgEl.textContent = rec.urgency;
    if (expEl) expEl.textContent = rec.explanation;

    const slider = document.getElementById('irrig-moisture-slider');
    const valDisplay = document.getElementById('irrig-slider-val');
    if (slider) slider.value = rec.current_moisture_pct;
    if (valDisplay) valDisplay.textContent = `${rec.current_moisture_pct}%`;
  },

  async applyIrrigation() {
    try {
      const res = await fetch('/api/irrigation/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_id: App.currentFieldId, water_depth_mm: 30.0, duration_hours: 2.5 })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("💧 Irrigation applied! Soil moisture recharged to optimal.", "success");
        await this.refreshRecommendation();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Failed to apply irrigation", "error");
    }
  }
};
