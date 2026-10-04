/**
 * Smart Crop Advisory - PMFBY Insurance Claim Dossier Controller
 */

const Insurance = {
  async init() {
    this.bindEvents();
    this.refreshClaims();
  },

  bindEvents() {
    const genBtn = document.getElementById('btn-generate-pmfby-claim');
    if (genBtn) {
      genBtn.addEventListener('click', () => this.generateDossier());
    }
  },

  async refreshClaims() {
    try {
      const res = await fetch('/api/insurance/claims');
      const json = await res.json();
      if (json.status === 'success') {
        this.renderClaimsTable(json.data);
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderClaimsTable(claims) {
    const tbody = document.getElementById('insurance-claims-tbody');
    if (!tbody) return;

    if (!claims || claims.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-muted text-center">No active insurance claim dossiers filed yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = claims.map(c => `
      <tr>
        <td><b>${c.claim_number}</b></td>
        <td>${c.field_code || 'FLD-01'}</td>
        <td><span class="badge badge-danger">${c.disaster_type}</span></td>
        <td>${c.affected_area_ha} Ha</td>
        <td class="font-bold">₹${c.claimed_loss_inr.toLocaleString()}</td>
        <td><span class="badge badge-info">${c.status}</span></td>
        <td>
          <a href="/api/insurance/download/${c.claim_number}" class="btn btn-secondary btn-sm" target="_blank" download>
            📄 Download Official PDF
          </a>
        </td>
      </tr>
    `).join('');
  },

  async generateDossier() {
    const perilSelect = document.getElementById('claim-peril-type');
    const areaInput = document.getElementById('claim-affected-ha');
    const lossInput = document.getElementById('claim-loss-amount');

    const peril = perilSelect ? perilSelect.value : 'Flash Flood / Crop Submersion';
    const area = parseFloat(areaInput ? areaInput.value : 1.8);
    const loss = parseFloat(lossInput ? lossInput.value : 52000);

    const btn = document.getElementById('btn-generate-pmfby-claim');
    if (btn) btn.disabled = true;

    try {
      App.showToast("Compiling official PMFBY claim package with satellite telemetry...", "info");
      const res = await fetch('/api/insurance/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          disaster_type: peril,
          affected_area_ha: area,
          claimed_loss_inr: loss
        })
      });
      const json = await res.json();
      if (btn) btn.disabled = false;

      if (json.status === 'success') {
        App.showToast("PMFBY Claim Dossier PDF compiled successfully!", "success");
        this.renderGeneratedModal(json.data);
        this.refreshClaims();
        Dashboard.loadDashboardData(App.currentFieldId);
      } else {
        App.showToast(json.message || "Failed to compile claim", "error");
      }
    } catch (e) {
      if (btn) btn.disabled = false;
      App.showToast("Error generating claim dossier", "error");
    }
  },

  renderGeneratedModal(data) {
    const container = document.getElementById('generated-claim-result');
    if (!container) return;

    container.style.display = 'block';
    container.innerHTML = `
      <div class="card" style="border: 2px solid var(--primary-light); background: var(--bg-card); margin-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h4 style="color: var(--primary-light); font-size: 1.15rem; font-weight: 800;">
            ✓ PMFBY Claim Dossier Compiled: ${data.claim_number}
          </h4>
          <span class="badge badge-success">${data.status}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 14px;">
          The multi-page PDF claim dossier integrates beneficiary profile, cadastral parcel bounds, Sentinel-2 spectral NDVI anomaly maps, and ground IoT soil saturation telemetry.
        </p>
        <div style="display: flex; gap: 12px;">
          <a href="${data.download_url}" class="btn btn-primary" download>
            📥 Download PMFBY Claim Dossier (PDF)
          </a>
          <button class="btn btn-secondary" onclick="document.getElementById('generated-claim-result').style.display='none'">
            Dismiss
          </button>
        </div>
      </div>
    `;
    container.scrollIntoView({ behavior: 'smooth' });
  }
};
