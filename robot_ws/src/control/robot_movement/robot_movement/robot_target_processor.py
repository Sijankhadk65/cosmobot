#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import cv2
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

class RobotCoordinates(Node):
    def __init__(self):
        super().__init__('robot_coordinates')

        self.image_sub = self.create_subscription(
            String, '/red_dots/debug_image', self.callback, 10)
        self.coords_pub = self.create_publisher(String, '/robot_coordinates', 10)

        self.x_offset = 0.30
        self.y_offset = 0.0
        self.z_offset = 0.50

    def callback(self, msg):
        values = msg.data.split(":")[1].strip().split(",")
        x,y,z = [float(v) for v in values]
        RB_x = self.x_offset - x
        RB_y = y + self.y_offset
        RB_z = self.z_offset - z
        self.get_logger().info(f"RB_x:{RB_x}, RB_y: {RB_y}, RB_z: {RB_z}")
        out_msg =f"red,{RB_x:.3f},{RB_y:.3f},0.200"
        self.coords_pub.publish(String(data=out_msg))
        
def main(args=None):
    rclpy.init(args=args)
    node = RobotCoordinates()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()