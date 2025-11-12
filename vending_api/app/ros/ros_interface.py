import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading

class RosInterface(Node):
    _instance = None
    _initialized = False

    def __init__(self):
        # init() must be called before creating a Node
        if not RosInterface._initialized:
            rclpy.init(args=None)
            RosInterface._initialized = True

        super().__init__('order_publisher_node')
        self.publisher_ = self.create_publisher(String, '/order_string', 10)

    @classmethod
    def get_instance(cls):
        """Create singleton instance safely"""
        if cls._instance is None:
            cls._instance = RosInterface()
            # Run spin in a background thread
            threading.Thread(target=rclpy.spin, args=(cls._instance,), daemon=True).start()
        return cls._instance

    def publish_order_string(self, order_string: str):
        """Publish order string to /order_string topic"""
        msg = String()
        msg.data = order_string
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published order string: {order_string}')
