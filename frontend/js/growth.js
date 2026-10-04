/**
 * Smart Crop Advisory - Crop Growth & Harvest Stage Tracking
 */

const Growth = {
  async init() {
    this.bindEvents();
    this.refreshData();
  },

  bindEvents() {
    const updateStageBtn = document.getElementById('btn-update-crop-stage');
    if (updateStageBtn) {
      updateStageBtn.addEventListener('click', () => this.updateStage());
    }
  },

  async refreshData() {
    try {
      const res = await fetch(`/api/growth/${App.currentFieldId}`);
      const json = await res.json();
      if (json.status === 'success') {
        this.renderHistory(json.data);
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderHistory(records) {
    const tbody = document.getElementById('growth-history-tbody');
    if (tbody) {
      if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-muted text-center">No growth records logged yet.</td></tr>`;
        return;
      }
      tbody.innerHTML = records.map(r => `
        <tr>
          <td><b>${r.stage_name}</b></td>
          <td>Day ${r.days_from_sowing}</td>
          <td>${r.cumulative_gdd} °C-days</td>
          <td>${r.plant_height_cm || 0} cm</td>
          <td><span class="badge badge-success">${r.health_index || 92}% Index</span></td>
        </tr>
      `).join('');
    }
  },

  async updateStage() {
    const stageSelect = document.getElementById('growth-stage-input');
    const gddInput = document.getElementById('growth-gdd-input');
    const heightInput = document.getElementById('growth-height-input');

    const stage = stageSelect ? stageSelect.value : 'Grain Filling / Dough';
    const gdd = parseFloat(gddInput ? gddInput.value : 1800);
    const height = parseFloat(heightInput ? heightInput.value : 95);

    try {
      const res = await fetch(`/api/growth/${App.currentFieldId}/update-stage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stage: stage,
          gdd: gdd,
          height_cm: height
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast(`Crop advanced to ${stage} stage. Timeline updated!`, "success");
        await this.refreshData();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Failed to update growth stage", "error");
    }
  }
};
