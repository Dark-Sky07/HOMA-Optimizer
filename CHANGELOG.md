# Changelog

All HOMA changes are released with a new version, a changelog entry, and a dedicated GitHub Release. This project follows [Semantic Versioning](https://semver.org/).

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

[5.2.0]: https://github.com/Dark-Sky07/HOMA-Optimizer/releases/tag/v5.2.0
