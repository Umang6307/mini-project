"""
Unit Tests for Smart Crop Advisory Backend & REST Endpoints (Standard Library)
"""

import unittest
import json
import threading
import time
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from backend.app import SmartCropRequestHandler
from backend.database import init_db

TEST_PORT = 3399
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

class TestBackendEndpoints(unittest.TestCase):
    server = None
    server_thread = None

    @classmethod
    def setUpClass(cls):
        init_db(force_reset=False)
        cls.server = ThreadingHTTPServer(('127.0.0.1', TEST_PORT), SmartCropRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.shutdown()
            cls.server.server_close()

    def get(self, path):
        req = urllib.request.Request(f"{BASE_URL}{path}")
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))

    def post(self, path, payload):
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode('utf-8'))

    def test_health_check(self):
        status, data = self.get('/health')
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'online')

    def test_demo_login(self):
        status, data = self.post('/api/login', {
            'username': 'ravi',
            'password': 'password123'
        })
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data['data']['username'], 'ravi')

    def test_invalid_login(self):
        status, data = self.post('/api/login', {
            'username': 'ravi',
            'password': 'wrongpassword'
        })
        self.assertEqual(status, 401)
        self.assertEqual(data.get('status'), 'error')

    def test_dashboard_data(self):
        status, data = self.get('/api/dashboard?field_id=1')
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('current_field', data['data'])
        self.assertIn('soil', data['data'])
        self.assertIn('weather', data['data'])

    def test_fields_list(self):
        status, data = self.get('/api/fields')
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(len(data['data']) >= 1)

if __name__ == '__main__':
    unittest.main()
