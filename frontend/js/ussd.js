/**
 * Smart Crop Advisory - USSD / SMS Phone Simulator (*515#)
 */

const Ussd = {
  screenText: "=== KISAN SMART ADVISORY ===\nReady to dial.\nType *515# and press SEND to query live farm telemetry without internet.",
  inputBuffer: "*515#",

  init() {
    this.bindEvents();
    this.updateScreen();
  },

  bindEvents() {
    const inputEl = document.getElementById('ussd-code-input');
    const sendBtn = document.getElementById('ussd-send-btn');
    const clearBtn = document.getElementById('ussd-clear-btn');

    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendCode());
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.inputBuffer = "";
        this.updateInput();
      });
    }

    // Keypad numbers
    document.querySelectorAll('.ussd-key').forEach(key => {
      key.addEventListener('click', (e) => {
        const val = e.currentTarget.getAttribute('data-val');
        if (val === 'CALL' || val === 'SEND') {
          this.sendCode();
        } else if (val === 'CLR') {
          this.inputBuffer = this.inputBuffer.slice(0, -1);
          this.updateInput();
        } else {
          this.inputBuffer += val;
          this.updateInput();
        }
      });
    });

    if (inputEl) {
      inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          this.sendCode();
        }
      });
    }
  },

  updateScreen() {
    const screen = document.getElementById('ussd-terminal-screen');
    if (screen) {
      screen.textContent = this.screenText;
    }
  },

  updateInput() {
    const input = document.getElementById('ussd-code-input');
    if (input) {
      input.value = this.inputBuffer;
    }
  },

  async sendCode() {
    const input = document.getElementById('ussd-code-input');
    const code = input ? input.value.trim() : this.inputBuffer.trim();

    if (!code) return;

    this.screenText = `[Dialing ${code} ...]\nConnecting to Rural Agri Gateway...`;
    this.updateScreen();

    try {
      const res = await fetch('/api/ussd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, field_id: App.currentFieldId })
      });
      const json = await res.json();
      if (json.status === 'success') {
        this.screenText = json.data.response;
        this.updateScreen();
        this.inputBuffer = "";
        this.updateInput();
      }
    } catch (e) {
      this.screenText = "Network Error: Unable to connect to Kisan USSD gateway.";
      this.updateScreen();
    }
  },

  dialShortcut(code) {
    this.inputBuffer = code;
    this.updateInput();
    this.sendCode();
  }
};
