import serial
import time


class WaveRover:
    def __init__(self, port="/dev/ttyAMA0", baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(0.5)

    def send_raw(self, cmd: str):
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode("utf-8"))
        self.ser.flush()

    def move_tank(self, left: float, right: float):
        cmd = f'{{"T":1,"L":{left},"R":{right}}}\n'
        self.send_raw(cmd)

    def stop(self):
        self.move_tank(0.0, 0.0)

    def forward(self, speed: float = 0.2):
        self.move_tank(speed, speed)

    def backward(self, speed: float = 0.2):
        self.move_tank(-speed, -speed)

    def left(self, speed: float = 0.5):
        self.move_tank(-speed, speed)

    def right(self, speed: float = 0.5):
        self.move_tank(speed, -speed)

    def close(self):
        self.ser.close()


def main():
    rover = WaveRover()
    speed = 0.2

    print("WaveRover Teleop")
    print("w = forward :: s = backward :: a = left :: d = right :: space = stop :: q = quit")
    print("Type a key, then press Enter.")

    try:
        while True:
            cmd = input("> ")

            if cmd == "w":
                rover.forward(speed)
            elif cmd == "s":
                rover.backward(speed)
            elif cmd == "a":
                rover.left(speed + 0.2)
            elif cmd == "d":
                rover.right(speed + 0.2)
            elif cmd == "1":
                speed = 0.15
                print(f"Speed set to {speed}")
            elif cmd == "2":
                speed = 0.25
                print(f"Speed set to {speed}")
            elif cmd == "3":
                speed = 0.40
                print(f"Speed set to {speed}")
            elif cmd == "" or cmd == " ":
                rover.stop()
            elif cmd == "q":
                rover.stop()
                break
            else:
                print("Unknown command.")
    finally:
        rover.stop()
        rover.close()

if __name__ == "__main__":
    main()
