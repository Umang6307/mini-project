/**
 * Smart Crop Advisory - Machinery Hub & Custom Hiring Controller
 */

const Machinery = {
  selectedMachineryId: null,

  async init() {
    this.bindEvents();
    this.refreshMachinery();
  },

  bindEvents() {
    const confirmBookBtn = document.getElementById('btn-confirm-booking');
    if (confirmBookBtn) {
      confirmBookBtn.addEventListener('click', () => this.confirmBooking());
    }
  },

  async refreshMachinery() {
    try {
      const res = await fetch('/api/machinery');
      const json = await res.json();
      if (json.status === 'success') {
        this.renderCatalog(json.data.equipment);
        this.renderBookings(json.data.recent_bookings);
      }
    } catch (e) {
      console.error(e);
    }
  },

  renderCatalog(items) {
    const container = document.getElementById('machinery-catalog-grid');
    if (!container) return;

    container.innerHTML = items.map(m => `
      <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main);">${m.equipment_name}</h4>
            <span class="badge ${m.status === 'Available' ? 'badge-success' : 'badge-warning'}">${m.status}</span>
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 10px;">
            Category: <b>${m.equipment_type}</b> • Reg: ${m.registration_number || 'CHC-Fleet'}
          </div>

          <div style="background: var(--bg-muted); padding: 10px; border-radius: var(--radius-sm); margin-bottom: 12px; font-size: 0.82rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="text-muted">Rental Rate:</span>
              <span class="font-bold" style="color: var(--primary-light);">₹${m.operating_cost_per_hour}/Hour</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span class="text-muted">Ownership:</span>
              <span>${m.ownership}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="text-muted">Contact:</span>
              <span>${m.contact_phone || '+91 94160 88210'}</span>
            </div>
          </div>
        </div>

        <div>
          <button class="btn btn-primary" style="width: 100%;" onclick="Machinery.openBookModal(${m.id}, '${m.equipment_name}', ${m.operating_cost_per_hour})">
            🚜 Book Equipment
          </button>
        </div>
      </div>
    `).join('');
  },

  renderBookings(bookings) {
    const tbody = document.getElementById('machinery-bookings-tbody');
    if (!tbody) return;

    if (!bookings || bookings.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-muted text-center">No recent equipment bookings.</td></tr>`;
      return;
    }

    tbody.innerHTML = bookings.map(b => `
      <tr>
        <td>${b.start_date}</td>
        <td><b>${b.activity_type}</b></td>
        <td>${b.duration_hours} Hours</td>
        <td>₹${b.cost_inr.toLocaleString()}</td>
        <td><span class="badge badge-success">${b.status}</span></td>
      </tr>
    `).join('');
  },

  openBookModal(id, name, rate) {
    this.selectedMachineryId = id;
    const nameEl = document.getElementById('book-machinery-name');
    const rateEl = document.getElementById('book-machinery-rate');
    if (nameEl) nameEl.textContent = name;
    if (rateEl) rateEl.textContent = `₹${rate}/Hour`;

    document.getElementById('modal-machinery').classList.add('active');
  },

  async confirmBooking() {
    const hours = parseFloat(document.getElementById('book-hours')?.value || 4.0);
    const dateVal = document.getElementById('book-date')?.value || new Date().toISOString().split('T')[0];

    try {
      const res = await fetch('/api/machinery/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          machinery_id: this.selectedMachineryId,
          field_id: App.currentFieldId,
          duration_hours: hours,
          start_date: dateVal
        })
      });
      const json = await res.json();
      if (json.status === 'success') {
        App.showToast("Equipment reserved! Logged in farm expenses and audit log.", "success");
        document.getElementById('modal-machinery').classList.remove('active');
        this.refreshMachinery();
        Dashboard.loadDashboardData(App.currentFieldId);
      }
    } catch (e) {
      App.showToast("Booking failed", "error");
    }
  }
};
