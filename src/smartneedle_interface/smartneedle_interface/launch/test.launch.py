from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch import LaunchDescription, actions
from launch.actions import DeclareLaunchArgument

def generate_launch_description():

    smartneedle_igtl = Node(
        package = "smartneedle_interface",
        executable = "smartneedle_igtl",
    )

    virtual_needle = Node(
        package = "smartneedle_interface",
        executable = "virtual_smartneedle",
    )

    return LaunchDescription([
        smartneedle_igtl,
        virtual_needle
    ])