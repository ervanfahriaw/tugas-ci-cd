import unittest
import threading
import json
import os
import shutil
import tempfile
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from pathlib import Path
from http.server import ThreadingHTTPServer

import app


class TestPythonCRUDAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup temporary data folder for isolated testing
        cls.test_dir = tempfile.mkdtemp()
        cls.test_file = Path(cls.test_dir) / "test_messages.json"
        app.DATA_FILE = cls.test_file

        # Start test HTTP server on random free port (5055)
        cls.server_port = 5055
        cls.server = ThreadingHTTPServer(("127.0.0.1", cls.server_port), app.APIHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def setUp(self):
        # Reset data file before each test
        if app.DATA_FILE.exists():
            app.DATA_FILE.unlink()

    def test_health_check(self):
        url = f"http://127.0.0.1:{self.server_port}/health"
        with urlopen(url) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "active")
            self.assertEqual(data.get("service"), "Backend API")

    def test_post_message_success(self):
        url = f"http://127.0.0.1:{self.server_port}/messages"
        payload = json.dumps({"message": "Hello CI/CD Jenkins"}).encode("utf-8")
        req = Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urlopen(req) as res:
            self.assertEqual(res.status, 201)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "created")
            self.assertEqual(data["message"]["message"], "Hello CI/CD Jenkins")
            self.assertIn("created_at", data["message"])

    def test_post_empty_message_validation(self):
        url = f"http://127.0.0.1:{self.server_port}/messages"
        payload = json.dumps({"message": "   "}).encode("utf-8")
        req = Request(url, data=payload, headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as ctx:
            urlopen(req)
        self.assertEqual(ctx.exception.code, 400)

    def test_get_message_by_index_success_and_not_found(self):
        # Add a test message first
        app.save_message("Test detail message")

        # Test valid index (0)
        url_valid = f"http://127.0.0.1:{self.server_port}/messages/0"
        with urlopen(url_valid) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data["index"], 0)
            self.assertEqual(data["item"]["message"], "Test detail message")

        # Test non-existent index (99)
        url_invalid = f"http://127.0.0.1:{self.server_port}/messages/99"
        with self.assertRaises(HTTPError) as ctx:
            urlopen(url_invalid)
        self.assertEqual(ctx.exception.code, 404)

    def test_delete_message(self):
        app.save_message("Pesan yang akan dihapus")
        url = f"http://127.0.0.1:{self.server_port}/messages?index=0"
        req = Request(url, method="DELETE")
        with urlopen(req) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode())
            self.assertEqual(data.get("status"), "deleted")


if __name__ == "__main__":
    unittest.main()
