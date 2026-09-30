#!/usr/bin/env python3
"""Browser-facing hardening of the remove-ai-marks HTTP service.

    python3 content/skills/remove-ai-marks/service/tests/test_server_security.py
"""

from __future__ import annotations

import base64
import http.client
import json
import os
import re
import subprocess
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

SERVICE = Path(__file__).resolve().parents[1]
SCRIPTS = SERVICE / "scripts"
COMPOSE = SERVICE.parent / "compose.yaml"
sys.path.insert(0, str(SCRIPTS))

import server  # noqa: E402

KEY = "test-key-not-a-secret"


class ServiceSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        server.API_KEY = KEY
        server.Handler.log_message = lambda *_a, **_k: None  # type: ignore[method-assign]
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        server.configure_allowlists(cls.port)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self) -> None:
        self._saved = (server.MAX_BODY_BYTES, server._SLOTS)
        server.configure_allowlists(self.port)

    def tearDown(self) -> None:
        server.MAX_BODY_BYTES, server._SLOTS = self._saved

    def request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        auth: bool = True,
    ) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        conn.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
        hdrs = {"Host": f"127.0.0.1:{self.port}"}
        if auth:
            hdrs["Authorization"] = f"Bearer {KEY}"
        if body is not None:
            hdrs["Content-Type"] = "application/json"
            hdrs["Content-Length"] = str(len(body))
        hdrs.update(headers or {})
        for k, v in hdrs.items():
            if v is not None:
                conn.putheader(k, v)
        conn.endheaders()
        if body is not None:
            conn.send(body)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, (json.loads(raw) if raw else {})

    @staticmethod
    def inspect_body() -> bytes:
        text = base64.b64encode(b"plain text").decode()
        return json.dumps({"file": text, "name": "a.txt"}).encode()

    # Content-Type: cross-origin "simple" requests cannot send application/json.
    def test_json_post_is_accepted(self) -> None:
        status, body = self.request("POST", "/inspect", self.inspect_body())
        self.assertEqual(status, 200, body)

    def test_json_with_charset_is_accepted(self) -> None:
        hdr = {"Content-Type": "application/json; charset=utf-8"}
        status, _ = self.request("POST", "/inspect", self.inspect_body(), hdr)
        self.assertEqual(status, 200)

    def test_text_plain_post_is_415(self) -> None:
        hdr = {"Content-Type": "text/plain"}
        status, _ = self.request("POST", "/inspect", self.inspect_body(), hdr)
        self.assertEqual(status, 415)

    def test_form_post_is_415(self) -> None:
        hdr = {"Content-Type": "application/x-www-form-urlencoded"}
        status, _ = self.request("POST", "/clean", self.inspect_body(), hdr)
        self.assertEqual(status, 415)

    def test_missing_content_type_is_415(self) -> None:
        status, _ = self.request("POST", "/inspect", self.inspect_body(), {"Content-Type": None})
        self.assertEqual(status, 415)

    # Host allowlist: a rebound DNS name still arrives with its own Host header.
    def test_loopback_hosts_are_allowed(self) -> None:
        for host in ("localhost", "127.0.0.1", "[::1]"):
            for value in (host, f"{host}:{self.port}"):
                status, _ = self.request("GET", "/health", headers={"Host": value})
                self.assertEqual(status, 200, value)

    def test_foreign_host_is_rejected(self) -> None:
        for value in (f"evil.example:{self.port}", "evil.example", "127.0.0.1.nip.io"):
            status, _ = self.request("GET", "/health", headers={"Host": value})
            self.assertEqual(status, 421, value)

    def test_foreign_host_rejected_on_post(self) -> None:
        hdr = {"Host": f"attacker.test:{self.port}"}
        status, _ = self.request("POST", "/inspect", self.inspect_body(), hdr)
        self.assertEqual(status, 421)

    def test_wrong_port_is_rejected(self) -> None:
        status, _ = self.request("GET", "/health", headers={"Host": "localhost:1"})
        self.assertEqual(status, 421)

    def test_missing_host_is_rejected(self) -> None:
        status, _ = self.request("GET", "/health", headers={"Host": None})
        self.assertEqual(status, 421)

    def test_env_extends_host_allowlist(self) -> None:
        os.environ["WATERMARKS_ALLOWED_HOSTS"] = "wr-core, box.lan:9000"
        try:
            server.configure_allowlists(self.port)
            for value in ("wr-core", f"wr-core:{self.port}", "box.lan:9000"):
                status, _ = self.request("GET", "/health", headers={"Host": value})
                self.assertEqual(status, 200, value)
            status, _ = self.request("GET", "/health", headers={"Host": "box.lan"})
            self.assertEqual(status, 421)
        finally:
            del os.environ["WATERMARKS_ALLOWED_HOSTS"]

    # Origin allowlist.
    def test_foreign_origin_is_403(self) -> None:
        for origin in ("https://evil.example", "null", f"http://evil.example:{self.port}"):
            hdr = {"Origin": origin}
            status, _ = self.request("POST", "/inspect", self.inspect_body(), hdr)
            self.assertEqual(status, 403, origin)
            status, _ = self.request("GET", "/health", headers=hdr)
            self.assertEqual(status, 403, origin)

    def test_loopback_origin_is_allowed(self) -> None:
        hdr = {"Origin": f"http://localhost:{self.port}"}
        status, _ = self.request("POST", "/inspect", self.inspect_body(), hdr)
        self.assertEqual(status, 200)

    def test_env_extends_origin_allowlist(self) -> None:
        os.environ["WATERMARKS_ALLOWED_ORIGINS"] = "https://app.example"
        try:
            server.configure_allowlists(self.port)
            status, _ = self.request("GET", "/health", headers={"Origin": "https://app.example"})
            self.assertEqual(status, 200)
        finally:
            del os.environ["WATERMARKS_ALLOWED_ORIGINS"]

    # Auth.
    def test_missing_key_is_401(self) -> None:
        status, _ = self.request("GET", "/capabilities", auth=False)
        self.assertEqual(status, 401)
        status, _ = self.request("POST", "/inspect", self.inspect_body(), auth=False)
        self.assertEqual(status, 401)

    def test_wrong_key_is_401(self) -> None:
        hdr = {"Authorization": "Bearer wrong"}
        status, _ = self.request("GET", "/capabilities", headers=hdr)
        self.assertEqual(status, 401)

    def test_right_key_is_200(self) -> None:
        status, _ = self.request("GET", "/capabilities")
        self.assertEqual(status, 200)

    def test_health_needs_no_key(self) -> None:
        status, body = self.request("GET", "/health", auth=False)
        self.assertEqual(status, 200)
        self.assertEqual(set(body), {"ok", "version"})

    def test_key_comparison_is_constant_time(self) -> None:
        src = (SCRIPTS / "server.py").read_text()
        self.assertIn("hmac.compare_digest(header.encode()", src)

    # Size and concurrency caps.
    def test_oversized_body_is_413(self) -> None:
        server.MAX_BODY_BYTES = 100
        status, _ = self.request("POST", "/inspect", b"{" + b" " * 200 + b"}")
        self.assertEqual(status, 413)

    def test_declared_oversize_is_413_before_reading(self) -> None:
        server.MAX_BODY_BYTES = 100
        hdr = {"Content-Length": "999999999"}
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.putrequest("POST", "/inspect", skip_host=True)
        for k, v in {
            "Host": f"localhost:{self.port}",
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            **hdr,
        }.items():
            conn.putheader(k, v)
        conn.endheaders()
        self.assertEqual(conn.getresponse().status, 413)
        conn.close()

    def test_missing_length_is_411(self) -> None:
        status, _ = self.request(
            "POST", "/inspect", headers={"Content-Type": "application/json"}
        )
        self.assertEqual(status, 411)

    def test_busy_server_is_503(self) -> None:
        server._SLOTS = threading.BoundedSemaphore(1)
        self.assertTrue(server._SLOTS.acquire(blocking=False))
        try:
            status, _ = self.request("POST", "/inspect", self.inspect_body())
            self.assertEqual(status, 503)
        finally:
            server._SLOTS.release()
        status, _ = self.request("POST", "/inspect", self.inspect_body())
        self.assertEqual(status, 200)

    def test_default_caps(self) -> None:
        self.assertLessEqual(server.MAX_BODY_BYTES, 64 << 20)
        self.assertLessEqual(server.MAX_CONCURRENT, 4)


class Startup(unittest.TestCase):
    def run_server(self, env: dict[str, str]) -> tuple[int | None, str]:
        clean = {k: v for k, v in os.environ.items() if not k.startswith("WATERMARKS_")}
        proc = subprocess.Popen(  # noqa: S603
            [sys.executable, str(SCRIPTS / "server.py"), "--port", "0"],
            env={**clean, **env},
            stderr=subprocess.PIPE,
            text=True,
            cwd=SERVICE.parent,
        )
        lines = []
        try:
            for line in proc.stderr:  # type: ignore[union-attr]
                lines.append(line)
                if "service" in line and "on http://" in line:
                    break
            code = proc.poll()
        finally:
            proc.terminate()
            proc.wait(timeout=10)
            proc.stderr.close()  # type: ignore[union-attr]
        return code, "".join(lines)

    def test_refuses_to_start_without_key(self) -> None:
        code, err = self.run_server({})
        self.assertEqual(code, 2, err)
        self.assertIn("no API key", err)

    def test_allow_no_auth_starts_on_loopback(self) -> None:
        code, err = self.run_server({"WATERMARKS_ALLOW_NO_AUTH": "1"})
        self.assertIsNone(code, err)
        self.assertRegex(err, r"on http://127\.0\.0\.1:\d+")

    def test_key_starts(self) -> None:
        code, err = self.run_server({"WATERMARKS_SERVER_API_KEY": KEY})
        self.assertIsNone(code, err)
        self.assertIn("API key required", err)


class Compose(unittest.TestCase):
    def test_no_key_value_in_compose(self) -> None:
        text = COMPOSE.read_text()
        self.assertNotIn("WATERMARKS_SERVER_API_KEY:-}", text)
        self.assertRegex(text, r"WATERMARKS_SERVER_API_KEY: \$\{WATERMARKS_SERVER_API_KEY:\?")

    def test_port_published_on_loopback_only(self) -> None:
        ports = re.findall(r'^\s*-\s*"([^"]+)"\s*$', COMPOSE.read_text(), re.M)
        published = [p for p in ports if p.count(":") >= 1 and p[0].isdigit()]
        self.assertTrue(published)
        for p in published:
            self.assertTrue(p.startswith("127.0.0.1:"), p)


if __name__ == "__main__":
    unittest.main(verbosity=1)
