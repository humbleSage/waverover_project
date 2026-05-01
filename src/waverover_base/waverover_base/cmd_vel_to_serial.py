import json
import time
import serial

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelToSerial(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_serial')

        self.declare_parameter('port', '/dev/ttyAMA0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('max_motor', 0.50)
        self.declare_parameter('linear_gain', 1.0)
        self.declare_parameter('angular_gain', 1.35)
        self.declare_parameter('timeout_sec', 0.5)

        port = self.get_parameter('port').get_parameter_value().string_value
        baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.max_motor = self.get_parameter('max_motor').get_parameter_value().double_value
        self.linear_gain = self.get_parameter('linear_gain').get_parameter_value().double_value
        self.angular_gain = self.get_parameter('angular_gain').get_parameter_value().double_value
        self.timeout_sec = self.get_parameter('timeout_sec').get_parameter_value().double_value

        self.ser = serial.Serial(port, baudrate, timeout = 1)
        time.sleep(0.5)

        self.last_cmd_time = time.time()
        self.last_left = 0.0
        self.last_right = 0.0

        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.timer = self.create_timer(0.1, self.watchdog_callback)

        self.get_logger().info(
            f'cmd_vel_to_serial listening on /cmd_vel, writing to {port}'
        )

    def clamp(self, value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    def send_tank(self, left: float, right: float):
        left = self.clamp(left, -self.max_motor, self.max_motor)
        right = self.clamp(right, -self.max_motor, self.max_motor)

        cmd = {
            "T": 1,
            "L": round(left, 3),
            "R": round(right, 3)
        }

        line = json.dumps(cmd) + '\n'
        self.ser.write(line.encode('utf-8'))
        self.ser.flush()

        self.last_left = left
        self.last_right = right

    def stop(self):
        try:
            self.send_tank(0.0, 0.0)
        except Exception:
            pass

    def cmd_vel_callback(self, msg: Twist):
        linear = msg.linear.x * self.linear_gain
        angular = msg.angular.z * self.angular_gain

        # Tank Mix
        left = linear - angular
        right = linear + angular

        self.send_tank(left, right)
        self.last_cmd_time = time.time()

    def watchdog_callback(self):
        if time.time() - self.last_cmd_time > self.timeout_sec:
            if abs(self.last_left) > 1e-4 or abs(self.last_right) > 1e-4:
                self.get_logger().warn('cmd_vel timeout, stopping rover')
                self.stop()

    def destroy_node(self):
        self.stop()
        try:
            self.ser.close()
        except Exception:
            pass
        super().destroy_node()

def main(args = None):
    rclpy.init(args = args)
    node = CmdVelToSerial()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

