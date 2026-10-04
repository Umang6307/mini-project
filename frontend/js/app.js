/**
 * Smart Crop Advisory - Master Application Orchestrator & View Switcher
 */

const App = {
  currentFieldId: 1,
  activeView: 'dashboard',

  async init() {
    // 1. Initialize Localization & Auth
    await Localization.init();
    Auth.updateHeaderProfile();

    // 2. Setup theme (Dark / Light)
    this.initTheme();

    // 3. Bind Global Navigation & Controls
    this.bindGlobalEvents();

    // 4. Load Fields into dropdown
    await this.loadFieldsDropdown();

    // 5. Initialize current view
    this.switchView('dashboard');
  },

  initTheme() {
    const savedTheme = localStorage.getItem('sca_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateThemeButton(savedTheme);
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('sca_theme', next);
    this.updateThemeButton(next);
  },

  updateThemeButton(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
      btn.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
    }
  },

  bindGlobalEvents() {
    // Navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const view = e.currentTarget.getAttribute('data-view');
        if (view) {
          this.switchView(view);
          // Close mobile drawer if open
          document.getElementById('sidebar')?.classList.remove('open');
          document.getElementById('sidebar-backdrop')?.classList.remove('active');
        }
      });
    });

    // Theme toggle
    document.getElementById('theme-toggle-btn')?.addEventListener('click', () => this.toggleTheme());

    // Language toggle
    document.getElementById('lang-toggle-btn')?.addEventListener('click', () => Localization.toggleLanguage());

    // Mobile drawer toggle
    document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
      document.getElementById('sidebar')?.classList.toggle('open');
      document.getElementById('sidebar-backdrop')?.classList.toggle('active');
    });

    document.getElementById('sidebar-backdrop')?.addEventListener('click', () => {
      document.getElementById('sidebar')?.classList.remove('open');
      document.getElementById('sidebar-backdrop')?.classList.remove('active');
    });

    // Field dropdown change
    document.getElementById('global-field-select')?.addEventListener('change', (e) => {
      this.currentFieldId = parseInt(e.target.value);
      this.onFieldChanged();
    });

    // Quick sensor simulation button in topbar
    document.getElementById('topbar-simulate-btn')?.addEventListener('click', async () => {
      await SoilWeather.simulateSensorPacket();
    });

    // Modal dismiss buttons
    document.querySelectorAll('.modal-close-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const modal = e.target.closest('.modal-overlay');
        if (modal) modal.classList.remove('active');
      });
    });
  },

  async loadFieldsDropdown() {
    try {
      const res = await fetch('/api/fields');
      const json = await res.json();
      if (json.status === 'success') {
        const sel = document.getElementById('global-field-select');
        if (sel) {
          sel.innerHTML = json.data.map(f => `
            <option value="${f.id}" ${f.id === this.currentFieldId ? 'selected' : ''}>
              ${f.field_code}: ${f.field_name} (${f.crop_name || 'Crop'} - ${f.area_value} ${f.area_unit})
            </option>
          `).join('');
        }
      }
    } catch (e) {
      console.warn("Could not load fields dropdown", e);
    }
  },

  onFieldChanged() {
    this.showToast(`Switched active parcel to Field ID: ${this.currentFieldId}`, "info");
    Dashboard.loadDashboardData(this.currentFieldId);
    if (this.activeView === 'irrigation') Irrigation.refreshRecommendation();
    if (this.activeView === 'fertilizer') Fertilizer.refreshRecommendation();
    if (this.activeView === 'soil_weather') SoilWeather.refreshData();
    if (this.activeView === 'growth') Growth.refreshData();
    if (this.activeView === 'finance') Finance.refreshData();
    if (this.activeView === 'satellite') Satellite.refreshData();
    if (this.activeView === 'audit') this.loadAuditTrail();
  },

  switchView(viewName) {
    this.activeView = viewName;

    // Update sidebar navigation active state
    document.querySelectorAll('.nav-item').forEach(el => {
      if (el.getAttribute('data-view') === viewName) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    // Hide all view sections and show requested view
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add('active');
    }

    // Lazy load/refresh controllers based on active view
    switch (viewName) {
      case 'dashboard':
        Dashboard.init(this.currentFieldId);
        break;
      case 'irrigation':
        Irrigation.init();
        break;
      case 'fertilizer':
        Fertilizer.init();
        break;
      case 'crop_health':
        CropHealth.init();
        break;
      case 'soil_weather':
        SoilWeather.init();
        break;
      case 'growth':
        Growth.init();
        break;
      case 'market':
        Market.init();
        break;
      case 'finance':
        Finance.init();
        break;
      case 'machinery':
        Machinery.init();
        break;
      case 'satellite':
        Satellite.init();
        break;
      case 'insurance':
        Insurance.init();
        break;
      case 'schemes':
        Government.init();
        break;
      case 'ussd':
        Ussd.init();
        break;
      case 'audit':
        this.loadAuditTrail();
        break;
    }
  },

  async runScenario(scenarioKey) {
    try {
      this.showToast(`Triggering Judge Scenario: ${scenarioKey.toUpperCase()}...`, "info");
      const res = await fetch('/api/scenarios/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioKey, field_id: this.currentFieldId })
      });
      const json = await res.json();
      if (json.status === 'success') {
        this.renderScenarioResult(json.data);
        Dashboard.loadDashboardData(this.currentFieldId);
        this.showToast(`Scenario '${json.data.title}' executed! Full cause-analysis chain updated.`, "success");
      }
    } catch (e) {
      this.showToast("Failed to run scenario", "error");
    }
  },

  renderScenarioResult(data) {
    const box = document.getElementById('scenario-active-display');
    if (!box) return;

    box.style.display = 'block';
    box.innerHTML = `
      <div class="card" style="border: 2px solid var(--primary-light); background: var(--bg-card); margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
          <div>
            <h3 style="color: var(--primary-light); font-size: 1.25rem; font-weight: 800;">
              ⚡ Activated Scenario: ${data.title}
            </h3>
            <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 2px;">
              <b>Root Cause:</b> ${data.cause}
            </p>
          </div>
          <span class="badge badge-warning">Simulated Event</span>
        </div>

        <h4 style="font-size: 0.9rem; font-weight: 700; margin: 12px 0 8px;">Automated Decision Support Chain:</h4>
        <div style="background: var(--bg-muted); padding: 12px; border-radius: var(--radius-sm); font-size: 0.85rem; line-height: 1.6;">
          ${data.steps.map(step => `<div>${step}</div>`).join('')}
        </div>

        <div style="margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap;">
          <button class="btn btn-primary btn-sm" onclick="App.switchView('dashboard')">View Updated Dashboard</button>
          <button class="btn btn-secondary btn-sm" onclick="App.switchView('satellite')">Inspect Satellite Anomaly</button>
          <button class="btn btn-secondary btn-sm" onclick="App.switchView('insurance')">View PMFBY Dossier</button>
        </div>
      </div>
    `;
    box.scrollIntoView({ behavior: 'smooth' });
  },

  async resetDemoDatabase() {
    if (!confirm("Reset all field readings, diagnoses, and financial ledgers back to default demo data?")) return;
    try {
      const res = await fetch('/api/demo/reset', { method: 'POST' });
      const json = await res.json();
      if (json.status === 'success') {
        this.showToast("Database restored to factory demo state.", "success");
        setTimeout(() => window.location.reload(), 600);
      }
    } catch (e) {
      this.showToast("Reset failed", "error");
    }
  },

  async loadAuditTrail() {
    const tbody = document.getElementById('audit-table-tbody');
    if (!tbody) return;

    try {
      const res = await fetch(`/api/audit/${this.currentFieldId}`);
      const json = await res.json();
      if (json.status === 'success') {
        tbody.innerHTML = json.data.map(a => `
          <tr>
            <td class="font-mono" style="font-size: 0.8rem;">${a.created_at}</td>
            <td><span class="badge badge-info">${a.action_type}</span></td>
            <td><b>${a.description}</b></td>
            <td>${a.operator || 'Farmer'}</td>
            <td>${a.cost_inr ? `₹${a.cost_inr.toLocaleString()}` : '-'}</td>
            <td class="text-muted" style="font-size: 0.8rem;">${a.notes || ''}</td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.warn(e);
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ';
    toast.innerHTML = `<span style="font-weight: bold; font-size: 1.1rem;">${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 3800);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
