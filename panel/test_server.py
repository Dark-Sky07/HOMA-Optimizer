#!/usr/bin/env python3
"""Dependency-free tests for the HOMA panel backend."""

from __future__ import annotations

import contextlib
import io
import tempfile
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

    def test_every_static_asset_exists(self) -> None:
        for filename, _ in server.STATIC_FILES.values():
            with self.subTest(asset=filename):
                self.assertTrue((server.STATIC_DIR / filename).is_file())


class ConfigurationTests(unittest.TestCase):
    def test_public_control_mode_requires_token(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            server.parse_args(["--host", "0.0.0.0"])

    def test_public_read_only_mode_is_allowed(self) -> None:
        args = server.parse_args(["--host", "0.0.0.0", "--port", "8787", "--read-only"])
        self.assertTrue(args.read_only)
        self.assertEqual(args.port, 8787)

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


if __name__ == "__main__":
    unittest.main()
