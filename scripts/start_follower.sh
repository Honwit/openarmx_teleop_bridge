#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

RIGHT_CAN_INTERFACE=${RIGHT_CAN_INTERFACE:-can0}
LEFT_CAN_INTERFACE=${LEFT_CAN_INTERFACE:-can1}
CAN_BITRATE=${CAN_BITRATE:-1000000}
OPENARMX_WS=${OPENARMX_WS:-}
DEFAULT_WS="$HOME/lerobot/openarmx_ws"

if [[ -z "$OPENARMX_WS" ]]; then
  if [[ -f "$PKG_DIR/../../install/setup.bash" ]]; then
    OPENARMX_WS="$(cd -- "$PKG_DIR/../.." && pwd)"
  elif [[ -f "$DEFAULT_WS/install/setup.bash" ]]; then
    OPENARMX_WS="$DEFAULT_WS"
  else
    echo "[ERROR] Cannot find openarmx workspace install/setup.bash"
    echo "        Set OPENARMX_WS, for example:"
    echo "        OPENARMX_WS=/path/to/openarmx_ws $0"
    exit 2
  fi
fi

is_can_up() {
  local ifname="$1"
  ip -br link show "$ifname" 2>/dev/null | awk '{print $2}' | grep -q '^UP$'
}

run_ip_cmd() {
  if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
    ip "$@"
    return
  fi

  sudo ip "$@"
}

ensure_can_up() {
  local ifname="$1"
  local i

  if ! ip -details link show "$ifname" >/dev/null 2>&1; then
    echo "[ERROR] CAN interface '$ifname' does not exist."
    echo "        Check your interface name (e.g. can0/can1/can2/can3)."
    exit 2
  fi

  if is_can_up "$ifname"; then
    echo "[INFO] CAN interface '$ifname' already UP, skip bring-up."
    return
  fi

  echo "[INFO] Bringing up '$ifname' at bitrate ${CAN_BITRATE}."
  run_ip_cmd link set "$ifname" down
  run_ip_cmd link set "$ifname" type can bitrate "$CAN_BITRATE"
  run_ip_cmd link set "$ifname" up

  for i in 1 2 3 4 5; do
    if is_can_up "$ifname"; then
      echo "[INFO] CAN interface '$ifname' is UP."
      return
    fi
    sleep 0.2
  done

  if ! is_can_up "$ifname"; then
    echo "[ERROR] Failed to bring CAN interface '$ifname' UP."
    ip -details link show "$ifname" || true
    exit 2
  fi
}

ensure_can_up "$RIGHT_CAN_INTERFACE"
ensure_can_up "$LEFT_CAN_INTERFACE"

set +u
source /opt/ros/humble/setup.bash
cd "$OPENARMX_WS"
source install/setup.bash
set -u

exec ros2 launch openarmx_bringup openarmx.bimanual.launch.py \
  right_can_interface:="$RIGHT_CAN_INTERFACE" \
  left_can_interface:="$LEFT_CAN_INTERFACE" \
  control_mode:=mit \
  robot_controller:=forward_position_controller
