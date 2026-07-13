# OpenArmX Bimanual Teleop (OpenArm Mini -> OpenArmX)

This package provides a robust bimanual teleoperation pipeline:
- Leader: two OpenArm Mini teleoperators (right/left)
- Bridge: ROS2 nodes that apply unit conversion, soft limits, anti-jitter filtering, and rate limiting
- Follower: OpenArmX bimanual robot running `forward_position_controller`

## Quick Run

1. Terminal 1

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_bringup openarmx.bimanual.launch.py \
  right_can_interface:=can0 \
  left_can_interface:=can1 \
  control_mode:=mit \
  robot_controller:=forward_position_controller
```

2. Terminal 2

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_teleop_bridge mini_to_openarmx_bimanual.launch.py
```

3. Terminal 3

```bash
source /home/will/lerobot/.venv/bin/activate
python /home/will/lerobot/openarmx_ws/src/openarmx_teleop_bridge/openarmx_teleop_bridge/mini_udp_sender_bimanual.py \
  --right-teleop-port /dev/ttyACM0 \
  --right-teleop-id my_openarm_mini_right \
  --left-teleop-port /dev/ttyACM1 \
  --left-teleop-id my_openarm_mini_left \
  --right-udp-host 127.0.0.1 \
  --right-udp-port 17777 \
  --left-udp-host 127.0.0.1 \
  --left-udp-port 17778 \
  --rate-hz 150
```

## 1. Environment Model

Use different environments per terminal:

- Terminal 1 (Follower): `bash` + ROS2 + `openarmx_ws`
- Terminal 2 (Bridge): `bash` + ROS2 + `openarmx_ws`
- Terminal 3 (Mini Sender): `lerobot` venv (Python 3.12)

Do **not** run all three in one environment.

## 2. Normal Startup (Bimanual)

### Terminal 1: Start follower

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_bringup openarmx.bimanual.launch.py \
  right_can_interface:=can0 \
  left_can_interface:=can1 \
  control_mode:=mit \
  robot_controller:=forward_position_controller
```

### Terminal 2: Start bridge

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_teleop_bridge mini_to_openarmx_bimanual.launch.py
```

### Terminal 3: Start bimanual mini sender

```bash
source /home/will/lerobot/.venv/bin/activate
python /home/will/lerobot/openarmx_ws/src/openarmx_teleop_bridge/openarmx_teleop_bridge/mini_udp_sender_bimanual.py \
  --right-teleop-port /dev/ttyACM0 \
  --right-teleop-id my_openarm_mini_right \
  --left-teleop-port /dev/ttyACM1 \
  --left-teleop-id my_openarm_mini_left \
  --right-udp-host 127.0.0.1 \
  --right-udp-port 17777 \
  --left-udp-host 127.0.0.1 \
  --left-udp-port 17778 \
  --rate-hz 150
```

## 3. Safety Defaults Included

The bridge includes:
- Degrees->radians conversion for arm joints
- Gripper conversion to meters
- Soft limits (including tighter inward shoulder limits)
- Per-cycle rate limiting
- Deadband + exponential smoothing to reduce jitter

## 4. Runtime Tuning (No restart)

Speed up:

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash

ros2 param set /right_follower_bridge_node max_joint_step_rad 0.014
ros2 param set /left_follower_bridge_node  max_joint_step_rad 0.014
ros2 param set /right_follower_bridge_node max_gripper_step_m 0.0014
ros2 param set /left_follower_bridge_node  max_gripper_step_m 0.0014
```

Reduce jitter:

```bash
ros2 param set /right_follower_bridge_node smoothing_alpha 0.35
ros2 param set /left_follower_bridge_node  smoothing_alpha 0.35
ros2 param set /right_follower_bridge_node joint_deadband_rad 0.003
ros2 param set /left_follower_bridge_node  joint_deadband_rad 0.003
```

## 5. Quick Health Checks

```bash
source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash

ros2 topic hz /teleop/right/leader/joint_state
ros2 topic hz /teleop/left/leader/joint_state
ros2 topic hz /right_forward_position_controller/commands
ros2 topic hz /left_forward_position_controller/commands
```

## 6. Common Issues

### `ModuleNotFoundError: lerobot`
Run sender in `.venv` only (Terminal 3).

### `/tf` not published
Check follower launch is running and not crashed. Validate CAN interface mapping.

### Hard-stop collision noise near limits
Reduce speed (`max_joint_step_rad`) and verify soft limits are active.

## 7. Stop Everything

```bash
pkill -f "ros2 launch openarmx_bringup"
pkill -f "ros2 launch openarmx_teleop_bridge"
pkill -f mini_udp_sender_bimanual.py
pkill -f mini_udp_sender.py
```
