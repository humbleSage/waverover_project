from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='waverover_base',
            executable='cmd_vel_to_serial',
            name='cmd_vel_to_serial',
            output='screen',
        ),

        ExecuteProcess(
            cmd=[
                'ustreamer',
                '--device=/dev/video0',
                '--format=MJPEG',
                '--resolution=640x480',
                '--desired-fps=30',
                '--host=0.0.0.0',
                '--port=8080',
                '--drop-same-frames=0',
            ],
            name='brio_ustreamer',
            output='screen',
        ),
    ])