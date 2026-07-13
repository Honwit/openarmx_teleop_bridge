#!/usr/bin/env bash
set -eo pipefail

set +u
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
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
