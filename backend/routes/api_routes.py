"""
REST API Routes for Smart Crop Advisory
Implements all agricultural endpoints with strict input validation,
error handling, and uniform JSON responses.
"""

import os
import hashlib
import json
from datetime import datetime, date
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from backend.config import Config
from backend.database import query_db, execute_db, init_db
from backend.utils.response_helper import success_response, error_response
from backend.utils.unit_converter import convert_to_hectares, convert_all_units
from backend.decision_engine.irrigation import calculate_irrigation
from backend.decision_engine.fertilizer import calculate_fertilizer
from backend.ai.gemini_vision import analyze_crop_image
from backend.ai.offline_fallback import OfflineFallbackManager
from backend.weather.weather_service import get_weather_data, simulate_new_reading
from backend.market.mandi_service import get_all_mandi_prices, get_crop_mandi_analysis
from backend.satellite.satellite_service import get_satellite_assessment, update_satellite_disaster
from backend.insurance.pdf_generator import generate_pmfby_dossier
from backend.services.ussd_service import process_ussd_code
from backend.services.scenario_service import run_scenario

api_bp = Blueprint('api', __name__, url_prefix='/api')

def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode('utf-8')).hexdigest()

# -------------------------------------------------------------
# 1. AUTHENTICATION & PROFILES
# -------------------------------------------------------------
@api_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return error_response("Please provide both username and password", 400)

        hashed = hash_password(password)
        user = query_db(
            "SELECT * FROM users WHERE (username = ? OR username = ?) AND password_hash = ?;",
            (username.lower(), username, hashed),
            one=True
        )

        if not user:
            # Check demo shortcuts
            if username.lower() in ['ravi', 'sunita', 'evaluator'] and (password == 'password123' or password == 'judge2026'):
                user = query_db("SELECT * FROM users WHERE username = ?;", (username.lower(),), one=True)

        if not user:
            return error_response("Invalid username or password. You can use demo accounts: ravi / password123, sunita / password123", 401)

        # Update last login
        execute_db("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?;", (user['id'],))

        # Get farmer profile
        farmer = None
        if user['farmer_id']:
            farmer = query_db("SELECT * FROM farmers WHERE id = ?;", (user['farmer_id'],), one=True)

        # Log audit action
        if farmer:
            execute_db("""
                INSERT INTO field_actions (field_id, action_type, description, operator)
                VALUES (1, 'LOGIN', 'Farmer logged into Smart Crop Advisory web portal', ?);
            """, (farmer['full_name'],))

        session_data = {
            "user_id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "is_demo": bool(user['is_demo_account']),
            "farmer": farmer
        }

        return success_response(session_data, "Login successful")

    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)

@api_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        state = data.get('state', 'Haryana').strip()
        district = data.get('district', 'Karnal').strip()
        village = data.get('village', 'Village').strip()
        crop_name = data.get('crop', 'Wheat').strip()
        area_val = float(data.get('area_value', 1.0))
        area_unit = data.get('area_unit', 'Acre').strip()

        if not name or not phone or not username or not password:
            return error_response("Full name, phone, username, and password are required", 400)

        # Check existing user
        existing = query_db("SELECT id FROM users WHERE username = ?;", (username.lower(),), one=True)
        if existing:
            return error_response("Username already registered. Please choose another username.", 400)

        farmer_code = f"FARMER-{district[:3].upper()}-{int(datetime.now().timestamp()) % 10000}"
        farmer_id = execute_db("""
            INSERT INTO farmers (farmer_code, full_name, phone, state, district, village)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (farmer_code, name, phone, state, district, village))

        farm_id = execute_db("""
            INSERT INTO farms (farmer_id, farm_name, total_area_ha, soil_type)
            VALUES (?, ?, ?, 'Alluvial Clay Loam');
        """, (farmer_id, f"{name}'s Farm", convert_to_hectares(area_val, area_unit)))

        area_ha = convert_to_hectares(area_val, area_unit)
        field_code = f"FLD-{farmer_id:02d}-01"
        field_id = execute_db("""
            INSERT INTO fields (farm_id, field_code, field_name, area_value, area_unit, area_hectares, current_stage, health_score, soil_moisture_pct, risk_level, sowing_date)
            VALUES (?, ?, 'Main Cultivation Plot', ?, ?, ?, 'Vegetative', 95, 35.0, 'LOW', DATE('now', '-30 days'));
        """, (farm_id, field_code, area_val, area_unit, area_ha))

        # Baseline sensors
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c)
            VALUES (?, 'SNS-NEW-01', 35.0, 38.0, 24.0);
        """, (field_id,))
        execute_db("""
            INSERT INTO weather_readings (field_id, station_name, temperature_c, humidity_pct, rainfall_prob_pct)
            VALUES (?, 'Karnal Agri-Met Station', 27.0, 65.0, 15.0);
        """, (field_id,))

        # Create user credentials
        hashed = hash_password(password)
        user_id = execute_db("""
            INSERT INTO users (farmer_id, username, password_hash, role, is_demo_account)
            VALUES (?, ?, ?, 'farmer', 0);
        """, (farmer_id, username.lower(), hashed))

        farmer_data = query_db("SELECT * FROM farmers WHERE id = ?;", (farmer_id,), one=True)

        return success_response({
            "user_id": user_id,
            "username": username,
            "farmer": farmer_data,
            "field_id": field_id
        }, "Registration successful! Welcome to Smart Crop Advisory.", 201)

    except Exception as e:
        return error_response(f"Signup error: {str(e)}", 500)

@api_bp.route('/farmers/<int:farmer_id>', methods=['GET'])
def get_farmer_profile(farmer_id):
    try:
        farmer = query_db("SELECT * FROM farmers WHERE id = ?;", (farmer_id,), one=True)
        if not farmer:
            return error_response("Farmer not found", 404)
        farms = query_db("SELECT * FROM farms WHERE farmer_id = ?;", (farmer_id,))
        return success_response({"farmer": farmer, "farms": farms})
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 2. FIELDS & DASHBOARD SUMMARY
# -------------------------------------------------------------
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    try:
        field_id = int(request.args.get('field_id', 1))
        field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
        if not field:
            field = query_db("SELECT * FROM fields LIMIT 1;", one=True)
            field_id = field['id'] if field else 1

        all_fields = query_db("""
            SELECT f.*, fm.farm_name, c.crop_name, c.hindi_name as crop_hindi, fr.full_name as farmer_name
            FROM fields f
            LEFT JOIN farms fm ON f.farm_id = fm.id
            LEFT JOIN crops c ON f.crop_id = c.id
            LEFT JOIN farmers fr ON fm.farmer_id = fr.id;
        """)

        # Latest soil reading
        soil = query_db(
            "SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;",
            (field_id,), one=True
        ) or {
            "moisture_15cm_pct": 34.0,
            "moisture_45cm_pct": 38.5,
            "soil_temp_c": 22.4,
            "ec_ds_m": 0.62,
            "ph": 7.3,
            "nitrogen_ppm": 138.0,
            "phosphorus_ppm": 24.5,
            "potassium_ppm": 182.0
        }

        # Latest weather
        weather = get_weather_data(field_id)

        # Active advices
        advices = query_db(
            "SELECT * FROM crop_advices WHERE field_id = ? ORDER BY priority DESC, created_at DESC LIMIT 5;",
            (field_id,)
        )

        # Recent activities (audit trail)
        activities = query_db(
            "SELECT * FROM field_actions WHERE field_id = ? ORDER BY created_at DESC LIMIT 8;",
            (field_id,)
        )

        # Mandi price for current crop
        crop_title = "Wheat"
        if field and field.get('crop_id') == 2:
            crop_title = "Paddy"
        elif field and field.get('crop_id') == 3:
            crop_title = "Mustard"

        mandi_summary = get_crop_mandi_analysis(crop_title)

        # Growth records for timeline
        growth_timeline = query_db(
            "SELECT * FROM growth_records WHERE field_id = ? ORDER BY days_from_sowing ASC;",
            (field_id,)
        )

        # Satellite summary
        satellite = get_satellite_assessment(field_id)

        # Farm finance overview
        expenses = query_db("SELECT SUM(cost_inr) as total_expenses FROM expenses WHERE field_id = ?;", (field_id,), one=True)
        sales = query_db("SELECT SUM(net_revenue_inr) as total_sales FROM sales WHERE field_id = ?;", (field_id,), one=True)
        tot_exp = expenses['total_expenses'] or 0.0
        tot_rev = sales['total_sales'] or 0.0

        return success_response({
            "current_field": field,
            "all_fields": all_fields,
            "soil": soil,
            "weather": weather,
            "advices": advices,
            "activities": activities,
            "mandi": mandi_summary,
            "growth_timeline": growth_timeline,
            "satellite": satellite,
            "finance": {
                "total_expenses": tot_exp,
                "total_revenue": tot_rev,
                "net_profit": tot_rev - tot_exp,
                "roi_pct": round(((tot_rev - tot_exp) / tot_exp * 100), 1) if tot_exp > 0 else 0
            }
        })

    except Exception as e:
        return error_response(f"Dashboard load failed: {str(e)}", 500)

@api_bp.route('/fields', methods=['GET'])
def get_fields():
    fields = query_db("""
        SELECT f.*, c.crop_name, c.hindi_name as crop_hindi, fm.farm_name, fr.full_name as farmer_name
        FROM fields f
        LEFT JOIN crops c ON f.crop_id = c.id
        LEFT JOIN farms fm ON f.farm_id = fm.id
        LEFT JOIN farmers fr ON fm.farmer_id = fr.id;
    """)
    return success_response(fields)

@api_bp.route('/fields', methods=['POST'])
def create_field():
    try:
        data = request.get_json(silent=True) or {}
        farm_id = int(data.get('farm_id', 1))
        name = data.get('field_name', '').strip()
        crop_id = int(data.get('crop_id', 1))
        area_val = float(data.get('area_value', 1.0))
        area_unit = data.get('area_unit', 'Acre').strip()
        variety = data.get('variety', 'Standard Variety').strip()
        sowing = data.get('sowing_date', str(date.today()))

        if not name:
            return error_response("Field name is required", 400)

        area_ha = convert_to_hectares(area_val, area_unit)
        count = query_db("SELECT COUNT(*) as c FROM fields WHERE farm_id = ?;", (farm_id,), one=True)['c']
        field_code = f"FLD-{farm_id:02d}-{count+1:02d}"

        field_id = execute_db("""
            INSERT INTO fields (farm_id, crop_id, field_code, field_name, area_value, area_unit, area_hectares, variety, sowing_date, current_stage, health_score, soil_moisture_pct, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Sowing & Germination', 96, 35.0, 'LOW');
        """, (farm_id, crop_id, field_code, name, area_val, area_unit, area_ha, variety, sowing))

        # Seed telemetry
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c)
            VALUES (?, 'SNS-NEW', 35.0, 38.0, 23.0);
        """, (field_id,))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description)
            VALUES (?, 'FIELD_CREATED', ?);
        """, (field_id, f"Registered new parcel: {name} ({area_val} {area_unit})"))

        return success_response({"field_id": field_id, "field_code": field_code}, "Field added successfully", 201)
    except Exception as e:
        return error_response(f"Error creating field: {str(e)}", 500)

# -------------------------------------------------------------
# 3. IRRIGATION DECISION ENGINE
# -------------------------------------------------------------
@api_bp.route('/irrigation/recommend', methods=['POST'])
def recommend_irrigation():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        
        # Pull field data
        field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
        crop = data.get('crop') or (field['variety'] if field else "Wheat")
        stage = data.get('stage') or (field['current_stage'] if field else "Flowering & Anthesis")
        area_ha = float(data.get('area_ha') or (field['area_hectares'] if field else 1.8))
        soil_type = data.get('soil_type', "Alluvial Clay Loam")

        # Moisture reading: from payload or DB
        if 'soil_moisture' in data:
            moisture = float(data['soil_moisture'])
        else:
            latest_soil = query_db("SELECT moisture_15cm_pct FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
            moisture = float(latest_soil['moisture_15cm_pct']) if latest_soil else 34.0

        # Weather reading
        weather = get_weather_data(field_id)['current']
        temp = float(weather.get('temperature_c', 27.0))
        rain_prob = float(weather.get('rainfall_prob_pct', 18.0))
        et0 = float(weather.get('et0_mm_day', 4.2))

        rec = calculate_irrigation(
            soil_moisture_pct=moisture,
            soil_type=soil_type,
            crop=crop,
            crop_stage=stage,
            area_ha=area_ha,
            temperature_c=temp,
            rainfall_prob_pct=rain_prob,
            et0_mm_day=et0
        )

        # Store recommendation in DB
        execute_db("""
            INSERT INTO irrigation_recommendations (
                field_id, moisture_status, current_moisture_pct, target_moisture_pct,
                water_depth_mm, water_volume_m3, duration_hours, urgency, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            field_id, rec['status'], rec['current_moisture_pct'], rec['target_moisture_pct'],
            rec['water_depth_mm'], rec['water_volume_m3'], rec['duration_hours'],
            rec['urgency'], rec['explanation']
        ))

        return success_response(rec, "Irrigation recommendation generated")
    except Exception as e:
        return error_response(f"Irrigation calculation error: {str(e)}", 500)

@api_bp.route('/irrigation/apply', methods=['POST'])
def apply_irrigation_action():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        depth_mm = float(data.get('water_depth_mm', 30.0))
        duration_hrs = float(data.get('duration_hours', 2.5))
        
        # Update field moisture back to optimal
        execute_db("UPDATE fields SET soil_moisture_pct = 36.5, health_score = min(100, health_score + 3), risk_level = 'LOW' WHERE id = ?;", (field_id,))
        
        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, is_simulated)
            VALUES (?, 'SNS-PUMP-01', 36.5, 39.0, 21.5, 1);
        """, (field_id,))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, quantity, unit, cost_inr)
            VALUES (?, 'IRRIGATION', ?, ?, 'Hours', 350.0);
        """, (field_id, f"Completed tube well irrigation of {depth_mm} mm over {duration_hrs} hours", duration_hrs))

        return success_response({"new_moisture": 36.5}, "Irrigation applied successfully. Soil moisture restored to optimal.")
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 4. FERTILIZER DECISION ENGINE
# -------------------------------------------------------------
@api_bp.route('/fertilizer/recommend', methods=['POST'])
def recommend_fertilizer():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
        crop = data.get('crop') or (field['variety'] if field else "Wheat")
        stage = data.get('stage') or (field['current_stage'] if field else "Flowering & Anthesis")
        area_ha = float(data.get('area_ha') or (field['area_hectares'] if field else 1.8))

        # Soil parameters
        latest_soil = query_db("SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
        n_ppm = float(data.get('nitrogen_ppm') or (latest_soil['nitrogen_ppm'] if latest_soil else 138.0))
        p_ppm = float(data.get('phosphorus_ppm') or (latest_soil['phosphorus_ppm'] if latest_soil else 24.5))
        k_ppm = float(data.get('potassium_ppm') or (latest_soil['potassium_ppm'] if latest_soil else 182.0))
        ph = float(data.get('ph') or (latest_soil['ph'] if latest_soil else 7.3))

        result = calculate_fertilizer(
            crop=crop,
            crop_stage=stage,
            nitrogen_ppm=n_ppm,
            phosphorus_ppm=p_ppm,
            potassium_ppm=k_ppm,
            ph=ph,
            area_ha=area_ha
        )

        return success_response(result, "Fertilizer prescription generated")
    except Exception as e:
        return error_response(f"Fertilizer engine error: {str(e)}", 500)

@api_bp.route('/fertilizer/apply', methods=['POST'])
def apply_fertilizer_action():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        fertilizer_name = data.get('fertilizer_name', 'Neem Coated Urea')
        quantity_kg = float(data.get('quantity_kg', 45.0))
        cost_inr = float(data.get('cost_inr', 266.5))

        # Restores nitrogen / phosphorus in soil
        execute_db("""
            UPDATE soil_readings SET nitrogen_ppm = 160.0 WHERE field_id = ?;
        """, (field_id,))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, quantity, unit, cost_inr)
            VALUES (?, 'FERTILIZER', ?, ?, 'Kg', ?);
        """, (field_id, f"Applied {fertilizer_name} ({quantity_kg} kg) as recommended", quantity_kg, cost_inr))

        execute_db("""
            INSERT INTO expenses (field_id, category, item_name, quantity, unit, cost_inr, expense_date)
            VALUES (?, 'Fertilizer', ?, ?, 'Kg', ?, DATE('now'));
        """, (field_id, fertilizer_name, quantity_kg, cost_inr))

        return success_response({"status": "applied"}, f"Applied {fertilizer_name} successfully. Logged in audit trail & expense ledger.")
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 5. AI CROP HEALTH & DISEASE DIAGNOSIS
# -------------------------------------------------------------
@api_bp.route('/crop-health/analyze', methods=['POST'])
def analyze_crop_health():
    try:
        crop = request.form.get('crop', 'Wheat').strip()
        stage = request.form.get('stage', 'Flowering & Anthesis').strip()
        symptoms = request.form.get('symptoms', '').strip()
        field_id = int(request.form.get('field_id', 1))

        image_bytes = None
        filename = "sample_leaf.jpg"

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = file.filename
                image_bytes = file.read()
                # Save locally in uploads
                save_path = Config.UPLOAD_DIR / filename
                with open(save_path, 'wb') as f:
                    f.write(image_bytes)

        # Run AI multimodal diagnosis with automatic fallback
        if image_bytes:
            diagnosis = analyze_crop_image(image_bytes, filename, crop, stage, symptoms)
        else:
            # No image uploaded - purely symptom & rule-based
            fallback_mgr = OfflineFallbackManager()
            diagnosis = fallback_mgr.diagnose(crop, stage, symptoms, filename)

        # Store in SQL
        execute_db("""
            INSERT INTO disease_diagnoses (
                field_id, crop_name, stage_at_diagnosis, condition_name, causal_organism,
                severity_level, risk_percentage, visual_symptoms, chemical_treatment,
                organic_treatment, estimated_cost_inr, image_filename, confidence_score, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            field_id, crop, stage, diagnosis.get('conditionName', 'Leaf Spot'),
            diagnosis.get('causalOrganism', 'Pathogen'), diagnosis.get('severityLevel', 'MEDIUM'),
            float(diagnosis.get('riskPct', 65.0)), json.dumps(diagnosis.get('visualSymptoms', [])),
            diagnosis.get('chemicalTreatment', ''), diagnosis.get('organicBioControl', ''),
            float(diagnosis.get('estimatedCostInr', 500)), filename,
            float(diagnosis.get('confidence', 0.90)), diagnosis.get('source', 'offline-rule-engine')
        ))

        # Log audit trail
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'DISEASE_SCAN', ?, ?);
        """, (field_id, f"Diagnosed: {diagnosis.get('conditionName')} ({diagnosis.get('severityLevel')})", f"Source: {diagnosis.get('sourceLabel')}"))

        return success_response(diagnosis, "Crop disease diagnostic completed")

    except Exception as e:
        return error_response(f"Diagnostic error: {str(e)}", 500)

@api_bp.route('/crop-health/history/<int:field_id>', methods=['GET'])
def get_diagnosis_history(field_id):
    records = query_db("SELECT * FROM disease_diagnoses WHERE field_id = ? ORDER BY created_at DESC LIMIT 10;", (field_id,))
    return success_response(records)

# -------------------------------------------------------------
# 6. SOIL & WEATHER TELEMETRY
# -------------------------------------------------------------
@api_bp.route('/soil/<int:field_id>', methods=['GET'])
def get_soil_telemetry(field_id):
    readings = query_db("SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 10;", (field_id,))
    latest = readings[0] if readings else None
    return success_response({"latest": latest, "history": readings})

@api_bp.route('/soil/<int:field_id>/simulate', methods=['POST'])
def simulate_sensor_update(field_id):
    try:
        # Realistic update
        import random
        latest = query_db("SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
        cur_moist = latest['moisture_15cm_pct'] if latest else 34.0
        
        # Add realistic drift
        new_moist = round(max(15.0, min(55.0, cur_moist + random.uniform(-2.5, 1.5))), 1)
        new_deep = round(max(18.0, min(60.0, new_moist + random.uniform(2.0, 5.0))), 1)
        new_temp = round(random.uniform(21.0, 26.5), 1)

        execute_db("""
            INSERT INTO soil_readings (field_id, sensor_id, moisture_15cm_pct, moisture_45cm_pct, soil_temp_c, is_simulated)
            VALUES (?, 'SNS-WHT-01', ?, ?, ?, 1);
        """, (field_id, new_moist, new_deep, new_temp))

        execute_db("UPDATE fields SET soil_moisture_pct = ?, last_sensor_update = CURRENT_TIMESTAMP WHERE id = ?;", (new_moist, field_id))
        
        # Weather update as well
        simulate_new_reading(field_id)

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description)
            VALUES (?, 'SENSOR_UPDATE', ?);
        """, (field_id, f"IoT sensor packet received: 15cm Moisture {new_moist}%, Temp {new_temp}°C"))

        return success_response({"moisture_15cm_pct": new_moist, "moisture_45cm_pct": new_deep, "soil_temp_c": new_temp}, "Simulated sensor readings updated realistically in SQL")
    except Exception as e:
        return error_response(str(e), 500)

@api_bp.route('/weather/<int:field_id>', methods=['GET'])
def get_weather_telemetry(field_id):
    data = get_weather_data(field_id)
    return success_response(data)

# -------------------------------------------------------------
# 7. MANDI MARKET INTELLIGENCE
# -------------------------------------------------------------
@api_bp.route('/market-prices', methods=['GET'])
def get_market_prices():
    prices = get_all_mandi_prices()
    return success_response(prices)

@api_bp.route('/market-prices/analysis', methods=['GET'])
def get_market_analysis():
    crop = request.args.get('crop', 'Wheat')
    analysis = get_crop_mandi_analysis(crop)
    return success_response(analysis)

# -------------------------------------------------------------
# 8. FARM FINANCE & P&L
# -------------------------------------------------------------
@api_bp.route('/finance/<int:field_id>', methods=['GET'])
def get_finance_data(field_id):
    expenses = query_db("SELECT * FROM expenses WHERE field_id = ? ORDER BY expense_date DESC;", (field_id,))
    sales = query_db("SELECT * FROM sales WHERE field_id = ? ORDER BY sale_date DESC;", (field_id,))
    
    tot_exp = sum(x['cost_inr'] for x in expenses)
    tot_rev = sum(s['net_revenue_inr'] for s in sales)
    profit = tot_rev - tot_exp
    roi = round((profit / tot_exp * 100), 1) if tot_exp > 0 else 0

    # Categorized breakdown
    categories = {}
    for e in expenses:
        cat = e['category']
        categories[cat] = categories.get(cat, 0.0) + e['cost_inr']

    return success_response({
        "expenses": expenses,
        "sales": sales,
        "summary": {
            "total_expenses": tot_exp,
            "total_revenue": tot_rev,
            "net_profit": profit,
            "roi_pct": roi,
            "category_breakdown": categories
        }
    })

@api_bp.route('/finance/expense', methods=['POST'])
def add_expense():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        category = data.get('category', 'Other').strip()
        item = data.get('item_name', '').strip()
        quantity = float(data.get('quantity', 1.0))
        unit = data.get('unit', 'Units').strip()
        cost = float(data.get('cost_inr', 0.0))
        exp_date = data.get('expense_date', str(date.today()))

        if not item or cost <= 0:
            return error_response("Item name and positive cost are required", 400)

        exp_id = execute_db("""
            INSERT INTO expenses (field_id, category, item_name, quantity, unit, cost_inr, expense_date)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (field_id, category, item, quantity, unit, cost, exp_date))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, cost_inr)
            VALUES (?, 'EXPENSE_ADDED', ?, ?);
        """, (field_id, f"Expense recorded: {item} ({category}) - Rs {cost}", cost))

        return success_response({"expense_id": exp_id}, "Expense logged successfully", 201)
    except Exception as e:
        return error_response(str(e), 500)

@api_bp.route('/finance/sale', methods=['POST'])
def add_sale():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        crop = data.get('crop_name', 'Wheat').strip()
        mandi = data.get('buyer_mandi', 'Karnal Mandi').strip()
        qty = float(data.get('quantity_quintals', 10.0))
        rate = float(data.get('price_per_quintal_inr', 2490.0))
        gross = qty * rate
        deductions = float(data.get('deductions_inr', 0.0))
        net = gross - deductions
        sale_date = data.get('sale_date', str(date.today()))

        sale_id = execute_db("""
            INSERT INTO sales (field_id, crop_name, buyer_mandi, quantity_quintals, price_per_quintal_inr, gross_revenue_inr, deductions_inr, net_revenue_inr, sale_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (field_id, crop, mandi, qty, rate, gross, deductions, net, sale_date))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, quantity, unit, cost_inr)
            VALUES (?, 'SALE_RECORDED', ?, ?, 'Quintals', ?);
        """, (field_id, f"Offloaded {qty} Qtl {crop} at {mandi} @ Rs {rate}/Qtl", qty, net))

        return success_response({"sale_id": sale_id, "net_revenue": net}, "Crop sale logged successfully", 201)
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 9. MACHINERY HUB
# -------------------------------------------------------------
@api_bp.route('/machinery', methods=['GET'])
def get_machinery():
    items = query_db("SELECT * FROM machinery ORDER BY equipment_name;")
    bookings = query_db("SELECT * FROM machinery_maintenance ORDER BY start_date DESC LIMIT 10;")
    return success_response({"equipment": items, "recent_bookings": bookings})

@api_bp.route('/machinery/book', methods=['POST'])
def book_machinery():
    try:
        data = request.get_json(silent=True) or {}
        mach_id = int(data.get('machinery_id', 1))
        field_id = int(data.get('field_id', 1))
        hours = float(data.get('duration_hours', 4.0))
        start = data.get('start_date', str(date.today()))
        notes = data.get('notes', 'Farmer custom hiring service booking').strip()

        mach = query_db("SELECT * FROM machinery WHERE id = ?;", (mach_id,), one=True)
        if not mach:
            return error_response("Machinery not found", 404)

        cost = hours * mach['operating_cost_per_hour']

        book_id = execute_db("""
            INSERT INTO machinery_maintenance (machinery_id, field_id, activity_type, start_date, duration_hours, cost_inr, notes, status)
            VALUES (?, ?, 'Booking', ?, ?, ?, ?, 'Confirmed');
        """, (mach_id, field_id, start, hours, cost, notes))

        # Log expense
        execute_db("""
            INSERT INTO expenses (field_id, category, item_name, quantity, unit, cost_inr, expense_date)
            VALUES (?, 'Machinery', ?, ?, 'Hours', ?, ?);
        """, (field_id, f"Custom hire: {mach['equipment_name']}", hours, cost, start))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, quantity, unit, cost_inr)
            VALUES (?, 'MACHINERY_BOOKED', ?, ?, 'Hours', ?);
        """, (field_id, f"Booked {mach['equipment_name']} for {hours}h", hours, cost))

        return success_response({"booking_id": book_id, "cost_inr": cost}, f"Successfully reserved {mach['equipment_name']}. Total estimated rental: Rs {cost:,.0f}")
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 10. SATELLITE DISASTER ASSESSMENT & PMFBY INSURANCE
# -------------------------------------------------------------
@api_bp.route('/satellite/<int:field_id>', methods=['GET'])
def get_satellite_data(field_id):
    sat = get_satellite_assessment(field_id)
    return success_response(sat)

@api_bp.route('/insurance/generate', methods=['POST'])
def generate_insurance_claim():
    try:
        data = request.get_json(silent=True) or {}
        field_id = int(data.get('field_id', 1))
        disaster_type = data.get('disaster_type', 'Flash Flood / Crop Submersion').strip()
        affected_area = float(data.get('affected_area_ha', 1.8))
        claimed_loss = float(data.get('claimed_loss_inr', 52000.0))

        field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
        farmer = query_db("SELECT * FROM farmers WHERE id = 1;", one=True)
        sat = get_satellite_assessment(field_id)

        claim_number = f"PMFBY-CLAIM-{int(datetime.now().timestamp())}"
        payload = {
            "claim_number": claim_number,
            "farmer": farmer,
            "field": field,
            "crop": field['variety'] if field else "Wheat",
            "variety": field['variety'] if field else "HD-3086",
            "disaster_type": disaster_type,
            "affected_area_ha": affected_area,
            "claimed_loss_inr": claimed_loss,
            "satellite": sat
        }

        pdf_path = generate_pmfby_dossier(payload)

        claim_id = execute_db("""
            INSERT INTO insurance_claims (
                claim_number, field_id, farmer_id, disaster_type, claimed_loss_inr,
                affected_area_ha, ndvi_anomaly_recorded, status, dossier_pdf_path, filing_date
            ) VALUES (?, ?, 1, ?, ?, ?, ?, 'Draft Generated', ?, DATE('now'));
        """, (
            claim_number, field_id, disaster_type, claimed_loss,
            affected_area, sat.get('ndvi_anomaly_pct', -48.6), pdf_path
        ))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description, notes)
            VALUES (?, 'INSURANCE_CLAIM_GENERATED', ?, ?);
        """, (field_id, f"Compiled official PMFBY claim dossier ({claim_number})", f"Peril: {disaster_type}, Assessed Loss: Rs {claimed_loss:,.0f}"))

        return success_response({
            "claim_id": claim_id,
            "claim_number": claim_number,
            "pdf_filename": os.path.basename(pdf_path),
            "download_url": f"/api/insurance/download/{claim_number}",
            "status": "Draft Generated"
        }, "PMFBY Claim Dossier PDF compiled successfully")
    except Exception as e:
        return error_response(f"Error compiling insurance dossier: {str(e)}", 500)

@api_bp.route('/insurance/download/<claim_number>', methods=['GET'])
def download_insurance_pdf(claim_number):
    try:
        filename = f"{claim_number}.pdf"
        file_path = Config.GENERATED_DIR / filename
        if not file_path.exists():
            # If not yet generated, generate sample dossier
            claim = query_db("SELECT * FROM insurance_claims WHERE claim_number = ?;", (claim_number,), one=True)
            field = query_db("SELECT * FROM fields WHERE id = 1;", one=True)
            farmer = query_db("SELECT * FROM farmers WHERE id = 1;", one=True)
            sat = get_satellite_assessment(1)
            payload = {
                "claim_number": claim_number,
                "farmer": farmer,
                "field": field,
                "crop": "Wheat",
                "variety": "HD-3086",
                "disaster_type": claim['disaster_type'] if claim else "Flash Flood / Crop Submersion",
                "affected_area_ha": claim['affected_area_ha'] if claim else 1.8,
                "claimed_loss_inr": claim['claimed_loss_inr'] if claim else 52000.0,
                "satellite": sat
            }
            file_path = generate_pmfby_dossier(payload)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"PMFBY_Claim_Dossier_{claim_number}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return error_response(f"PDF download failed: {str(e)}", 500)

@api_bp.route('/insurance/claims', methods=['GET'])
def list_insurance_claims():
    claims = query_db("""
        SELECT ic.*, f.field_code, f.field_name
        FROM insurance_claims ic
        LEFT JOIN fields f ON ic.field_id = f.id
        ORDER BY ic.created_at DESC;
    """)
    return success_response(claims)

# -------------------------------------------------------------
# 11. GOVERNMENT SCHEMES
# -------------------------------------------------------------
@api_bp.route('/government/schemes', methods=['GET'])
def get_schemes():
    schemes = query_db("SELECT * FROM government_schemes WHERE is_active = 1 ORDER BY id ASC;")
    return success_response(schemes)

# -------------------------------------------------------------
# 12. USSD SIMULATOR
# -------------------------------------------------------------
@api_bp.route('/ussd', methods=['POST'])
def ussd_terminal():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code', '*515#').strip()
        field_id = int(data.get('field_id', 1))
        result = process_ussd_code(code, field_id)
        return success_response(result)
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------------------------------------------
# 13. JUDGES' DEMO CENTER SCENARIOS
# -------------------------------------------------------------
@api_bp.route('/scenarios/run', methods=['POST'])
def execute_demo_scenario():
    try:
        data = request.get_json(silent=True) or {}
        scenario_key = data.get('scenario', 'flash_flood').strip()
        field_id = int(data.get('field_id', 1))
        
        result = run_scenario(scenario_key, field_id)
        return success_response(result, f"Scenario '{result['title']}' executed successfully")
    except Exception as e:
        return error_response(f"Scenario failed: {str(e)}", 500)

# -------------------------------------------------------------
# 14. ADVICES & AUDIT TRAIL
# -------------------------------------------------------------
@api_bp.route('/advice/<int:field_id>', methods=['GET'])
def get_field_advices(field_id):
    advices = query_db("SELECT * FROM crop_advices WHERE field_id = ? ORDER BY priority DESC, created_at DESC;", (field_id,))
    return success_response(advices)

@api_bp.route('/advice/<int:advice_id>/acknowledge', methods=['POST'])
def acknowledge_advice(advice_id):
    try:
        advice = query_db("SELECT * FROM crop_advices WHERE id = ?;", (advice_id,), one=True)
        if not advice:
            return error_response("Advice not found", 404)

        execute_db("UPDATE crop_advices SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP WHERE id = ?;", (advice_id,))
        
        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description)
            VALUES (?, 'ADVICE_ACKNOWLEDGED', ?);
        """, (advice['field_id'], f"Acknowledged Advisory: {advice['title']}"))

        return success_response({"id": advice_id, "acknowledged": 1}, "Advisory acknowledged and logged in audit history")
    except Exception as e:
        return error_response(str(e), 500)

@api_bp.route('/growth/<int:field_id>', methods=['GET'])
def get_growth_records(field_id):
    records = query_db("SELECT * FROM growth_records WHERE field_id = ? ORDER BY days_from_sowing ASC;", (field_id,))
    return success_response(records)

@api_bp.route('/growth/<int:field_id>/update-stage', methods=['POST'])
def update_crop_stage(field_id):
    try:
        data = request.get_json(silent=True) or {}
        new_stage = data.get('stage', 'Flowering & Anthesis').strip()
        gdd = float(data.get('gdd', 1400.0))
        height = float(data.get('height_cm', 85.0))
        canopy = float(data.get('canopy_cover_pct', 90.0))

        execute_db("UPDATE fields SET current_stage = ? WHERE id = ?;", (new_stage, field_id))
        
        execute_db("""
            INSERT INTO growth_records (field_id, stage_name, days_from_sowing, cumulative_gdd, canopy_cover_pct, plant_height_cm, health_index)
            VALUES (?, ?, 90, ?, ?, ?, 94.0);
        """, (field_id, new_stage, gdd, canopy, height))

        execute_db("""
            INSERT INTO field_actions (field_id, action_type, description)
            VALUES (?, 'STAGE_UPDATED', ?);
        """, (field_id, f"Crop growth stage advanced to: {new_stage} (GDD: {gdd})"))

        return success_response({"stage": new_stage}, "Crop stage updated successfully")
    except Exception as e:
        return error_response(str(e), 500)

@api_bp.route('/audit/<int:field_id>', methods=['GET'])
def get_audit_trail(field_id):
    actions = query_db("SELECT * FROM field_actions WHERE field_id = ? ORDER BY created_at DESC LIMIT 50;", (field_id,))
    return success_response(actions)

@api_bp.route('/demo/reset', methods=['POST'])
def reset_demo_database():
    try:
        init_db(force_reset=True)
        return success_response({"status": "reset"}, "Demo database restored to default factory baseline.")
    except Exception as e:
        return error_response(f"Reset failed: {str(e)}", 500)

@api_bp.route('/translations', methods=['GET'])
def get_translations():
    trans_file = Config.DATA_DIR / 'translations.json'
    if trans_file.exists():
        with open(trans_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})
