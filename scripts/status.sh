#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
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

set +u
source /opt/ros/humble/setup.bash
cd "$OPENARMX_WS"
source install/setup.bash
set -u

echo "== Processes =="
ps -ef | grep -E "openarmx_bringup|openarmx_teleop_bridge|mini_udp_sender_bimanual|mini_udp_sender|ros2_control_node|robot_state_publisher" | grep -v grep || true

echo
echo "== Topic rates (5s) =="
(timeout 5 ros2 topic hz /teleop/right/leader/joint_state) || true
(timeout 5 ros2 topic hz /teleop/left/leader/joint_state) || true
(timeout 5 ros2 topic hz /right_forward_position_controller/commands) || true
(timeout 5 ros2 topic hz /left_forward_position_controller/commands) || true
