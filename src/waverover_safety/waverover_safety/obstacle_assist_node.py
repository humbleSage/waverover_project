#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class ObstacleAssistNode(Node):
    def __init__(self):
        super().__init__('obstacle_assist_node')
        
        self.declare_parameter("front_angle_deg", 25.0)
        self.declare_parameter("stop_distance_m", 0.35)
        self.declare_parameter("slow_distance_m", 0.70)
        self.declare_parameter("enable_speed_scaling", False)
        self.declare_parameter("enabled", True)

        self.latest_scan = None

        self.cmd_sub = self.create_subscription(
            Twist,
            "/cmd_vel_raw",
            self.cmd_callback,
            10,
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10,
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10,
        )

        self.get_logger().info("Obstacle Assist Node has been started.")
        self.get_logger().info("Input: /cmd_vel_raw (Twist), /scan (LaserScan)")
        self.get_logger().info("Output: /cmd_vel (Twist)")

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def cmd_callback(self, msg: Twist):
        enabled = self.get_parameter("enabled").value

        if not enabled or self.latest_scan is None:
            self.cmd_pub.publish(msg)
            return
        
        filtered_cmd = Twist()
        filtered_cmd.linear.x = msg.linear.x
        filtered_cmd.linear.y = msg.linear.y
        filtered_cmd.linear.z = msg.linear.z
        filtered_cmd.angular.x = msg.angular.x
        filtered_cmd.angular.y = msg.angular.y
        filtered_cmd.angular.z = msg.angular.z

        # Only interfere with forward motion.
        if msg.linear.x <= 0.0:
            self.cmd_pub.publish(filtered_cmd)
            return
        
        front_distance = self.get_front_min_distance()

        if front_distance is None:
            self.cmd_pub.publish(filtered_cmd)
            return
        
        stop_distance = self.get_parameter("stop_distance_m").value
        slow_distance = self.get_parameter("slow_distance_m").value
        enable_speed_scaling = self.get_parameter("enable_speed_scaling").value

        if front_distance < stop_distance:
            filtered_cmd.linear.x = 0.0
            self.get_logger().warn(
                f"Forward blocked! Obstacle at {front_distance:.2f} m. Stopping robot.",
                throttle_duration_sec=1.0,
            )

        elif enable_speed_scaling and front_distance < slow_distance:
            scale = (front_distance - stop_distance) / (slow_distance - stop_distance)
            scale = max(0.0, min(1.0, scale))
            filtered_cmd.linear.x = msg.linear.x * scale

            self.get_logger().info(
                f"Forward slowed! Obstacle at {front_distance:.2f} m. Scaling speed by {scale:.2f}.",
                throttle_duration_sec=1.0,
            )

        self.cmd_pub.publish(filtered_cmd)

    def get_front_min_distance(self):
        scan = self.latest_scan
        front_angle_deg = self.get_parameter("front_angle_deg").value
        front_angle_rad = math.radians(front_angle_deg)

        min_distance = None

        for i, distance in enumerate(scan.ranges):
            if math.isinf(distance) or math.isnan(distance):
                continue
            
            if distance < scan.range_min or distance > scan.range_max:
                continue

            angle = scan.angle_min + i * scan.angle_increment

            if -front_angle_rad <= angle <= front_angle_rad:
                if min_distance is None or distance < min_distance:
                    min_distance = distance

        return min_distance
    
def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAssistNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()