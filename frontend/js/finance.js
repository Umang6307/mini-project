/**
 * Smart Crop Advisory - Farm Finance, Expense Ledger & P&L Controller
 */

const Finance = {
  data: null,

  async init() {
    this.bindEvents();
    this.refreshData();
  },

  bindEvents() {
    const addExpenseBtn = document.getElementById('btn-add-expense-modal');
    if (addExpenseBtn) {
      addExpenseBtn.addEventListener('click', () => {
        document.getElementById('modal-expense').classList.add('active');
      });
    }

    const saveExpenseBtn = document.getElementById('btn-save-expense');
    if (saveExpenseBtn) {
      saveExpenseBtn.addEventListener('click', () => this.saveExpense());
    }

    const addSaleBtn = document.getElementById('btn-add-sale-modal');
    if (addSaleBtn) {
      addSaleBtn.addEventListener('click', () => {
        document.getElementById('modal-sale').classList.add('active');
      });
    }

    const saveSaleBtn = document.getElementById('btn-save-sale');
    if (saveSaleBtn) {
      saveSaleBtn.addEventListener('click', () => this.saveSale());
    }
  },

  async refreshData() {
    try {
      const res = await fetch(`/api/finance/${App.currentFieldId}`);
      const json = await res.json();
      if (json.status === 'success') {
        this.data = json.data;
        this.renderSummary();
        this.renderExpenses();
        this.renderSales();
        this.renderCategoryChart();
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderSummary() {
    if (!this.data?.summary) return;
    const s = this.data.summary;

    const expEl = document.getElementById('fin-total-expense');
    const revEl = document.getElementById('fin-total-revenue');
    const profitEl = document.getElementById('fin-net-profit');
    const roiEl = document.getElementById('fin-roi');

    if (expEl) expEl.textContent = `₹${s.total_expenses.toLocaleString()}`;
    if (revEl) revEl.textContent = `₹${s.total_revenue.toLocaleString()}`;
    if (profitEl) {
      profitEl.textContent = `₹${s.net_profit.toLocaleString()}`;
      profitEl.style.color = s.net_profit >= 0 ? 'var(--success)' : 'var(--danger)';
    }
    if (roiEl) roiEl.textContent = `${s.roi_pct}%`;
  },

  renderExpenses() {
    const tbody = document.getElementById('expenses-tbody');
    if (!tbody || !this.data?.expenses) return;

    if (this.data.expenses.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-muted text-center">No expenses recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.data.expenses.map(e => `
      <tr>
        <td>${e.expense_date}</td>
        <td><span class="badge badge-info">${e.category}</span></td>
        <td><b>${e.item_name}</b></td>
        <td>${e.quantity} ${e.unit || ''}</td>
        <td class="font-bold text-right">₹${e.cost_inr.toLocaleString()}</td>
      </tr>
    `).join('');
  },

  renderSales() {
    const tbody = document.getElementById('sales-tbody');
    if (!tbody || !this.data?.sales) return;

    if (this.data.sales.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-muted text-center">No harvest sales recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.data.sales.map(s => `
      <tr>
        <td>${s.sale_date}</td>
        <td><b>${s.crop_name}</b></td>
        <td>${s.buyer_mandi}</td>
        <td>${s.quantity_quintals} Qtl</td>
        <td>₹${s.price_per_quintal_inr}/Qtl</td>
        <td class="font-bold text-right" style="color: var(--success);">₹${s.net_revenue_inr.toLocaleString()}</td>
      </tr>
    `).join('');
  },

  renderCategoryChart() {
    const container = document.getElementById('finance-chart-container');
    if (!container || !this.data?.summary?.category_breakdown) return;

    const cats = this.data.summary.category_breakdown;
    const entries = Object.entries(cats);
    if (entries.length === 0) {
      container.innerHTML = `<div class="text-muted text-center" style="padding: 20px;">No expense categories to chart.</div>`;
      return;
    }

    const total = Object.values(cats).reduce((a, b) => a + b, 0);

    const colors = ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#b7e4c7', '#d8f3dc'];

    let barsHtml = '';
    entries.forEach(([cat, val], idx) => {
      const pct = total > 0 ? (val / total * 100).toFixed(1) : 0;
      const col = colors[idx % colors.length];
      barsHtml += `
        <div style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span><b>${cat}</b> (${pct}%)</span>
            <span>₹${val.toLocaleString()}</span>
          </div>
          <div style="background: var(--border); height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="background: ${col}; width: ${pct}%; height: 100%;"></div>
          </div>
        </div>
      `;
    });

    container.innerHTML = barsHtml;
  },

  async saveExpense() {
    const cat = document.getElementById('exp-category')?.value || 'Fertilizer';
    const item = document.getElementById('exp-item')?.value || 'Fertilizer Bag';
    const qty = parseFloat(document.getElementById('exp-quantity')?.value || 1);
    const cost = parseFloat(document.getElementById('exp-cost')?.value || 0);

    if (!item || cost <= 0) {
      App.showToast("Please enter an item name and valid cost", "warning");
      return;
    }

    try {
      const res = await fetch('/api/finance/expense', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          category: cat,
          item_name: item,
          quantity: qty,
          cost_inr: cost
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("Expense logged successfully!", "success");
        document.getElementById('modal-expense').classList.remove('active');
        this.refreshData();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Error saving expense", "error");
    }
  },

  async saveSale() {
    const crop = document.getElementById('sale-crop')?.value || 'Wheat';
    const mandi = document.getElementById('sale-mandi')?.value || 'Karnal Mandi';
    const qty = parseFloat(document.getElementById('sale-qty')?.value || 10);
    const rate = parseFloat(document.getElementById('sale-rate')?.value || 2490);

    if (qty <= 0 || rate <= 0) {
      App.showToast("Please enter valid quantity and rate", "warning");
      return;
    }

    try {
      const res = await fetch('/api/finance/sale', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          field_id: App.currentFieldId,
          crop_name: crop,
          buyer_mandi: mandi,
          quantity_quintals: qty,
          price_per_quintal_inr: rate
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("Harvest sale recorded successfully!", "success");
        document.getElementById('modal-sale').classList.remove('active');
        this.refreshData();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Error saving sale", "error");
    }
  }
};
