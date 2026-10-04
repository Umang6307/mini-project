"""
Judges' Demo Center Scenario Service
Executes full-chain agricultural simulations across soil, weather, disease,
satellite, insurance, and mandi intelligence.
"""

from datetime import datetime
from backend.database import query_db, execute_db
from backend.insurance.pdf_generator import generate_pmfby_dossier

def run_scenario(scenario_key: str, field_id: int = 1) -> dict:
    scenario = scenario_key.strip().lower()
    field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
    if not field:
        field_id = 1

    steps = []

    if scenario == "severe_drought" or scenario == "drought":
        # 1. Update soil & weather
        execute_db("""
            UPDATE fields SET soil_moisture_pct = 14.5, health_score = 64, risk_level = 'HIGH' WHERE id = ?;
        """, (field_id,))
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, is_simulated)
            VALUES (?, 'SNS-WHT-01', 14.5, 18.0, 32.5, 1);
        """, (field_id,))
        execute_db("""
            INSERT INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, rainfall_prob_pct, actual_rainfall_mm, forecast_summary, is_simulated)
            VALUES (?, 'Karnal Agri-Met Station', 36.8, 28.0, 5.0, 0.0, 'Severe dry spell & heatwave alert. Precipitation deficit exceeding 78%.', 1);
        """, (field_id,))
        # 2. Satellite anomaly
        execute_db("""
            INSERT INTO satellite_assessments (field_id, disaster_type, baseline_ndvi, current_ndvi, ndvi_anomaly_pct, affected_acreage, severity, estimated_yield_loss_pct, estimated_financial_loss_inr, assessment_date)
            VALUES (?, 'Severe Meteorological & Soil Drought', 0.74, 0.44, -40.5, 1.8, 'HIGH', 45.0, 36000.0, DATE('now'));
        """, (field_id,))
        # 3. Advisory
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'IRRIGATION', 'URGENT', 'CRITICAL DROUGHT: Apply Emergency Irrigation', 'Soil moisture dropped to 14.5% (below Wilting Point). Immediate tube well irrigation required within 8h.', 'Run submersible pump for 12 hours');
        """, (field_id,))
        # 4. Audit
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Severe Drought & Heatwave Event', 'Triggered by Evaluator in Demo Center');
        """, (field_id,))

        steps = [
            "1. Meteorological Drought Triggered: Precipitation anomaly -78%, Ambient Temp spiked to 36.8°C.",
            "2. Root-zone Telemetry Updated: Soil moisture collapsed from 34% down to 14.5% (Severe Deficit).",
            "3. Satellite Anomaly Logged: Sentinel-2 NDVI dropped by -40.5% (Canopy desiccation).",
            "4. Advisory Generated: Urgent irrigation recommendation computed (60mm emergency recharge).",
            "5. PMFBY Drought Draft Dossier unlocked with Rs 36,000 estimated crop stress compensation."
        ]

        title = "Severe Drought & Heatwave Crisis"
        cause = "High ambient heatwave combined with zero rainfall over 21 days."

    elif scenario == "flash_flood" or scenario == "flood":
        execute_db("""
            UPDATE fields SET soil_moisture_pct = 78.5, health_score = 52, risk_level = 'CRITICAL' WHERE id = ?;
        """, (field_id,))
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, is_simulated)
            VALUES (?, 'SNS-WHT-01', 78.5, 82.0, 19.5, 1);
        """, (field_id,))
        execute_db("""
            INSERT INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, leaf_wetness_pct, rainfall_prob_pct, actual_rainfall_mm, forecast_summary, is_simulated)
            VALUES (?, 'Karnal Agri-Met Station', 21.0, 96.0, 95.0, 90.0, 114.5, 'Cloudburst & Flash Inundation: 114.5 mm recorded in 12 hours.', 1);
        """, (field_id,))
        execute_db("""
            INSERT INTO satellite_assessments (field_id, disaster_type, baseline_ndvi, current_ndvi, ndvi_anomaly_pct, affected_acreage, severity, estimated_yield_loss_pct, estimated_financial_loss_inr, assessment_date)
            VALUES (?, 'Flash Flood / Crop Submersion', 0.74, 0.38, -48.6, 1.8, 'SEVERE', 65.0, 52000.0, DATE('now'));
        """, (field_id,))
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'WEATHER', 'URGENT', 'FLASH FLOOD ALERT: Clear Field Drainage Immediately', '114.5mm cloudburst caused standing water submersion. Drain root-zone to prevent root rot hypoxia.', 'Open plot drainage gates immediately');
        """, (field_id,))

        # Automatically generate PMFBY claim draft
        claim_number = f"PMFBY-FLD01-{int(datetime.now().timestamp())}"
        farmer = query_db("SELECT * FROM farmers WHERE id = 1;", one=True)
        claim_payload = {
            "claim_number": claim_number,
            "farmer": farmer,
            "field": field,
            "crop": "Wheat",
            "variety": field['variety'] if field else "HD-3086",
            "disaster_type": "Flash Flood / Crop Submersion",
            "affected_area_ha": 1.8,
            "claimed_loss_inr": 52000.0,
            "satellite": {
                "baseline_ndvi": 0.74,
                "current_ndvi": 0.38,
                "ndvi_anomaly_pct": -48.6,
                "severity": "CRITICAL / SEVERE",
                "estimated_yield_loss_pct": 65.0
            }
        }
        pdf_path = generate_pmfby_dossier(claim_payload)

        execute_db("""
            INSERT INTO insurance_claims (claim_number, field_id, farmer_id, disaster_type, claimed_loss_inr, affected_area_ha, ndvi_anomaly_recorded, status, dossier_pdf_path, filing_date)
            VALUES (?, ?, 1, 'Flash Flood / Crop Submersion', 52000.0, 1.8, -48.6, 'Draft Generated', ?, DATE('now'));
        """, (claim_number, field_id, pdf_path))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, cost_inr, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Flash Flood & 114mm Cloudburst Inundation', 0.0, 'Official PMFBY claim dossier drafted automatically');
        """, (field_id,))

        steps = [
            "1. Cloudburst Inundation: 114.5 mm torrential downpour logged in agro-met station.",
            "2. Root-zone Inundation: Soil moisture saturated at 78.5% (Root hypoxia risk).",
            "3. Satellite SAR/MSI Detection: Sentinel-2 recorded -48.6% NDVI vegetation index drop.",
            "4. Damage Quantified: 65% estimated yield destruction across 1.8 hectares.",
            "5. PMFBY Claim Dossier Auto-Compiled: Full PDF ready with GPS parcel coordinates and loss tally."
        ]
        title = "Flash Flood & Cloudburst Inundation"
        cause = "Extreme precipitation (114.5mm) caused localized field waterlogging."

    elif scenario == "yellow_rust" or scenario == "yellow_rust_outbreak":
        execute_db("""
            UPDATE fields SET health_score = 61, risk_level = 'HIGH' WHERE id = ?;
        """, (field_id,))
        execute_db("""
            INSERT INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, leaf_wetness_pct, rainfall_prob_pct, forecast_summary, is_simulated)
            VALUES (?, 'Karnal Agri-Met Station', 16.5, 94.0, 88.0, 40.0, 'Cool morning mist, heavy dew and persistent overcast skies. High disease predisposition.', 1);
        """, (field_id,))
        execute_db("""
            INSERT INTO disease_diagnoses (field_id, crop_name, stage_at_diagnosis, condition_name, causal_organism, severity_level, risk_percentage, visual_symptoms, chemical_treatment, organic_treatment, estimated_cost_inr, confidence_score, source)
            VALUES (?, 'Wheat', 'Flowering & Anthesis', 'Yellow Stripe Rust', 'Puccinia striiformis f. sp. tritici', 'HIGH', 85.0, '["Bright yellow linear stripes on leaf blades", "Yellow powder on fingers", "Spikelet chlorosis"]',
                    'Foliar spray of Propiconazole 25% EC (Tilt) @ 200 ml/acre in 200L water.', 'Trichoderma harzianum @ 5g/L + Neem oil 1500 ppm @ 3ml/L.', 680.0, 0.94, 'offline-rule-engine');
        """, (field_id,))
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'DISEASE', 'URGENT', 'YELLOW STRIPE RUST OUTBREAK DETECTED', 'High pathogen activity detected in Karnal cluster. Immediate prophylactic fungicide spray required.', 'Spray Propiconazole 25% EC @ 1ml/L water');
        """, (field_id,))
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Yellow Stripe Rust Fungal Spore Surge', 'Triggered by Evaluator in Demo Center');
        """, (field_id,))

        steps = [
            "1. Micro-Climate Shift: Persistent morning dew and cool 16.5°C temperature triggered spore germination.",
            "2. Disease Detection: Yellow stripe pustules identified across foliage (85% pathogen risk).",
            "3. Crop Health Impact: Overall plot health score downgraded from 92% to 61%.",
            "4. Immediate Prescriptions: Chemical (Propiconazole Tilt) and Organic (Trichoderma + Neem) formulated.",
            "5. Action logged in farmer audit history."
        ]
        title = "Yellow Stripe Rust Epidemic Surge"
        cause = "High relative humidity (94%) and optimal spore incubation temperature (16.5°C)."

    elif scenario == "nitrogen_deficiency":
        execute_db("""
            UPDATE fields SET health_score = 72, risk_level = 'MEDIUM' WHERE id = ?;
        """, (field_id,))
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, nitrogen_ppm, phosphorus_ppm, potassium_ppm, is_simulated)
            VALUES (?, 'SNS-WHT-01', 33.0, 36.0, 22.0, 68.0, 24.0, 180.0, 1);
        """, (field_id,))
        execute_db("""
            INSERT INTO fertilizer_recommendations (field_id, crop_name, crop_stage, deficiency_detected, severity, recommended_fertilizer, recommended_quantity_kg, application_timing, explanation, estimated_cost_inr)
            VALUES (?, 'Wheat', 'Flowering & Anthesis', 'Nitrogen (Severe)', 'HIGH', 'Neem Coated Urea (46% N)', 144.0, 'Top dress split application before irrigation', 'Soil N plunged to 68 ppm. Rapid top dress needed to avert premature leaf senescence.', 852.0);
        """, (field_id,))
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'FERTILIZER', 'HIGH', 'Severe Nitrogen Deficiency Alert', 'Soil telemetry reports Nitrogen at 68 ppm (critically below 120 ppm baseline). Chlorosis spreading from lower leaf tips.', 'Apply 3.2 bags of Neem Coated Urea');
        """, (field_id,))
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Severe Nitrogen Depletion & Chlorosis', 'Triggered by Evaluator in Demo Center');
        """, (field_id,))

        steps = [
            "1. Soil Sensor Alert: Available nitrogen plummeted to 68 ppm (Severe deficiency).",
            "2. Visual Indicator: V-shaped chlorosis on basal canopy leaves.",
            "3. Fertilizer Decision Engine: Recommended 144 kg (3.2 bags) of Neem Coated Urea.",
            "4. Economic Cost Calculated: Subsidized investment of INR 852.00.",
            "5. Field status updated to MEDIUM risk."
        ]
        title = "Severe Nitrogen Deficiency (Chlorosis)"
        cause = "Leaching from earlier irrigation combined with heavy nutrient draw during vegetative flush."

    elif scenario == "mandi_crash":
        execute_db("""
            UPDATE mandi_prices SET modal_price = 1980.0, min_price = 1920.0, max_price = 2050.0,
            price_diff_msp = -295.0, trend = 'FALLING', trend_pct = -14.5 WHERE crop_name = 'Wheat' AND mandi_name = 'Karnal';
        """)
        execute_db("""
            UPDATE mandi_prices SET modal_price = 1940.0, min_price = 1890.0, max_price = 2010.0,
            price_diff_msp = -335.0, trend = 'FALLING', trend_pct = -16.2 WHERE crop_name = 'Wheat' AND mandi_name = 'Gharaunda';
        """)
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'HARVEST', 'HIGH', 'MARKET ALERT: Karnal Mandi Prices Slump Below MSP', 'Modal price plunged to Rs 1,980/Qtl (Rs 295 below MSP of Rs 2,275). Hold grain in warehouse or register for Govt FCI procurement.', 'Avail PM-AASHA / FCI MSP procurement portal');
        """, (field_id,))
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Mandi Commodity Market Crash (-15%)', 'Triggered by Evaluator in Demo Center');
        """, (field_id,))

        steps = [
            "1. Mandi Price Crash: Karnal market modal price fell from Rs 2,490 down to Rs 1,980/Qtl.",
            "2. Negative MSP Parity: Trades are now -Rs 295 BELOW sovereign Minimum Support Price.",
            "3. Trend Direction: 'FALLING' (-14.5% sharp contraction).",
            "4. Decision Support Advisory: Recommends holding harvest stock in registered warehouse (WDRA) or selling to FCI.",
            "5. Farm revenue projections recalculated."
        ]
        title = "Mandi Price Slump Below MSP"
        cause = "Sudden surge in regional arrivals (unloading gluts) depressed spot market trading."

    elif scenario == "mandi_spike":
        execute_db("""
            UPDATE mandi_prices SET modal_price = 2860.0, min_price = 2780.0, max_price = 2940.0,
            price_diff_msp = 585.0, trend = 'RISING', trend_pct = 15.8 WHERE crop_name = 'Wheat' AND mandi_name = 'Karnal';
        """)
        execute_db("""
            UPDATE mandi_prices SET modal_price = 2890.0, min_price = 2810.0, max_price = 2960.0,
            price_diff_msp = 615.0, trend = 'RISING', trend_pct = 16.5 WHERE crop_name = 'Wheat' AND mandi_name = 'Panipat';
        """)
        execute_db("""
            INSERT INTO crop_advices (field_id, advice_type, priority, title, message, action_required)
            VALUES (?, 'HARVEST', 'NORMAL', 'MARKET OPPORTUNITY: Spot Wheat Hits Season High (Rs 2,860/Qtl)', 'Export demand and flour mill buying spurred a +Rs 585 premium over MSP. Favorable window to offload buffer stock.', 'Consider booking transport to Karnal or Panipat Mandi');
        """, (field_id,))
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'SCENARIO_TRIGGERED', 'Simulated Scenario: Mandi Commodity Bull Run (+16%)', 'Triggered by Evaluator in Demo Center');
        """, (field_id,))

        steps = [
            "1. Mandi Price Surge: Karnal spot price climbed to Rs 2,860/Qtl (+15.8% increase).",
            "2. Premium Over MSP: Rs 585 per quintal above sovereign guarantee rate.",
            "3. Trend Direction: 'RISING' (High buyer liquidity).",
            "4. Market Intelligence Advisory: Best pricing located at Panipat Mandi (Rs 2,890).",
            "5. Projected farm profit margins enhanced."
        ]
        title = "Mandi Commodity Price Bull Run"
        cause = "High bulk institutional flour mill tenders and lower carryover national buffer stock."

    else:
        # Reset to pristine baseline
        from backend.database import init_db
        init_db(force_reset=True)
        steps = ["Database cleanly reset to standard baseline demo data."]
        title = "Reset to Normal Baseline"
        cause = "Reset requested."

    return {
        "scenario": scenario_key,
        "title": title,
        "cause": cause,
        "steps": steps,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
