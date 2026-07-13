#!/usr/bin/env python3
import argparse
import json
import socket
import time

from lerobot.teleoperators.openarm_mini import OpenArmMini, OpenArmMiniConfig


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


def make_sender(port: str, teleop_id: str, side: str):
    cfg = OpenArmMiniConfig(port=port, id=teleop_id, side=side)
    teleop = OpenArmMini(cfg)
    teleop.connect(calibrate=False)
    return teleop


def to_payload(teleop):
    action = teleop.get_action()
    return {
        "position": [float(action.get(f"{joint}.pos", 0.0)) for joint in JOINT_ORDER]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read right+left OpenArm Mini and send positions over UDP.")
    parser.add_argument("--right-teleop-port", default="/dev/ttyACM0")
    parser.add_argument("--right-teleop-id", default="my_openarm_mini_right")
    parser.add_argument("--left-teleop-port", default="/dev/ttyACM1")
    parser.add_argument("--left-teleop-id", default="my_openarm_mini_left")

    parser.add_argument("--right-udp-host", default="127.0.0.1")
    parser.add_argument("--right-udp-port", type=int, default=17777)
    parser.add_argument("--left-udp-host", default="127.0.0.1")
    parser.add_argument("--left-udp-port", type=int, default=17778)

    parser.add_argument("--rate-hz", type=float, default=100.0)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    right = make_sender(args.right_teleop_port, args.right_teleop_id, "right")
    left = make_sender(args.left_teleop_port, args.left_teleop_id, "left")

    period = 1.0 / max(args.rate_hz, 1.0)
    try:
        while True:
            t0 = time.perf_counter()
            sock.sendto(
                json.dumps(to_payload(right)).encode("utf-8"),
                (args.right_udp_host, args.right_udp_port),
            )
            sock.sendto(
                json.dumps(to_payload(left)).encode("utf-8"),
                (args.left_udp_host, args.left_udp_port),
            )
            dt = time.perf_counter() - t0
            if dt < period:
                time.sleep(period - dt)
    finally:
        right.disconnect()
        left.disconnect()
        sock.close()


if __name__ == "__main__":
    main()
