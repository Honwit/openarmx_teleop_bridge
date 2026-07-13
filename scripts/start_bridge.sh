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

exec ros2 launch openarmx_teleop_bridge mini_to_openarmx_bimanual.launch.py
