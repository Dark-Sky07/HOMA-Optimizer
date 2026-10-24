#!/usr/bin/env bash
#===============================================================================
#  HOMA — VPS Optimizer & Graphical Command Center
#  Installs all modules in /opt/homa and registers the homa / homa-panel commands.
#
#  Options:
#    --no-launch   Do not open the interactive terminal menu after installation
#    --no-panel    Install the web panel but do not start its systemd service
#===============================================================================

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
set -euo pipefail

INSTALL_DIR="/opt/homa"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
PANEL_DIR="${INSTALL_DIR}/panel"
BIN_LINK="/usr/local/bin/homa"
PANEL_BIN_LINK="/usr/local/bin/homa-panel"
CONFIG_DIR="/etc/homa"
PANEL_ENV="${CONFIG_DIR}/panel.env"
REPO_NAME="Dark-Sky07/HOMA-Optimizer"
AUTO_LAUNCH=1
START_PANEL=1
TMP_DL=""

for arg in "$@"; do
  case "$arg" in
    --no-launch) AUTO_LAUNCH=0 ;;
    --no-panel) START_PANEL=0 ;;
    *) printf "Unknown installer option: %s\n" "$arg"; exit 1 ;;
  esac
done

if [ -t 1 ]; then
  C_G=$'\033[0;32m'; C_Y=$'\033[0;33m'; C_R=$'\033[0;31m'
  C_B=$'\033[1;33m'; C_W=$'\033[1;37m'; C_0=$'\033[0m'
else
  C_G=""; C_Y=""; C_R=""; C_B=""; C_W=""; C_0=""
fi
ok() { printf "%s[OK]%s %s\n" "$C_G" "$C_0" "$1"; }
warn() { printf "%s[WARN]%s %s\n" "$C_Y" "$C_0" "$1"; }
fail() { printf "%s[FAIL]%s %s\n" "$C_R" "$C_0" "$1"; }

cleanup() {
  if [ -n "$TMP_DL" ] && [ -d "$TMP_DL" ]; then rm -rf "$TMP_DL"; fi
}
trap cleanup EXIT

if [ "$(id -u)" -ne 0 ]; then
  fail "Installer must be run as root."
  printf "Please run: sudo bash %s\n" "$0"
  exit 1
fi
for dependency in python3 tar; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    fail "Required dependency is missing: $dependency"
    exit 1
  fi
done
if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
  fail "Either curl or wget is required to download HOMA."
  exit 1
fi

printf "\n%s=== Installing HOMA · VPS Optimizer & Command Center ===%s\n\n" "$C_B" "$C_0"

SCRIPT_FILES=(
  "homa-menu.sh"
  "homa-boost.sh"
  "homa-operator-fix.sh"
  "homa-instagram-fix.sh"
  "homa-client-opt.sh"
  "homa-scheduler.sh"
  "homa-domain-checker.sh"
  "homa-hardware-opt.sh"
  "homa-speedtest.sh"
  "homa-cf-scanner.sh"
  "homa-monitor.sh"
  "homa-port-doctor.sh"
  "homa-unban.sh"
  "homa-iran-unlocker.sh"
  "homa-watchdog.sh"
  "homa-telegram.sh"
  "homa-dns.sh"
  "homa-bridge.sh"
  "homa-iran-probe.sh"
  "homa-sni-checker.sh"
  "homa-security.sh"
  "homa-backup.sh"
  "homa-cron.sh"
  "homa-sysupdate.sh"
  "homa-preflight.sh"
)

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT=""
if [ -f "${SOURCE_DIR}/scripts/homa-menu.sh" ] && [ -f "${SOURCE_DIR}/panel/server.py" ]; then
  PACKAGE_ROOT="$SOURCE_DIR"
elif [ -f "${SOURCE_DIR}/homa-menu.sh" ] && [ -f "${SOURCE_DIR}/../panel/server.py" ]; then
  PACKAGE_ROOT="$(cd "${SOURCE_DIR}/.." && pwd)"
fi

if [ -z "$PACKAGE_ROOT" ]; then
  printf "No local release found; downloading the latest HOMA package...\n"
  TMP_DL="$(mktemp -d)"
  LATEST_TAG=""
  if command -v curl >/dev/null 2>&1; then
    LATEST_TAG="$(curl -sI --max-time 12 "https://github.com/${REPO_NAME}/releases/latest" 2>/dev/null | awk -F'/' '/[Ll]ocation:/ {print $NF}' | tr -d '\r\n')" || true
  fi

  URLS=()
  if [ -n "$LATEST_TAG" ] && [ "$LATEST_TAG" != "latest" ]; then
    URLS+=("https://github.com/${REPO_NAME}/archive/refs/tags/${LATEST_TAG}.tar.gz")
  fi
  URLS+=("https://github.com/${REPO_NAME}/archive/refs/heads/main.tar.gz")

  DOWNLOAD_OK=0
  for url in "${URLS[@]}"; do
    printf "Downloading: %s\n" "$url"
    if command -v curl >/dev/null 2>&1; then
      if curl -fsSL --max-time 120 "$url" | tar -xz -C "$TMP_DL" --strip-components=1 2>/dev/null; then
        DOWNLOAD_OK=1
        break
      fi
    elif wget -qO- "$url" | tar -xz -C "$TMP_DL" --strip-components=1 2>/dev/null; then
      DOWNLOAD_OK=1
      break
    fi
  done
  if [ "$DOWNLOAD_OK" -ne 1 ] || [ ! -f "${TMP_DL}/scripts/homa-menu.sh" ]; then
    fail "Could not download a valid HOMA release from GitHub."
    exit 1
  fi
  PACKAGE_ROOT="$TMP_DL"
else
  printf "Installing from local package: %s\n" "$PACKAGE_ROOT"
fi

mkdir -p "$SCRIPTS_DIR" "$PANEL_DIR/static" "${INSTALL_DIR}/backup" "${INSTALL_DIR}/backups"
SOURCE_SCRIPTS_DIR="$(cd "${PACKAGE_ROOT}/scripts" && pwd)"
TARGET_SCRIPTS_DIR="$(cd "$SCRIPTS_DIR" && pwd)"
SOURCE_PANEL_DIR="$(cd "${PACKAGE_ROOT}/panel" && pwd)"
TARGET_PANEL_DIR="$(cd "$PANEL_DIR" && pwd)"
chmod 700 "${INSTALL_DIR}/backup" "${INSTALL_DIR}/backups"

for file in "${SCRIPT_FILES[@]}"; do
  source_file="${PACKAGE_ROOT}/scripts/${file}"
  if [ ! -f "$source_file" ]; then
    fail "Release package is incomplete: scripts/$file is missing."
    exit 1
  fi
  if [ "$SOURCE_SCRIPTS_DIR" != "$TARGET_SCRIPTS_DIR" ]; then
    install -m 0755 "$source_file" "${SCRIPTS_DIR}/${file}"
  fi
  # Root-level copies are used by the small persistent HOMA services.
  install -m 0755 "$source_file" "${INSTALL_DIR}/${file}"
done
ok "All ${#SCRIPT_FILES[@]} HOMA modules installed."

if [ ! -d "${PACKAGE_ROOT}/panel/static" ]; then
  fail "Release package is incomplete: graphical panel assets are missing."
  exit 1
fi
if [ "$SOURCE_PANEL_DIR" != "$TARGET_PANEL_DIR" ]; then
  install -m 0755 "${PACKAGE_ROOT}/panel/server.py" "${PANEL_DIR}/server.py"
  install -m 0644 "${PACKAGE_ROOT}/panel/homa-panel.service" "${PANEL_DIR}/homa-panel.service"
  cp -R "${PACKAGE_ROOT}/panel/static/." "${PANEL_DIR}/static/"
fi
chown -R root:root "$PANEL_DIR"
find "$PANEL_DIR" -type d -exec chmod 0755 {} +
find "$PANEL_DIR" -type f -exec chmod 0644 {} +
chmod 0755 "${PANEL_DIR}/server.py"
ok "Graphical control panel installed."

# Keep credentials outside the public application directory and preserve them on update.
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"
touch "$PANEL_ENV"
chmod 600 "$PANEL_ENV"
if ! grep -q '^HOMA_PANEL_TOKEN=.' "$PANEL_ENV" 2>/dev/null; then
  NEW_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  printf '\nHOMA_PANEL_TOKEN=%s\n' "$NEW_TOKEN" >> "$PANEL_ENV"
fi
if ! grep -q '^HOMA_PANEL_HOST=' "$PANEL_ENV" 2>/dev/null; then
  printf 'HOMA_PANEL_HOST=127.0.0.1\n' >> "$PANEL_ENV"
fi
if ! grep -q '^HOMA_PANEL_PORT=' "$PANEL_ENV" 2>/dev/null; then
  printf 'HOMA_PANEL_PORT=8787\n' >> "$PANEL_ENV"
fi

cat <<'EOF' > "$BIN_LINK"
#!/usr/bin/env bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
if [ ! -t 0 ] && [ -e /dev/tty ] && [ "$#" -eq 0 ]; then exec </dev/tty; fi
exec bash /opt/homa/scripts/homa-menu.sh "$@"
EOF
chmod 0755 "$BIN_LINK"

cat <<'EOF' > "$PANEL_BIN_LINK"
#!/usr/bin/env bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
if [ -r /etc/homa/panel.env ]; then
  set -a
  . /etc/homa/panel.env
  set +a
fi
exec python3 /opt/homa/panel/server.py "$@"
EOF
chmod 0755 "$PANEL_BIN_LINK"

PANEL_STARTED=0
if [ -f "${PACKAGE_ROOT}/panel/homa-panel.service" ] && command -v systemctl >/dev/null 2>&1; then
  install -m 0644 "${PACKAGE_ROOT}/panel/homa-panel.service" /etc/systemd/system/homa-panel.service
  if [ -d /run/systemd/system ]; then
    systemctl daemon-reload || true
    if [ "$START_PANEL" -eq 1 ]; then
      if systemctl enable homa-panel.service >/dev/null 2>&1 && systemctl restart homa-panel.service >/dev/null 2>&1; then
        PANEL_STARTED=1
        ok "HOMA panel service is enabled on the local interface."
      else
        warn "Panel was installed but its service could not be started. Run: homa-panel"
      fi
    fi
  fi
fi

PANEL_TOKEN="$(sed -n 's/^HOMA_PANEL_TOKEN=//p' "$PANEL_ENV" | tail -n 1)"
printf "\n%s[COMPLETE] HOMA is ready for flight.%s\n\n" "$C_G" "$C_0"
printf "  Installation:     %s\n" "$INSTALL_DIR"
printf "  Terminal suite:   %shoma%s\n" "$C_W" "$C_0"
printf "  Graphical panel:  %shoma-panel%s\n" "$C_W" "$C_0"
printf "  Local URL:        %shttp://127.0.0.1:8787%s\n" "$C_W" "$C_0"
if [ "${HOMA_NONINTERACTIVE:-0}" = "1" ]; then
  printf "  Access token:     stored in %s\n" "$PANEL_ENV"
else
  printf "  Access token:     %s%s%s\n" "$C_W" "$PANEL_TOKEN" "$C_0"
fi
if [ "$PANEL_STARTED" -eq 1 ]; then
  printf "  Panel service:    active (homa-panel.service)\n"
else
  printf "  Panel service:    installed, not running\n"
fi
printf "\n  Remote access (recommended):\n"
printf "  ssh -L 8787:127.0.0.1:8787 USER@SERVER\n"
printf "  Then open http://127.0.0.1:8787 and enter the access token.\n\n"

if [ "$AUTO_LAUNCH" -eq 1 ] && [ "${HOMA_NONINTERACTIVE:-0}" != "1" ]; then
  if [ -t 0 ]; then
    exec /usr/local/bin/homa
  elif [ -e /dev/tty ]; then
    exec /usr/local/bin/homa </dev/tty
  fi
fi
printf "Run %shoma%s for the terminal suite or %shoma-panel%s for the graphical panel.\n" "$C_G" "$C_0" "$C_G" "$C_0"
