#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImageRelayNode(Node):
    """
    Node A: Subscribes to camera image and republishes it to an internal topic.
    Useful for decoupling camera drivers from processing and for topic remapping.
    """

    def __init__(self):
        super().__init__("image_relay_node")

        self.declare_parameter("input_topic", "/camera/color/image_raw")
        self.declare_parameter("output_topic", "/perception/image_raw")
        self.declare_parameter("queue_size", 10)

        self.input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        self.output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        self.queue_size = self.get_parameter("queue_size").get_parameter_value().integer_value

        self.pub = self.create_publisher(Image, self.output_topic, self.queue_size)

        self.sub = self.create_subscription(
            Image,
            self.input_topic,
            self.cb,
            self.queue_size,
        )

        self.get_logger().info(f"Relaying: {self.input_topic}  ->  {self.output_topic}")

    def cb(self, msg: Image) -> None:
        # Keep header (stamp + frame_id) unchanged
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = ImageRelayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()