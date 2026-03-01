#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class SimpleProcessorNode(Node):
    """
    Node B: Subscribes to relayed image, processes it, publishes a debug image.
    Replace the processing block with your real detection later.
    """

    def __init__(self):
        super().__init__("simple_processor_node")

        self.declare_parameter("input_topic", "/perception/image_raw")
        self.declare_parameter("output_topic", "/perception/debug_image")
        self.declare_parameter("queue_size", 10)

        self.input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        self.output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        self.queue_size = self.get_parameter("queue_size").get_parameter_value().integer_value

        self.bridge = CvBridge()

        self.pub = self.create_publisher(Image, self.output_topic, self.queue_size)
        self.sub = self.create_subscription(Image, self.input_topic, self.cb, self.queue_size)

        self.get_logger().info(f"Processing: {self.input_topic}  ->  {self.output_topic}")

    def cb(self, msg: Image) -> None:
        try:
            bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"cv_bridge conversion failed: {e}")
            return

        # --- "processing" example (replace later) ---
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        out = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        h, w = out.shape[:2]
        cv2.putText(out, f"Processor OK | {w}x{h}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.circle(out, (w // 2, h // 2), 10, (255, 0, 0), -1)
        # ------------------------------------------

        try:
            out_msg = self.bridge.cv2_to_imgmsg(out, encoding="bgr8")
            out_msg.header = msg.header
            self.pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f"publish failed: {e}")


def main():
    rclpy.init()
    node = SimpleProcessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()