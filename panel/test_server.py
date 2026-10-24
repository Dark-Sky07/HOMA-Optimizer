#!/usr/bin/env python3
"""Dependency-free tests for the HOMA panel backend."""

from __future__ import annotations

import argparse
import contextlib
import http.client
import io
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import server


class ActionContractTests(unittest.TestCase):
    def test_action_ids_are_unique_and_modules_exist(self) -> None:
        ids = [action["id"] for action in server.ACTIONS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(server.ACTION_MAP))
        for action in server.ACTIONS:
            with self.subTest(action=action["id"]):
                self.assertTrue(action["script"].startswith("homa-"))
                self.assertTrue((server.SCRIPTS_DIR / action["script"]).is_file())
                self.assertIsInstance(action["args"], tuple)
                self.assertGreater(action["timeout"], 0)

    def test_full_optimization_is_explicitly_noninteractive(self) -> None:
        action = server.ACTION_MAP["full-optimize"]
        self.assertEqual(action["args"], ("--one-click", "--yes"))
        self.assertTrue(action["mutating"])

    def test_suite_update_is_official_noninteractive_and_restarts(self) -> None:
        action = server.ACTION_MAP["suite-update"]
        self.assertEqual(action["script"], "homa-menu.sh")
        self.assertEqual(action["args"], ("--update", "--from-panel"))
        self.assertTrue(action["mutating"])
        self.assertTrue(action["restart_on_success"])

    def test_every_static_asset_exists(self) -> None:
        for filename, _ in server.STATIC_FILES.values():
            with self.subTest(asset=filename):
                self.assertTrue((server.STATIC_DIR / filename).is_file())


class ConfigurationTests(unittest.TestCase):
    def test_public_control_mode_requires_token(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            server.parse_args(["--host", "0.0.0.0"])

    def test_public_read_only_mode_requires_explicit_opt_in(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            server.parse_args(["--host", "0.0.0.0", "--port", "8787", "--read-only"])

    def test_public_demo_requires_host_allowlist(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            server.parse_args(["--host", "0.0.0.0", "--read-only", "--allow-public-read-only"])

    def test_explicit_public_read_only_demo_is_allowed(self) -> None:
        args = server.parse_args([
            "--host", "0.0.0.0",
            "--port", "8787",
            "--read-only",
            "--allow-public-read-only",
            "--allowed-host", "demo.example.com",
        ])
        self.assertTrue(args.read_only)
        self.assertEqual(args.port, 8787)
        self.assertEqual(args.allowed_hosts, ["demo.example.com"])

    def test_loopback_detection(self) -> None:
        self.assertFalse(server.non_loopback("127.0.0.1"))
        self.assertFalse(server.non_loopback("localhost"))
        self.assertTrue(server.non_loopback("0.0.0.0"))
        self.assertTrue(server.non_loopback("example.com"))


class MetricsTests(unittest.TestCase):
    def test_snapshot_has_real_telemetry_schema(self) -> None:
        collector = server.SystemMetrics()
        time.sleep(0.02)
        with mock.patch.object(server, "service_snapshot", return_value=[]):
            snapshot = collector.snapshot()
        self.assertGreater(snapshot["cpu"]["cores"], 0)
        self.assertGreaterEqual(snapshot["cpu"]["percent"], 0)
        self.assertLessEqual(snapshot["cpu"]["percent"], 100)
        self.assertGreater(snapshot["memory"]["total"], 0)
        self.assertGreater(snapshot["disk"]["total"], 0)
        self.assertGreaterEqual(snapshot["network"]["rx_rate"], 0)
        self.assertGreaterEqual(snapshot["network"]["tx_rate"], 0)
        self.assertGreaterEqual(snapshot["uptime"], 0)
        self.assertIn(snapshot["health"]["score"], range(80, 101))


class JobManagerTests(unittest.TestCase):
    def test_read_only_mode_blocks_mutating_action(self) -> None:
        manager = server.JobManager(read_only=True)
        job, error = manager.start("network-optimize")
        self.assertIsNone(job)
        self.assertEqual(error, "read_only")

    def test_mutating_action_requires_root(self) -> None:
        manager = server.JobManager(read_only=False)
        with mock.patch.object(server.os, "geteuid", return_value=1000):
            job, error = manager.start("network-optimize")
        self.assertIsNone(job)
        self.assertEqual(error, "root_required")

    def test_safe_job_streams_output_and_finishes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "homa-boost.sh"
            script.write_text("#!/usr/bin/env bash\nprintf '\\033[1;33msafe audit\\033[0m\\n'\n")
            manager = server.JobManager(read_only=True)
            with mock.patch.object(server, "SCRIPTS_DIR", Path(directory)):
                job, error = manager.start("network-audit")
                self.assertIsNone(error)
                assert job is not None
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    result = manager.get(job["id"])
                    assert result is not None
                    if result["status"] not in {"queued", "running"}:
                        break
                    time.sleep(0.02)
                result = manager.get(job["id"])
                assert result is not None
                self.assertEqual(result["status"], "succeeded")
                self.assertEqual(result["exit_code"], 0)
                self.assertIn("safe audit", result["output"])
                self.assertNotIn("\x1b", result["output"])

    def test_timeout_escalates_when_process_group_ignores_sigterm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "homa-boost.sh"
            script.write_text("#!/usr/bin/env bash\ntrap '' TERM\nprintf 'ready\\n'\nsleep 30\n")
            manager = server.JobManager(read_only=True)
            with mock.patch.object(server, "SCRIPTS_DIR", Path(directory)), \
                 mock.patch.object(server, "PROCESS_STOP_GRACE", 0.1), \
                 mock.patch.dict(server.ACTION_MAP["network-audit"], {"timeout": 0.1}):
                job, error = manager.start("network-audit")
                self.assertIsNone(error)
                self.assertIsNotNone(job)
                deadline = time.monotonic() + 4
                while time.monotonic() < deadline:
                    result = manager.get(job["id"])
                    self.assertIsNotNone(result)
                    if result["status"] not in {"queued", "running"}:
                        break
                    time.sleep(0.02)
                result = manager.get(job["id"])
                self.assertEqual(result["status"], "failed")
                self.assertNotEqual(result["exit_code"], 0)
                self.assertIn("time limit reached", result["output"])
                self.assertIsNone(manager.active())

    def test_successful_update_schedules_controlled_panel_restart(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "homa-menu.sh"
            script.write_text("#!/usr/bin/env bash\nprintf 'update installed\\n'\n")
            manager = server.JobManager(read_only=False)
            with mock.patch.object(server, "SCRIPTS_DIR", Path(directory)), \
                 mock.patch.object(server.os, "geteuid", return_value=0), \
                 mock.patch.object(manager, "_schedule_panel_restart") as restart:
                job, error = manager.start("suite-update")
                self.assertIsNone(error)
                assert job is not None
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    result = manager.get(job["id"])
                    assert result is not None
                    if result["status"] not in {"queued", "running"}:
                        break
                    time.sleep(0.02)
                self.assertEqual(result["status"], "succeeded")
                restart.assert_called_once()

    def test_manual_panel_does_not_restart_a_separate_systemd_service(self) -> None:
        manager = server.JobManager(read_only=False)
        job = {"lines": [], "output_chars": 0, "truncated": False, "restart_scheduled": False}
        with mock.patch.dict(server.os.environ, {}, clear=True), \
             mock.patch.object(server.shutil, "which") as which:
            manager._schedule_panel_restart(job)
        self.assertFalse(job["restart_scheduled"])
        which.assert_not_called()
        self.assertIn("Restart homa-panel", "".join(job["lines"]))

    def test_systemd_restart_is_delayed_and_noninteractive(self) -> None:
        manager = server.JobManager(read_only=False)
        job = {"lines": [], "output_chars": 0, "truncated": False, "restart_scheduled": False}
        timer = mock.Mock()
        with mock.patch.dict(server.os.environ, {"INVOCATION_ID": "panel-test"}), \
             mock.patch.object(server.shutil, "which", return_value="/usr/bin/systemctl"), \
             mock.patch.object(server.subprocess, "run", return_value=mock.Mock(returncode=0)) as run, \
             mock.patch.object(server.threading, "Timer", return_value=timer) as timer_class:
            manager._schedule_panel_restart(job)
        self.assertTrue(job["restart_scheduled"])
        self.assertEqual(run.call_args.args[0], ["/usr/bin/systemctl", "is-active", "--quiet", "homa-panel.service"])
        self.assertEqual(timer_class.call_args.args[0], 6)
        self.assertTrue(timer.daemon)
        timer.start.assert_called_once_with()

    def test_only_one_job_can_run_at_a_time(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "homa-boost.sh"
            script.write_text("#!/usr/bin/env bash\nsleep 0.3\n")
            manager = server.JobManager(read_only=True)
            with mock.patch.object(server, "SCRIPTS_DIR", Path(directory)):
                first, error = manager.start("network-audit")
                self.assertIsNone(error)
                assert first is not None
                second, error = manager.start("network-audit")
                self.assertIsNone(second)
                self.assertEqual(error, "busy")
                deadline = time.monotonic() + 3
                while manager.active() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertIsNone(manager.active())


class HttpSecurityTests(unittest.TestCase):
    def make_server(self, **overrides) -> server.HomaHTTPServer:
        config = argparse.Namespace(
            host="127.0.0.1",
            port=0,
            token="",
            read_only=True,
            allow_public_read_only=False,
            allowed_hosts=[],
        )
        for key, value in overrides.items():
            setattr(config, key, value)
        httpd = server.HomaHTTPServer(("127.0.0.1", 0), server.HomaHandler, config)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        def cleanup() -> None:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=2)

        self.addCleanup(cleanup)
        return httpd

    def request(self, httpd: server.HomaHTTPServer, method: str, path: str, **kwargs):
        connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
        try:
            connection.request(method, path, **kwargs)
            response = connection.getresponse()
            payload = response.read()
            return response, payload
        finally:
            connection.close()

    def test_tokenless_loopback_rejects_dns_rebinding_host(self) -> None:
        httpd = self.make_server()
        response, payload = self.request(httpd, "GET", "/api/session", headers={"Host": "attacker.example"})
        self.assertEqual(response.status, 403)
        self.assertEqual(json.loads(payload)["error"]["code"], "invalid_host")

    def test_tokenless_loopback_accepts_local_host(self) -> None:
        httpd = self.make_server()
        response, payload = self.request(httpd, "GET", "/api/session")
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(payload)["version"], server.VERSION)

    def test_public_demo_allows_only_configured_public_host(self) -> None:
        httpd = self.make_server(host="0.0.0.0", allowed_hosts=["demo.example.com"], allow_public_read_only=True)
        response, _ = self.request(httpd, "GET", "/api/session", headers={"Host": "demo.example.com"})
        self.assertEqual(response.status, 200)
        response, _ = self.request(httpd, "GET", "/api/session", headers={"Host": "other.example.com"})
        self.assertEqual(response.status, 403)

    def test_chunked_action_body_is_rejected_before_execution(self) -> None:
        httpd = self.make_server()
        httpd.jobs.start = mock.Mock(side_effect=AssertionError("operation must not run"))
        response, payload = self.request(
            httpd,
            "POST",
            "/api/actions/network-audit",
            body=b"0\r\n\r\n",
            headers={"Transfer-Encoding": "chunked", "X-HOMA-Request": "dashboard"},
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(json.loads(payload)["error"]["code"], "invalid_body")
        httpd.jobs.start.assert_not_called()

    def test_get_with_unexpected_body_is_rejected(self) -> None:
        httpd = self.make_server()
        response, payload = self.request(httpd, "GET", "/api/session", body=b"bad")
        self.assertEqual(response.status, 400)
        self.assertEqual(json.loads(payload)["error"]["code"], "invalid_body")


if __name__ == "__main__":
    unittest.main()
