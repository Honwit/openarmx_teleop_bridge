#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

RATE_HZ=${1:-150}
LEROBOT_VENV=${LEROBOT_VENV:-$HOME/lerobot/.venv}
SENDER_PY=${SENDER_PY:-$PKG_DIR/openarmx_teleop_bridge/mini_udp_sender_bimanual.py}

if [[ ! -f "$SENDER_PY" ]]; then
  echo "[ERROR] Sender script not found: $SENDER_PY"
  exit 2
fi

set +u
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  if [[ -f "$LEROBOT_VENV/bin/activate" ]]; then
    source "$LEROBOT_VENV/bin/activate"
  else
    echo "[ERROR] Cannot find lerobot venv activate script: $LEROBOT_VENV/bin/activate"
    echo "        Set LEROBOT_VENV, for example:"
    echo "        LEROBOT_VENV=/path/to/.venv $0"
    exit 2
  fi
fi
set -u

exec python "$SENDER_PY" \
  --right-teleop-port /dev/ttyACM0 \
  --right-teleop-id my_openarm_mini_right \
  --left-teleop-port /dev/ttyACM1 \
  --left-teleop-id my_openarm_mini_left \
  --right-udp-host 127.0.0.1 \
  --right-udp-port 17777 \
  --left-udp-host 127.0.0.1 \
  --left-udp-port 17778 \
  --rate-hz "$RATE_HZ"
