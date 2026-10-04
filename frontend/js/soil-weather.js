/**
 * Smart Crop Advisory - Soil & Weather Telemetry Controller
 */

const SoilWeather = {
  async init() {
    this.bindEvents();
    this.refreshData();
  },

  bindEvents() {
    const simBtn = document.getElementById('btn-simulate-sensor');
    if (simBtn) {
      simBtn.addEventListener('click', () => this.simulateSensorPacket());
    }
  },

  async refreshData() {
    try {
      const [soilRes, weatherRes] = await Promise.all([
        fetch(`/api/soil/${App.currentFieldId}`),
        fetch(`/api/weather/${App.currentFieldId}`)
      ]);
      const soilJson = await soilRes.json();
      const weatherJson = await weatherRes.json();

      if (soilJson.status === 'success') this.renderSoil(soilJson.data);
      if (weatherJson.status === 'success') this.renderWeather(weatherJson.data);
    } catch (e) {
      console.error(e);
    }
  },

  renderSoil(data) {
    const s = data.latest || {};
    const m15 = document.getElementById('soil-val-15cm');
    const m45 = document.getElementById('soil-val-45cm');
    const temp = document.getElementById('soil-val-temp');
    const ec = document.getElementById('soil-val-ec');
    const ph = document.getElementById('soil-val-ph');
    const n = document.getElementById('soil-val-n');
    const p = document.getElementById('soil-val-p');
    const k = document.getElementById('soil-val-k');

    if (m15) m15.textContent = `${(s.moisture_15cm_pct || 34.0).toFixed(1)}%`;
    if (m45) m45.textContent = `${(s.moisture_45cm_pct || 38.5).toFixed(1)}%`;
    if (temp) temp.textContent = `${(s.soil_temp_c || 22.4).toFixed(1)}°C`;
    if (ec) ec.textContent = `${(s.ec_ds_m || 0.62).toFixed(2)} dS/m`;
    if (ph) ph.textContent = `${(s.ph || 7.3).toFixed(1)}`;
    if (n) n.textContent = `${(s.nitrogen_ppm || 138).toFixed(0)} ppm`;
    if (p) p.textContent = `${(s.phosphorus_ppm || 24.5).toFixed(1)} ppm`;
    if (k) k.textContent = `${(s.potassium_ppm || 182).toFixed(0)} ppm`;

    // History Table
    const tbody = document.getElementById('soil-history-tbody');
    if (tbody && data.history) {
      tbody.innerHTML = data.history.map(row => `
        <tr>
          <td>${row.recorded_at}</td>
          <td><b>${row.moisture_15cm_pct}%</b></td>
          <td>${row.moisture_45cm_pct}%</td>
          <td>${row.soil_temp_c}°C</td>
          <td>${row.ph}</td>
          <td>${row.nitrogen_ppm} ppm</td>
          <td><span class="badge badge-info">Simulated IoT</span></td>
        </tr>
      `).join('');
    }
  },

  renderWeather(data) {
    const cur = data.current || {};
    const t = document.getElementById('weather-cur-temp');
    const h = document.getElementById('weather-cur-hum');
    const r = document.getElementById('weather-cur-rain');
    const w = document.getElementById('weather-cur-wind');
    const et = document.getElementById('weather-cur-et0');
    const cond = document.getElementById('weather-cur-cond');

    if (t) t.textContent = `${cur.temperature_c || 27.4}°C`;
    if (h) h.textContent = `${cur.humidity_pct || 68}%`;
    if (r) r.textContent = `${cur.rainfall_prob_pct || 18}%`;
    if (w) w.textContent = `${cur.wind_speed_kmh || 12} km/h ${cur.wind_direction || 'NNW'}`;
    if (et) et.textContent = `${cur.et0_mm_day || 4.2} mm/day`;
    if (cond) cond.textContent = cur.condition || 'Partly Cloudy';

    // 5-day forecast
    const forecastContainer = document.getElementById('weather-forecast-grid');
    if (forecastContainer && data.forecast_5d) {
      forecastContainer.innerHTML = data.forecast_5d.map(f => `
        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px; text-align: center;">
          <div style="font-weight: 700; font-size: 0.9rem; color: var(--text-main);">${f.day}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px;">${f.date}</div>
          <div style="font-size: 1.4rem; font-weight: bold; color: var(--primary-light);">${f.temp_max}° / <span style="font-size: 1rem; color: var(--text-muted);">${f.temp_min}°</span></div>
          <div style="font-size: 0.8rem; margin: 6px 0; color: var(--text-main);">${f.condition}</div>
          <div style="font-size: 0.72rem; color: var(--info); font-weight: 600;">Rain: ${f.rainfall_prob_pct}%</div>
        </div>
      `).join('');
    }
  },

  async simulateSensorPacket() {
    try {
      const res = await fetch(`/api/soil/${App.currentFieldId}/simulate`, { method: 'POST' });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("📡 Simulated sensor telemetry packet dispatched and stored in SQL database.", "success");
        await this.refreshData();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Sensor simulation failed", "error");
    }
  }
};
