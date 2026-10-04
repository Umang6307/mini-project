"""
Fertilizer Decision Engine for Indian Soils
Analyzes N-P-K, pH, and Micronutrients to provide targeted agronomic recommendations.
"""

import json
from pathlib import Path
from backend.config import Config

# Standard Indian Soil Test Benchmarks (Available Nutrients in kg/ha)
# N: Low < 280, Medium 280-560, High > 560
# P (P2O5): Low < 23, Medium 23-56, High > 56
# K (K2O): Low < 140, Medium 140-280, High > 280
# In ppm (approx / 2.24):
# N ppm: Low < 125, Medium 125-250, High > 250
# P ppm: Low < 10, Medium 10-25, High > 25
# K ppm: Low < 60, Medium 60-125, High > 125

FERTILIZER_DATABASE = [
    {
        "code": "UREA",
        "name": "Neem Coated Urea (46% N)",
        "bag_size_kg": 45,
        "price_per_bag_inr": 266.5,
        "nutrient_pct": {"N": 46.0, "P": 0, "K": 0}
    },
    {
        "code": "DAP",
        "name": "Di-Ammonium Phosphate (18% N, 46% P2O5)",
        "bag_size_kg": 50,
        "price_per_bag_inr": 1350.0,
        "nutrient_pct": {"N": 18.0, "P": 46.0, "K": 0}
    },
    {
        "code": "MOP",
        "name": "Muriate of Potash (60% K2O)",
        "bag_size_kg": 50,
        "price_per_bag_inr": 1700.0,
        "nutrient_pct": {"N": 0, "P": 0, "K": 60.0}
    },
    {
        "code": "ZINC_SULFATE",
        "name": "Zinc Sulfate 21% (Heptahydrate)",
        "bag_size_kg": 25,
        "price_per_bag_inr": 780.0,
        "nutrient_pct": {"Zn": 21.0, "S": 10.0}
    }
]

def calculate_fertilizer(crop: str,
                         crop_stage: str,
                         nitrogen_ppm: float,
                         phosphorus_ppm: float,
                         potassium_ppm: float,
                         ph: float = 7.2,
                         soil_type: str = "Alluvial Clay Loam",
                         area_ha: float = 1.8) -> dict:
    
    recommendations = []
    total_cost_inr = 0.0
    deficiencies = []
    
    # 1. Nitrogen Assessment
    if nitrogen_ppm < 120.0:
        sev = "HIGH" if nitrogen_ppm < 80 else "MODERATE"
        deficiencies.append(f"Nitrogen ({sev})")
        # Need top dress of urea
        if "sow" in crop_stage.lower() or "basal" in crop_stage.lower():
            urea_kg_ha = 65.0
            timing = "Basal application at sowing along with phosphorus"
        else:
            urea_kg_ha = 80.0
            timing = "Top dress split application right before upcoming irrigation"
        
        total_kg = round(urea_kg_ha * area_ha, 1)
        bags = round(total_kg / 45.0, 1)
        cost = round(bags * 266.5, 0)
        total_cost_inr += cost

        recommendations.append({
            "nutrient": "Nitrogen (N)",
            "deficiency_severity": sev,
            "current_value": f"{nitrogen_ppm:.1f} ppm (Low)",
            "recommended_fertilizer": "Neem Coated Urea (46% N)",
            "rate_kg_ha": urea_kg_ha,
            "total_quantity_kg": total_kg,
            "bags_needed": bags,
            "application_timing": timing,
            "estimated_cost_inr": cost,
            "explanation": f"Crop requires nitrogen for leaf area expansion and protein synthesis at {crop_stage} stage."
        })
    elif nitrogen_ppm < 150.0 and ("tillering" in crop_stage.lower() or "vegetative" in crop_stage.lower()):
        # Mild booster
        urea_kg_ha = 45.0
        total_kg = round(urea_kg_ha * area_ha, 1)
        bags = round(total_kg / 45.0, 1)
        cost = round(bags * 266.5, 0)
        total_cost_inr += cost
        recommendations.append({
            "nutrient": "Nitrogen (N)",
            "deficiency_severity": "MILD",
            "current_value": f"{nitrogen_ppm:.1f} ppm (Borderline)",
            "recommended_fertilizer": "Neem Coated Urea (46% N)",
            "rate_kg_ha": urea_kg_ha,
            "total_quantity_kg": total_kg,
            "bags_needed": bags,
            "application_timing": "Light top dressing during tillering/vegetative flush",
            "estimated_cost_inr": cost,
            "explanation": "Maintain canopy vigor; prevent yellowing of lower vegetative nodes."
        })

    # 2. Phosphorus Assessment
    if phosphorus_ppm < 14.0:
        sev = "HIGH" if phosphorus_ppm < 8 else "MODERATE"
        deficiencies.append(f"Phosphorus ({sev})")
        dap_kg_ha = 100.0
        total_kg = round(dap_kg_ha * area_ha, 1)
        bags = round(total_kg / 50.0, 1)
        cost = round(bags * 1350.0, 0)
        total_cost_inr += cost

        recommendations.append({
            "nutrient": "Phosphorus (P2O5)",
            "deficiency_severity": sev,
            "current_value": f"{phosphorus_ppm:.1f} ppm (Deficient)",
            "recommended_fertilizer": "Di-Ammonium Phosphate (DAP 18:46:0)",
            "rate_kg_ha": dap_kg_ha,
            "total_quantity_kg": total_kg,
            "bags_needed": bags,
            "application_timing": "Basal seed-furrow placement or side banding",
            "estimated_cost_inr": cost,
            "explanation": "Essential for root branching, crown root initiation, and ATP energy transfer in early stages."
        })

    # 3. Potassium Assessment
    if potassium_ppm < 100.0:
        sev = "HIGH" if potassium_ppm < 70 else "MODERATE"
        deficiencies.append(f"Potassium ({sev})")
        mop_kg_ha = 50.0
        total_kg = round(mop_kg_ha * area_ha, 1)
        bags = round(total_kg / 50.0, 1)
        cost = round(bags * 1700.0, 0)
        total_cost_inr += cost

        recommendations.append({
            "nutrient": "Potassium (K2O)",
            "deficiency_severity": sev,
            "current_value": f"{potassium_ppm:.1f} ppm (Low)",
            "recommended_fertilizer": "Muriate of Potash (MOP 60% K2O)",
            "rate_kg_ha": mop_kg_ha,
            "total_quantity_kg": total_kg,
            "bags_needed": bags,
            "application_timing": "Apply at boot stage / panicle initiation",
            "estimated_cost_inr": cost,
            "explanation": "Crucial for stomatal conductance, grain test weight, and resisting lodging in wind."
        })

    # 4. pH and Micronutrient Check (Zinc)
    if ph > 7.8:
        # High pH in Northern India causes Zinc fixation
        zn_kg_ha = 25.0
        total_kg = round(zn_kg_ha * area_ha, 1)
        bags = round(total_kg / 25.0, 1)
        cost = round(bags * 780.0, 0)
        total_cost_inr += cost

        recommendations.append({
            "nutrient": "Zinc & Micronutrient (Zn + S)",
            "deficiency_severity": "MODERATE",
            "current_value": f"pH {ph:.1f} (Alkaline induced fixation)",
            "recommended_fertilizer": "Zinc Sulfate 21% (Heptahydrate)",
            "rate_kg_ha": zn_kg_ha,
            "total_quantity_kg": total_kg,
            "bags_needed": bags,
            "application_timing": "Broadcast with sand or spray 0.5% ZnSO4 + 0.25% slaked lime",
            "estimated_cost_inr": cost,
            "explanation": f"Alkaline soil (pH {ph}) binds zinc. Supplementation prevents Khaira disease in rice and interveinal chlorosis in wheat."
        })

    # If completely optimal
    if not recommendations:
        return {
            "status": "BALANCED",
            "deficiencies": ["None Detected - Balanced Soil Profile"],
            "recommendations": [{
                "nutrient": "Overall Soil Nutrition",
                "deficiency_severity": "NONE",
                "current_value": f"N: {nitrogen_ppm:.0f}, P: {phosphorus_ppm:.0f}, K: {potassium_ppm:.0f} ppm",
                "recommended_fertilizer": "Maintain Scheduled Routine",
                "rate_kg_ha": 0,
                "total_quantity_kg": 0,
                "bags_needed": 0,
                "application_timing": "N/A",
                "estimated_cost_inr": 0,
                "explanation": "Current N-P-K and pH levels are adequate for the current crop stage. No immediate supplemental fertilizer required."
            }],
            "total_estimated_cost_inr": 0,
            "soil_ph": ph,
            "soil_type": soil_type
        }

    return {
        "status": "DEFICIENCY_DETECTED",
        "deficiencies": deficiencies,
        "recommendations": recommendations,
        "total_estimated_cost_inr": total_cost_inr,
        "soil_ph": ph,
        "soil_type": soil_type
    }
