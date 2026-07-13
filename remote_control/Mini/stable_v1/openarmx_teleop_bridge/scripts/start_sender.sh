#!/usr/bin/env bash
set -eo pipefail

RATE_HZ=${1:-150}

set +u
source /home/will/lerobot/.venv/bin/activate
set -u

exec python /home/will/lerobot/openarmx_ws/src/openarmx_teleop_bridge/openarmx_teleop_bridge/mini_udp_sender_bimanual.py \
  --right-teleop-port /dev/ttyACM0 \
  --right-teleop-id my_openarm_mini_right \
  --left-teleop-port /dev/ttyACM1 \
  --left-teleop-id my_openarm_mini_left \
  --right-udp-host 127.0.0.1 \
  --right-udp-port 17777 \
  --left-udp-host 127.0.0.1 \
  --left-udp-port 17778 \
  --rate-hz "$RATE_HZ"
