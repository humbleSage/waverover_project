import serial
import time
import json

PORT = "/dev/ttyAMA0"
BAUD = 115200

def send_cmd(ser, obj, pause = 0.2):
    line = json.dumps(obj) + "\n"
    print(f">>> {line.strip()}")
    ser.write(line.encode("utf-8"))
    ser.flush()
    time.sleep(pause)

def main():
    ser = serial.Serial(PORT, BAUD, timeout = 0.2)
    print(f"Opened {ser.name} @ {BAUD}")

    # Clear any junk already buffered.
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    # Turn on echo so you can see your own commands if the board supports it.
    send_cmd(ser, {"T": 143, "cmd": 1})

    # Turn on continuous feedback mode.
    send_cmd(ser, {"T": 131, "cmd": 1})

    # One-shot queries too.
    send_cmd(ser, {"T": 126})   # IMU data
    send_cmd(ser, {"T": 130})


    print("\nListening for 20 seconds...\n")
    start = time.time()

    while time.time() - start < 20:
        raw = ser.readline()
        if not raw:
            continue

        try:
            text = raw.decode("utf-8", errors = "replace").strip()
        except Exception:
            print("RAW BYTES:" , raw)
            continue

        if not text:
            continue

        print("<<<", text)

    print("\nTurning continuous feedback back off...")
    send_cmd(ser, {"T": 131, "cmd": 0}, pause = 0.1)

    ser.close()
    print("Done.")

if __name__ == "__main__":
    main()
