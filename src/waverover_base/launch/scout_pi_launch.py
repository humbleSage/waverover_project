from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='waverover_base',
            executable='cmd_vel_to_serial',
            name='cmd_vel_to_serial',
            output='screen',
        ),

        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='brio_camera',
            output='screen',
            parameters=[{
                'video_device': '/dev/video0',
                'image_width': 640,
                'image_height': 480,
                'framerate': 15.0,
                'pixel_format': 'mjpeg2rgb',
            }],
        ),
    ])