# SMART CROP ADVISORY (स्मार्ट फसल सलाहकार)
### Precision Agricultural Decision-Support System for Indian Farmers

A comprehensive, full-stack agricultural decision-support platform designed to act as a digital control center for Indian farmers. The platform integrates soil telemetry, weather observations, precision irrigation and fertilizer recommendations, AI multimodal crop disease diagnosis, mandi market intelligence, farm finances, machinery booking, Sentinel-2 satellite disaster assessment, official PMFBY claim dossier generation, government welfare schemes, and an offline USSD/SMS phone simulator.

---

## Architecture & Technology Stack

- **Frontend:** Semantic HTML5, CSS3 with CSS custom properties (Dark/Light themes), Vanilla JavaScript (No React, Vue, Angular, or Node frontend frameworks).
- **Backend:** Python 3.10+ (Flask REST API serving structured JSON).
- **Database:** SQLite3 normalized relational database with 21 relational tables, foreign key constraints, and audit logging.
- **Data Exchange:** Pure REST JSON endpoints.
- **Reporting Engine:** ReportLab for official PMFBY PDF claim dossiers.
- **AI Diagnostics:** Dual-mode architecture (Google Gemini Multimodal Vision API when configured; automated `OfflineFallbackManager` heuristic rule-based engine when offline).

---

## Table of Contents
1. [Prerequisites](#a-prerequisites)
2. [Python Installation](#b-python-installation)
3. [Database Setup](#c-database-setup)
4. [Environment Variables](#d-environment-variables)
5. [Installing Dependencies](#e-installing-dependencies)
6. [Starting the Full-Stack Application](#f-starting-the-application)
7. [Opening the Frontend](#g-opening-the-frontend)
8. [Demo Login Credentials](#h-demo-login-credentials)
9. [How to Test Every Module](#i-how-to-test-every-module)
10. [How to Run Without Gemini API (Offline Fallback)](#j-how-to-run-without-gemini-api)
11. [How to Reset Demo Data](#k-how-to-reset-demo-data)
12. [Judges' Quick-Demo Workflow](#l-judges-quick-demo-workflow)
13. [Troubleshooting](#m-troubleshooting)

---

### A. Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

### B. Python Installation
Verify Python and pip are installed:
```bash
python3 --version
pip3 --version
```
If Python is not installed on Debian/Ubuntu systems:
```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

---

### C. Database Setup
The SQLite relational database (`database/smart_crop.db`) initializes automatically upon starting the application using:
- `database/schema.sql` (Creates all 21 normalized relational tables and indexes)
- `database/seed.sql` (Seeds crop catalogs, fertilizers, machinery, government schemes)
- `database/demo_data.sql` (Populates demonstration farmers Ravi Kumar and Sunita Devi, field parcels, soil readings, weather readings, and audit trails)

To manually initialize or inspect the database:
```bash
sqlite3 database/smart_crop.db < database/schema.sql
sqlite3 database/smart_crop.db < database/seed.sql
sqlite3 database/smart_crop.db < database/demo_data.sql
```

---

### D. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Configuration variables:
```ini
PORT=3000
SECRET_KEY=smart_crop_advisory_production_key_2026
DATABASE_PATH=database/smart_crop.db

# Optional: Google Gemini API Key for vision-based crop disease diagnosis.
# If left blank, system automatically uses OfflineFallbackManager.
GEMINI_API_KEY=
```

---

### E. Installing Dependencies
Install all required Python packages from `requirements.txt`:
```bash
pip3 install -r requirements.txt
```
*(Dependencies: `flask`, `reportlab`, `pillow`, `requests`)*

---

### F. Starting the Application
Start the full-stack Python application:
```bash
python3 backend/app.py
```
Or using the package script:
```bash
npm run dev
```
The server will start listening on `http://0.0.0.0:3000`.

---

### G. Opening the Frontend
Open your browser and navigate to:
```
http://localhost:3000
```
- Direct Dashboard: `http://localhost:3000/dashboard.html`
- Login Page: `http://localhost:3000/login.html`

---

### H. Demo Login Credentials

| Role | Username | Password | Location | Primary Crop |
| :--- | :--- | :--- | :--- | :--- |
| **Farmer (Default)** | `ravi` | `password123` | Karnal, Haryana | Wheat (HD-3086) |
| **Farmer (Secondary)** | `sunita` | `password123` | Nilokheri, Haryana | Paddy (Basmati 1121) |
| **Evaluator / Judge** | `evaluator` | `judge2026` | Karnal | Multi-Crop Demo Mode |

*Tip: Click the "One-Click Demo Mode" buttons on `/login.html` to instantly sign in without typing.*

---

### I. How to Test Every Module

1. **Dashboard (`/dashboard.html`):**
   - View top metrics: Crop, 15cm Soil Moisture, Temperature, Humidity, Health Score, Harvest Estimate, Mandi Rate.
   - Observe the 7-Day Moisture Trend SVG chart and interactive Crop Phenology Lifecycle timeline.
   - Switch parcels using the topbar dropdown between `FLD-01` (Wheat), `FLD-02` (Mustard), and `FLD-03` (Paddy).

2. **Irrigation Decision Engine:**
   - Navigate to **Irrigation Engine** in the sidebar.
   - Drag the Soil Moisture slider from 34% down to 18% (Deficit).
   - Click **Recalculate Decision Engine**. Notice the system computes required water depth (e.g. 28 mm), water volume in m³, pump duration in hours, and urgency ("IMMEDIATE within 6-12h").
   - Click **Execute & Record Irrigation** to restore root-zone moisture and log the activity into the audit trail.

3. **Fertilizer & Nutrient Module:**
   - Navigate to **Nutrient & Fertilizer**.
   - Input test values (e.g. Nitrogen 65 ppm, Phosphorus 12 ppm, pH 7.8).
   - Click **Generate Fertilizer Prescription**.
   - Inspect the recommended Neem Coated Urea, DAP, and Zinc Sulfate dosages, required bags, application timing, and total subsidized cost.
   - Click **Mark Applied & Log Expense** to record in the farm finance ledger.

4. **AI Crop Disease Diagnosis:**
   - Navigate to **AI Disease Diagnosis**.
   - Drag and drop or upload a crop leaf photo (or test without photo using the symptom field).
   - Enter symptoms such as *"Yellow powdery stripes along leaf veins"* and select *Wheat*.
   - Click **Run Disease Diagnostic Scan**.
   - The diagnosis displays disease name (*Yellow Stripe Rust*), causal agent (*Puccinia striiformis*), severity, risk percentage, chemical treatment (Propiconazole Tilt), and bio-control (Trichoderma + Neem oil).
   - Notice the engine status banner: *"Engine: Offline Demo / Rule-Based Analysis"* (or Gemini Vision if API key is set).

5. **Soil & Weather Telemetry:**
   - Navigate to **Soil & Weather**.
   - View real-time 15cm & 45cm moisture, soil temp, EC, and pH.
   - Click **Simulate Sensor Telemetry Update** to trigger a realistic sensor packet broadcast and observe immediate SQL persistence.
   - Review the 5-day agro-met forecast with rainfall probability.

6. **Mandi Market Intelligence:**
   - Navigate to **Mandi Intelligence**.
   - Compare spot rates across *Karnal, Gharaunda, Panipat, Kurukshetra, and Taraori*.
   - Filter by crop (Wheat, Paddy, Mustard). Review MSP comparisons and *RISING / FALLING / STABLE* trend indicators.

7. **Farm Finance & P&L:**
   - Navigate to **Farm Finance & P&L**.
   - Inspect total expenses, revenue, net profit, and ROI percentage.
   - Click **+ Log Expense** or **+ Record Sale** to add transactions.

8. **Machinery Hub:**
   - Navigate to **Machinery Hub**.
   - Browse custom hiring implements (Mahindra Tractor, Zero-Till Happy Seeder, Drone Sprayer, Laser Leveler).
   - Click **Book Equipment**, specify hours, and confirm reservation.

9. **Satellite Disaster & PMFBY Claim Dossier:**
   - Navigate to **Satellite Disaster** to inspect Sentinel-2 NDVI anomaly indexes.
   - Navigate to **PMFBY Claim Dossier**.
   - Select disaster type (e.g. *Flash Flood / Crop Submersion*), affected hectares, and loss amount.
   - Click **Compile & Generate Official PDF Claim Dossier**.
   - Click **Download Official PDF** to open the multi-page, formatted PMFBY insurance claim package generated by ReportLab.

10. **USSD / SMS Feature Phone Simulator:**
    - Navigate to **USSD / SMS Simulator**.
    - Dial `*515#` and click **SEND** to access the rural GSM shortcode menu.
    - Dial `1` or `*515*1#` to retrieve instant soil moisture and irrigation urgency without internet.
    - Dial `2` for Mandi rates, `3` for Weather advisory, and `4` for PMFBY claim status.

11. **Multilingual & Dark Mode:**
    - Click **🌐 हिन्दी** in the topbar to dynamically translate all cards and navigation labels to Hindi. Click **🌐 English** to return.
    - Click **🌙 Dark / ☀️ Light** to toggle themes (preference is saved in localStorage).

---

### J. How to Run Without Gemini API
The platform includes the **`OfflineFallbackManager`** heuristic engine.
- If `GEMINI_API_KEY` is not set or empty in `.env`, the system automatically routes all image/symptom scans to the local rule-based engine.
- The UI transparently displays the badge: `Engine: Offline Demo / Rule-Based Analysis`.
- No crashes, timeouts, or unhandled exceptions occur when offline.

---

### K. How to Reset Demo Data
To cleanly reset all field telemetries, diagnoses, and financial ledgers back to default factory baseline:
- Click **Judges' Demo Center** in the sidebar.
- Click **↺ Reset All Demo Data to Baseline**.
- Or via API:
```bash
curl -X POST http://localhost:3000/api/demo/reset
```

---

### L. Judges' Quick-Demo Workflow (Section 37)
For a 3-minute comprehensive presentation:
1. **Sign In:** Click **Evaluator Demo Mode** on the login screen.
2. **Dashboard:** Point out the live telemetry pulse, soil moisture (34%), and 7-day trend chart.
3. **Moisture Deficit:** Go to **Irrigation Engine**, drag moisture to 18%, click **Recalculate** to show the FAO-56 deficit warning. Click **Execute & Record Irrigation**.
4. **AI Pathology:** Go to **AI Disease Diagnosis**, type *"Yellow powdery stripes"*, and click **Run Disease Diagnostic Scan** to show instant treatment formulation with offline fallback labeling.
5. **Mandi Market:** Open **Mandi Intelligence** to show the Karnal and Panipat spot rates vs MSP.
6. **Activate Flash Flood Crisis:** Open **Judges' Demo Center**, click **[ Flash Flood / Inundation ]**.
   - Point out the cause-and-effect chain: 114mm cloudburst → 78.5% soil waterlogging → -48.6% Sentinel-2 NDVI drop → automated generation of PMFBY Claim Dossier PDF.
7. **Download PMFBY Dossier:** Open **PMFBY Claim Dossier** and click **Download Official PDF** to review the printable PDF package.
8. **USSD Simulator:** Open **USSD Simulator**, dial `*515#`, and query option `1` to demonstrate rural telephony accessibility.
9. **Audit Trail:** Open **Audit Trail & Logs** to demonstrate the immutable SQL log of every action taken.

---

### M. Troubleshooting
- **Port 3000 already in use:** Specify a different port via `PORT=3001 python3 backend/app.py`.
- **Missing dependencies:** Run `pip3 install -r requirements.txt`.
- **Database lock:** Delete `database/smart_crop.db` and re-run `python3 backend/app.py` to recreate a fresh database.
- **Run Automated Tests:** Run `python3 -m unittest discover tests` to verify all 16 tests pass.

---

*Smart Crop Advisory • Developed for Indian Farmers • Jai Kisan*
