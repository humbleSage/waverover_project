#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleAssistNode(Node):
    def __init__(self):
        super().__init__("obstacle_assist_node")

        # Front sector tuning
        self.declare_parameter("front_center_deg", 0.0)
        self.declare_parameter("front_angle_deg", 25.0)

        # Obstacle behavior
        self.declare_parameter("stop_distance_m", 0.35)
        self.declare_parameter("slow_distance_m", 0.70)
        self.declare_parameter("enable_speed_scaling", False)
        self.declare_parameter("enabled", True)

        # Debugging
        self.declare_parameter("debug_sectors", True)

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

        self.get_logger().info("Obstacle Assist Node has started.")
        self.get_logger().info("Input:  /cmd_vel_raw (Twist), /scan (LaserScan)")
        self.get_logger().info("Output: /cmd_vel (Twist)")
        self.get_logger().info(
            "Tune with: -p front_center_deg:=0.0 -p front_angle_deg:=25.0"
        )

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def cmd_callback(self, msg: Twist):
        enabled = self.get_parameter("enabled").value

        if not enabled or self.latest_scan is None:
            self.cmd_pub.publish(msg)
            return

        filtered_cmd = self.copy_twist(msg)

        debug_sectors = self.get_parameter("debug_sectors").value
        if debug_sectors:
            self.log_sector_distances()

        # Only interfere with forward motion.
        # Reverse and turning are always allowed so the rover can escape.
        if msg.linear.x <= 0.0:
            self.cmd_pub.publish(filtered_cmd)
            return

        front_distance = self.get_front_min_distance()

        if front_distance is None:
            self.get_logger().info(
                "No valid front-sector readings. Passing command through.",
                throttle_duration_sec=1.0,
            )
            self.cmd_pub.publish(filtered_cmd)
            return

        stop_distance = self.get_parameter("stop_distance_m").value
        slow_distance = self.get_parameter("slow_distance_m").value
        enable_speed_scaling = self.get_parameter("enable_speed_scaling").value

        if front_distance <= stop_distance:
            filtered_cmd.linear.x = 0.0
            self.get_logger().warn(
                f"Forward blocked. Front obstacle at {front_distance:.2f} m.",
                throttle_duration_sec=1.0,
            )

        elif enable_speed_scaling and front_distance < slow_distance:
            scale = (front_distance - stop_distance) / (slow_distance - stop_distance)
            scale = max(0.0, min(1.0, scale))
            filtered_cmd.linear.x = msg.linear.x * scale

            self.get_logger().info(
                f"Forward slowed. Front obstacle at {front_distance:.2f} m. "
                f"Scale: {scale:.2f}",
                throttle_duration_sec=1.0,
            )

        else:
            self.get_logger().info(
                f"Front clear enough. Nearest front obstacle: {front_distance:.2f} m.",
                throttle_duration_sec=1.0,
            )

        self.cmd_pub.publish(filtered_cmd)

    def copy_twist(self, msg: Twist) -> Twist:
        copied = Twist()

        copied.linear.x = msg.linear.x
        copied.linear.y = msg.linear.y
        copied.linear.z = msg.linear.z

        copied.angular.x = msg.angular.x
        copied.angular.y = msg.angular.y
        copied.angular.z = msg.angular.z

        return copied

    def get_front_min_distance(self):
        front_center_deg = self.get_parameter("front_center_deg").value
        front_angle_deg = self.get_parameter("front_angle_deg").value

        return self.get_sector_min_distance(
            center_deg=front_center_deg,
            width_deg=front_angle_deg * 2.0,
        )

    def get_sector_min_distance(self, center_deg: float, width_deg: float):
        scan = self.latest_scan

        center_rad = math.radians(center_deg)
        half_width_rad = math.radians(width_deg / 2.0)

        min_distance = None

        for i, distance in enumerate(scan.ranges):
            if math.isinf(distance) or math.isnan(distance):
                continue

            if distance < scan.range_min or distance > scan.range_max:
                continue

            angle = scan.angle_min + i * scan.angle_increment

            relative_angle = self.normalize_angle(angle - center_rad)

            if -half_width_rad <= relative_angle <= half_width_rad:
                if min_distance is None or distance < min_distance:
                    min_distance = distance

        return min_distance

    def normalize_angle(self, angle_rad: float) -> float:
        return math.atan2(math.sin(angle_rad), math.cos(angle_rad))

    def log_sector_distances(self):
        sectors = [
            ("0", 0.0),
            ("45", 45.0),
            ("90", 90.0),
            ("135", 135.0),
            ("180", 180.0),
            ("-135", -135.0),
            ("-90", -90.0),
            ("-45", -45.0),
        ]

        sector_width_deg = 30.0
        results = []

        for name, center_deg in sectors:
            distance = self.get_sector_min_distance(
                center_deg=center_deg,
                width_deg=sector_width_deg,
            )

            if distance is None:
                results.append(f"{name}: none")
            else:
                results.append(f"{name}: {distance:.2f}m")

        front_center_deg = self.get_parameter("front_center_deg").value
        front_angle_deg = self.get_parameter("front_angle_deg").value
        front_distance = self.get_front_min_distance()

        if front_distance is None:
            front_text = "front: none"
        else:
            front_text = f"front: {front_distance:.2f}m"

        self.get_logger().info(
            f"{' | '.join(results)} || "
            f"{front_text} "
            f"(center={front_center_deg:.1f}°, half-width={front_angle_deg:.1f}°)",
            throttle_duration_sec=1.0,
        )


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