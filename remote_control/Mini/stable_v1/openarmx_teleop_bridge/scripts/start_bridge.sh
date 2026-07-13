#!/usr/bin/env bash
set -eo pipefail

set +u
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
set -u

exec ros2 launch openarmx_teleop_bridge mini_to_openarmx_bimanual.launch.py
