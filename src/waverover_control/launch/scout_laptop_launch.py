from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='game_controller_node',
            name='game_controller_node',
            output='screen',
        ),

        Node(
            package='waverover_control',
            executable='joy_to_cmdvel',
            name='joy_to_cmdvel',
            output='screen',
        ),

        Node(
            package='image_view',
            executable='image_view',
            name='image_view',
            output='screen',
            remappings=[
                ('image', '/image_raw'),
            ],
            parameters=[{
                'image_transport': 'compressed',
            }],
        ),
    ])