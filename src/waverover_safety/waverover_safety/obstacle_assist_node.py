#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleAssistNode(Node):
    def __init__(self):
        super().__init__("obstacle_assist_node")

        # LiDAR sector tuning.
        # On this rover, the physical front is 180 degrees in the laser frame.
        self.declare_parameter("front_center_deg", 180.0)
        self.declare_parameter("front_half_width_deg", 25.0)

        # Obstacle behavior.
        self.declare_parameter("stop_distance_m", 0.35)
        self.declare_parameter("slow_distance_m", 0.70)
        self.declare_parameter("enable_speed_scaling", False)
        self.declare_parameter("enabled", True)

        # Debug sector logging for calibration.
        self.declare_parameter("debug_sectors", False)

        self.latest_scan = None

        self.create_subscription(Twist, "/cmd_vel_raw", self.cmd_callback, 10)
        self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.get_logger().info("Obstacle assist node started.")
        self.get_logger().info("Input:  /cmd_vel_raw + /scan")
        self.get_logger().info("Output: /cmd_vel")
        self.get_logger().info(
            "Defaults: front_center_deg=180.0, "
            "front_half_width_deg=25.0, stop_distance_m=0.35"
        )

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def cmd_callback(self, msg: Twist):
        if not self.get_parameter("enabled").value or self.latest_scan is None:
            self.cmd_pub.publish(msg)
            return

        filtered_cmd = self.copy_twist(msg)

        if self.get_parameter("debug_sectors").value:
            self.log_sector_distances()

        # Only block/scale forward motion.
        # Reverse and turning remain available so the rover can escape.
        if msg.linear.x <= 0.0:
            self.cmd_pub.publish(filtered_cmd)
            return

        front_distance = self.get_front_distance()

        if front_distance is None:
            self.get_logger().warn(
                "No valid front-sector LiDAR readings. Passing command through.",
                throttle_duration_sec=1.0,
            )
            self.cmd_pub.publish(filtered_cmd)
            return

        stop_distance = self.get_parameter("stop_distance_m").value
        slow_distance = self.get_parameter("slow_distance_m").value
        speed_scaling_enabled = self.get_parameter("enable_speed_scaling").value

        if front_distance <= stop_distance:
            filtered_cmd.linear.x = 0.0
            self.get_logger().warn(
                f"Forward blocked. Front obstacle at {front_distance:.2f} m.",
                throttle_duration_sec=1.0,
            )

        elif speed_scaling_enabled and front_distance < slow_distance:
            scale = self.compute_speed_scale(front_distance, stop_distance, slow_distance)
            filtered_cmd.linear.x = msg.linear.x * scale

            self.get_logger().info(
                f"Forward slowed. Front obstacle at {front_distance:.2f} m. "
                f"Scale={scale:.2f}.",
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

    def get_front_distance(self):
        return self.get_sector_min_distance(
            center_deg=self.get_parameter("front_center_deg").value,
            half_width_deg=self.get_parameter("front_half_width_deg").value,
        )

    def get_sector_min_distance(self, center_deg: float, half_width_deg: float):
        scan = self.latest_scan
        center_rad = math.radians(center_deg)
        half_width_rad = math.radians(half_width_deg)

        min_distance = None

        for index, distance in enumerate(scan.ranges):
            if not self.is_valid_range(distance, scan):
                continue

            angle = scan.angle_min + index * scan.angle_increment
            relative_angle = self.normalize_angle(angle - center_rad)

            if -half_width_rad <= relative_angle <= half_width_rad:
                if min_distance is None or distance < min_distance:
                    min_distance = distance

        return min_distance

    def is_valid_range(self, distance: float, scan: LaserScan) -> bool:
        if math.isinf(distance) or math.isnan(distance):
            return False

        return scan.range_min <= distance <= scan.range_max

    def normalize_angle(self, angle_rad: float) -> float:
        return math.atan2(math.sin(angle_rad), math.cos(angle_rad))

    def compute_speed_scale(
        self,
        distance: float,
        stop_distance: float,
        slow_distance: float,
    ) -> float:
        if slow_distance <= stop_distance:
            return 0.0

        scale = (distance - stop_distance) / (slow_distance - stop_distance)
        return max(0.0, min(1.0, scale))

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

        readings = []

        for label, center_deg in sectors:
            distance = self.get_sector_min_distance(
                center_deg=center_deg,
                half_width_deg=15.0,
            )

            if distance is None:
                readings.append(f"{label}: none")
            else:
                readings.append(f"{label}: {distance:.2f}m")

        front_distance = self.get_front_distance()
        front_text = "front: none" if front_distance is None else f"front: {front_distance:.2f}m"

        self.get_logger().info(
            " | ".join(readings) + f" || {front_text}",
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