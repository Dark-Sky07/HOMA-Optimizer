#!/usr/bin/env bash
# ========================================================================
#   HOMA VPS All In One Optimizer — Smart Anti-Pollution DNS Cache
#   File: scripts/homa-dns.sh
#   Description: Fast, cached DNS resolver eliminating lookup lag
# ========================================================================

set -u

if [ -t 1 ]; then
  C_G=$'\033[0;32m'; C_Y=$'\033[0;33m'; C_R=$'\033[0;31m'
  C_B=$'\033[1;36m'; C_W=$'\033[1;37m'; C_C=$'\033[0;36m'; C_0=$'\033[0m'
else
  C_G=""; C_Y=""; C_R=""; C_B=""; C_W=""; C_C=""; C_0=""
fi

RESOLVED_CONF="/etc/systemd/resolved.conf"
RESOLVED_BACKUP="/opt/homa/resolved.conf.bak"

check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    printf "%s[FAIL] Root privileges required. Run with sudo.%s\n" "$C_R" "$C_0"
    return 1
  fi
}

test_dns_speed() {
  printf "\n%s=== BENCHMARKING DNS RESOLUTION SPEED ===%s\n" "$C_B" "$C_0"
  local domains=("google.com" "instagram.com" "cloudflare.com" "telegram.org")

  for d in "${domains[@]}"; do
    local start
    start=$(date +%s%N)
    getent hosts "$d" >/dev/null 2>&1 || true
    local end
    end=$(date +%s%N)
    local diff_ms=$(( (end - start) / 1000000 ))
    printf "  %-18s -> %s%3d ms%s\n" "$d" "$C_G" "$diff_ms" "$C_0"
  done
}

apply_dns_optimization() {
  check_root || return 1
  printf "\n%s=== APPLYING SMART ANTI-POLLUTION DNS CACHE ===%s\n" "$C_B" "$C_0"
  if ! mkdir -p /opt/homa /etc/systemd; then
    printf "%s[FAIL] Could not prepare DNS configuration directories.%s\n" "$C_R" "$C_0"
    return 1
  fi

  if [ -f "$RESOLVED_CONF" ] && [ ! -f "$RESOLVED_BACKUP" ]; then
    if ! cp "$RESOLVED_CONF" "$RESOLVED_BACKUP"; then
      printf "%s[FAIL] Could not back up the current resolver configuration.%s\n" "$C_R" "$C_0"
      return 1
    fi
  fi

  # Configure high-speed tier-1 upstream resolvers with local in-memory caching
  if ! cat <<EOF > "$RESOLVED_CONF"
[Resolve]
DNS=1.1.1.1 8.8.8.8 9.9.9.9 1.0.0.1
FallbackDNS=8.8.4.4 149.112.112.112
Domains=~.
DNSSEC=allow-downgrade
DNSOverTLS=no
Cache=yes
CacheFromLocalhost=yes
DNSStubListener=yes
ReadEtcHosts=yes
EOF
  then
    printf "%s[FAIL] Could not write the resolver configuration.%s\n" "$C_R" "$C_0"
    return 1
  fi

  if systemctl is-active --quiet systemd-resolved 2>/dev/null; then
    if ! systemctl restart systemd-resolved 2>/dev/null; then
      printf "%s[FAIL] Could not restart systemd-resolved.%s\n" "$C_R" "$C_0"
      return 1
    fi
  else
    if ! systemctl enable --now systemd-resolved 2>/dev/null; then
      printf "%s[FAIL] Could not activate systemd-resolved.%s\n" "$C_R" "$C_0"
      return 1
    fi
  fi

  # Link /etc/resolv.conf if possible
  if [ -L /etc/resolv.conf ] || [ -f /etc/resolv.conf ]; then
    if ! ln -sfn /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf 2>/dev/null; then
      printf "%s[FAIL] Could not link /etc/resolv.conf to systemd-resolved.%s\n" "$C_R" "$C_0"
      return 1
    fi
  fi

  printf "%s[OK] Local DNS cache enabled! Resolving domains through Tier-1 Anycast engines.%s\n" "$C_G" "$C_0"
  test_dns_speed
}

rollback_dns() {
  check_root || return 1
  printf "\n%s=== ROLLING BACK DNS SETTINGS ===%s\n" "$C_B" "$C_0"
  if [ -f "$RESOLVED_BACKUP" ]; then
    if ! cp "$RESOLVED_BACKUP" "$RESOLVED_CONF"; then
      printf "%s[FAIL] Could not restore the resolver backup.%s\n" "$C_R" "$C_0"
      return 1
    fi
    if systemctl is-active --quiet systemd-resolved 2>/dev/null &&
       ! systemctl restart systemd-resolved 2>/dev/null; then
      printf "%s[FAIL] The backup was restored, but systemd-resolved could not restart.%s\n" "$C_R" "$C_0"
      return 1
    fi
    printf "%s[OK] DNS configuration restored to original state.%s\n" "$C_G" "$C_0"
  else
    printf "%s[!] No previous backup found. Reverting to standard Cloudflare/Google DNS.%s\n" "$C_Y" "$C_0"
    if ! rm -f "$RESOLVED_CONF" || ! rm -f /etc/resolv.conf ||
       ! printf 'nameserver 1.1.1.1\nnameserver 8.8.8.8\n' > /etc/resolv.conf; then
      printf "%s[FAIL] Could not write the fallback DNS configuration.%s\n" "$C_R" "$C_0"
      return 1
    fi
    if systemctl is-active --quiet systemd-resolved 2>/dev/null &&
       ! systemctl restart systemd-resolved 2>/dev/null; then
      printf "%s[FAIL] Fallback DNS was written, but systemd-resolved could not restart.%s\n" "$C_R" "$C_0"
      return 1
    fi
    printf "%s[OK] Standard Cloudflare/Google DNS configured.%s\n" "$C_G" "$C_0"
  fi
}

menu() {
  while true; do
    printf "\n%s========================================================================%s\n" "$C_B" "$C_0"
    printf "          %sHOMA VPS SMART ANTI-POLLUTION DNS CACHE%s\n" "$C_W" "$C_0"
    printf "%s========================================================================%s\n" "$C_B" "$C_0"
    printf "  %s[1]%s Test Current DNS Resolution Speed (Latency Benchmark)\n" "$C_C" "$C_0"
    printf "  %s[2]%s Enable Smart DNS Cache & Anycast Upstreams\n" "$C_C" "$C_0"
    printf "  %s[3]%s Revert DNS Configuration to System Default\n" "$C_C" "$C_0"
    printf "  %s[0]%s Back to Main Menu\n" "$C_C" "$C_0"
    printf "%s\n" "------------------------------------------------------------------------"
    printf "Select an option: "
    read -r opt
    case "$opt" in
      1) test_dns_speed ;;
      2) apply_dns_optimization ;;
      3) rollback_dns ;;
      0) break ;;
      *) printf "%sInvalid option.%s\n" "$C_R" "$C_0" ;;
    esac
  done
}

case "${1:-}" in
  apply|--apply)
    apply_dns_optimization
    ;;
  rollback|--rollback)
    rollback_dns
    ;;
  status|test|--status)
    test_dns_speed
    ;;
  "")
    menu
    ;;
  *)
    printf "Usage: %s {apply|rollback|status}\n" "$0"
    exit 1
    ;;
esac
