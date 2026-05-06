from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # RPLIDAR publishes /scan.
        Node(
            package="rplidar_ros",
            executable="rplidar_node",
            name="rplidar_node",
            output="screen",
            parameters=[{
                "serial_port": "/dev/ttyUSB0",
                "serial_baudrate": 115200,
                "frame_id": "laser",
                "inverted": False,
                "angle_compensate": True,
                "scan_mode": "Standard",
            }],
        ),

        # LiDAR obstacle assist:
        # /cmd_vel_raw + /scan -> /cmd_vel
        Node(
            package="waverover_safety",
            executable="obstacle_assist_node",
            name="obstacle_assist_node",
            output="screen",
            parameters=[{
                "front_center_deg": 180.0,
                "front_half_width_deg": 25.0,
                "stop_distance_m": 0.35,
                "slow_distance_m": 0.70,
                "enable_speed_scaling": False,
                "enabled": True,
                "debug_sectors": False,
            }],
        ),

        # Motor bridge:
        # /cmd_vel -> Wave Rover serial controller
        Node(
            package="waverover_base",
            executable="cmd_vel_to_serial",
            name="cmd_vel_to_serial",
            output="screen",
        ),

        # Brio camera stream.
        # View at:
        # http://waverover.local:8080/stream?advance_headers=1
        ExecuteProcess(
            cmd=[
                "ustreamer",
                "--device=/dev/video0",
                "--format=MJPEG",
                "--resolution=640x480",
                "--desired-fps=30",
                "--host=0.0.0.0",
                "--port=8080",
                "--drop-same-frames=0",
            ],
            name="brio_ustreamer",
            output="screen",
        ),
    ])