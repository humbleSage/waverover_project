import serial
import time

class WaveRover:
    def __init__(self, port = "/dev/ttyAMA0", baudrate = 115200, timeout = 1):
        self.ser = serial.Serial(port, baudrate, timeout = timeout)
        time.sleep(0.5)

    def send_raw(self, cmd: str):
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode("utf-8"))
        self.ser.flush()

    def move_tank(self, left: float, right: float):
        cmd = f'{{"T":1, "L":{left}, "R":{right}}}\n'
        self.send_raw(cmd)

    def stop(self):
        self.move_tank(0.0, 0.0)

    def forward(self, speed: float = 0.2):
        self.move_tank(speed, speed)

    def backward(self, speed: float = 0.2):
        self.move_tank(-speed, -speed)

    def left(self, speed: float = 0.2):
        self.move_tank(-speed, speed)

    def right(self, speed: float = 0.2):
        self.move_tank(speed, -speed)

    def forward_for(self, duration: float, speed: float = 0.2):
        self.forward(speed)
        time.sleep(duration)
        self.stop()

    def backward_for(self, duration: float, speed: float = 0.2):
        self.backward(speed)
        time.sleep(duration)
        self.stop()

    def left_for(self, duration: float, speed: float = 0.2):
        self.left(speed)
        time.sleep(duration)
        self.stop()

    def right_for(self, duration: float, speed: float = 0.2):
        self.right(speed)
        time.sleep(duration)
        self.stop()

    def close(self):
        self.ser.close()

def main():
    rover = WaveRover()

    try:
        print("Behavior: forward, stop, left, stop, forward, stop.")
        rover.forward_for(0.5, 0.2)
        time.sleep(0.5)

        rover.left_for(0.6, 0.4)
        time.sleep(0.5)

        rover.forward_for(0.5, 0.2)
        time.sleep(0.5)

    finally:
        rover.stop()
        rover.close()

if __name__ == "__main__":
    main()
