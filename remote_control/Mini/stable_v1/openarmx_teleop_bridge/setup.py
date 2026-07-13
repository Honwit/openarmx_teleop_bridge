from setuptools import setup

package_name = "openarmx_teleop_bridge"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (
            f"share/{package_name}/launch",
            [
                "launch/mini_to_openarmx_single.launch.py",
                "launch/mini_to_openarmx_bimanual.launch.py",
            ],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="will",
    maintainer_email="will@example.com",
    description="Bridge Mini leader actions to OpenArmX follower command topic.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "mini_leader_node = openarmx_teleop_bridge.mini_leader_node:main",
            "follower_bridge_node = openarmx_teleop_bridge.follower_bridge_node:main",
            "mini_udp_sender = openarmx_teleop_bridge.mini_udp_sender:main",
            "mini_udp_sender_bimanual = openarmx_teleop_bridge.mini_udp_sender_bimanual:main",
        ],
    },
)
