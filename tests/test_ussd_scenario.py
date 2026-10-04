"""
Unit Tests for USSD Simulator and Demo Center Scenarios
"""

import unittest
from backend.services.ussd_service import process_ussd_code
from backend.services.scenario_service import run_scenario
from backend.database import init_db

class TestUssdAndScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db(force_reset=False)

    def test_ussd_main_menu(self):
        res = process_ussd_code("*515#")
        self.assertIn("KISAN SMART ADVISORY", res['response'])
        self.assertIn("1. Soil Moisture", res['response'])

    def test_ussd_soil_option(self):
        res = process_ussd_code("*515*1#", field_id=1)
        self.assertIn("Root Moisture", res['response'])
        self.assertIn("ADVISORY", res['response'])

    def test_flash_flood_scenario(self):
        res = run_scenario("flash_flood", field_id=1)
        self.assertEqual(res['scenario'], 'flash_flood')
        self.assertTrue(len(res['steps']) >= 4)
        self.assertIn("Inundation", res['title'])

if __name__ == '__main__':
    unittest.main()
