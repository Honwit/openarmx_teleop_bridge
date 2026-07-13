#!/usr/bin/env bash
set -euo pipefail

pkill -f "ros2 launch openarmx_bringup" || true
pkill -f "ros2 launch openarmx_teleop_bridge" || true
pkill -f mini_udp_sender_bimanual.py || true
pkill -f mini_udp_sender.py || true
pkill -f mini_leader_node || true
pkill -f follower_bridge_node || true
pkill -f ros2_control_node || true
pkill -f robot_state_publisher || true
pkill -f rviz2 || true

echo "Stopped teleop-related processes."
