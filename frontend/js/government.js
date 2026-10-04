/**
 * Smart Crop Advisory - Government Welfare Schemes Controller
 */

const Government = {
  async init() {
    this.loadSchemes();
  },

  async loadSchemes() {
    try {
      const res = await fetch('/api/government/schemes');
      const json = await res.json();
      if (json.status === 'success') {
        this.renderSchemes(json.data);
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderSchemes(schemes) {
    const container = document.getElementById('schemes-grid-container');
    if (!container) return;

    container.innerHTML = schemes.map(s => `
      <div class="card" style="border-top: 4px solid var(--primary-light); display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="font-size: 0.72rem; color: var(--primary-light); font-weight: 700; text-transform: uppercase; margin-bottom: 4px;">
            ${s.ministry}
          </div>
          <h3 style="font-size: 1.15rem; font-weight: 800; color: var(--text-main); margin-bottom: 2px;">
            ${s.scheme_name}
          </h3>
          ${s.hindi_name ? `<div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px;">${s.hindi_name}</div>` : ''}

          <p style="font-size: 0.84rem; color: var(--text-main); margin-bottom: 12px; line-height: 1.5;">
            ${s.purpose}
          </p>

          <div style="background: var(--bg-muted); padding: 10px; border-radius: var(--radius-sm); margin-bottom: 12px; font-size: 0.8rem;">
            <div style="margin-bottom: 6px;">
              <b>Eligibility:</b> ${s.eligibility_info}
            </div>
            <div>
              <b>Direct Benefits:</b> ${s.benefits_summary}
            </div>
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; pt: 10px; border-top: 1px solid var(--border); font-size: 0.82rem;">
          <span class="text-muted">Toll-Free: <b>${s.helpline_number}</b></span>
          <a href="${s.official_portal_url}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">
            Official Portal ↗
          </a>
        </div>
      </div>
    `).join('');
  }
};
