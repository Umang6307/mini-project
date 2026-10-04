"""
Unit Tests for Irrigation and Fertilizer Decision Engines & Unit Conversion
"""

import unittest
from backend.decision_engine.irrigation import calculate_irrigation
from backend.decision_engine.fertilizer import calculate_fertilizer
from backend.utils.unit_converter import convert_to_hectares, convert_all_units

class TestDecisionEngines(unittest.TestCase):
    def test_irrigation_deficit(self):
        # 18% moisture on Clay Loam should trigger DEFICIT
        rec = calculate_irrigation(
            soil_moisture_pct=18.0,
            soil_type="Alluvial Clay Loam",
            crop="Wheat",
            crop_stage="Flowering & Anthesis",
            area_ha=1.8
        )
        self.assertEqual(rec['status'], 'DEFICIT')
        self.assertGreater(rec['water_depth_mm'], 0)
        self.assertGreater(rec['water_volume_m3'], 0)
        self.assertGreater(rec['duration_hours'], 0)
        self.assertIn("IMMEDIATE", rec['urgency'])

    def test_irrigation_optimal(self):
        # 34% moisture is in the safe buffer zone for Clay Loam
        rec = calculate_irrigation(
            soil_moisture_pct=34.0,
            soil_type="Alluvial Clay Loam",
            crop="Wheat",
            crop_stage="Flowering & Anthesis"
        )
        self.assertEqual(rec['status'], 'OPTIMAL')
        self.assertEqual(rec['water_depth_mm'], 0.0)

    def test_fertilizer_nitrogen_deficiency(self):
        # N at 75 ppm is low
        rec = calculate_fertilizer(
            crop="Wheat",
            crop_stage="Tillering",
            nitrogen_ppm=75.0,
            phosphorus_ppm=22.0,
            potassium_ppm=180.0,
            ph=7.2,
            area_ha=1.8
        )
        self.assertEqual(rec['status'], 'DEFICIENCY_DETECTED')
        self.assertTrue(any("Neem Coated Urea" in r['recommended_fertilizer'] for r in rec['recommendations']))
        self.assertGreater(rec['total_estimated_cost_inr'], 0)

    def test_unit_conversions(self):
        # 2.471 Acres = 1 Hectare
        ha = convert_to_hectares(2.47105, 'Acre')
        self.assertAlmostEqual(ha, 1.0, places=2)

        # All units conversion
        units = convert_all_units(1.0, 'Hectare')
        self.assertEqual(units['hectare'], 1.0)
        self.assertAlmostEqual(units['acre'], 2.471, places=1)
        self.assertAlmostEqual(units['kanal'], 19.77, places=1)

if __name__ == '__main__':
    unittest.main()
