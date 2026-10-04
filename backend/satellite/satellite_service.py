"""
Satellite Disaster Assessment Service
Simulates multi-spectral Sentinel-2 (10m) and Landsat vegetation index (NDVI) telemetry.
Calculates crop canopy vigor, anomaly percentages, affected acreage, and financial damage.
Clearly labeled as SIMULATED unless connected to Copernicus Open Access Hub.
"""

from backend.database import query_db, execute_db

def get_satellite_assessment(field_id: int = 1) -> dict:
    assessment = query_db(
        "SELECT * FROM satellite_assessments WHERE field_id = ? ORDER BY assessment_date DESC LIMIT 1;",
        (field_id,),
        one=True
    )
    if not assessment:
        # Provide default normal baseline
        assessment = {
            "field_id": field_id,
            "disaster_type": "Normal / Healthy Crop Canopy",
            "baseline_ndvi": 0.74,
            "current_ndvi": 0.72,
            "ndvi_anomaly_pct": -2.7,
            "affected_acreage": 0.0,
            "severity": "LOW",
            "estimated_yield_loss_pct": 0.0,
            "estimated_financial_loss_inr": 0.0,
            "satellite_source": "Sentinel-2 MSI Simulated (10m Resolution)",
            "is_simulated": 1,
            "assessment_date": "2026-09-30"
        }
    assessment["data_source_label"] = "SIMULATED SATELLITE TELEMETRY"
    return assessment

def update_satellite_disaster(field_id: int, disaster_type: str, current_ndvi: float,
                              affected_ha: float, severity: str, yield_loss_pct: float,
                              financial_loss_inr: float):
    execute_db("""
        INSERT INTO satellite_assessments (
            field_id, disaster_type, baseline_ndvi, current_ndvi, ndvi_anomaly_pct,
            affected_acreage, severity, estimated_yield_loss_pct, estimated_financial_loss_inr,
            satellite_source, is_simulated, assessment_date
        ) VALUES (?, ?, 0.74, ?, ?, ?, ?, ?, ?, 'Sentinel-2 MSI Simulated (10m Resolution)', 1, DATE('now'));
    """, (
        field_id, disaster_type, current_ndvi,
        round(((current_ndvi - 0.74) / 0.74) * 100, 1),
        affected_ha, severity, yield_loss_pct, financial_loss_inr
    ))
