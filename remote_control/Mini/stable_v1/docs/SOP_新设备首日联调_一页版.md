# 新设备首日联调 SOP（一页版）

目标：在最短时间内完成 OpenArm Mini -> OpenArmX 双臂遥操的安全首通，并留下可复用参数。

适用范围：
- ROS2 Humble
- OpenArmX 双臂跟随
- OpenArm Mini 双手主端
- UDP 解耦架构（主端读取与 ROS 桥分环境运行）

## 0. 启动前 60 秒检查

1. 急停可用，机械臂周围无人、无遮挡。
2. 电源和线缆牢靠，关节无明显卡滞。
3. 串口存在：/dev/ttyACM0、/dev/ttyACM1（如不同，先记下实际编号）。
4. CAN 接口确认：先以 can0/can1 尝试；若设备不同，按实际替换。
5. 默认先低速参数，不要一上来提速。

## 1. 三终端标准启动顺序

顺序不可变：Follower -> Bridge -> Sender。

### 终端 A（Follower）

source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_bringup openarmx.bimanual.launch.py \
  right_can_interface:=can0 \
  left_can_interface:=can1 \
  control_mode:=mit \
  robot_controller:=forward_position_controller

### 终端 B（Bridge）

source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 launch openarmx_teleop_bridge mini_to_openarmx_bimanual.launch.py

### 终端 C（Sender，必须在 .venv）

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
  --rate-hz 120

首日建议 120Hz，稳定后再升到 150Hz。

## 2. 首通动作流程（2 分钟）

1. 先仅右臂做小幅动作，观察方向、幅度、夹爪开合。
2. 右臂稳定后，仅左臂小幅动作。
3. 最后双臂同时低速联动，不做大幅下压动作。
4. 任一异常立即停机（见第 5 节）。

## 3. 现场必查四项

1. 领导臂话题频率
- /teleop/right/leader/joint_state
- /teleop/left/leader/joint_state

2. 跟随指令频率
- /right_forward_position_controller/commands
- /left_forward_position_controller/commands

3. 桥节点在跑且无持续报错。
4. 机械臂无碰限位、无连续抖动、无异常噪音。

可执行检查命令：

source /opt/ros/humble/setup.bash
cd /home/will/lerobot/openarmx_ws
source install/setup.bash
ros2 topic hz /teleop/right/leader/joint_state
ros2 topic hz /teleop/left/leader/joint_state
ros2 topic hz /right_forward_position_controller/commands
ros2 topic hz /left_forward_position_controller/commands

## 4. 快速调参规则（先安全后速度）

优先顺序：
1. 先限速（防突跳）
2. 再滤波/死区（防抖）
3. 最后提速

常用在线参数：
- max_joint_step_rad
- max_gripper_step_m
- smoothing_alpha
- joint_deadband_rad
- gripper_deadband_m

示例（轻微提速）：

ros2 param set /right_follower_bridge_node max_joint_step_rad 0.014
ros2 param set /left_follower_bridge_node  max_joint_step_rad 0.014

## 5. 异常停机（立刻执行）

pkill -f "ros2 launch openarmx_bringup"
pkill -f "ros2 launch openarmx_teleop_bridge"
pkill -f mini_udp_sender_bimanual.py
pkill -f mini_udp_sender.py

## 6. 五类常见故障分流

1. 启动即失败
- 优先看 CAN 名称是否匹配（can0/can1 不一定固定）。

2. Sender 报缺包
- 检查是否在 .venv。

3. 有主端数据但无跟随动作
- 检查 bridge 输出话题与控制器话题是否一致。

4. 动作突跳或抖动
- 先降 max_joint_step_rad，再提高 smoothing_alpha，适当增大 deadband。

5. 接近极限位置异响/碰撞
- 立即停机，收紧软限位后再测试。

## 7. 收尾与记录（当天必须）

1. 记录本机实际串口与 CAN 映射。
2. 记录最终稳定参数（速度、滤波、死区、软限位）。
3. 记录异常现象与对应处理，写入调试汇总文档。

执行标准：
- 单臂稳定 1 分钟 + 双臂稳定 1 分钟
- 无碰撞、无持续抖动、无持续报错
- 才可进入下一轮提速或业务任务
