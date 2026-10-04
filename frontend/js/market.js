/**
 * Smart Crop Advisory - Mandi Market Intelligence Controller
 */

const Market = {
  async init() {
    this.bindEvents();
    this.refreshPrices();
  },

  bindEvents() {
    const cropFilter = document.getElementById('mandi-crop-filter');
    if (cropFilter) {
      cropFilter.addEventListener('change', () => this.refreshPrices());
    }
  },

  async refreshPrices() {
    const filter = document.getElementById('mandi-crop-filter')?.value || 'All';
    try {
      const res = await fetch('/api/market-prices');
      const json = await res.json();
      if (json.status === 'success') {
        let prices = json.data;
        if (filter !== 'All') {
          prices = prices.filter(p => p.crop_name.toLowerCase().includes(filter.toLowerCase()));
        }
        this.renderTable(prices);
        this.renderSummary(prices);
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderSummary(prices) {
    if (!prices || prices.length === 0) return;
    const best = prices.reduce((max, p) => p.modal_price > max.modal_price ? p : max, prices[0]);
    const avg = prices.reduce((sum, p) => sum + p.modal_price, 0) / prices.length;

    const bestEl = document.getElementById('market-top-mandi');
    const bestPriceEl = document.getElementById('market-top-price');
    const avgEl = document.getElementById('market-avg-price');

    if (bestEl) bestEl.textContent = `${best.mandi_name} (${best.crop_name})`;
    if (bestPriceEl) bestPriceEl.textContent = `₹${best.modal_price.toLocaleString()}/Qtl`;
    if (avgEl) avgEl.textContent = `₹${avg.toFixed(0)}/Qtl`;
  },

  renderTable(prices) {
    const tbody = document.getElementById('mandi-table-tbody');
    if (!tbody) return;

    if (prices.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-muted text-center">No market quotes found.</td></tr>`;
      return;
    }

    tbody.innerHTML = prices.map(p => {
      const diff = p.modal_price - p.msp_price;
      const isPositive = diff >= 0;
      const trendColor = p.trend === 'RISING' ? 'var(--success)' : p.trend === 'FALLING' ? 'var(--danger)' : 'var(--text-muted)';
      const trendIcon = p.trend === 'RISING' ? '▲' : p.trend === 'FALLING' ? '▼' : '▬';

      return `
        <tr>
          <td><b>${p.mandi_name}</b></td>
          <td>${p.district}, ${p.state}</td>
          <td>${p.crop_name} <span class="text-muted">(${p.variety || ''})</span></td>
          <td><b>₹${p.modal_price.toLocaleString()}</b></td>
          <td>₹${p.msp_price.toLocaleString()}</td>
          <td style="font-weight: 700; color: ${isPositive ? 'var(--success)' : 'var(--danger)'};">
            ${isPositive ? '+' : ''}₹${diff.toLocaleString()}
          </td>
          <td>
            <span style="font-weight: bold; color: ${trendColor};">
              ${trendIcon} ${p.trend} (${p.trend_pct > 0 ? '+' : ''}${p.trend_pct}%)
            </span>
          </td>
          <td>${p.arrival_tonnes ? `${p.arrival_tonnes} MT` : '350 MT'}</td>
        </tr>
      `;
    }).join('');
  }
};
