from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    right_udp_bind_host = DeclareLaunchArgument("right_udp_bind_host", default_value="127.0.0.1")
    right_udp_bind_port = DeclareLaunchArgument("right_udp_bind_port", default_value="17777")
    left_udp_bind_host = DeclareLaunchArgument("left_udp_bind_host", default_value="127.0.0.1")
    left_udp_bind_port = DeclareLaunchArgument("left_udp_bind_port", default_value="17778")

    publish_rate_hz = DeclareLaunchArgument("publish_rate_hz", default_value="100.0")

    right_input_topic = DeclareLaunchArgument("right_input_topic", default_value="/teleop/right/leader/joint_state")
    left_input_topic = DeclareLaunchArgument("left_input_topic", default_value="/teleop/left/leader/joint_state")

    right_output_topic = DeclareLaunchArgument(
        "right_output_topic", default_value="/right_forward_position_controller/commands"
    )
    left_output_topic = DeclareLaunchArgument(
        "left_output_topic", default_value="/left_forward_position_controller/commands"
    )

    right_mini_node = Node(
        package="openarmx_teleop_bridge",
        executable="mini_leader_node",
        name="mini_right_leader_node",
        output="screen",
        parameters=[
            {
                "udp_bind_host": LaunchConfiguration("right_udp_bind_host"),
                "udp_bind_port": LaunchConfiguration("right_udp_bind_port"),
                "publish_topic": LaunchConfiguration("right_input_topic"),
                "publish_rate_hz": LaunchConfiguration("publish_rate_hz"),
            }
        ],
    )

    left_mini_node = Node(
        package="openarmx_teleop_bridge",
        executable="mini_leader_node",
        name="mini_left_leader_node",
        output="screen",
        parameters=[
            {
                "udp_bind_host": LaunchConfiguration("left_udp_bind_host"),
                "udp_bind_port": LaunchConfiguration("left_udp_bind_port"),
                "publish_topic": LaunchConfiguration("left_input_topic"),
                "publish_rate_hz": LaunchConfiguration("publish_rate_hz"),
            }
        ],
    )

    right_follower_node = Node(
        package="openarmx_teleop_bridge",
        executable="follower_bridge_node",
        name="right_follower_bridge_node",
        output="screen",
        parameters=[
            {
                "input_topic": LaunchConfiguration("right_input_topic"),
                "output_topic": LaunchConfiguration("right_output_topic"),
                "arm_side": "right",
                "max_joint_step_rad": 0.012,
                "max_gripper_step_m": 0.0012,
                "smoothing_alpha": 0.45,
                "joint_deadband_rad": 0.0025,
                "gripper_deadband_m": 0.0006,
                # Tighten shoulder inward limit (joint_2) to avoid hard-stop collision.
                "joint_min_rad": [-1.10, 0.05, -1.40, 0.00, -1.40, -0.80, -1.20],
                "joint_max_rad": [1.10, 1.50, 1.40, 2.00, 1.40, 0.80, 1.20],
                "gripper_min_m": 0.0005,
                "gripper_max_m": 0.043,
            }
        ],
    )

    left_follower_node = Node(
        package="openarmx_teleop_bridge",
        executable="follower_bridge_node",
        name="left_follower_bridge_node",
        output="screen",
        parameters=[
            {
                "input_topic": LaunchConfiguration("left_input_topic"),
                "output_topic": LaunchConfiguration("left_output_topic"),
                "arm_side": "left",
                "max_joint_step_rad": 0.012,
                "max_gripper_step_m": 0.0012,
                "smoothing_alpha": 0.45,
                "joint_deadband_rad": 0.0025,
                "gripper_deadband_m": 0.0006,
                # Tighten shoulder inward limit (joint_2) to avoid hard-stop collision.
                "joint_min_rad": [-1.10, -1.50, -1.40, 0.00, -1.40, -0.80, -1.20],
                "joint_max_rad": [1.10, -0.05, 1.40, 2.00, 1.40, 0.80, 1.20],
                "gripper_min_m": 0.0005,
                "gripper_max_m": 0.043,
            }
        ],
    )

    return LaunchDescription(
        [
            right_udp_bind_host,
            right_udp_bind_port,
            left_udp_bind_host,
            left_udp_bind_port,
            publish_rate_hz,
            right_input_topic,
            left_input_topic,
            right_output_topic,
            left_output_topic,
            right_mini_node,
            left_mini_node,
            right_follower_node,
            left_follower_node,
        ]
    )
