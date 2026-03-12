#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

import cv2
import numpy as np

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

from .geometry_utils import classify_contour

class BlueContourDetector(Node):
    def __init__(self):
        super().__init__("blue_contour_detector")

        # ---- Parameters ----
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("debug_topic", "/blue_contours/debug")

        # RGB intrinsics for 424x240 Gazebo camera
        self.declare_parameter("fx", 570.34)
        self.declare_parameter("fy", 570.34)
        self.declare_parameter("cx", 319.5)
        self.declare_parameter("cy", 239.5)

        # Constant depth assumption (meters)
        self.declare_parameter("z_const", 0.3)

        # Detection tuning
        self.declare_parameter("min_area", 20.0)
        self.declare_parameter("max_results", 10)

        # HSV thresholds for blue
        self.declare_parameter("h_low", 100)
        self.declare_parameter("h_high", 130)
        self.declare_parameter("s_low", 100)
        self.declare_parameter("v_low", 100)

        # Morphology kernel
        self.declare_parameter("kernel_size", 5)
        self.declare_parameter("open_iters", 1)
        self.declare_parameter("close_iters", 1)

        self.bridge = CvBridge()

        image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        debug_topic = self.get_parameter("debug_topic").get_parameter_value().string_value

        self.sub = self.create_subscription(Image, image_topic, self.image_cb, 10)
        self.pub_debug = self.create_publisher(String, debug_topic, 10)

        self.get_logger().info(f"Subscribed to: {image_topic}")
        self.get_logger().info(f"Publishing debug to: {debug_topic}")

    def pixel_to_xyz(self, u: float, v: float, z_m: float, fx: float, fy: float, cx: float, cy: float):
        X = (u - cx) * (z_m - 0.01) / fx
        Y = (v - cy) * (z_m - 0.01) / fy
        return X, Y, z_m

    def process_image(self, bgr: np.ndarray):
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        h_low = self.get_parameter("h_low").value
        h_high = self.get_parameter("h_high").value
        s_low = self.get_parameter("s_low").value
        v_low = self.get_parameter("v_low").value

        lower = np.array([h_low, s_low, v_low], dtype=np.uint8)
        upper = np.array([h_high, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower, upper)

        k = self.get_parameter("kernel_size").value
        if k % 2 == 0: k += 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=self.get_parameter("open_iters").value)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=self.get_parameter("close_iters").value)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results = []
        min_area = self.get_parameter("min_area").value

        for c in contours:
            area = cv2.contourArea(c)
            if area < min_area:
                continue

            M = cv2.moments(c)
            if M["m00"] == 0: continue
            
            u = int(M["m10"] / M["m00"])
            v = int(M["m01"] / M["m00"])
            
            shape_type = classify_contour(c)
            results.append((u, v, area, shape_type, c))

        results.sort(key=lambda t: t[2], reverse=True)
        return mask, results

    def image_cb(self, msg: Image):
        try:
            bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge error: {e}")
            return

        mask, detections = self.process_image(bgr)

        fx = self.get_parameter("fx").value
        fy = self.get_parameter("fy").value
        cx = self.get_parameter("cx").value
        cy = self.get_parameter("cy").value
        z_const = self.get_parameter("z_const").value
        max_results = self.get_parameter("max_results").value

        vis = bgr.copy()

        for i, (u, v, area, shape_type, contour) in enumerate(detections[:max_results]):
            X, Y, Z = self.pixel_to_xyz(u, v, z_const, fx, fy, cx, cy)
            label = f"{shape_type}: Z={Z:.3f}"

            color = (255, 0, 0) # Blue in BGR
            if shape_type == "line": color = (0, 255, 0)
            elif shape_type == "curve": color = (0, 165, 255) # Orange-ish

            cv2.drawContours(vis, [contour], -1, color, 2)
            cv2.circle(vis, (u, v), 3, color, -1)
            cv2.putText(vis, label, (u + 10, v - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Publish string message as requested
            msg_str = f"shape: {shape_type}, z: {Z:.3f}"
            self.pub_debug.publish(String(data=msg_str))

        # Show visualization
        try:
            cv2.imshow("Detection", vis)
            cv2.waitKey(1)
        except Exception:
            pass

def main():
    rclpy.init()
    node = BlueContourDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
