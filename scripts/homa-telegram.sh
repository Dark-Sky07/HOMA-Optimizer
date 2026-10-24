#!/usr/bin/env bash
# ========================================================================
#   HOMA VPS All In One Optimizer — Telegram Notification Manager
#   File: scripts/homa-telegram.sh
#   Description: Instant alerts for server status, watchdog, & IP unban
# ========================================================================

set -u
umask 077

if [ -t 1 ]; then
  C_G=$'\033[0;32m'; C_Y=$'\033[0;33m'; C_R=$'\033[0;31m'
  C_B=$'\033[1;36m'; C_W=$'\033[1;37m'; C_C=$'\033[0;36m'; C_0=$'\033[0m'
else
  C_G=""; C_Y=""; C_R=""; C_B=""; C_W=""; C_C=""; C_0=""
fi

CONF_DIR="/opt/homa"
CONF_FILE="$CONF_DIR/telegram.conf"

load_config() {
  BOT_TOKEN=""
  CHAT_ID=""
  TG_ENABLED="0"
  if [ ! -r "$CONF_FILE" ]; then
    return 0
  fi

  # Parse only the three known scalar keys. Never source a configuration file:
  # even a legacy or accidentally modified file must not execute shell code.
  local key value
  while IFS='=' read -r key value; do
    value="${value%$'\r'}"
    value="${value#\"}"; value="${value%\"}"
    value="${value#\'}"; value="${value%\'}"
    case "$key" in
      BOT_TOKEN) BOT_TOKEN="$value" ;;
      CHAT_ID) CHAT_ID="$value" ;;
      TG_ENABLED) TG_ENABLED="$value" ;;
    esac
  done < "$CONF_FILE"
  if [ "$TG_ENABLED" != "1" ]; then
    TG_ENABLED="0"
  fi
}

valid_credentials() {
  [[ "${BOT_TOKEN:-}" =~ ^[0-9]+:[A-Za-z0-9_-]{20,}$ ]] && [[ "${CHAT_ID:-}" =~ ^-?[0-9]+$ ]]
}

save_config() {
  if ! mkdir -p "$CONF_DIR"; then
    return 1
  fi
  local tmp_file
  if ! tmp_file="$(mktemp "${CONF_DIR}/.telegram.conf.XXXXXX")"; then
    return 1
  fi
  if ! printf '%s\n' \
    '# HOMA Telegram Alerts Configuration (scalar values; never shell-source this file)' \
    "BOT_TOKEN=$BOT_TOKEN" \
    "CHAT_ID=$CHAT_ID" \
    "TG_ENABLED=$TG_ENABLED" > "$tmp_file"; then
    rm -f "$tmp_file"
    return 1
  fi
  if ! chmod 600 "$tmp_file" || ! mv -f "$tmp_file" "$CONF_FILE"; then
    rm -f "$tmp_file"
    return 1
  fi
}

telegram_url_config() {
  # Passing the URL through curl's stdin config keeps the bot token out of
  # curl's command line and therefore out of the local process list.
  printf 'url = "https://api.telegram.org/bot%s/sendMessage"\n' "$BOT_TOKEN"
}

send_msg() {
  local message="$1"
  load_config

  if [ "${TG_ENABLED:-0}" != "1" ] || ! valid_credentials; then
    return 1
  fi

  local host_name
  host_name=$(hostname)
  local server_ip
  server_ip=$(curl -s4m 3 https://api.ipify.org || printf 'VPS')

  local payload="🖥️ *HOMA VPS ALERT* — \`${host_name}\` (${server_ip})%0A%0A${message}"

  telegram_url_config | curl -sS --config - \
    --connect-timeout 5 --max-time 15 \
    -X POST \
    -d "chat_id=${CHAT_ID}" \
    -d "text=${payload}" \
    -d "parse_mode=Markdown" > /dev/null 2>&1
}

configure_bot() {
  load_config
  printf "\n%s=== CONFIGURE TELEGRAM NOTIFICATIONS ===%s\n" "$C_B" "$C_0"
  printf "To receive instant alerts when Xray dies, IP is unbanned, or backups complete:\n"
  printf "  1. Create a bot via @BotFather and copy the HTTP API Token.\n"
  printf "  2. Start your bot or message @userinfobot to get your numeric Chat ID.\n\n"

  local token_display="not configured"
  if [ -n "$BOT_TOKEN" ]; then
    token_display="configured (hidden)"
  fi
  printf "Enter Telegram Bot Token [%s]: " "$token_display"
  local input_token=""
  if [ -t 0 ]; then
    read -r -s input_token || true
    printf "\n"
  else
    read -r input_token || true
  fi
  [ -n "$input_token" ] && BOT_TOKEN="$input_token"

  printf "Enter Your Telegram Chat ID [%s]: " "${CHAT_ID:-None}"
  local input_chat=""
  read -r input_chat || true
  [ -n "$input_chat" ] && CHAT_ID="$input_chat"

  if ! valid_credentials; then
    printf "\n%s[FAIL] Enter a valid bot token and numeric Telegram chat ID.%s\n" "$C_R" "$C_0"
    return 1
  fi

  TG_ENABLED="1"
  if ! save_config; then
    printf "\n%s[FAIL] Could not securely save %s.%s\n" "$C_R" "$CONF_FILE" "$C_0"
    return 1
  fi
  printf "\n%s[OK] Telegram configuration saved with owner-only permissions!%s\n" "$C_G" "$C_0"
  test_notification
}

test_notification() {
  load_config
  if ! valid_credentials; then
    printf "%s[FAIL] Telegram bot is not configured yet. Run configuration first.%s\n" "$C_R" "$C_0"
    return 1
  fi

  printf "Sending test message to Telegram... "
  local response
  response=$(telegram_url_config | curl -sS --config - \
    --connect-timeout 5 --max-time 15 \
    -w $'\n%{http_code}' -X POST \
    -d "chat_id=${CHAT_ID}" \
    -d "text=🚀 *HOMA VPS Optimizer* notification test successful!%0A✅ Server alerts are actively connected." \
    -d "parse_mode=Markdown" 2>&1)
  local curl_status=$?

  if [ "$curl_status" -ne 0 ]; then
    printf "%s[REQUEST FAILED]%s\n" "$C_R" "$C_0"
    printf "%s\n" "$response"
    return 1
  fi

  local res="${response##*$'\n'}"
  local body="${response%$'\n'*}"
  if [ "$res" = "200" ]; then
    printf "%s[DELIVERED]%s\n" "$C_G" "$C_0"
    printf "%sCheck your Telegram bot. A test notification was received!%s\n" "$C_W" "$C_0"
  else
    printf "%s[FAILED (HTTP %s)]%s\n" "$C_R" "$res" "$C_0"
    printf "%s\n" "$body"
    return 1
  fi
}

toggle_alerts() {
  load_config
  if [ "${TG_ENABLED:-0}" = "1" ]; then
    TG_ENABLED="0"
  elif valid_credentials; then
    TG_ENABLED="1"
  else
    printf "%s[!] Please configure a valid Bot Token and Chat ID first.%s\n" "$C_R" "$C_0"
    return 1
  fi

  if ! save_config; then
    printf "%s[FAIL] Could not update Telegram configuration.%s\n" "$C_R" "$C_0"
    return 1
  fi
  if [ "$TG_ENABLED" = "1" ]; then
    printf "%s[ENABLED] Telegram notifications are active!%s\n" "$C_G" "$C_0"
  else
    printf "%s[DISABLED] Telegram notifications are now muted.%s\n" "$C_Y" "$C_0"
  fi
}

menu() {
  while true; do
    load_config
    local status_text="${C_R}Disabled / Unconfigured${C_0}"
    if [ "${TG_ENABLED:-0}" = "1" ] && valid_credentials; then
      status_text="${C_G}Active & Connected (Chat: ${CHAT_ID})${C_0}"
    fi

    printf "\n%s========================================================================%s\n" "$C_B" "$C_0"
    printf "          %sHOMA VPS TELEGRAM NOTIFICATIONS%s\n" "$C_W" "$C_0"
    printf "  Alert Status: %b\n" "$status_text"
    printf "%s========================================================================%s\n" "$C_B" "$C_0"
    printf "  %s[1]%s Configure Telegram Bot & Chat ID\n" "$C_C" "$C_0"
    printf "  %s[2]%s Send Test Notification Now\n" "$C_C" "$C_0"
    printf "  %s[3]%s Toggle Alerts On/Off\n" "$C_C" "$C_0"
    printf "  %s[4]%s Delete Telegram Configuration\n" "$C_C" "$C_0"
    printf "  %s[0]%s Back to Main Menu\n" "$C_C" "$C_0"
    printf "%s\n" "------------------------------------------------------------------------"
    printf "Select an option: "
    local opt=""
    read -r opt || break
    case "$opt" in
      1) configure_bot ;;
      2) test_notification ;;
      3) toggle_alerts ;;
      4)
        if rm -f "$CONF_FILE"; then
          printf "%s[OK] Configuration deleted.%s\n" "$C_G" "$C_0"
        else
          printf "%s[FAIL] Could not delete configuration.%s\n" "$C_R" "$C_0"
        fi
        ;;
      0) break ;;
      *) printf "%sInvalid option.%s\n" "$C_R" "$C_0" ;;
    esac
  done
}

if [ "${1:-}" = "send" ]; then
  shift
  send_msg "$*"
elif [ "${1:-}" = "test" ]; then
  test_notification
else
  menu
fi
