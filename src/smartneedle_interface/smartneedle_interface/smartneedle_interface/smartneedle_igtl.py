import rclpy
import numpy as np
import datetime

from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Point
from ros2_igtl_bridge.msg import PointArray, String

################################################################################
#
# SmartNeedle Interface Node
#
# Description:
# This node gets current needle shape and pushes the needle shape to 3DSlicer
# throught OpenIGTLink bridge
#
# Subscribes:   
# '/needle/state/current_shape' (geometry_msgs.msg.PoseArray)    - needle frame
#
# Publishes:    
# 'IGTL_STRING_OUT'             (ros2_igtl_bridge.msg.String)     - needle frame
# 'IGTL_POINT_OUT'              (ros2_igtl_bridge.msg.PointArray) - needle frame
# 
#
#################################################################################


class SmartNeedleInterface(Node):

#### Node initialization###################################################

    def __init__(self):
        super().__init__('smart_needle_interface')

    #### Stored variables ###################################################

        # NeedleShape Bridge message
        self.shapecount = 0                         # Number of shape packace received
        self.shapeheader = None                     # Shape message header to push to 3D Slicer
        self.shapedata = None                       # Shape message data to push to 3D Slicer

    #### Subscribed topics ###################################################

        #Topics from smart needle node
        self.subscription_sensor = self.create_subscription(PoseArray, '/needle/state/current_shape', self.shape_callback,  10)
        self.subscription_sensor # prevent unused variable warning

    #### Published topics ###################################################

        # Needle shape (needle frame)
        timer_period_shape = 1.0 # seconds
        self.timer_shape = self.create_timer(timer_period_shape, self.timer_shape_callback)        
        self.publisher_shapeheader = self.create_publisher(String, 'IGTL_STRING_OUT', 10)
        self.publisher_shape = self.create_publisher(PointArray, 'IGTL_POINT_OUT', 10)

        # Print numpy floats with only 3 decimal places
        np.set_printoptions(formatter={'float': lambda x: "{0:0.15f}".format(x)})

#### Listening callbacks ###################################################

    # Get current sensor measurements
    def shape_callback(self, msg_sensor):
        # From shape, get tip (last point)
        self.shapecount += 1
        self.get_logger().info('Shape received = %i' %self.shapecount)
        shape = msg_sensor.poses      
        N = len(shape) 
        # Tip is last point in shape
        # TODO: If needed somewhere else, use this info to publish a tip topic
        # p_tip = np.array([shape[N-1].position.x, shape[N-1].position.y, shape[N-1].position.z]) 
        # q_tip = np.array([shape[N-1].orientation.w, shape[N-1].orientation.x, shape[N-1].orientation.y, shape[N-1].orientation.z])
        # Build shape message to push to 3D Slicer
        frame_id = 'needle'
        timestamp = msg_sensor.header.stamp
        # Convert timestamp to a readable format
        now = datetime.datetime.now()
        timestamp_duration = datetime.timedelta(seconds=timestamp.nanosec / 1e9)
        duration_since_epoch = now - timestamp_duration
        # Get the time_t object from the datetime
        time_t_object = datetime.datetime.fromtimestamp(duration_since_epoch.timestamp())
        # Format the timestamp with seconds and milliseconds
        formatted_timestamp = time_t_object.strftime('%Y-%m-%d %H:%M:%S') + '.{:03d}'.format(int(timestamp.nanosec % 1e6 / 1e3))
        self.shapeheader = formatted_timestamp + ';' +str(self.shapecount) + ';'+ str(N) + ';' + frame_id
        # Get shape data points
        self.shapedata = []
        for pose in msg_sensor.poses:
            point = Point()
            point.x = pose.position.x
            point.y = pose.position.y
            point.z = pose.position.z
            self.shapedata.append(point)

#### Publishing callbacks ###################################################

    # Publishes needle shape (robot frame) to IGTLink bridge
    def timer_shape_callback(self):
        if (self.shapedata is not None) and (self.shapeheader is not None):
            string_msg = String()
            string_msg.name = 'NeedleShapeHeader'
            string_msg.data = self.shapeheader
            pointarray_msg = PointArray()
            pointarray_msg.name = 'NeedleShape'
            pointarray_msg.pointdata = self.shapedata
            # Push shape to IGTLBridge
            self.publisher_shapeheader.publish(string_msg)
            self.publisher_shape.publish(pointarray_msg)

########################################################################

def main(args=None):
    rclpy.init(args=args)
    smart_needle_interface = SmartNeedleInterface()
    smart_needle_interface.get_logger().warn('Waiting smart_needle...')

    # Wait for smart_needle
    while rclpy.ok():
        rclpy.spin_once(smart_needle_interface)
        if smart_needle_interface.shapedata is None: # Keep loop while stage position not set
            pass
        else:
            break
    rclpy.spin(smart_needle_interface)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    smart_needle_interface.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()