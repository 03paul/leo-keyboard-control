import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class KeyboardControl(Node):
    def __init__(self):
        super().__init__("keyboard_control")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.linear_speed = 0.12
        self.angular_speed = 0.5
        self.get_logger().info("W/S = vor/zurück, A/D = drehen, SPACE = stop, Q = quit")

    def get_key(self):
        settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ""
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def publish_cmd(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.pub.publish(msg)

    def run(self):
        while rclpy.ok():
            key = self.get_key()

            if key == "w":
                self.publish_cmd(self.linear_speed, 0.0)
            elif key == "s":
                self.publish_cmd(-self.linear_speed, 0.0)
            elif key == "a":
                self.publish_cmd(0.0, self.angular_speed)
            elif key == "d":
                self.publish_cmd(0.0, -self.angular_speed)
            elif key == " ":
                self.publish_cmd(0.0, 0.0)
            elif key == "q":
                self.publish_cmd(0.0, 0.0)
                break


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardControl()
    try:
        node.run()
    finally:
        node.publish_cmd(0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()