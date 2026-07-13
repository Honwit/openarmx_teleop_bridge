#!/usr/bin/env python3
import math
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


JOINT_ORDER = [
    "joint_1",
    "joint_2",
    "joint_3",
    "joint_4",
    "joint_5",
    "joint_6",
    "joint_7",
    "gripper",
]


@dataclass
class BridgeRuntimeConfig:
    input_topic: str
    output_topic: str
    stale_timeout_sec: float
    max_joint_step_rad: float
    max_gripper_step_m: float
    arm_side: str
    joint_min_rad: list[float]
    joint_max_rad: list[float]
    gripper_min_m: float
    gripper_max_m: float
    smoothing_alpha: float
    joint_deadband_rad: float
    gripper_deadband_m: float


# MINI reports arm joints in degrees and gripper in OpenArm follower degrees.
DEG_TO_RAD = math.pi / 180.0
GRIPPER_DEG_TO_M = 0.044 / 65.0


class FollowerBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__("follower_bridge_node")

        self.declare_parameter("input_topic", "/teleop/leader/joint_state")
        self.declare_parameter("output_topic", "/right_forward_position_controller/commands")
        self.declare_parameter("stale_timeout_sec", 0.2)
        self.declare_parameter("max_joint_step_rad", 0.03)
        self.declare_parameter("max_gripper_step_m", 0.002)
        self.declare_parameter("arm_side", "auto")  # auto|left|right
        self.declare_parameter("gripper_min_m", 0.0)
        self.declare_parameter("gripper_max_m", 0.044)
        self.declare_parameter("smoothing_alpha", 0.35)
        self.declare_parameter("joint_deadband_rad", 0.003)
        self.declare_parameter("gripper_deadband_m", 0.0007)

        output_topic = self.get_parameter("output_topic").value
        inferred_side = "left" if "left_" in output_topic else "right"
        side = self.get_parameter("arm_side").value
        if side not in {"left", "right"}:
            side = inferred_side

        # OpenArm follower defaults from robot config (deg -> rad).
        left_limits_deg = [(-75.0, 75.0), (-90.0, 9.0), (-85.0, 85.0), (0.0, 135.0), (-85.0, 85.0), (-40.0, 40.0), (-80.0, 80.0)]
        right_limits_deg = [(-75.0, 75.0), (-9.0, 90.0), (-85.0, 85.0), (0.0, 135.0), (-85.0, 85.0), (-40.0, 40.0), (-80.0, 80.0)]
        limits_deg = left_limits_deg if side == "left" else right_limits_deg
        default_joint_min_rad = [mn * DEG_TO_RAD for mn, _ in limits_deg]
        default_joint_max_rad = [mx * DEG_TO_RAD for _, mx in limits_deg]

        # Declare as DOUBLE_ARRAY explicitly by providing float defaults.
        self.declare_parameter("joint_min_rad", default_joint_min_rad)
        self.declare_parameter("joint_max_rad", default_joint_max_rad)

        user_joint_min = list(self.get_parameter("joint_min_rad").value)
        user_joint_max = list(self.get_parameter("joint_max_rad").value)
        if len(user_joint_min) != 7:
            user_joint_min = default_joint_min_rad
        if len(user_joint_max) != 7:
            user_joint_max = default_joint_max_rad

        cfg = BridgeRuntimeConfig(
            input_topic=self.get_parameter("input_topic").value,
            output_topic=output_topic,
            stale_timeout_sec=float(self.get_parameter("stale_timeout_sec").value),
            max_joint_step_rad=float(self.get_parameter("max_joint_step_rad").value),
            max_gripper_step_m=float(self.get_parameter("max_gripper_step_m").value),
            arm_side=side,
            joint_min_rad=[float(v) for v in user_joint_min],
            joint_max_rad=[float(v) for v in user_joint_max],
            gripper_min_m=float(self.get_parameter("gripper_min_m").value),
            gripper_max_m=float(self.get_parameter("gripper_max_m").value),
            smoothing_alpha=float(self.get_parameter("smoothing_alpha").value),
            joint_deadband_rad=float(self.get_parameter("joint_deadband_rad").value),
            gripper_deadband_m=float(self.get_parameter("gripper_deadband_m").value),
        )

        self.cmd_pub = self.create_publisher(Float64MultiArray, cfg.output_topic, 20)
        self.leader_sub = self.create_subscription(JointState, cfg.input_topic, self._on_leader, 20)

        self.last_msg_time = self.get_clock().now()
        self.stale_timeout_sec = max(cfg.stale_timeout_sec, 0.01)
        self.max_joint_step_rad = max(cfg.max_joint_step_rad, 0.001)
        self.max_gripper_step_m = max(cfg.max_gripper_step_m, 0.0005)
        self.arm_side = cfg.arm_side
        self.joint_min_rad = cfg.joint_min_rad
        self.joint_max_rad = cfg.joint_max_rad
        self.gripper_min_m = min(cfg.gripper_min_m, cfg.gripper_max_m)
        self.gripper_max_m = max(cfg.gripper_min_m, cfg.gripper_max_m)
        self.smoothing_alpha = min(max(cfg.smoothing_alpha, 0.0), 1.0)
        self.joint_deadband_rad = max(cfg.joint_deadband_rad, 0.0)
        self.gripper_deadband_m = max(cfg.gripper_deadband_m, 0.0)
        self.last_cmd = [0.0] * len(JOINT_ORDER)
        self.stale_timer = self.create_timer(0.05, self._on_stale_timer)

        self.get_logger().info(
            f"Follower bridge ready: {cfg.input_topic} -> {cfg.output_topic}, side={self.arm_side}, timeout={self.stale_timeout_sec}s"
        )

    def _on_leader(self, msg: JointState) -> None:
        idx_by_name = {name: i for i, name in enumerate(msg.name)}

        positions = []
        for joint in JOINT_ORDER:
            i = idx_by_name.get(joint)
            raw = float(msg.position[i]) if i is not None and i < len(msg.position) else 0.0
            if joint == "gripper":
                target = max(self.gripper_min_m, min(self.gripper_max_m, (-raw) * GRIPPER_DEG_TO_M))
            else:
                # Right arm elbow (joint_4) is mechanically mirrored; invert only this axis.
                if self.arm_side == "right" and joint == "joint_4":
                    raw = -raw
                target = raw * DEG_TO_RAD
                j = len(positions)
                target = max(self.joint_min_rad[j], min(self.joint_max_rad[j], target))
            positions.append(target)

        safe_positions = []
        for i, target in enumerate(positions):
            prev = self.last_cmd[i]
            deadband = self.gripper_deadband_m if i == 7 else self.joint_deadband_rad

            # Suppress tiny oscillations near rest.
            if abs(target - prev) < deadband:
                target = prev

            # Smooth commands before rate limiting to reduce jitter.
            target = self.smoothing_alpha * target + (1.0 - self.smoothing_alpha) * prev

            max_step = self.max_gripper_step_m if i == 7 else self.max_joint_step_rad
            delta = target - prev
            if delta > max_step:
                target = prev + max_step
            elif delta < -max_step:
                target = prev - max_step
            safe_positions.append(target)

        out = Float64MultiArray()
        out.data = safe_positions
        self.cmd_pub.publish(out)
        self.last_cmd = safe_positions
        self.last_msg_time = self.get_clock().now()

    def _on_stale_timer(self) -> None:
        dt = (self.get_clock().now() - self.last_msg_time).nanoseconds / 1e9
        if dt > self.stale_timeout_sec:
            self.get_logger().warning(
                f"Leader topic stale for {dt:.3f}s. Last command held by follower controller.",
                throttle_duration_sec=2.0,
            )


def main() -> None:
    rclpy.init()
    node = FollowerBridgeNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
