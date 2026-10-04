"""
Irrigation Decision Engine for Indian Agro-Climatic Zones
Calculates moisture deficits, required depth, volume, pump runtime, and urgency.
"""

SOIL_CHARACTERISTICS = {
    "alluvial clay loam": {"fc": 36.0, "pwp": 16.0, "mad": 0.50, "bulk_density": 1.35},
    "clay loam": {"fc": 35.0, "pwp": 17.0, "mad": 0.50, "bulk_density": 1.35},
    "clay": {"fc": 42.0, "pwp": 22.0, "mad": 0.45, "bulk_density": 1.25},
    "sandy loam": {"fc": 22.0, "pwp": 9.0, "mad": 0.55, "bulk_density": 1.45},
    "silt loam": {"fc": 32.0, "pwp": 14.0, "mad": 0.50, "bulk_density": 1.30},
    "black cotton soil": {"fc": 45.0, "pwp": 24.0, "mad": 0.40, "bulk_density": 1.20}
}

CROP_STAGE_ROOT_DEPTH_MM = {
    "sowing": 150,
    "germination": 200,
    "tillering": 350,
    "vegetative": 400,
    "jointing & booting": 550,
    "panicle initiation": 500,
    "flowering & anthesis": 650,
    "flowering": 600,
    "grain filling / dough": 650,
    "maturity & harvest": 650
}

def calculate_irrigation(soil_moisture_pct: float,
                         soil_type: str = "Alluvial Clay Loam",
                         crop: str = "Wheat",
                         crop_stage: str = "Flowering & Anthesis",
                         area_ha: float = 1.8,
                         temperature_c: float = 27.0,
                         rainfall_prob_pct: float = 18.0,
                         et0_mm_day: float = 4.2) -> dict:
    
    soil_key = soil_type.strip().lower()
    soil_props = SOIL_CHARACTERISTICS.get(soil_key, SOIL_CHARACTERISTICS["alluvial clay loam"])
    fc = soil_props["fc"]
    pwp = soil_props["pwp"]
    available_water_cap = fc - pwp
    critical_threshold = pwp + (available_water_cap * (1 - soil_props["mad"]))

    stage_key = crop_stage.strip().lower()
    root_depth_mm = 500
    for k, v in CROP_STAGE_ROOT_DEPTH_MM.items():
        if k in stage_key:
            root_depth_mm = v
            break

    current_moisture = float(soil_moisture_pct)
    
    # Check if high rain is imminent (>70% prob)
    rain_suppression = rainfall_prob_pct >= 70.0

    if current_moisture >= fc:
        status = "SURPLUS"
        water_depth_mm = 0.0
        urgency = "NO_IRRIGATION"
        explanation = (f"Soil moisture ({current_moisture:.1f}%) exceeds Field Capacity ({fc}%). "
                       f"Risk of root hypoxia or waterlogging. Ensure drainage ditches are clear.")
    elif current_moisture >= critical_threshold:
        status = "OPTIMAL"
        water_depth_mm = 0.0
        urgency = "MONITOR"
        days_until_deficit = max(1, int((current_moisture - critical_threshold) / (et0_mm_day * 0.4)))
        explanation = (f"Current soil moisture ({current_moisture:.1f}%) is in the optimal buffer zone "
                       f"({critical_threshold:.1f}% - {fc}%). Next re-assessment recommended in {days_until_deficit} days.")
    else:
        status = "DEFICIT"
        # Depth needed to bring back to 90% of field capacity
        moisture_deficit_pct = max(0.0, (fc * 0.92) - current_moisture)
        # Depth in mm = (% deficit / 100) * root_depth_mm
        raw_depth_mm = (moisture_deficit_pct / 100.0) * root_depth_mm
        water_depth_mm = round(min(70.0, max(20.0, raw_depth_mm)), 1)

        if rain_suppression:
            urgency = "DEFERRED"
            explanation = (f"Moisture is in deficit ({current_moisture:.1f}%), but weather forecast predicts "
                           f"{rainfall_prob_pct:.0f}% probability of rain. Hold off irrigation to conserve power and avoid waterlogging.")
        elif current_moisture <= pwp + 4.0:
            urgency = "IMMEDIATE (Within 6-12 hours)"
            explanation = (f"CRITICAL STRESS: Soil moisture ({current_moisture:.1f}%) is near Wilting Point ({pwp}%). "
                           f"Apply {water_depth_mm} mm irrigation immediately to prevent irreversible yield loss at {crop_stage} stage.")
        else:
            urgency = "URGENT (Within 18-24 hours)"
            explanation = (f"Moisture deficit detected ({current_moisture:.1f}% vs target {fc * 0.9:.1f}%). "
                           f"Apply {water_depth_mm} mm irrigation within 18-24 hours to support active transpirational demand.")

    # 1 mm over 1 hectare = 10 cubic meters
    water_volume_m3 = round(water_depth_mm * 10 * area_ha, 1)
    # Typical standard 7.5 HP electric submersible pump discharges ~40 m3/hour
    pumping_capacity_m3_h = 40.0
    duration_hours = round(water_volume_m3 / pumping_capacity_m3_h, 1) if water_volume_m3 > 0 else 0.0

    return {
        "status": status,
        "current_moisture_pct": round(current_moisture, 1),
        "target_moisture_pct": round(fc, 1),
        "critical_threshold_pct": round(critical_threshold, 1),
        "water_depth_mm": water_depth_mm,
        "water_volume_m3": water_volume_m3,
        "duration_hours": duration_hours,
        "urgency": urgency,
        "explanation": explanation,
        "metadata": {
            "crop": crop,
            "stage": crop_stage,
            "soil_type": soil_type,
            "root_depth_mm": root_depth_mm,
            "area_ha": area_ha,
            "et0_mm_day": et0_mm_day,
            "rainfall_prob_pct": rainfall_prob_pct,
            "model_type": "FAO-56 Dual Crop Evapotranspiration Heuristic"
        }
    }
