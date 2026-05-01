import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoyToCmdVel(Node):
    def __init__(self):
        super().__init__('joy_to_cmdvel')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)

        self.max_linear = 1.0
        self.max_angular = 1.0

        self.deadzone_horizontal = 0.20
        self.deadzone_vertical = 0.12
        self.cardinal_forward_threshold = 0.40
        self.cardinal_turn_suppress_threshold = 0.20

        self.get_logger().info('joy_to_cmdvel node started')

    def apply_deadzone(self, value: float, deadzone: float) -> float:
        if abs(value) < deadzone:
            return 0.0
        return value

    def sign_axis(self, value: float) -> float:
        if value > 0.0:
            return 1.0
        elif value < 0.0:
            return -1.0
        return 0.0

    def joy_callback(self, msg: Joy):
        left_stick_horizontal = self.apply_deadzone(msg.axes[0], self.deadzone_horizontal)
        left_stick_vertical = self.apply_deadzone(msg.axes[1], self.deadzone_vertical)
        right_trigger = msg.axes[5]

        # Trigger: released = 0.0, pressed = -1.0
        throttle = max(0.0, -right_trigger)

        # Help "mostly forward" mean straight instead of accidental diagonal
        if (
            abs(left_stick_vertical) > self.cardinal_forward_threshold
            and abs(left_stick_horizontal) < self.cardinal_turn_suppress_threshold
        ):
            left_stick_horizontal = 0.0

        # Direction intent only; trigger controls magnitude
        left_stick_horizontal = self.sign_axis(left_stick_horizontal)
        left_stick_vertical = self.sign_axis(left_stick_vertical)

        twist = Twist()
        twist.linear.x = left_stick_vertical * self.max_linear * throttle
        twist.angular.z = left_stick_horizontal * self.max_angular * throttle

        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = JoyToCmdVel()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()