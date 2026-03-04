#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

class RedDotDetector(Node):
    def __init__(self):
        super().__init__("red_dot_detector")
        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, "/camera_head/color/image_raw", self.image_cb, 10)
        self.pub = self.create_publisher(String, "/red_dots/debug_image", 10)
        self.get_logger().info("Red Dot Detector started. Looking for red dots...")

    def image_cb(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"CvBridge Error: {e}")
            return

        # Convert to HSV and threshold for red
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Get the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 100:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    self.get_logger().info(f"Dot Position: x={cx}, y={cy}")
                    self.pub.publish(String(data=f"coords: {cx},{cy},0.0"))
                    cv2.circle(cv_image, (cx, cy), 10, (0, 255, 0), -1)
                    cv2.putText(cv_image, f"x: {cx}, y: {cy}", (cx + 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Show the image
        cv2.imshow("Red Dot Detection", cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = RedDotDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()