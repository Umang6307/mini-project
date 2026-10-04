-- Smart Crop Advisory Database Schema
-- SQLite3 Relational Normalized Architecture

PRAGMA foreign_keys = ON;

-- 1. Farmers
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    state TEXT NOT NULL DEFAULT 'Haryana',
    district TEXT NOT NULL DEFAULT 'Karnal',
    village TEXT NOT NULL,
    pincode TEXT,
    language_pref TEXT NOT NULL DEFAULT 'en',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Farms
CREATE TABLE IF NOT EXISTS farms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    farm_name TEXT NOT NULL,
    total_area_ha REAL NOT NULL,
    primary_water_source TEXT DEFAULT 'Canal & Tube well',
    soil_type TEXT NOT NULL DEFAULT 'Alluvial Clay Loam',
    latitude REAL,
    longitude REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 3. Crops Catalog
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT UNIQUE NOT NULL,
    hindi_name TEXT,
    scientific_name TEXT,
    season TEXT NOT NULL, -- Rabi, Kharif, Zaid, Annual
    base_temp_c REAL DEFAULT 5.0,
    msp_inr_quintal REAL,
    avg_yield_q_ha REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Fields
CREATE TABLE IF NOT EXISTS fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_id INTEGER NOT NULL,
    crop_id INTEGER,
    field_code TEXT UNIQUE NOT NULL,
    field_name TEXT NOT NULL,
    area_value REAL NOT NULL,
    area_unit TEXT NOT NULL DEFAULT 'Hectare', -- Acre, Hectare, Bigha, Kanal, Guntha
    area_hectares REAL NOT NULL,
    variety TEXT,
    sowing_date DATE,
    current_stage TEXT NOT NULL DEFAULT 'Vegetative',
    health_score INTEGER NOT NULL DEFAULT 90, -- 0 to 100
    soil_moisture_pct REAL NOT NULL DEFAULT 32.0,
    risk_level TEXT NOT NULL DEFAULT 'LOW', -- LOW, MEDIUM, HIGH, CRITICAL
    harvest_estimate_date DATE,
    sensor_id TEXT,
    last_sensor_update DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id)
);

-- 5. Users & Auth Sessions
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'farmer', -- farmer, admin, evaluator
    is_demo_account INTEGER DEFAULT 0,
    session_token TEXT,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE SET NULL
);

-- 6. Soil Readings (Telemetry)
CREATE TABLE IF NOT EXISTS soil_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    sensor_id TEXT,
    moisture_15cm_pct REAL NOT NULL,
    moisture_45cm_pct REAL NOT NULL,
    soil_temp_c REAL NOT NULL,
    ec_ds_m REAL NOT NULL DEFAULT 0.65, -- Electrical Conductivity
    ph REAL NOT NULL DEFAULT 7.2,
    nitrogen_ppm REAL DEFAULT 140.0,
    phosphorus_ppm REAL DEFAULT 22.0,
    potassium_ppm REAL DEFAULT 185.0,
    organic_carbon_pct REAL DEFAULT 0.58,
    is_simulated INTEGER DEFAULT 1,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 7. Weather Readings
CREATE TABLE IF NOT EXISTS weather_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER,
    station_name TEXT DEFAULT 'Karnal Agri-Met Station',
    temperature_c REAL NOT NULL,
    humidity_pct REAL NOT NULL,
    leaf_wetness_pct REAL DEFAULT 20.0,
    rainfall_prob_pct REAL DEFAULT 10.0,
    actual_rainfall_mm REAL DEFAULT 0.0,
    wind_speed_kmh REAL DEFAULT 12.0,
    wind_direction TEXT DEFAULT 'NW',
    et0_evapotranspiration_mm REAL DEFAULT 4.2,
    solar_radiation_w_m2 REAL DEFAULT 650.0,
    forecast_summary TEXT,
    is_simulated INTEGER DEFAULT 1,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE SET NULL
);

-- 8. Crop Advices
CREATE TABLE IF NOT EXISTS crop_advices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    advice_type TEXT NOT NULL, -- IRRIGATION, FERTILIZER, DISEASE, WEATHER, HARVEST
    priority TEXT NOT NULL DEFAULT 'NORMAL', -- LOW, NORMAL, HIGH, URGENT
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    action_required TEXT,
    acknowledged INTEGER DEFAULT 0,
    acknowledged_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 9. Field Actions (Audit Trail)
CREATE TABLE IF NOT EXISTS field_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    action_type TEXT NOT NULL, -- IRRIGATION, FERTILIZER, DISEASE_SCAN, ADVICE_ACKNOWLEDGED, MACHINERY_BOOKED, EXPENSE_ADDED, SCENARIO_TRIGGERED
    description TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
    operator TEXT DEFAULT 'Farmer',
    cost_inr REAL DEFAULT 0.0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 10. Disease Diagnoses
CREATE TABLE IF NOT EXISTS disease_diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    stage_at_diagnosis TEXT,
    condition_name TEXT NOT NULL,
    causal_organism TEXT,
    severity_level TEXT NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    risk_percentage REAL NOT NULL,
    visual_symptoms TEXT, -- JSON array string
    chemical_treatment TEXT,
    organic_treatment TEXT,
    estimated_cost_inr REAL,
    image_filename TEXT,
    confidence_score REAL DEFAULT 0.90,
    source TEXT NOT NULL, -- 'gemini-vision' or 'offline-rule-engine'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 11. Fertilizer Recommendations
CREATE TABLE IF NOT EXISTS fertilizer_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    crop_stage TEXT NOT NULL,
    deficiency_detected TEXT NOT NULL,
    severity TEXT NOT NULL,
    recommended_fertilizer TEXT NOT NULL,
    recommended_quantity_kg REAL NOT NULL,
    application_timing TEXT,
    explanation TEXT,
    estimated_cost_inr REAL,
    applied INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 12. Irrigation Recommendations
CREATE TABLE IF NOT EXISTS irrigation_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    moisture_status TEXT NOT NULL, -- DEFICIT, OPTIMAL, SURPLUS
    current_moisture_pct REAL NOT NULL,
    target_moisture_pct REAL NOT NULL,
    water_depth_mm REAL NOT NULL,
    water_volume_m3 REAL NOT NULL,
    duration_hours REAL NOT NULL,
    urgency TEXT NOT NULL,
    explanation TEXT,
    applied INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 13. Growth Records
CREATE TABLE IF NOT EXISTS growth_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    stage_name TEXT NOT NULL,
    days_from_sowing INTEGER NOT NULL,
    cumulative_gdd REAL NOT NULL,
    canopy_cover_pct REAL,
    plant_height_cm REAL,
    health_index REAL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 14. Mandi Prices
CREATE TABLE IF NOT EXISTS mandi_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mandi_name TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    crop_name TEXT NOT NULL,
    variety TEXT,
    min_price REAL NOT NULL,
    max_price REAL NOT NULL,
    modal_price REAL NOT NULL,
    msp_price REAL NOT NULL,
    price_diff_msp REAL NOT NULL,
    trend TEXT NOT NULL, -- RISING, FALLING, STABLE
    trend_pct REAL DEFAULT 0.0,
    arrival_tonnes REAL,
    price_date DATE NOT NULL,
    is_live_data INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 15. Expenses
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- Seeds, Fertilizer, Diesel, Labour, Machinery, Irrigation, Pesticides, Other
    item_name TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
    cost_inr REAL NOT NULL,
    expense_date DATE NOT NULL,
    receipt_no TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 16. Sales
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    crop_name TEXT NOT NULL,
    buyer_mandi TEXT NOT NULL,
    quantity_quintals REAL NOT NULL,
    price_per_quintal_inr REAL NOT NULL,
    gross_revenue_inr REAL NOT NULL,
    deductions_inr REAL DEFAULT 0.0,
    net_revenue_inr REAL NOT NULL,
    sale_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 17. Machinery
CREATE TABLE IF NOT EXISTS machinery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER,
    equipment_name TEXT NOT NULL,
    equipment_type TEXT NOT NULL, -- Tractor, Seed Drill, Drone Sprayer, Laser Land Leveler, Harvester, Rotavator
    ownership TEXT NOT NULL DEFAULT 'Rented', -- Owned, Rented, Custom Hiring Center (CHC)
    registration_number TEXT,
    operating_cost_per_hour REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available', -- Available, Booked, In Use, Under Maintenance
    last_service_date DATE,
    next_service_due DATE,
    contact_phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE SET NULL
);

-- 18. Machinery Maintenance & Bookings
CREATE TABLE IF NOT EXISTS machinery_maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machinery_id INTEGER NOT NULL,
    field_id INTEGER,
    activity_type TEXT NOT NULL, -- Booking, Routine Service, Breakdown Repair, Calibration
    start_date DATE NOT NULL,
    duration_hours REAL NOT NULL,
    cost_inr REAL DEFAULT 0.0,
    notes TEXT,
    status TEXT DEFAULT 'Confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (machinery_id) REFERENCES machinery(id) ON DELETE CASCADE,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE SET NULL
);

-- 19. Satellite Assessments
CREATE TABLE IF NOT EXISTS satellite_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id INTEGER NOT NULL,
    disaster_type TEXT NOT NULL, -- Flood / Crop Submersion, Severe Drought, Hailstorm, Pest Outbreak, Normal
    baseline_ndvi REAL NOT NULL DEFAULT 0.74,
    current_ndvi REAL NOT NULL DEFAULT 0.72,
    ndvi_anomaly_pct REAL NOT NULL DEFAULT 0.0,
    affected_acreage REAL NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'LOW', -- LOW, MEDIUM, HIGH, SEVERE
    estimated_yield_loss_pct REAL NOT NULL DEFAULT 0.0,
    estimated_financial_loss_inr REAL NOT NULL DEFAULT 0.0,
    satellite_source TEXT DEFAULT 'Sentinel-2 Simulated MSI (10m)',
    is_simulated INTEGER DEFAULT 1,
    assessment_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
);

-- 20. Insurance Claims (PMFBY)
CREATE TABLE IF NOT EXISTS insurance_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_number TEXT UNIQUE NOT NULL,
    field_id INTEGER NOT NULL,
    farmer_id INTEGER NOT NULL,
    disaster_type TEXT NOT NULL,
    claimed_loss_inr REAL NOT NULL,
    affected_area_ha REAL NOT NULL,
    ndvi_anomaly_recorded REAL,
    status TEXT NOT NULL DEFAULT 'Draft Generated', -- Draft Generated, Submitted for Inspection, Under Local Survey
    dossier_pdf_path TEXT,
    declaration_accepted INTEGER DEFAULT 1,
    filing_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
);

-- 21. Government Schemes
CREATE TABLE IF NOT EXISTS government_schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    scheme_name TEXT NOT NULL,
    hindi_name TEXT,
    ministry TEXT NOT NULL,
    purpose TEXT NOT NULL,
    eligibility_info TEXT NOT NULL,
    benefits_summary TEXT NOT NULL,
    official_portal_url TEXT,
    helpline_number TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fields_farm_id ON fields(farm_id);
CREATE INDEX IF NOT EXISTS idx_soil_field_id ON soil_readings(field_id);
CREATE INDEX IF NOT EXISTS idx_advices_field_id ON crop_advices(field_id);
CREATE INDEX IF NOT EXISTS idx_actions_field_id ON field_actions(field_id);
CREATE INDEX IF NOT EXISTS idx_mandi_crop ON mandi_prices(crop_name, mandi_name);
CREATE INDEX IF NOT EXISTS idx_expenses_field ON expenses(field_id);
