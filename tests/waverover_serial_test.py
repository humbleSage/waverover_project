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

	def close(self):
		self.ser.close()

if __name__ == "__main__":
	rover = WaveRover()

	try:
		rover.forward(0.2)
		time.sleep(1.0)

		rover.stop()
		time.sleep(0.5)

		rover.left(0.2)
		time.sleep(0.8)

		rover.right(0.2)
		time.sleep(0.8)

		rover.backward(0.2)
		time.sleep(1.0)

		rover.stop()
	finally:
		rover.close()
