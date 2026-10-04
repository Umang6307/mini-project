"""
Unit Tests for PMFBY Insurance Claim Dossier PDF Generation
"""

import unittest
import os
from pathlib import Path
from backend.insurance.pdf_generator import generate_pmfby_dossier

class TestPdfGeneration(unittest.TestCase):
    def test_pmfby_pdf_creates_file(self):
        sample_claim = {
            "claim_number": "PMFBY-TEST-001",
            "farmer": {
                "full_name": "Ravi Kumar",
                "farmer_code": "FARMER-HR-001",
                "phone": "+91 98120 12345",
                "state": "Haryana",
                "district": "Karnal",
                "village": "Kachhwa"
            },
            "field": {
                "field_code": "FLD-01",
                "field_name": "North Canal Wheat Plot",
                "area_value": 1.8,
                "area_unit": "Hectares",
                "area_hectares": 1.8,
                "variety": "HD-3086"
            },
            "crop": "Wheat",
            "variety": "HD-3086",
            "disaster_type": "Flash Flood / Crop Submersion",
            "affected_area_ha": 1.8,
            "claimed_loss_inr": 52000.0,
            "satellite": {
                "baseline_ndvi": 0.74,
                "current_ndvi": 0.38,
                "ndvi_anomaly_pct": -48.6,
                "severity": "CRITICAL",
                "estimated_yield_loss_pct": 65.0
            }
        }

        output_path = generate_pmfby_dossier(sample_claim)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 1000)

        # Clean up test artifact if desired
        try:
            os.remove(output_path)
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main()
