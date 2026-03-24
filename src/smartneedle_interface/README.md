# Package: smartneedle_interface

## Description
Reads the needle shape ROS2 topic: 
  '/needle/state/current_shape' (geometry_msgs.msg.PoseArray)
Packages into IGTL messages:
  'IGTL_STRING_OUT' (ros2_igtl_bridge.msg.String) - For the header
  'IGTL_POINT_OUT' (ros2_igtl_bridge.msg.PointArray) - For the shape points coordinates
Creates OpenIGTLink server and pushes IGTL messages when new /needle/state/current_shape is published

## Usage <a name="usage"></a>

Remember to install [OpenIGTLink](https://github.com/openigtlink/OpenIGTLink)

To build workspace packages:
```bash
  colcon build --cmake-args -DOpenIGTLink_DIR:PATH=<insert_path_to_openigtlink>/OpenIGTLink-build --symlink-install
```

#### Running:
To use the smartneedle interface with OpenIGTLink connection bridge
1. Run your needle publisher node in a different terminal and launch:
```bash
  ros2 run smartneedle_interface bridge.launch.py
```
If needed, you can adjust optional arguments for post and ip
Default arguments:
  mode:=server
  port:=18944
  ip:=localhost

Example:
```bash
  ros2 run smartneedle_interface bridge.launch.py ip:=192.168.2.21
```
