#!/usr/bin/env python3
import json
import socket
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


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
class LeaderRuntimeConfig:
    udp_bind_host: str
    udp_bind_port: int
    publish_topic: str
    publish_rate_hz: float


class MiniLeaderNode(Node):
    def __init__(self) -> None:
        super().__init__("mini_leader_node")

        self.declare_parameter("udp_bind_host", "127.0.0.1")
        self.declare_parameter("udp_bind_port", 17777)
        self.declare_parameter("publish_topic", "/teleop/leader/joint_state")
        self.declare_parameter("publish_rate_hz", 100.0)

        cfg = LeaderRuntimeConfig(
            udp_bind_host=self.get_parameter("udp_bind_host").value,
            udp_bind_port=int(self.get_parameter("udp_bind_port").value),
            publish_topic=self.get_parameter("publish_topic").value,
            publish_rate_hz=float(self.get_parameter("publish_rate_hz").value),
        )

        self.publisher = self.create_publisher(JointState, cfg.publish_topic, 20)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((cfg.udp_bind_host, cfg.udp_bind_port))
        self.sock.setblocking(False)

        self.last_positions = [0.0] * len(JOINT_ORDER)
        period = 1.0 / max(cfg.publish_rate_hz, 1.0)
        self.timer = self.create_timer(period, self._on_timer)

        self.get_logger().info(
            f"Mini leader UDP receiver listening on {cfg.udp_bind_host}:{cfg.udp_bind_port}, rate={cfg.publish_rate_hz}Hz"
        )

    def _on_timer(self) -> None:
        while True:
            try:
                data, _ = self.sock.recvfrom(65535)
            except BlockingIOError:
                break
            try:
                payload = json.loads(data.decode("utf-8"))
                pos = payload.get("position", [])
                if isinstance(pos, list) and len(pos) == len(JOINT_ORDER):
                    self.last_positions = [float(x) for x in pos]
            except Exception:
                continue

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_ORDER
        msg.position = self.last_positions
        self.publisher.publish(msg)

    def destroy_node(self) -> bool:
        try:
            self.sock.close()
        except Exception:
            pass
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = MiniLeaderNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
