-- Demonstration Data for Evaluators and Judges
-- Profiles: Ravi Kumar (Karnal) & Sunita Devi (Nilokheri)

-- 1. Farmers
INSERT OR IGNORE INTO farmers (id, farmer_code, full_name, phone, email, state, district, village, pincode, language_pref) VALUES
(1, 'FARMER-HR-001', 'Ravi Kumar', '+91 98120 12345', 'ravi.karnal@agriadvisory.in', 'Haryana', 'Karnal', 'Kachhwa Village', '132001', 'en'),
(2, 'FARMER-HR-002', 'Sunita Devi', '+91 94160 54321', 'sunita.devi@agriadvisory.in', 'Haryana', 'Karnal', 'Nilokheri', '132117', 'hi');

-- 2. Farms
INSERT OR IGNORE INTO farms (id, farmer_id, farm_name, total_area_ha, primary_water_source, soil_type, latitude, longitude) VALUES
(1, 1, 'Kachhwa Green Acre Farm', 3.0, 'Canal & Solar Submersible Tube well', 'Alluvial Clay Loam', 29.6857, 76.9905),
(2, 2, 'Nilokheri Agro Organic Plot', 2.5, 'Electric Tube well & Micro-Sprinkler', 'Silt Loam', 29.8324, 76.9208);

-- 3. Fields
-- Field 1: Ravi Kumar - Wheat HD-3086 (Flowering, 1.8 ha, 92% health, 34% moisture)
-- Field 2: Ravi Kumar - Mustard RH-749 (Vegetative, 1.2 ha, 95% health, 31% moisture)
-- Field 3: Sunita Devi - Paddy Basmati 1121 (Panicle Initiation, 2.5 ha, 88% health, 58% moisture)
INSERT OR IGNORE INTO fields (id, farm_id, crop_id, field_code, field_name, area_value, area_unit, area_hectares, variety, sowing_date, current_stage, health_score, soil_moisture_pct, risk_level, harvest_estimate_date, sensor_id) VALUES
(1, 1, 1, 'FLD-01', 'North Canal Wheat Plot', 1.8, 'Hectare', 1.8, 'HD-3086 (Pusa Gautami)', '2026-11-05', 'Flowering & Anthesis', 92, 34.0, 'LOW', '2027-04-12', 'SNS-WHT-01'),
(2, 1, 3, 'FLD-02', 'South Mustard Terraced Field', 1.2, 'Hectare', 1.2, 'RH-749', '2026-10-18', 'Vegetative', 95, 31.0, 'LOW', '2027-02-25', 'SNS-MST-02'),
(3, 2, 2, 'FLD-03', 'Nilokheri Basmati Paddy Field', 2.5, 'Hectare', 2.5, 'Basmati 1121', '2026-06-25', 'Panicle Initiation', 88, 58.0, 'LOW', '2026-10-28', 'SNS-PDY-03');

-- 4. Users (Demo credentials: ravi / password123, sunita / password123, evaluator / judge2026)
-- Passwords stored as SHA256 hex hashes:
-- 'password123' -> 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
-- 'judge2026' -> '69212002fe57bb8a832f0525287515f4886b6279f649bb77b58ae078dfbb1fa0'
INSERT OR IGNORE INTO users (id, farmer_id, username, password_hash, role, is_demo_account) VALUES
(1, 1, 'ravi', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'farmer', 1),
(2, 2, 'sunita', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'farmer', 1),
(3, 1, 'evaluator', '69212002fe57bb8a832f0525287515f4886b6279f649bb77b58ae078dfbb1fa0', 'evaluator', 1);

-- 5. Soil Readings Telemetry
INSERT OR IGNORE INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, ec_ds_m, ph, nitrogen_ppm, phosphorus_ppm, potassium_ppm, organic_carbon_pct, is_simulated) VALUES
(1, 'SNS-WHT-01', 34.0, 38.5, 22.4, 0.62, 7.3, 138.0, 24.5, 182.0, 0.60, 1),
(2, 'SNS-MST-02', 31.0, 34.2, 21.8, 0.58, 7.1, 115.0, 18.0, 160.0, 0.55, 1),
(3, 'SNS-PDY-03', 58.0, 62.0, 25.1, 0.70, 7.6, 160.0, 28.0, 210.0, 0.68, 1);

-- 6. Weather Readings
INSERT OR IGNORE INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, leaf_wetness_pct, rainfall_prob_pct, actual_rainfall_mm, wind_speed_kmh, wind_direction, et0_evapotranspiration_mm, solar_radiation_w_m2, forecast_summary, is_simulated) VALUES
(1, 'Karnal Agri-Met Station (ICAR-CSSRI)', 27.4, 68.0, 32.0, 18.0, 0.0, 12.5, 'NNW', 4.2, 680.0, 'Clear sky turning partly cloudy by evening. Favorable for pollination.', 1),
(2, 'Karnal South Automatic Weather Station', 27.2, 66.0, 28.0, 15.0, 0.0, 11.8, 'NNW', 4.1, 675.0, 'Dry conditions. Good sunshine hours.', 1),
(3, 'Nilokheri Agri Station', 28.1, 72.0, 45.0, 25.0, 0.0, 14.0, 'WNW', 4.5, 710.0, 'Warm and moderately humid. Monitor leaf wetness.', 1);

-- 7. Active Crop Advices
INSERT OR IGNORE INTO crop_advices (id, field_id, advice_type, priority, title, message, action_required, acknowledged) VALUES
(1, 1, 'IRRIGATION', 'NORMAL', 'Optimal Moisture Level', 'Current root-zone moisture (34%) is in the safe buffer. Next scheduled irrigation check in 48 hours.', 'Monitor soil telemetry tomorrow morning', 0),
(2, 1, 'FERTILIZER', 'LOW', 'Trace Zinc Supplement Recommended', 'Soil test indicates mild zinc depletion (0.75 ppm). Foliar spray of 0.5% ZnSO4 recommended during boot leaf.', 'Prepare 200L spray tank with 1kg Zinc Sulfate + 0.5kg lime', 0),
(3, 1, 'DISEASE', 'NORMAL', 'Favorable Weather for Yellow Rust Alert', 'Cool morning temperatures (14-16°C) and dew increase risk of fungal spore spread in Northern Haryana.', 'Scout northern border of field for powdery yellow streaks', 0);

-- 8. Field Actions (Audit Trail)
INSERT OR IGNORE INTO field_actions (field_id, action_type, description, quantity, unit, operator, cost_inr, notes) VALUES
(1, 'SOWING', 'Direct drilled Wheat variety HD-3086 using Zero-Till Happy Seeder', 1.8, 'Hectare', 'Ravi Kumar', 3200.0, 'Treated seed with Trichoderma viride'),
(1, 'FERTILIZER', 'Basal application of DAP and MOP at sowing', 125.0, 'Kg', 'Ravi Kumar', 3450.0, '2.5 bags DAP + 1 bag MOP applied in bands'),
(1, 'IRRIGATION', 'First Crown Root Initiation (CRI) irrigation completed via canal water', 60.0, 'mm', 'Ravi Kumar', 400.0, 'Tubewell electricity subsidy applied'),
(1, 'DISEASE_SCAN', 'Foliar camera diagnosis scan: Leaf health normal (96% clean)', 1.0, 'Scan', 'Ravi Kumar', 0.0, 'No rust pustules detected');

-- 9. Growth Records (Timeline Tracking)
INSERT OR IGNORE INTO growth_records (field_id, stage_name, days_from_sowing, cumulative_gdd, canopy_cover_pct, plant_height_cm, health_index) VALUES
(1, 'Sowing & Germination', 10, 115.0, 15.0, 6.5, 96.0),
(1, 'Crown Root Initiation (CRI)', 22, 340.0, 35.0, 18.2, 95.0),
(1, 'Tillering', 42, 680.0, 65.0, 38.0, 93.0),
(1, 'Jointing & Booting', 68, 1090.0, 85.0, 68.5, 94.0),
(1, 'Flowering & Anthesis', 86, 1420.0, 92.0, 88.0, 92.0);

-- 10. Mandi Prices
INSERT OR IGNORE INTO mandi_prices (id, mandi_name, state, district, crop_name, variety, min_price, max_price, modal_price, msp_price, price_diff_msp, trend, trend_pct, arrival_tonnes, price_date, is_live_data) VALUES
(1, 'Karnal', 'Haryana', 'Karnal', 'Wheat', 'HD-3086', 2400.0, 2580.0, 2490.0, 2275.0, 215.0, 'RISING', 2.4, 420.5, '2026-09-30', 0),
(2, 'Gharaunda', 'Haryana', 'Karnal', 'Wheat', 'PBW-550', 2380.0, 2510.0, 2445.0, 2275.0, 170.0, 'STABLE', 0.2, 280.0, '2026-09-30', 0),
(3, 'Panipat', 'Haryana', 'Panipat', 'Wheat', 'DBW-187', 2420.0, 2590.0, 2515.0, 2275.0, 240.0, 'RISING', 1.8, 390.2, '2026-09-30', 0),
(4, 'Taraori', 'Haryana', 'Karnal', 'Paddy (Basmati)', 'Basmati 1121', 4100.0, 4650.0, 4480.0, 2300.0, 2180.0, 'RISING', 4.1, 650.0, '2026-09-30', 0),
(5, 'Kurukshetra', 'Haryana', 'Kurukshetra', 'Mustard', 'RH-749', 5400.0, 5850.0, 5680.0, 5650.0, 30.0, 'FALLING', -1.5, 140.0, '2026-09-30', 0);

-- 11. Farm Expenses
INSERT OR IGNORE INTO expenses (field_id, category, item_name, quantity, unit, cost_inr, expense_date, receipt_no) VALUES
(1, 'Seeds', 'Certified Wheat Seed HD-3086 (80 kg)', 80.0, 'Kg', 3200.0, '2026-11-02', 'REC-KRN-101'),
(1, 'Fertilizer', 'DAP Fertilizer (2.5 bags) + Urea (2 bags)', 4.5, 'Bags', 3910.0, '2026-11-05', 'REC-IFFCO-882'),
(1, 'Machinery', 'Laser Land Leveling & Happy Seeder custom hire', 6.0, 'Hours', 2700.0, '2026-11-04', 'REC-CHC-419'),
(1, 'Labour', 'Irrigation canal trench preparation & sowing assistance', 3.0, 'Days', 1800.0, '2026-11-08', 'LAB-102'),
(1, 'Diesel', 'Diesel for irrigation pump set (35 Litres)', 35.0, 'Litres', 3150.0, '2026-12-15', 'PETRO-774');

-- 12. Farm Sales (Previous harvest records for ROI calculations)
INSERT OR IGNORE INTO sales (field_id, crop_name, buyer_mandi, quantity_quintals, price_per_quintal_inr, gross_revenue_inr, deductions_inr, net_revenue_inr, sale_date) VALUES
(1, 'Paddy (Basmati 1121)', 'Karnal Mandi Yard', 92.0, 4420.0, 406640.0, 6100.0, 400540.0, '2026-10-22'),
(2, 'Mustard', 'Taraori Grain Market', 24.5, 5700.0, 139650.0, 2100.0, 137550.0, '2026-03-28');

-- 13. Satellite Assessment Baseline
INSERT OR IGNORE INTO satellite_assessments (field_id, disaster_type, baseline_ndvi, current_ndvi, ndvi_anomaly_pct, affected_acreage, severity, estimated_yield_loss_pct, estimated_financial_loss_inr, assessment_date) VALUES
(1, 'Normal / Healthy Crop Canopy', 0.74, 0.72, -2.7, 0.0, 'LOW', 0.0, 0.0, '2026-09-28'),
(2, 'Normal / Early Vegetative', 0.68, 0.66, -2.9, 0.0, 'LOW', 0.0, 0.0, '2026-09-28'),
(3, 'Normal / Submerged Paddy Canopy', 0.78, 0.75, -3.8, 0.0, 'LOW', 0.0, 0.0, '2026-09-28');
