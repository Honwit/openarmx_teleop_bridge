from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    udp_bind_host = DeclareLaunchArgument("udp_bind_host", default_value="127.0.0.1")
    udp_bind_port = DeclareLaunchArgument("udp_bind_port", default_value="17777")
    publish_rate_hz = DeclareLaunchArgument("publish_rate_hz", default_value="100.0")

    input_topic = DeclareLaunchArgument("input_topic", default_value="/teleop/leader/joint_state")
    output_topic = DeclareLaunchArgument(
        "output_topic", default_value="/right_forward_position_controller/commands"
    )

    mini_node = Node(
        package="openarmx_teleop_bridge",
        executable="mini_leader_node",
        name="mini_leader_node",
        output="screen",
        parameters=[
            {
                "udp_bind_host": LaunchConfiguration("udp_bind_host"),
                "udp_bind_port": LaunchConfiguration("udp_bind_port"),
                "publish_topic": LaunchConfiguration("input_topic"),
                "publish_rate_hz": LaunchConfiguration("publish_rate_hz"),
            }
        ],
    )

    follower_node = Node(
        package="openarmx_teleop_bridge",
        executable="follower_bridge_node",
        name="follower_bridge_node",
        output="screen",
        parameters=[
            {
                "input_topic": LaunchConfiguration("input_topic"),
                "output_topic": LaunchConfiguration("output_topic"),
            }
        ],
    )

    return LaunchDescription(
        [
            udp_bind_host,
            udp_bind_port,
            publish_rate_hz,
            input_topic,
            output_topic,
            mini_node,
            follower_node,
        ]
    )
