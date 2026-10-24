#!/usr/bin/env bash
#===============================================================================
#  homa-backup — 3x-ui Panel & System Disaster Recovery Backup Manager
#  Part of HOMA VPS All In One Optimizer
#
#  Features:
#    1. One-click backup of 3x-ui panel database (/etc/x-ui/x-ui.db)
#    2. Backup of SSL certificates (/root/cert, /etc/x-ui/)
#    3. Backup of system network & optimizer configurations
#    4. Easy one-click restore with pre-restore safety snapshots
#===============================================================================

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
set -u
umask 077

BASE_DIR="/opt/homa"
BACKUP_DIR="${BASE_DIR}/backups"

# Color helpers
if [ -t 1 ]; then
  C_G=$'\033[0;32m'; C_Y=$'\033[0;33m'; C_R=$'\033[0;31m'
  C_B=$'\033[1;36m'; C_W=$'\033[1;37m'; C_0=$'\033[0m'
else
  C_G=""; C_Y=""; C_R=""; C_B=""; C_W=""; C_0=""
fi

section(){ printf "\n%s=== %s ===%s\n" "$C_B" "$1" "$C_0"; }
ok(){      printf "%s[OK]%s %s\n" "$C_G" "$C_0" "$1"; }
warn(){    printf "%s[WARN]%s %s\n" "$C_Y" "$C_0" "$1"; }
bad(){     printf "%s[FAIL]%s %s\n" "$C_R" "$C_0" "$1"; }
info(){    printf "    %s\n" "$1"; }

check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    bad "Root privileges required."
    printf "    Please execute with sudo: sudo bash %s\n" "$0"
    exit 1
  fi
}

prepare_backup_dir() {
  if ! mkdir -p "$BACKUP_DIR" || ! chmod 700 "$BACKUP_DIR"; then
    bad "Unable to secure backup directory: $BACKUP_DIR"
    return 1
  fi
  # Older releases could leave archives containing private keys world-readable.
  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'homa-panel-backup-*.tar.gz' -exec chmod 600 {} +
}

create_backup() {
  check_root
  section "Creating Panel & System Disaster Recovery Backup"

  prepare_backup_dir || return 1
  local timestamp
  timestamp="$(date +%Y%m%d-%H%M%S)"
  local archive
  if ! archive="$(mktemp "${BACKUP_DIR}/homa-panel-backup-${timestamp}-XXXXXX.tar.gz")"; then
    bad "Unable to allocate a unique backup archive."
    return 1
  fi

  local items_to_backup=()

  # Check 3x-ui database and configs
  if [ -f "/etc/x-ui/x-ui.db" ]; then
    items_to_backup+=("/etc/x-ui/x-ui.db")
  fi
  if [ -d "/etc/x-ui" ]; then
    items_to_backup+=("/etc/x-ui")
  fi
  if [ -d "/root/cert" ]; then
    items_to_backup+=("/root/cert")
  fi
  if [ -f "/etc/sysctl.d/99-homa-boost.conf" ]; then
    items_to_backup+=("/etc/sysctl.d/99-homa-boost.conf")
  fi

  if [ ${#items_to_backup[@]} -eq 0 ]; then
    warn "No standard panel database (/etc/x-ui/x-ui.db) found to backup."
    items_to_backup+=("/etc/sysctl.conf")
  fi

  info "Compressing files into: $archive"
  if ! tar -czf "$archive" -- "${items_to_backup[@]}" 2>/dev/null; then
    rm -f "$archive"
    bad "Backup creation failed; the incomplete archive was removed."
    return 1
  fi
  if ! chmod 600 "$archive"; then
    rm -f "$archive"
    bad "Unable to protect the backup archive."
    return 1
  fi

  local arc_size
  arc_size="$(du -h "$archive" 2>/dev/null | awk '{print $1}')"

  printf "\n"
  ok "Backup created successfully!"
  printf "  File: %s%s%s (%s)\n" "$C_W" "$archive" "$C_0" "$arc_size"
  info "You can download this file via SFTP or restore it anytime with the Restore option."

  if [ -f "/opt/homa/homa-telegram.sh" ]; then
    bash /opt/homa/homa-telegram.sh send "💾 *HOMA Backup Created!*%0AFile: \`$(basename "$archive")\` ($arc_size)" >/dev/null 2>&1 || true
  fi
}

list_backups() {
  section "Available Panel Backups"
  prepare_backup_dir || return 1

  local count=0
  for f in "${BACKUP_DIR}"/homa-panel-backup-*.tar.gz; do
    if [ -f "$f" ]; then
      count=$((count + 1))
      local sz
      sz="$(du -h "$f" | awk '{print $1}')"
      local dt
      dt="$(date -r "$f" "+%Y-%m-%d %H:%M:%S")"
      printf "  [%d] %-48s %-8s (%s)\n" "$count" "$(basename "$f")" "$sz" "$dt"
    fi
  done

  if [ "$count" -eq 0 ]; then
    info "No backup archives found in $BACKUP_DIR."
  fi
}

restore_backup() {
  check_root
  section "Restore Panel from Backup"
  prepare_backup_dir || return 1

  local backups=()
  for f in "${BACKUP_DIR}"/homa-panel-backup-*.tar.gz; do
    [ -f "$f" ] && backups+=("$f")
  done

  if [ ${#backups[@]} -eq 0 ]; then
    bad "No backups found to restore."
    return 1
  fi

  printf "Select a backup archive to restore:\n"
  local idx=1
  for f in "${backups[@]}"; do
    local sz
    sz="$(du -h "$f" | awk '{print $1}')"
    printf "  [%d] %s (%s)\n" "$idx" "$(basename "$f")" "$sz"
    idx=$((idx + 1))
  done
  printf "  [0] Cancel\n\n"

  local sel=""
  read -r -p "Enter number [0-$((idx - 1))]: " sel || sel="0"
  # Validate before any integer test or array subscript: arithmetic expansion
  # must never evaluate untrusted input as a Bash expression.
  if ! [[ "$sel" =~ ^[0-9]+$ ]] || [ "${#sel}" -gt 9 ]; then
    bad "Invalid backup selection."
    return 1
  fi
  # Force decimal interpretation so valid selections such as 08 and 09 are
  # not treated as invalid octal numbers by Bash arithmetic.
  sel=$((10#$sel))
  if [ "$sel" -eq 0 ]; then
    info "Restore cancelled."
    return 0
  fi
  if [ "$sel" -ge "$idx" ]; then
    bad "Backup selection is out of range."
    return 1
  fi

  local target_archive="${backups[$((sel - 1))]}"
  info "Selected: $(basename "$target_archive")"
  if ! tar -tzf "$target_archive" >/dev/null 2>&1; then
    bad "The selected archive is invalid or unreadable; nothing was restored."
    return 1
  fi

  # Safety snapshot of current state before restoring.
  if [ -f "/etc/x-ui/x-ui.db" ]; then
    info "Taking pre-restore snapshot of current database..."
    if ! cp "/etc/x-ui/x-ui.db" "/etc/x-ui/x-ui.db.pre-restore"; then
      bad "Could not create the pre-restore database snapshot; restore aborted."
      return 1
    fi
  fi

  local panel_service=""
  for candidate in x-ui 3x-ui; do
    if systemctl is-active --quiet "$candidate" 2>/dev/null; then
      panel_service="$candidate"
      break
    fi
  done
  if [ -n "$panel_service" ]; then
    info "Stopping $panel_service while its database is restored..."
    if ! systemctl stop "$panel_service" 2>/dev/null; then
      bad "Could not stop $panel_service safely; restore aborted."
      return 1
    fi
  fi

  info "Extracting backup..."
  if ! tar -xzf "$target_archive" -C / 2>/dev/null; then
    if [ -n "$panel_service" ]; then
      bad "Restore failed. $panel_service was left stopped; verify files before recovery."
    else
      bad "Restore failed; verify the restored files before starting the panel."
    fi
    return 1
  fi

  if [ -n "$panel_service" ]; then
    info "Restarting $panel_service to load the restored database..."
    if ! systemctl restart "$panel_service" 2>/dev/null; then
      bad "Files were restored, but $panel_service could not be restarted."
      return 1
    fi
  fi

  printf "\n"
  ok "Panel database restored successfully from $(basename "$target_archive")!"
}

CMD="${1:---backup}"
case "$CMD" in
  --backup|-b)
    create_backup
    ;;
  --list|-l)
    list_backups
    ;;
  --restore|-r)
    restore_backup
    ;;
  *)
    create_backup
    ;;
esac
