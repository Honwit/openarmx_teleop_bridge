# 换设备迁移清单（OpenArm Mini -> OpenArmX）

## 一、必须修改项

### 1) MINI 串口
编辑启动命令或脚本参数：
- `--right-teleop-port /dev/ttyACM0`
- `--left-teleop-port /dev/ttyACM1`

### 2) MINI 标识符
- `--right-teleop-id my_openarm_mini_right`
- `--left-teleop-id my_openarm_mini_left`

如重标定后 ID 变化，必须同步更新。

### 3) Follower CAN 接口
编辑 `scripts/start_follower.sh`：
- `right_can_interface:=can0`
- `left_can_interface:=can1`

若新机是 `can2/can3`，按实际替换。

### 4) UDP 端口
默认：
- right: `17777`
- left: `17778`

如端口冲突，`start_sender.sh` 与 bimanual launch 保持一致修改。

## 二、建议校准项

### 1) 软限位
文件：`openarmx_teleop_bridge/follower_bridge_node.py`
- `joint_min_rad`
- `joint_max_rad`
- `gripper_min_m`
- `gripper_max_m`

按新机械臂实际可动范围更新。

### 2) 安全速度
- `max_joint_step_rad`
- `max_gripper_step_m`

新设备先小后大，逐步提速。

### 3) 防抖参数
- `smoothing_alpha`
- `joint_deadband_rad`
- `gripper_deadband_m`

输入噪声大时，提高滤波、适当增大死区。

## 三、标准联调流程

1. 先启动 follower（仅控制链路，不开 sender）。
2. 再启动 bridge。
3. 最后启动 sender。
4. 小幅动作验证方向、幅度、夹爪。
5. 单臂稳定后再双臂联动。

## 四、快速诊断

- 领导臂话题频率：
  - `/teleop/right/leader/joint_state`
  - `/teleop/left/leader/joint_state`
- 跟随指令频率：
  - `/right_forward_position_controller/commands`
  - `/left_forward_position_controller/commands`

## 五、推荐目录使用方式

- 把本目录作为“迁移模板”。
- 换新设备时，仅改脚本参数与限位参数。
- 每次改完先做 2 分钟低速安全测试。
