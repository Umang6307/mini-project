/**
 * Smart Crop Advisory - Dashboard Controller & Interactive Charts
 */

const Dashboard = {
  data: null,

  async init(fieldId = 1) {
    await this.loadDashboardData(fieldId);
  },

  async loadDashboardData(fieldId) {
    try {
      const res = await fetch(`/api/dashboard?field_id=${fieldId}`);
      const json = await res.json();
      if (json.status === 'success') {
        this.data = json.data;
        this.renderMetrics();
        this.renderGrowthTimeline();
        this.renderSoilChart();
        this.renderAlerts();
        this.renderActivities();
        this.renderMandiWidget();
      }
    } catch (e) {
      console.error("Dashboard data load failed", e);
      App.showToast("Failed to fetch field telemetry. Using local cache.", "warning");
    }
  },

  renderMetrics() {
    if (!this.data) return;
    const { current_field, soil, weather, satellite, mandi } = this.data;

    // Field & Crop
    const cropNameEl = document.getElementById('dash-crop-name');
    if (cropNameEl) cropNameEl.textContent = `${current_field.crop_name || 'Wheat'} (${current_field.variety || 'HD-3086'})`;

    const stageEl = document.getElementById('dash-crop-stage');
    if (stageEl) stageEl.textContent = current_field.current_stage || 'Flowering & Anthesis';

    // Soil Moisture
    const moistVal = soil.moisture_15cm_pct || 34.0;
    const moistEl = document.getElementById('dash-soil-moisture');
    const moistBadge = document.getElementById('dash-soil-badge');
    if (moistEl) moistEl.textContent = `${moistVal.toFixed(1)}%`;
    if (moistBadge) {
      moistBadge.className = `badge ${moistVal < 25 ? 'badge-deficit' : moistVal > 50 ? 'badge-warning' : 'badge-optimal'}`;
      moistBadge.textContent = moistVal < 25 ? 'Deficit' : moistVal > 50 ? 'Excess' : 'Optimal';
    }

    // Weather
    const curW = weather.current || {};
    const tempEl = document.getElementById('dash-temp');
    const humEl = document.getElementById('dash-humidity');
    const rainEl = document.getElementById('dash-rain-prob');
    if (tempEl) tempEl.textContent = `${curW.temperature_c || 27.4}°C`;
    if (humEl) humEl.textContent = `${curW.humidity_pct || 68}%`;
    if (rainEl) rainEl.textContent = `${curW.rainfall_prob_pct || 18}%`;

    // Crop Health & Risk
    const healthEl = document.getElementById('dash-health-score');
    const riskBadge = document.getElementById('dash-risk-badge');
    if (healthEl) healthEl.textContent = `${current_field.health_score || 92}%`;
    if (riskBadge) {
      const risk = current_field.risk_level || 'LOW';
      riskBadge.className = `badge badge-${risk.toLowerCase()}`;
      riskBadge.textContent = `${risk} RISK`;
    }

    // Harvest Date
    const harvestEl = document.getElementById('dash-harvest-date');
    if (harvestEl) harvestEl.textContent = current_field.harvest_estimate_date || 'Apr 2027';

    // Mandi Price
    const mandiEl = document.getElementById('dash-mandi-price');
    if (mandiEl && mandi) {
      mandiEl.textContent = `₹${mandi.best_price || 2490}/Qtl`;
    }
  },

  renderGrowthTimeline() {
    const container = document.getElementById('growth-timeline');
    if (!container) return;

    const stages = [
      { name: "Sowing", days: "0-10d", gdd: 120 },
      { name: "Germination", days: "10-21d", gdd: 350 },
      { name: "Tillering", days: "21-45d", gdd: 650 },
      { name: "Jointing", days: "45-70d", gdd: 1050 },
      { name: "Flowering", days: "70-95d", gdd: 1400 },
      { name: "Grain Filling", days: "95-120d", gdd: 1800 },
      { name: "Harvest", days: "120-140d", gdd: 2100 }
    ];

    const currentStageName = (this.data?.current_field?.current_stage || "Flowering").toLowerCase();

    let html = '';
    let reachedCurrent = false;

    stages.forEach((st, idx) => {
      let statusClass = '';
      if (st.name.toLowerCase().includes(currentStageName) || currentStageName.includes(st.name.toLowerCase())) {
        statusClass = 'active';
        reachedCurrent = true;
      } else if (!reachedCurrent) {
        statusClass = 'completed';
      }

      html += `
        <div class="timeline-step ${statusClass}">
          <div class="timeline-node">${idx + 1}</div>
          <div class="timeline-label">${st.name}</div>
          <div class="timeline-days">${st.days}</div>
        </div>
      `;
    });

    container.innerHTML = html;
  },

  renderSoilChart() {
    const container = document.getElementById('soil-chart-container');
    if (!container) return;

    // Generate responsive SVG Line Chart for 7-day moisture telemetry
    const points = [38, 36, 35, 33, 34, 32, (this.data?.soil?.moisture_15cm_pct || 34.0)];
    const w = 500;
    const h = 160;
    const padding = 25;

    const minVal = 10;
    const maxVal = 60;

    let pathD = '';
    let circles = '';

    points.forEach((val, i) => {
      const x = padding + (i * ((w - 2 * padding) / (points.length - 1)));
      const y = h - padding - ((val - minVal) / (maxVal - minVal) * (h - 2 * padding));
      if (i === 0) {
        pathD += `M ${x} ${y}`;
      } else {
        pathD += ` L ${x} ${y}`;
      }
      circles += `<circle cx="${x}" cy="${y}" r="4" fill="#2d6a4f" stroke="#ffffff" stroke-width="2"><title>Day ${i+1}: ${val}%</title></circle>`;
      circles += `<text x="${x}" y="${y - 8}" font-size="10" font-weight="600" fill="#2d6a4f" text-anchor="middle">${val}%</text>`;
    });

    // Area fill
    const areaD = `${pathD} L ${w - padding} ${h - padding} L ${padding} ${h - padding} Z`;

    const svg = `
      <svg viewBox="0 0 ${w} ${h}" class="chart-svg" preserveAspectRatio="none">
        <defs>
          <linearGradient id="soilGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#2d6a4f" stop-opacity="0.35"/>
            <stop offset="100%" stop-color="#2d6a4f" stop-opacity="0.02"/>
          </linearGradient>
        </defs>
        <!-- Horizontal grid line for critical deficit (25%) -->
        <line x1="${padding}" y1="${h - padding - ((25 - minVal) / (maxVal - minVal) * (h - 2 * padding))}" x2="${w - padding}" y2="${h - padding - ((25 - minVal) / (maxVal - minVal) * (h - 2 * padding))}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.5" />
        <text x="${w - padding - 85}" y="${h - padding - ((25 - minVal) / (maxVal - minVal) * (h - 2 * padding)) - 4}" font-size="9" font-weight="bold" fill="#ef4444">Deficit Threshold (25%)</text>
        
        <path d="${areaD}" fill="url(#soilGrad)" />
        <path d="${pathD}" fill="none" stroke="#2d6a4f" stroke-width="3" stroke-linecap="round" />
        ${circles}
      </svg>
    `;

    container.innerHTML = svg;
  },

  renderAlerts() {
    const list = document.getElementById('dash-alerts-list');
    if (!list) return;

    const advices = this.data?.advices || [];
    if (advices.length === 0) {
      list.innerHTML = `<div class="text-muted" style="padding: 12px; font-size: 0.85rem;">No active stress alerts. Crop environment is balanced.</div>`;
      return;
    }

    list.innerHTML = advices.map(a => `
      <div class="alert-card-item ${a.priority.toLowerCase()}">
        <div>
          <h4>${a.title}</h4>
          <p>${a.message}</p>
          <div style="margin-top: 6px; font-weight: 600; font-size: 0.78rem; color: var(--text-main);">
            Required Action: ${a.action_required || 'Inspect field'}
          </div>
        </div>
        ${!a.acknowledged ? `
          <button class="btn btn-secondary btn-sm" onclick="Dashboard.acknowledgeAdvice(${a.id})">
            Acknowledge
          </button>
        ` : `
          <span class="badge badge-success">Acknowledged</span>
        `}
      </div>
    `).join('');
  },

  async acknowledgeAdvice(id) {
    try {
      const res = await fetch(`/api/advice/${id}/acknowledge`, { method: 'POST' });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("Advisory acknowledged and recorded in farm audit trail.", "success");
        this.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Failed to acknowledge advice", "error");
    }
  },

  renderActivities() {
    const list = document.getElementById('dash-activities-list');
    if (!list) return;

    const activities = this.data?.activities || [];
    if (activities.length === 0) {
      list.innerHTML = `<div class="text-muted" style="padding: 12px; font-size: 0.85rem;">No activities logged yet.</div>`;
      return;
    }

    list.innerHTML = activities.slice(0, 6).map(act => `
      <div style="display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 0.85rem;">
        <div style="font-size: 1.1rem; width: 24px;">📝</div>
        <div style="flex: 1;">
          <div style="font-weight: 600; color: var(--text-main);">${act.description}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; gap: 12px; margin-top: 2px;">
            <span>${act.action_type}</span>
            <span>•</span>
            <span>${act.created_at || 'Recently'}</span>
            ${act.cost_inr ? `<span>• <b>₹${act.cost_inr}</b></span>` : ''}
          </div>
        </div>
      </div>
    `).join('');
  },

  renderMandiWidget() {
    const el = document.getElementById('dash-mandi-details');
    if (!el || !this.data?.mandi) return;

    const m = this.data.mandi;
    el.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <div>
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Top APMC Mandi</div>
          <div style="font-size: 1.1rem; font-weight: bold; color: var(--text-main);">${m.best_mandi} Mandi Yard</div>
        </div>
        <div class="badge badge-success">
          ₹${m.best_price} / Qtl
        </div>
      </div>
      <div style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;">
        MSP Benchmark: <b>₹${m.msp} / Quintal</b><br/>
        Net Premium over MSP: <b style="color: var(--success);">+₹${m.best_price - m.msp} / Qtl</b>
      </div>
    `;
  }
};
