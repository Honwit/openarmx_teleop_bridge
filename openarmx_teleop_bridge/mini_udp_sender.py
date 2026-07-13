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


def main() -> None:
    parser = argparse.ArgumentParser(description="Read OpenArm Mini via LeRobot and send positions over UDP.")
    parser.add_argument("--teleop-port", default="/dev/ttyACM0")
    parser.add_argument("--teleop-id", default="my_openarm_mini_right")
    parser.add_argument("--teleop-side", default="right")
    parser.add_argument("--udp-host", default="127.0.0.1")
    parser.add_argument("--udp-port", type=int, default=17777)
    parser.add_argument("--rate-hz", type=float, default=100.0)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cfg = OpenArmMiniConfig(port=args.teleop_port, id=args.teleop_id, side=args.teleop_side)
    teleop = OpenArmMini(cfg)
    teleop.connect(calibrate=False)

    period = 1.0 / max(args.rate_hz, 1.0)
    try:
        while True:
            t0 = time.perf_counter()
            action = teleop.get_action()
            payload = {
                "position": [float(action.get(f"{joint}.pos", 0.0)) for joint in JOINT_ORDER]
            }
            sock.sendto(json.dumps(payload).encode("utf-8"), (args.udp_host, args.udp_port))
            dt = time.perf_counter() - t0
            if dt < period:
                time.sleep(period - dt)
    finally:
        teleop.disconnect()
        sock.close()


if __name__ == "__main__":
    main()
