/**
 * Smart Crop Advisory - Localization Manager (English & हिन्दी)
 */

const Localization = {
  currentLang: localStorage.getItem('sca_lang') || 'en',
  translations: {},

  async init() {
    try {
      const res = await fetch('/api/translations');
      if (res.ok) {
        this.translations = await res.json();
      }
    } catch (e) {
      console.warn("Could not load translations from API, using defaults", e);
    }
    this.applyLanguage(this.currentLang);
  },

  setLanguage(lang) {
    this.currentLang = lang;
    localStorage.setItem('sca_lang', lang);
    this.applyLanguage(lang);
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
      langBtn.textContent = lang === 'en' ? '🌐 हिन्दी' : '🌐 English';
    }
  },

  toggleLanguage() {
    this.setLanguage(this.currentLang === 'en' ? 'hi' : 'en');
  },

  t(key, defaultText = "") {
    if (this.translations[key] && this.translations[key][this.currentLang]) {
      return this.translations[key][this.currentLang];
    }
    return defaultText || key;
  },

  applyLanguage(lang) {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.translations[key] && this.translations[key][lang]) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = this.translations[key][lang];
        } else {
          el.textContent = this.translations[key][lang];
        }
      }
    });
  }
};
