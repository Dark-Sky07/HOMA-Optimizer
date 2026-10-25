# Changelog

All HOMA changes are released with a new version, a changelog entry, and a dedicated GitHub Release. This project follows [Semantic Versioning](https://semver.org/).

## [5.2.2] - 2026-10-25

### Changed

- Change the default panel port from `8787` to `8788` to avoid conflicting with the Simorgh project. New installations write `HOMA_PANEL_PORT=8788` while existing configuration remains preserved during updates.
- Read the effective configured port in terminal-menu and installer connection instructions instead of displaying a hardcoded URL, including SSH tunnel commands for custom ports.
- Document the one-time port migration required for existing installations that still use the legacy default.

### Tests

- Add backend coverage for the new default and environment-based port overrides; rerun backend, installer, menu, syntax, ShellCheck, and browser preview checks on port `8788`.

## [5.2.1] - 2026-10-25

### Security

- Require a token on every non-loopback panel by default. Token-less public read-only demos now require explicit opt-in plus a public Host allowlist.
- Validate Host headers to block DNS rebinding into local panels; reject unexpected GET/HEAD bodies, chunked action requests, and duplicate/missing Content-Length framing, and bound connection reads with a timeout.
- Create backup directories with mode `700` and backup archives with mode `600`, including tightening legacy HOMA archives. Validate restore selections before arithmetic evaluation, validate archives before extraction, and stop the panel during database replacement.
- Parse Telegram configuration without `source`, strictly validate credentials, save updates atomically with mode `600`, remove the predictable `/tmp` response file, hide the configured token, and keep the bot token out of curl's process arguments.
- Allocate preflight reports with `mktemp` and mode `600`; restrict nightly temporary-file cleanup to HOMA-owned report files instead of arbitrary `/tmp` content.
- Preserve operator firewall backups atomically with mode `600`, and stop the Instagram optimizer from deleting unrelated generic UDP/443 rules.

### Fixed

- Escalate timed-out jobs from SIGTERM to SIGKILL across the whole process group so ignored signals or inherited output pipes cannot leave a job running forever.
- Propagate failed modules through one-click optimization and report service activation, package installation, sysctl, firewall, and backup failures instead of unconditional success.
- Use a fresh candidate directory for every installer/updater download attempt, validate package completeness, validate release tags, and replace static assets as a set so removed files cannot linger after an update. Restore the previous static set if either rename fails.
- Harden swap replacement against failed `swapoff`, allocation, formatting, activation, and persistence steps; never unlink an active swapfile after a failed deactivation. Interpret custom sizes as decimal and remove only the exact swap entry from `fstab`.
- Route `homa-dns.sh rollback` to the actual rollback function and enforce root checks for DNS, scheduler, watchdog, and unban mutations. Propagate DNS restore/restart failures and remove HOMA resolver configuration when applying the no-backup fallback.
- Apply the documented 20:00–01:30 Tehran peak window with 15-minute scheduler checks, preserve complete IPv4/IPv6 peers in the live monitor, and accept leading-zero decimal backup selections.
- Preserve unrelated Docker daemon settings with an atomic JSON merge and refuse to overwrite invalid existing JSON.
- Correct SNI failure detection, Cloudflare empty-result handling, speedtest byte accounting and fallback behavior, and millisecond timing without a Python dependency.
- Fix the terminal dashboard's Peak Scheduler spacing and expose the exact panel version on the main page.

### Tests

- Expanded the dependency-free backend suite from 15 to 23 tests, including real HTTP Host/framing checks and a process-group timeout regression.
- Re-ran ShellCheck, Bandit, Bash/Python/JavaScript syntax checks, isolated backup/Telegram/Docker/one-click regression harnesses, and desktop/mobile browser checks.
- Passed 14 additional focused regression groups covering scheduler boundaries, IPv6 monitoring, swap and DNS rollback, firewall failures, staged updates, and isolated installer asset rollback.

## [5.2.0] - 2026-10-25

### Added

- Complete HOMA rebrand across scripts, commands, services, paths, documentation, and user-facing surfaces.
- Bilingual Persian/English graphical command center with live CPU, memory, disk, network, service, and health telemetry.
- Controlled execution of optimization and read-only diagnostic modules with live operation logs.
- In-panel suite updates through the fixed `homa-menu.sh --update --from-panel` action and the `homa --update` terminal command.
- Delayed systemd panel restart and automatic browser reconnection after a successful update.
- Homa-inspired flight-route map, animated network paths, feather-style health gauge, and responsive restart experience.
- Referenced HOMA OPTIMIZER emblem across the dashboard, sidebar, sign-in screen, updater, chart, restart screen, README, and favicon.
- Dependency-free backend contract tests and desktop/mobile browser validation.

### Changed

- Optimized the user-supplied 2048×2048 emblem into a transparent 768×768 WebP and a 96×96 PNG favicon without replacing its artwork.
- Replaced the previous generated emblem and hero artwork with the referenced HOMA logo.
- Static code and branding assets now revalidate on every load so updated panels do not retain stale interfaces.
- Installers preserve panel credentials while suppressing access-token output during noninteractive updates.

### Security

- Mutating actions remain root-only and are blocked in read-only mode.
- Panel updates accept no browser-supplied URL, shell command, or arbitrary argument; downloads are restricted to the official HOMA repository.
- Same-origin request checks, explicit confirmation, constant-time token comparison, and restrictive content-security headers remain enforced.

[5.2.2]: https://github.com/Dark-Sky07/HOMA-Optimizer/releases/tag/v5.2.2
[5.2.1]: https://github.com/Dark-Sky07/HOMA-Optimizer/releases/tag/v5.2.1
[5.2.0]: https://github.com/Dark-Sky07/HOMA-Optimizer/releases/tag/v5.2.0
