/**
 * Smart Crop Advisory - AI Crop Health & Disease Diagnostic Controller
 */

const CropHealth = {
  currentFile: null,

  init() {
    this.bindEvents();
    this.loadHistory();
  },

  bindEvents() {
    const fileInput = document.getElementById('disease-file-input');
    const dropzone = document.getElementById('disease-dropzone');
    const previewImg = document.getElementById('disease-preview-img');
    const analyzeBtn = document.getElementById('btn-analyze-disease');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());
      
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleFile(e.target.files[0]);
        }
      });

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--primary-light)';
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'var(--border)';
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => this.analyzeImage());
    }
  },

  handleFile(file) {
    this.currentFile = file;
    const previewImg = document.getElementById('disease-preview-img');
    const dropPrompt = document.getElementById('dropzone-prompt');

    if (previewImg) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewImg.style.display = 'block';
        if (dropPrompt) dropPrompt.style.display = 'none';
      };
      reader.readAsDataURL(file);
    }
  },

  async analyzeImage() {
    const cropSelect = document.getElementById('disease-crop-select');
    const stageSelect = document.getElementById('disease-stage-select');
    const symptomInput = document.getElementById('disease-symptoms-input');
    const statusBox = document.getElementById('diagnostic-status-box');

    const crop = cropSelect ? cropSelect.value : 'Wheat';
    const stage = stageSelect ? stageSelect.value : 'Flowering & Anthesis';
    const symptoms = symptomInput ? symptomInput.value : '';

    const formData = new FormData();
    formData.append('crop', crop);
    formData.append('stage', stage);
    formData.append('symptoms', symptoms);
    formData.append('field_id', App.currentFieldId);

    if (this.currentFile) {
      formData.append('image', this.currentFile);
    }

    if (statusBox) {
      statusBox.style.display = 'block';
      statusBox.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <div class="pulse-dot"></div>
          <div><b>Executing Agricultural Pathology Diagnostics...</b> Scanning visual foliar patterns & analyzing pathogen risk.</div>
        </div>
      `;
    }

    try {
      const res = await fetch('/api/crop-health/analyze', {
        method: 'POST',
        body: formData
      });
      const json = await res.json();

      if (statusBox) statusBox.style.display = 'none';

      if (json.status === 'success') {
        this.renderDiagnosis(json.data);
        this.loadHistory();
        App.showToast(`Diagnosed: ${json.data.conditionName}`, "success");
      } else {
        App.showToast(json.message || "Diagnostic failed", "error");
      }
    } catch (e) {
      if (statusBox) statusBox.style.display = 'none';
      App.showToast("Analysis request failed. Please check network.", "error");
    }
  },

  renderDiagnosis(diag) {
    const resContainer = document.getElementById('disease-result-container');
    if (!resContainer) return;

    resContainer.style.display = 'block';
    resContainer.scrollIntoView({ behavior: 'smooth' });

    const isOffline = diag.source === 'offline-rule-engine';

    resContainer.innerHTML = `
      <div class="card" style="border-top: 5px solid ${diag.severityLevel === 'HIGH' || diag.severityLevel === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)'};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
          <div>
            <div style="display: flex; align-items: center; gap: 10px;">
              <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main);">${diag.conditionName}</h3>
              ${diag.hindiName ? `<span style="font-size: 1rem; color: var(--text-muted);">(${diag.hindiName})</span>` : ''}
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">
              Causal Agent: <i>${diag.causalOrganism || 'Fungal Spore Complex'}</i>
            </div>
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <span class="badge ${diag.severityLevel === 'CRITICAL' || diag.severityLevel === 'HIGH' ? 'badge-danger' : 'badge-warning'}">
              ${diag.severityLevel} SEVERITY
            </span>
            <span class="badge badge-info">
              Risk: ${diag.riskPct}%
            </span>
          </div>
        </div>

        <!-- Engine Indicator Badge Required by Section 11 & 12 -->
        <div style="margin-bottom: 16px; padding: 8px 12px; background: ${isOffline ? '#fef3c7' : '#dcfce7'}; border-radius: var(--radius-sm); font-size: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
          <span style="font-weight: 700; color: ${isOffline ? '#92400e' : '#166534'};">
            Engine: ${isOffline ? 'Offline Demo / Rule-Based Analysis' : 'Gemini 2.5 Multimodal Vision AI'}
          </span>
          <span style="color: var(--text-muted);">Confidence: ${(diag.confidence * 100).toFixed(0)}%</span>
        </div>

        <!-- Symptoms -->
        <div style="margin-bottom: 16px;">
          <h4 style="font-size: 0.92rem; font-weight: 700; margin-bottom: 6px;">Identified Visual Symptoms:</h4>
          <ul style="padding-left: 20px; font-size: 0.85rem; color: var(--text-main); line-height: 1.6;">
            ${(diag.visualSymptoms || []).map(s => `<li>${s}</li>`).join('')}
          </ul>
        </div>

        <!-- Treatments Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px;">
          <div style="background: var(--bg-muted); padding: 14px; border-radius: var(--radius-sm); border-left: 3px solid #0284c7;">
            <h5 style="font-size: 0.88rem; font-weight: 700; color: #0284c7; margin-bottom: 6px;">💊 Chemical Control Prescription:</h5>
            <p style="font-size: 0.82rem; line-height: 1.5; color: var(--text-main);">${diag.chemicalTreatment || 'N/A'}</p>
          </div>
          <div style="background: var(--bg-muted); padding: 14px; border-radius: var(--radius-sm); border-left: 3px solid #16a34a;">
            <h5 style="font-size: 0.88rem; font-weight: 700; color: #16a34a; margin-bottom: 6px;">🌿 Organic / Bio-Control Alternative:</h5>
            <p style="font-size: 0.82rem; line-height: 1.5; color: var(--text-main);">${diag.organicBioControl || 'N/A'}</p>
          </div>
        </div>

        <!-- Economic Impact -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border); font-size: 0.88rem;">
          <div>Estimated Intervention Cost: <b style="color: var(--primary-light);">₹${(diag.estimatedCostInr || 500).toLocaleString()} / Acre</b></div>
          <button class="btn btn-primary btn-sm" onclick="App.switchView('finance')">Log In Expense Ledger</button>
        </div>
      </div>
    `;
  },

  async loadHistory() {
    const list = document.getElementById('disease-history-list');
    if (!list) return;

    try {
      const res = await fetch(`/api/crop-health/history/${App.currentFieldId}`);
      const json = await res.json();
      if (json.status === 'success' && json.data.length > 0) {
        list.innerHTML = json.data.map(h => `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 0.84rem;">
            <div>
              <div style="font-weight: 700; color: var(--text-main);">${h.condition_name} (${h.crop_name})</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">${h.created_at} • Source: ${h.source}</div>
            </div>
            <span class="badge ${h.severity_level === 'HIGH' ? 'badge-danger' : 'badge-warning'}">${h.severity_level}</span>
          </div>
        `).join('');
      } else {
        list.innerHTML = `<div class="text-muted" style="font-size: 0.82rem; padding: 8px 0;">No prior disease scans logged for this plot.</div>`;
      }
    } catch (e) {
      console.warn(e);
    }
  }
};
