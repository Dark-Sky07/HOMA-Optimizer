#!/usr/bin/env python3
"""HOMA web control panel.

A dependency-free, same-origin HTTP server for Linux system telemetry and a
strict allow-list of HOMA optimization commands. It never accepts arbitrary
shell commands from the browser.
"""

from __future__ import annotations

import argparse
import hmac
import ipaddress
import json
import os
import platform
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

VERSION = "5.2.1"
PANEL_DIR = Path(__file__).resolve().parent
STATIC_DIR = PANEL_DIR / "static"
INSTALL_ROOT = PANEL_DIR.parent
SCRIPTS_DIR = INSTALL_ROOT / "scripts"
MAX_BODY_BYTES = 4096
MAX_JOBS = 60
MAX_OUTPUT_CHARS = 300_000
PROCESS_STOP_GRACE = 3.0
REQUEST_TIMEOUT = 20
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

ACTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "suite-update",
        "script": "homa-menu.sh",
        "args": ("--update", "--from-panel"),
        "category": "system",
        "icon": "refresh",
        "mutating": True,
        "restart_on_success": True,
        "timeout": 300,
    },
    {
        "id": "full-optimize",
        "script": "homa-menu.sh",
        "args": ("--one-click", "--yes"),
        "category": "optimize",
        "icon": "sparkles",
        "mutating": True,
        "danger": True,
        "timeout": 1800,
    },
    {
        "id": "network-optimize",
        "script": "homa-boost.sh",
        "args": ("--apply",),
        "category": "optimize",
        "icon": "network",
        "mutating": True,
        "timeout": 180,
    },
    {
        "id": "hardware-optimize",
        "script": "homa-hardware-opt.sh",
        "args": ("--all",),
        "category": "optimize",
        "icon": "cpu",
        "mutating": True,
        "timeout": 300,
    },
    {
        "id": "client-guard",
        "script": "homa-client-opt.sh",
        "args": ("apply",),
        "category": "optimize",
        "icon": "shield",
        "mutating": True,
        "timeout": 120,
    },
    {
        "id": "security-hardening",
        "script": "homa-security.sh",
        "args": ("--apply",),
        "category": "optimize",
        "icon": "lock",
        "mutating": True,
        "timeout": 600,
    },
    {
        "id": "watchdog-enable",
        "script": "homa-watchdog.sh",
        "args": ("enable",),
        "category": "optimize",
        "icon": "pulse",
        "mutating": True,
        "timeout": 120,
    },
    {
        "id": "scheduler-enable",
        "script": "homa-scheduler.sh",
        "args": ("enable",),
        "category": "optimize",
        "icon": "clock",
        "mutating": True,
        "timeout": 120,
    },
    {
        "id": "backup-create",
        "script": "homa-backup.sh",
        "args": ("--backup",),
        "category": "optimize",
        "icon": "archive",
        "mutating": True,
        "timeout": 300,
    },
    {
        "id": "network-rollback",
        "script": "homa-boost.sh",
        "args": ("--rollback",),
        "category": "optimize",
        "icon": "rollback",
        "mutating": True,
        "danger": True,
        "timeout": 120,
    },
    {
        "id": "system-audit",
        "script": "homa-preflight.sh",
        "args": ("--no-net",),
        "category": "diagnostics",
        "icon": "scan",
        "mutating": False,
        "timeout": 90,
    },
    {
        "id": "network-audit",
        "script": "homa-boost.sh",
        "args": ("--dry-run",),
        "category": "diagnostics",
        "icon": "sliders",
        "mutating": False,
        "timeout": 60,
    },
    {
        "id": "port-scan",
        "script": "homa-port-doctor.sh",
        "args": ("--scan",),
        "category": "diagnostics",
        "icon": "radar",
        "mutating": False,
        "timeout": 90,
    },
    {
        "id": "cloudflare-scan",
        "script": "homa-cf-scanner.sh",
        "args": (),
        "category": "diagnostics",
        "icon": "cloud",
        "mutating": False,
        "timeout": 90,
    },
    {
        "id": "speedtest",
        "script": "homa-speedtest.sh",
        "args": (),
        "category": "diagnostics",
        "icon": "gauge",
        "mutating": False,
        "timeout": 180,
    },
    {
        "id": "iran-probe",
        "script": "homa-iran-probe.sh",
        "args": (),
        "category": "diagnostics",
        "icon": "signal",
        "mutating": False,
        "timeout": 240,
    },
)
ACTION_MAP = {action["id"]: action for action in ACTIONS}

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/assets/homa-logo.webp": ("assets/homa-logo.webp", "image/webp"),
    "/assets/homa-favicon.png": ("assets/homa-favicon.png", "image/png"),
    "/assets/pattern.svg": ("assets/pattern.svg", "image/svg+xml"),
    "/assets/vazirmatn-arabic.woff2": ("assets/vazirmatn-arabic.woff2", "font/woff2"),
    "/assets/vazirmatn-latin.woff2": ("assets/vazirmatn-latin.woff2", "font/woff2"),
    "/assets/FONT-LICENSE.txt": ("assets/FONT-LICENSE.txt", "text/plain; charset=utf-8"),
    "/favicon.png": ("assets/homa-favicon.png", "image/png"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_text(path: str | Path, default: str = "") -> str:
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError):
        return default


def read_sysctl(key: str, default: str = "unknown") -> str:
    return read_text(Path("/proc/sys") / Path(*key.split(".")), default)


def pretty_os() -> str:
    for line in read_text("/etc/os-release").splitlines():
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip().strip('"')
    return platform.platform()


def service_states() -> dict[str, str]:
    units = (
        "x-ui",
        "3x-ui",
        "homa-watchdog.service",
        "homa-scheduler.timer",
        "homa-unban.timer",
        "fail2ban",
    )
    result = {unit: "unknown" for unit in units}
    systemctl = shutil.which("systemctl")
    if not systemctl:
        return result
    try:
        proc = subprocess.run(
            [systemctl, "is-active", *units],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        lines = (proc.stdout + "\n" + proc.stderr).splitlines()
        for unit, state in zip(units, lines):
            state = state.strip()
            result[unit] = state if state in {"active", "inactive", "failed", "activating"} else "unknown"
    except (OSError, subprocess.SubprocessError):
        pass
    return result


def service_snapshot() -> list[dict[str, str]]:
    states = service_states()
    panel_state = "not_detected"
    if "active" in (states["x-ui"], states["3x-ui"]):
        panel_state = "active"
    elif Path("/usr/local/x-ui").exists() or Path("/etc/x-ui").exists():
        panel_state = "inactive"

    bbr_active = read_sysctl("net.ipv4.tcp_congestion_control") == "bbr"
    client_active = Path("/opt/homa/client-opt.active").exists()
    return [
        {"id": "panel", "status": panel_state},
        {"id": "network", "status": "active" if bbr_active else "inactive"},
        {"id": "watchdog", "status": states["homa-watchdog.service"]},
        {"id": "scheduler", "status": states["homa-scheduler.timer"]},
        {"id": "security", "status": states["fail2ban"]},
        {"id": "client", "status": "active" if client_active else "inactive"},
    ]


class SystemMetrics:
    """Small /proc-based telemetry collector with rate-aware snapshots."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_cpu = self._cpu_times()
        self._last_net = self._network_bytes()
        self._last_time = time.monotonic()

    @staticmethod
    def _cpu_times() -> tuple[int, int]:
        fields = read_text("/proc/stat").splitlines()
        if not fields:
            return (0, 0)
        values = [int(value) for value in fields[0].split()[1:]]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return (sum(values), idle)

    @staticmethod
    def _network_bytes() -> tuple[int, int]:
        rx = tx = 0
        for line in read_text("/proc/net/dev").splitlines()[2:]:
            if ":" not in line:
                continue
            interface, data = line.split(":", 1)
            if interface.strip() == "lo":
                continue
            values = data.split()
            if len(values) >= 16:
                rx += int(values[0])
                tx += int(values[8])
        return rx, tx

    @staticmethod
    def _memory() -> dict[str, int | float]:
        values: dict[str, int] = {}
        for line in read_text("/proc/meminfo").splitlines():
            key, raw = line.split(":", 1)
            values[key] = int(raw.strip().split()[0]) * 1024
        total = values.get("MemTotal", 0)
        available = values.get("MemAvailable", values.get("MemFree", 0))
        used = max(0, total - available)
        swap_total = values.get("SwapTotal", 0)
        swap_free = values.get("SwapFree", 0)
        return {
            "total": total,
            "used": used,
            "available": available,
            "percent": round((used / total * 100) if total else 0, 1),
            "swap_total": swap_total,
            "swap_used": max(0, swap_total - swap_free),
        }

    @staticmethod
    def _connections() -> int:
        count = 0
        for path in ("/proc/net/tcp", "/proc/net/tcp6"):
            for line in read_text(path).splitlines()[1:]:
                fields = line.split()
                if len(fields) > 3 and fields[3] == "01":
                    count += 1
        return count

    @staticmethod
    def _default_interface() -> str:
        for line in read_text("/proc/net/route").splitlines()[1:]:
            fields = line.split()
            if len(fields) > 1 and fields[1] == "00000000":
                return fields[0]
        return "—"

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            now = time.monotonic()
            elapsed = max(0.001, now - self._last_time)
            cpu = self._cpu_times()
            cpu_delta = max(0, cpu[0] - self._last_cpu[0])
            idle_delta = max(0, cpu[1] - self._last_cpu[1])
            cpu_percent = (1 - idle_delta / cpu_delta) * 100 if cpu_delta else 0
            self._last_cpu = cpu

            net = self._network_bytes()
            rx_rate = max(0, net[0] - self._last_net[0]) / elapsed
            tx_rate = max(0, net[1] - self._last_net[1]) / elapsed
            self._last_net = net
            self._last_time = now

        disk = shutil.disk_usage("/")
        try:
            load = list(os.getloadavg())
        except OSError:
            load = [0.0, 0.0, 0.0]
        memory = self._memory()
        disk_percent = round(disk.used / disk.total * 100, 1) if disk.total else 0
        health = 100
        if cpu_percent > 90:
            health -= 15
        if memory["percent"] > 90:
            health -= 15
        if disk_percent > 90:
            health -= 15

        return {
            "timestamp": utc_now(),
            "host": {
                "name": platform.node(),
                "os": pretty_os(),
                "kernel": platform.release(),
                "architecture": platform.machine(),
            },
            "cpu": {
                "percent": round(max(0, min(100, cpu_percent)), 1),
                "cores": os.cpu_count() or 1,
                "load": [round(value, 2) for value in load],
            },
            "memory": memory,
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk_percent,
            },
            "network": {
                "rx_rate": round(rx_rate, 1),
                "tx_rate": round(tx_rate, 1),
                "rx_total": net[0],
                "tx_total": net[1],
                "interface": self._default_interface(),
            },
            "connections": self._connections(),
            "uptime": float(read_text("/proc/uptime", "0").split()[0]),
            "services": service_snapshot(),
            "health": {
                "score": health,
                "status": "excellent" if health == 100 else "attention",
            },
            "optimization": {
                "congestion_control": read_sysctl("net.ipv4.tcp_congestion_control"),
                "qdisc": read_sysctl("net.core.default_qdisc"),
            },
        }


class JobManager:
    def __init__(self, read_only: bool = False) -> None:
        self.read_only = read_only
        self._jobs: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def public(self, job: dict[str, Any], output: bool = False) -> dict[str, Any]:
        result = {
            key: value
            for key, value in job.items()
            if not key.startswith("_") and key not in {"lines", "output_chars"}
        }
        if output:
            result["output"] = "".join(job["lines"])
            result["truncated"] = bool(job.get("truncated", False))
        return result

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return [self.public(job) for job in reversed(self._jobs.values())]

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return self.public(job, output=True) if job else None

    def active(self) -> dict[str, Any] | None:
        with self._lock:
            for job in reversed(self._jobs.values()):
                if job["status"] in {"queued", "running"}:
                    return self.public(job)
        return None

    def start(self, action_id: str) -> tuple[dict[str, Any] | None, str | None]:
        action = ACTION_MAP[action_id]
        if action["mutating"] and self.read_only:
            return None, "read_only"
        if action["mutating"] and hasattr(os, "geteuid") and os.geteuid() != 0:
            return None, "root_required"
        script = SCRIPTS_DIR / action["script"]
        if not script.is_file():
            return None, "script_missing"

        with self._lock:
            if any(job["status"] in {"queued", "running"} for job in self._jobs.values()):
                return None, "busy"
            job_id = secrets.token_hex(8)
            job = {
                "id": job_id,
                "action": action_id,
                "status": "queued",
                "created_at": utc_now(),
                "started_at": None,
                "finished_at": None,
                "exit_code": None,
                "lines": [],
                "output_chars": 0,
                "truncated": False,
                "_timed_out": False,
            }
            if action.get("restart_on_success"):
                job["restart_scheduled"] = False
            self._jobs[job_id] = job
            while len(self._jobs) > MAX_JOBS:
                self._jobs.popitem(last=False)

        thread = threading.Thread(target=self._run, args=(job_id, action, script), daemon=True)
        thread.start()
        return self.public(job), None

    def _append(self, job: dict[str, Any], text: str) -> None:
        text = ANSI_RE.sub("", text).replace("\x00", "")
        with self._lock:
            job["lines"].append(text)
            job["output_chars"] += len(text)
            while job["output_chars"] > MAX_OUTPUT_CHARS and job["lines"]:
                removed = job["lines"].pop(0)
                job["output_chars"] -= len(removed)
                job["truncated"] = True

    def _schedule_panel_restart(self, job: dict[str, Any]) -> None:
        """Restart only the systemd-managed panel after a successful update."""
        if not os.environ.get("INVOCATION_ID"):
            self._append(job, "\nHOMA · Update installed. Restart homa-panel to load the new backend.\n")
            return
        systemctl = shutil.which("systemctl")
        if not systemctl:
            self._append(job, "\nHOMA · Update installed. Restart homa-panel to load the new backend.\n")
            return
        try:
            active = subprocess.run(
                [systemctl, "is-active", "--quiet", "homa-panel.service"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
                check=False,
            ).returncode == 0
        except (OSError, subprocess.SubprocessError):
            active = False
        if not active:
            self._append(job, "\nHOMA · Update installed. Restart homa-panel to load the new backend.\n")
            return

        with self._lock:
            job["restart_scheduled"] = True
        self._append(job, "\nHOMA · Update installed. Panel will restart in 6 seconds and reconnect automatically.\n")

        def restart_panel() -> None:
            try:
                subprocess.run(
                    [systemctl, "restart", "homa-panel.service"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError):
                pass

        restart_timer = threading.Timer(6, restart_panel)
        restart_timer.daemon = True
        restart_timer.start()

    def _run(self, job_id: str, action: dict[str, Any], script: Path) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job["status"] = "running"
            job["started_at"] = utc_now()
        self._append(job, f"HOMA · Starting {action['id']}\n")
        env = os.environ.copy()
        env.update({"TERM": "dumb", "HOMA_NONINTERACTIVE": "1"})
        env["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:" + env.get("PATH", "")
        process: subprocess.Popen[str] | None = None
        timer: threading.Timer | None = None
        kill_timer: threading.Timer | None = None
        finished = threading.Event()
        try:
            process = subprocess.Popen(
                ["/bin/bash", str(script), *action["args"]],
                cwd=str(SCRIPTS_DIR),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
                bufsize=1,
                start_new_session=True,
            )

            def stop_on_timeout() -> None:
                nonlocal kill_timer
                with self._lock:
                    if finished.is_set() or job["status"] != "running":
                        return
                    job["_timed_out"] = True
                self._append(job, "\nHOMA · Operation time limit reached; stopping safely.\n")
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except (ProcessLookupError, PermissionError):
                    pass

                def force_stop() -> None:
                    if finished.is_set():
                        return
                    try:
                        # A child can ignore SIGTERM or inherit the output pipe
                        # after its parent exits. Always escalate the whole group.
                        os.killpg(process.pid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass

                kill_timer = threading.Timer(PROCESS_STOP_GRACE, force_stop)
                kill_timer.daemon = True
                kill_timer.start()

            timer = threading.Timer(action["timeout"], stop_on_timeout)
            timer.daemon = True
            timer.start()
            if process.stdout is None:
                raise RuntimeError("Unable to capture operation output")
            for line in process.stdout:
                self._append(job, line)
            exit_code = process.wait()
            with self._lock:
                finished.set()
                timed_out = bool(job["_timed_out"])
            if exit_code == 0 and not timed_out and action.get("restart_on_success"):
                self._schedule_panel_restart(job)
            with self._lock:
                job["exit_code"] = -signal.SIGTERM if timed_out and exit_code == 0 else exit_code
                job["status"] = "succeeded" if exit_code == 0 and not timed_out else "failed"
        except Exception as exc:  # The API must preserve a useful audit trail.
            self._append(job, f"HOMA · Unable to execute operation: {exc}\n")
            with self._lock:
                job["status"] = "failed"
                job["exit_code"] = -1
        finally:
            finished.set()
            if timer:
                timer.cancel()
            if kill_timer:
                kill_timer.cancel()
            if process and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    process.wait(timeout=PROCESS_STOP_GRACE)
                except subprocess.SubprocessError:
                    pass
            if process and process.stdout:
                process.stdout.close()
            self._append(job, "\nHOMA · Operation finished.\n")
            with self._lock:
                job["finished_at"] = utc_now()


class HomaHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 64

    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], config: argparse.Namespace):
        super().__init__(address, handler)
        self.config = config
        self.metrics = SystemMetrics()
        self.jobs = JobManager(config.read_only)


class HomaHandler(BaseHTTPRequestHandler):
    server: HomaHTTPServer
    protocol_version = "HTTP/1.1"

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(REQUEST_TIMEOUT)

    def log_message(self, message: str, *args: Any) -> None:
        sys.stderr.write(f"[homa-panel] {self.address_string()} {message % args}\n")

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; "
            "base-uri 'none'; form-action 'self'",
        )
        super().end_headers()

    def _authorized(self) -> bool:
        token = self.server.config.token
        if not token:
            return True
        supplied = self.headers.get("X-HOMA-Token", "")
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            supplied = auth[7:]
        return hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8"))

    def _valid_host(self) -> bool:
        """Prevent DNS rebinding into token-less local or explicit demo panels."""
        host_headers = self.headers.get_all("Host") or []
        if len(host_headers) != 1:
            return False
        raw_host = host_headers[0].strip()
        if not raw_host or any(char.isspace() for char in raw_host) or any(char in raw_host for char in "/\\@"):
            return False
        try:
            parsed = urlsplit(f"http://{raw_host}")
            hostname = parsed.hostname
            parsed.port  # Validate the port even though the allowlist only uses names.
        except ValueError:
            return False
        if not hostname or parsed.username is not None or parsed.path or parsed.query or parsed.fragment:
            return False
        hostname = hostname.lower().rstrip(".")
        if not non_loopback(hostname):
            return True

        allowed_hosts = getattr(self.server.config, "allowed_hosts", [])
        for raw_pattern in allowed_hosts:
            pattern = raw_pattern.strip().lower().rstrip(".")
            if not pattern:
                continue
            if pattern.startswith(("*.", ".")):
                suffix = pattern[1:] if pattern.startswith("*.") else pattern
                if hostname.endswith(suffix) and len(hostname) > len(suffix):
                    return True
            elif hostname == pattern:
                return True

        # A strong token blocks rebinding on its own. Without a token, only
        # loopback names or an explicit public-host allowlist are acceptable.
        return bool(self.server.config.token) and not allowed_hosts

    def _has_unexpected_body(self) -> bool:
        lengths = self.headers.get_all("Content-Length") or []
        return bool(
            self.headers.get("Transfer-Encoding") is not None
            or len(lengths) > 1
            or (lengths and lengths[0].strip() != "0")
        )

    def _send_json(self, payload: Any, status: int = 200, body: bool = True) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(encoded)

    def _error(self, status: int, code: str, message: str) -> None:
        # Error responses close the connection so an unread rejected request body
        # can never be interpreted as a subsequent request on the same socket.
        self.close_connection = True
        self._send_json({"error": {"code": code, "message": message}}, status)

    def _api_get(self, path: str, body: bool = True) -> None:
        if path == "/api/session":
            self._send_json(
                {
                    "version": VERSION,
                    "auth_required": bool(self.server.config.token),
                    "read_only": self.server.config.read_only,
                },
                body=body,
            )
            return
        if not self._authorized():
            self._error(HTTPStatus.UNAUTHORIZED, "unauthorized", "A valid HOMA access token is required.")
            return
        if path == "/api/overview":
            self._send_json(
                {
                    "version": VERSION,
                    "read_only": self.server.config.read_only,
                    "root": not hasattr(os, "geteuid") or os.geteuid() == 0,
                    "metrics": self.server.metrics.snapshot(),
                    "active_job": self.server.jobs.active(),
                },
                body=body,
            )
        elif path == "/api/actions":
            actions = []
            for action in ACTIONS:
                actions.append(
                    {
                        key: value
                        for key, value in action.items()
                        if key not in {"script", "args", "timeout"}
                    }
                )
            self._send_json({"actions": actions, "active_job": self.server.jobs.active()}, body=body)
        elif path == "/api/jobs":
            self._send_json({"jobs": self.server.jobs.list()}, body=body)
        elif path.startswith("/api/jobs/"):
            job = self.server.jobs.get(path.rsplit("/", 1)[-1])
            if job:
                self._send_json({"job": job}, body=body)
            else:
                self._error(HTTPStatus.NOT_FOUND, "job_not_found", "Operation not found.")
        else:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "API endpoint not found.")

    def _serve_static(self, path: str, body: bool = True) -> None:
        clean_path = urlsplit(path).path
        entry = STATIC_FILES.get(clean_path)
        if not entry:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "Resource not found.")
            return
        filename, content_type = entry
        target = STATIC_DIR / filename
        try:
            content = target.read_bytes()
        except OSError:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "Resource not found.")
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        # Code and branding assets revalidate on every load so a panel update
        # never leaves an old interface running against a new backend.
        cache_control = "public, max-age=86400" if filename.endswith(".woff2") else "no-cache"
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        if body:
            self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if not self._valid_host():
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "The request Host is not allowed.")
            return
        if self._has_unexpected_body():
            self._error(HTTPStatus.BAD_REQUEST, "invalid_body", "GET requests must not include a body.")
            return
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            self._api_get(path)
        else:
            self._serve_static(path)

    def do_HEAD(self) -> None:  # noqa: N802
        if not self._valid_host():
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "The request Host is not allowed.")
            return
        if self._has_unexpected_body():
            self._error(HTTPStatus.BAD_REQUEST, "invalid_body", "HEAD requests must not include a body.")
            return
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            self._api_get(path, body=False)
        else:
            self._serve_static(path, body=False)

    def do_POST(self) -> None:  # noqa: N802
        if not self._valid_host():
            self._error(HTTPStatus.FORBIDDEN, "invalid_host", "The request Host is not allowed.")
            return
        path = urlsplit(self.path).path
        if not path.startswith("/api/actions/"):
            self._error(HTTPStatus.NOT_FOUND, "not_found", "API endpoint not found.")
            return
        if not self._authorized():
            self._error(HTTPStatus.UNAUTHORIZED, "unauthorized", "A valid HOMA access token is required.")
            return
        if self.headers.get("X-HOMA-Request") != "dashboard":
            self._error(HTTPStatus.FORBIDDEN, "invalid_request", "Same-origin dashboard request required.")
            return
        origin = self.headers.get("Origin")
        if origin and urlsplit(origin).netloc != self.headers.get("Host"):
            self._error(HTTPStatus.FORBIDDEN, "invalid_origin", "Cross-origin requests are not allowed.")
            return
        action_id = path.rsplit("/", 1)[-1]
        if action_id not in ACTION_MAP:
            self._error(HTTPStatus.NOT_FOUND, "action_not_found", "Unknown operation.")
            return
        length_headers = self.headers.get_all("Content-Length") or []
        if self.headers.get("Transfer-Encoding") is not None or len(length_headers) != 1:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_body", "A single Content-Length header is required.")
            return
        try:
            length = int(length_headers[0])
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_body", "A small JSON request body is required.")
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, "invalid_json", "Invalid JSON request body.")
            return
        if not isinstance(payload, dict):
            self._error(HTTPStatus.BAD_REQUEST, "invalid_json", "The JSON body must be an object.")
            return
        if ACTION_MAP[action_id]["mutating"] and payload.get("confirm") is not True:
            self._error(HTTPStatus.BAD_REQUEST, "confirmation_required", "Explicit confirmation is required.")
            return
        job, error = self.server.jobs.start(action_id)
        if error:
            status_messages = {
                "read_only": (HTTPStatus.FORBIDDEN, "This panel is running in read-only mode."),
                "root_required": (HTTPStatus.FORBIDDEN, "Run HOMA panel as root to apply optimizations."),
                "script_missing": (HTTPStatus.SERVICE_UNAVAILABLE, "The HOMA module is not installed."),
                "busy": (HTTPStatus.CONFLICT, "Another HOMA operation is already running."),
            }
            status, message = status_messages[error]
            self._error(status, error, message)
            return
        self._send_json({"job": job}, HTTPStatus.ACCEPTED)


def non_loopback(host: str) -> bool:
    if host.lower() == "localhost":
        return False
    try:
        return not ipaddress.ip_address(host).is_loopback
    except ValueError:
        return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HOMA graphical VPS control panel")
    parser.add_argument("--host", default=os.environ.get("HOMA_PANEL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("HOMA_PANEL_PORT", "8787")))
    parser.add_argument("--token", default=os.environ.get("HOMA_PANEL_TOKEN", ""))
    parser.add_argument(
        "--read-only",
        action="store_true",
        default=os.environ.get("HOMA_PANEL_READ_ONLY", "").lower() in {"1", "true", "yes"},
        help="Disable every operation that changes the server",
    )
    parser.add_argument(
        "--allow-public-read-only",
        action="store_true",
        default=os.environ.get("HOMA_PANEL_ALLOW_PUBLIC_READ_ONLY", "").lower() in {"1", "true", "yes"},
        help="Explicitly permit a token-less public demo; requires --read-only and --allowed-host",
    )
    parser.add_argument(
        "--allowed-host",
        dest="allowed_hosts",
        action="append",
        default=[item.strip() for item in os.environ.get("HOMA_PANEL_ALLOWED_HOSTS", "").split(",") if item.strip()],
        metavar="NAME",
        help="Allowed public Host header; repeat as needed (also HOMA_PANEL_ALLOWED_HOSTS)",
    )
    parser.add_argument("--version", action="version", version=f"HOMA Panel {VERSION}")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    for pattern in args.allowed_hosts:
        if pattern == "*" or not pattern or any(char.isspace() or char in "/\\@" for char in pattern):
            parser.error("Allowed hosts must be exact names or suffixes such as .example.com")
    if non_loopback(args.host) and not args.token:
        if not args.read_only or not args.allow_public_read_only:
            parser.error("A token is required on non-loopback interfaces; public demos require explicit read-only opt-in")
        if not args.allowed_hosts:
            parser.error("A token-less public demo requires at least one --allowed-host")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not STATIC_DIR.is_dir():
        print(f"HOMA static assets not found: {STATIC_DIR}", file=sys.stderr)
        return 1
    try:
        server = HomaHTTPServer((args.host, args.port), HomaHandler, args)
    except OSError as exc:
        print(f"Unable to start HOMA panel: {exc}", file=sys.stderr)
        return 1
    mode = "read-only" if args.read_only else "control"
    if non_loopback(args.host) and not args.token:
        print("WARNING: token-less public read-only demo enabled; never use this mode for production.", file=sys.stderr)
    print(f"HOMA Panel {VERSION} · http://{args.host}:{args.port} · {mode} mode", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
