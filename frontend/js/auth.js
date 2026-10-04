/**
 * Smart Crop Advisory - Authentication & Session Management
 */

const Auth = {
  getUser() {
    try {
      const data = localStorage.getItem('sca_user');
      return data ? JSON.parse(data) : {
        user_id: 1,
        username: 'ravi',
        role: 'farmer',
        is_demo: true,
        farmer: {
          id: 1,
          full_name: 'Ravi Kumar',
          village: 'Kachhwa Village',
          district: 'Karnal',
          state: 'Haryana',
          phone: '+91 98120 12345'
        }
      };
    } catch (e) {
      return null;
    }
  },

  setUser(userData) {
    localStorage.setItem('sca_user', JSON.stringify(userData));
    this.updateHeaderProfile();
  },

  isLoggedIn() {
    return Boolean(localStorage.getItem('sca_user'));
  },

  logout() {
    localStorage.removeItem('sca_user');
    window.location.href = '/login.html';
  },

  async login(username, password) {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.status === 'success') {
        this.setUser(data.data);
        return { success: true, data: data.data };
      }
      return { success: false, message: data.message };
    } catch (err) {
      return { success: false, message: "Network error during login." };
    }
  },

  async signup(formData) {
    try {
      const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.status === 'success') {
        this.setUser(data.data);
        return { success: true, data: data.data };
      }
      return { success: false, message: data.message };
    } catch (err) {
      return { success: false, message: "Network error during registration." };
    }
  },

  loadDemoAccount(profile) {
    if (profile === 'sunita') {
      const sunita = {
        user_id: 2,
        username: 'sunita',
        role: 'farmer',
        is_demo: true,
        farmer: {
          id: 2,
          full_name: 'Sunita Devi',
          village: 'Nilokheri',
          district: 'Karnal',
          state: 'Haryana',
          phone: '+91 94160 54321'
        }
      };
      this.setUser(sunita);
    } else {
      const ravi = {
        user_id: 1,
        username: 'ravi',
        role: 'farmer',
        is_demo: true,
        farmer: {
          id: 1,
          full_name: 'Ravi Kumar',
          village: 'Kachhwa Village',
          district: 'Karnal',
          state: 'Haryana',
          phone: '+91 98120 12345'
        }
      };
      this.setUser(ravi);
    }
    window.location.reload();
  },

  updateHeaderProfile() {
    const user = this.getUser();
    if (user && user.farmer) {
      const nameEl = document.getElementById('farmer-display-name');
      const locEl = document.getElementById('farmer-display-location');
      const avatarEl = document.getElementById('farmer-avatar');
      if (nameEl) nameEl.textContent = user.farmer.full_name;
      if (locEl) locEl.textContent = `${user.farmer.village}, ${user.farmer.district}`;
      if (avatarEl) avatarEl.textContent = user.farmer.full_name.charAt(0);
    }
  }
};
