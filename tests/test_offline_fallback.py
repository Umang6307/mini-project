"""
Unit Tests for OfflineFallbackManager Disease Diagnosis Engine
"""

import unittest
from backend.ai.offline_fallback import OfflineFallbackManager

class TestOfflineFallbackManager(unittest.TestCase):
    def setUp(self):
        self.mgr = OfflineFallbackManager()

    def test_yellow_rust_matching(self):
        diag = self.mgr.diagnose(
            crop="Wheat",
            stage="Flowering & Anthesis",
            symptoms_text="Yellow powdery stripes on leaf blades"
        )
        self.assertEqual(diag['conditionName'], 'Yellow Stripe Rust')
        self.assertEqual(diag['severityLevel'], 'HIGH')
        self.assertEqual(diag['source'], 'offline-rule-engine')
        self.assertIn("Tilt", diag['chemicalTreatment'])
        self.assertGreater(diag['estimatedCostInr'], 0)

    def test_rice_blast_matching(self):
        diag = self.mgr.diagnose(
            crop="Paddy (Rice)",
            stage="Tillering",
            symptoms_text="Spindle-shaped lesions with grey center on leaves"
        )
        self.assertIn("Blast", diag['conditionName'])
        self.assertEqual(diag['source'], 'offline-rule-engine')

    def test_generic_fallback(self):
        # Even with vague or unusual inputs, it must never crash
        diag = self.mgr.diagnose(crop="Sugarcane", symptoms_text="dry foliage")
        self.assertIsNotNone(diag['conditionName'])
        self.assertIsNotNone(diag['chemicalTreatment'])
        self.assertEqual(diag['source'], 'offline-rule-engine')

if __name__ == '__main__':
    unittest.main()
