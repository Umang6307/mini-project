"""
USSD / SMS Offline Farmer Telephony Simulator (*515#)
Allows non-smartphone farmers with feature phones to query vital advisory data.
"""

from backend.database import query_db

def process_ussd_code(code_string: str, field_id: int = 1) -> dict:
    code = code_string.strip()

    # Normalize code
    if code in ["*515#", "MENU", "*515"]:
        return {
            "session_active": True,
            "response": (
                "=== KISAN SMART ADVISORY ===\n"
                "1. Soil Moisture & Water\n"
                "2. Mandi Rates (Wheat/Paddy)\n"
                "3. Weather Advisory\n"
                "4. PMFBY Claim Status\n"
                "5. Fertilizer Recommendation\n"
                "0. Exit\n"
                "Reply with option number:"
            )
        }

    # Direct deep-links or menu options
    if code in ["1", "*515*1#", "*515*1"]:
        field = query_db("SELECT * FROM fields WHERE id = ?;", (field_id,), one=True)
        soil = query_db("SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
        code_name = field['field_code'] if field else "FLD-01"
        moist = soil['moisture_15cm_pct'] if soil else 34.0
        
        if moist < 30.0:
            status_text = "DEFICIT"
            action_text = "Apply 25mm irrigation within 18h."
        elif moist > 45.0:
            status_text = "SURPLUS"
            action_text = "Do not irrigate. Check drainage."
        else:
            status_text = "OPTIMAL"
            action_text = "Moisture adequate. Check in 48h."

        return {
            "session_active": False,
            "response": (
                f"[{code_name} - {field['crop_name'] if 'crop_name' in (field or {}) else 'Wheat'}]\n"
                f"Root Moisture: {moist:.1f}% ({status_text})\n"
                f"Soil Temp: {soil['soil_temp_c'] if soil else 22.4}C\n"
                f"ADVISORY: {action_text}"
            )
        }

    if code in ["2", "*515*2#", "*515*2"]:
        mandi = query_db("SELECT * FROM mandi_prices WHERE crop_name = 'Wheat' AND mandi_name = 'Karnal' LIMIT 1;", one=True)
        paddy = query_db("SELECT * FROM mandi_prices WHERE crop_name LIKE '%Paddy%' LIMIT 1;", one=True)
        w_modal = mandi['modal_price'] if mandi else 2490
        p_modal = paddy['modal_price'] if paddy else 4480
        return {
            "session_active": False,
            "response": (
                "=== MANDI RATES (Rs/Qtl) ===\n"
                f"Karnal Wheat (HD-3086): Rs {w_modal} [MSP: 2275, +{w_modal-2275}]\n"
                f"Taraori Basmati (1121): Rs {p_modal} (Trend: RISING)\n"
                "SMS 'MANDI' to 51500 for more."
            )
        }

    if code in ["3", "*515*3#", "*515*3"]:
        weather = query_db("SELECT * FROM weather_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
        temp = weather['temperature_c'] if weather else 27.4
        rain = weather['rainfall_prob_pct'] if weather else 18
        hum = weather['humidity_pct'] if weather else 68
        return {
            "session_active": False,
            "response": (
                "=== KARNAL AGRI-MET ===\n"
                f"Temp: {temp}C | Humidity: {hum}%\n"
                f"Rainfall Prob: {rain:.0f}%\n"
                "Wind: 12 km/h NNW\n"
                "Clear sky. Safe for spraying."
            )
        }

    if code in ["4", "*515*4#", "*515*4"]:
        claim = query_db("SELECT * FROM insurance_claims WHERE field_id = ? ORDER BY created_at DESC LIMIT 1;", (field_id,), one=True)
        if claim:
            return {
                "session_active": False,
                "response": (
                    f"=== PMFBY CLAIM STATUS ===\n"
                    f"Claim No: {claim['claim_number']}\n"
                    f"Peril: {claim['disaster_type']}\n"
                    f"Assessed Loss: Rs {claim['claimed_loss_inr']:,.0f}\n"
                    f"Status: {claim['status']}\n"
                    "Dossier ready for official submission."
                )
            }
        else:
            return {
                "session_active": False,
                "response": (
                    "=== PMFBY CLAIM STATUS ===\n"
                    "No open disaster claims recorded for FLD-01.\n"
                    "Crop standing healthy. Dial *515*0# for helpline."
                )
            }

    if code in ["5", "*515*5#", "*515*5"]:
        soil = query_db("SELECT * FROM soil_readings WHERE field_id = ? ORDER BY recorded_at DESC LIMIT 1;", (field_id,), one=True)
        n = soil['nitrogen_ppm'] if soil else 138.0
        return {
            "session_active": False,
            "response": (
                "=== FERTILIZER ADVICE ===\n"
                f"Nitrogen: {n:.0f} ppm (Adequate/Medium)\n"
                "Top-dress Neem Coated Urea @ 35 kg/acre before irrigation.\n"
                "Subsidy price: Rs 266.50/45kg bag."
            )
        }

    if code == "0":
        return {
            "session_active": False,
            "response": "Thank you for using Smart Crop Advisory USSD Service. Jai Kisan!"
        }

    return {
        "session_active": False,
        "response": "Invalid selection. Please dial *515# to access main Kisan menu."
    }
