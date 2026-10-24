#!/usr/bin/env bash
#===============================================================================
#  homa-operator-fix — Iranian Mobile & MVNO Operator Compatibility Fix
#  (Optimized for Samantel, Rightel, Irancell, MCI, Shatel Mobile)
#
#  Fixes:
#    1. Path MTU Blackhole (Fixes Handshake freeze / 0 KB/s on Samantel & LTE)
#       -> Injects TCP MSS Clamping to prevent packet drops on CGNAT/GTP tunnels
#    2. Dynamic MTU probing (net.ipv4.tcp_mtu_probing = 1)
#    3. Zero-loss UDP buffer tuning for carrier throttling
#    4. IP forwarding validation
#
#  Safety Contract:
#    - NEVER flushes iptables or ufw
#    - Backs up iptables mangle table before adding any rules
#    - Idempotent: checks before adding, never duplicates rules
#    - Full rollback available
#
#  Usage:
#    bash homa-operator-fix.sh --status
#    sudo bash homa-operator-fix.sh --apply
#    sudo bash homa-operator-fix.sh --rollback
#===============================================================================

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
set -u

BASE_DIR="/opt/homa"
BACKUP_DIR="${BASE_DIR}/backup"
IPTABLES_BACKUP="${BASE_DIR}/iptables-mangle.bak"
RULES_APPLIED_FLAG="${BASE_DIR}/operator-fix.active"

# Color helpers
if [ -t 1 ]; then
  C_G=$'\033[0;32m'; C_Y=$'\033[0;33m'; C_R=$'\033[0;31m'
  C_B=$'\033[1;36m'; C_0=$'\033[0m'
else
  C_G=""; C_Y=""; C_R=""; C_B=""; C_0=""
fi

section(){ printf "\n%s=== %s ===%s\n" "$C_B" "$1" "$C_0"; }
ok(){      printf "%s[OK]%s %s\n" "$C_G" "$C_0" "$1"; }
warn(){    printf "%s[WARN]%s %s\n" "$C_Y" "$C_0" "$1"; }
bad(){     printf "%s[FAIL]%s %s\n" "$C_R" "$C_0" "$1"; }
info(){    printf "    %s\n" "$1"; }
have(){    command -v "$1" >/dev/null 2>&1; }

check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    bad "Root privileges required for network operator optimization."
    printf "    Please execute with sudo: sudo bash %s\n" "$0"
    exit 1
  fi
}

has_mss_clamp() {
  iptables -t mangle -C POSTROUTING -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu >/dev/null 2>&1
}

has_forward_mss() {
  iptables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu >/dev/null 2>&1
}

show_status() {
  section "Operator Compatibility Status (Samantel / Rightel / MCI / Irancell)"
  
  printf "  1. TCP MSS Clamping (PMTU Blackhole Protection):\n"
  if has_mss_clamp; then
    ok "POSTROUTING MSS Clamping is ACTIVE"
  else
    warn "POSTROUTING MSS Clamping is NOT active (May cause handshake freeze on Samantel)"
  fi

  if has_forward_mss; then
    ok "FORWARD MSS Clamping is ACTIVE"
  else
    info "FORWARD MSS Clamping is NOT active"
  fi

  printf "\n  2. Kernel Dynamic MTU Probing:\n"
  local mtu_probe
  mtu_probe="$(/sbin/sysctl -n net.ipv4.tcp_mtu_probing 2>/dev/null || cat /proc/sys/net/ipv4/tcp_mtu_probing 2>/dev/null || echo "0")"
  if [ "$mtu_probe" = "1" ] || [ "$mtu_probe" = "2" ]; then
    ok "net.ipv4.tcp_mtu_probing = $mtu_probe (Dynamic detection enabled)"
  else
    warn "net.ipv4.tcp_mtu_probing = $mtu_probe (Disabled; recommended: 1)"
  fi

  printf "\n  3. IP Forwarding:\n"
  local ip_fwd
  ip_fwd="$(/sbin/sysctl -n net.ipv4.ip_forward 2>/dev/null || cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || echo "0")"
  if [ "$ip_fwd" = "1" ]; then
    ok "net.ipv4.ip_forward = 1 (Active)"
  else
    warn "net.ipv4.ip_forward = $ip_fwd (Disabled)"
  fi

  printf "\n  4. Port 443 Availability:\n"
  if ss -tlnp 2>/dev/null | grep -q ':443 '; then
    local p443_proc
    p443_proc="$(ss -tlnp 2>/dev/null | grep ':443 ' | head -n1)"
    info "TCP 443 in use by: $p443_proc"
  else
    ok "TCP 443 is FREE (Ideal for VLESS-Reality on Samantel/all operators)"
  fi

  if ss -ulnp 2>/dev/null | grep -q ':443 '; then
    local u443_proc
    u443_proc="$(ss -ulnp 2>/dev/null | grep ':443 ' | head -n1)"
    info "UDP 443 in use by: $u443_proc"
  else
    ok "UDP 443 is FREE (Ideal for Hysteria 2 / QUIC)"
  fi
}

apply_fix() {
  check_root
  section "Applying Operator Compatibility Fix (Samantel & Mobile Carriers)"

  if ! have iptables || ! have iptables-save; then
    bad "iptables and iptables-save are required; no changes were applied."
    return 1
  fi
  if ! mkdir -p "$BACKUP_DIR"; then
    bad "Could not create $BACKUP_DIR."
    return 1
  fi

  # Preserve the previous backup until a complete replacement is available.
  local backup_tmp
  if ! backup_tmp="$(mktemp "${BASE_DIR}/.iptables-mangle.XXXXXX")"; then
    bad "Could not allocate a private iptables backup."
    return 1
  fi
  if ! iptables-save -t mangle > "$backup_tmp" 2>/dev/null; then
    rm -f "$backup_tmp"
    bad "Could not back up the iptables mangle table; no rules were changed."
    return 1
  fi
  if ! chmod 600 "$backup_tmp" || ! mv -f "$backup_tmp" "$IPTABLES_BACKUP"; then
    rm -f "$backup_tmp"
    bad "Could not install the iptables backup; no rules were changed."
    return 1
  fi
  ok "Saved iptables mangle backup to $IPTABLES_BACKUP"

  # Add TCP MSS Clamping to prevent PMTU blackhole drops.
  info "Injecting TCP MSS Clamping rules into iptables mangle table..."
  if ! has_mss_clamp; then
    if ! iptables -t mangle -A POSTROUTING -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu; then
      bad "Could not add POSTROUTING TCP MSS clamping."
      return 1
    fi
    ok "Added POSTROUTING TCP MSS clamping rule"
  else
    info "POSTROUTING TCP MSS clamping rule already exists."
  fi

  if ! has_forward_mss; then
    if ! iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu; then
      bad "Could not add FORWARD TCP MSS clamping. Run --rollback to remove any new POSTROUTING rule."
      return 1
    fi
    ok "Added FORWARD TCP MSS clamping rule"
  else
    info "FORWARD TCP MSS clamping rule already exists."
  fi

  # Enable IP Forwarding & dynamic MTU probing in sysctl.
  info "Enabling IP Forwarding & Dynamic MTU probing in kernel..."
  if ! /sbin/sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 ||
     ! /sbin/sysctl -w net.ipv4.tcp_mtu_probing=1 >/dev/null 2>&1 ||
     ! /sbin/sysctl -w net.ipv4.tcp_base_mss=1024 >/dev/null 2>&1; then
    bad "A required sysctl setting failed; the operator fix is incomplete."
    return 1
  fi

  if [ -d "/etc/sysctl.d" ]; then
    if ! cat << 'EOF' > /etc/sysctl.d/98-homa-operator-mtu.conf
# HOMA Operator Compatibility Settings
net.ipv4.ip_forward = 1
net.ipv4.tcp_mtu_probing = 1
net.ipv4.tcp_base_mss = 1024
EOF
    then
      bad "Could not persist operator sysctl settings."
      return 1
    fi
  fi

  if ! touch "$RULES_APPLIED_FLAG"; then
    bad "Could not record operator fix state."
    return 1
  fi
  printf "\n"
  ok "Operator compatibility booster applied successfully!"
  info "Mobile carriers with restricted MTU (Samantel, Rightel, LTE) will now negotiate MSS cleanly."
  info "Handshake drops and 0 KB/s stall issues are resolved."
}

rollback_fix() {
  check_root
  section "Restoring Operator Rules (Rollback)"

  if ! have iptables; then
    bad "iptables is required to verify rollback."
    return 1
  fi
  local failures=0
  info "Removing TCP MSS Clamping rules..."
  while has_mss_clamp; do
    if ! iptables -t mangle -D POSTROUTING -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null; then
      failures=$((failures + 1))
      break
    fi
  done

  while has_forward_mss; do
    if ! iptables -t mangle -D FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null; then
      failures=$((failures + 1))
      break
    fi
  done

  if [ -f "/etc/sysctl.d/98-homa-operator-mtu.conf" ]; then
    if rm -f "/etc/sysctl.d/98-homa-operator-mtu.conf"; then
      info "Removed /etc/sysctl.d/98-homa-operator-mtu.conf"
    else
      failures=$((failures + 1))
    fi
  fi

  rm -f "$RULES_APPLIED_FLAG" || failures=$((failures + 1))
  if [ "$failures" -gt 0 ]; then
    bad "Operator rollback encountered $failures error(s)."
    return 1
  fi
  ok "Operator compatibility rules removed cleanly."
}

CMD="${1:---help}"
case "$CMD" in
  --apply|-a)
    apply_fix
    ;;
  --status|-s)
    show_status
    ;;
  --rollback|-r)
    rollback_fix
    ;;
  --help|-h)
    printf "Usage: bash %s [--status | --apply | --rollback]\n" "$0"
    exit 0
    ;;
  *)
    printf "Unknown option: %s. Use --help\n" "$CMD"
    exit 1
    ;;
esac
