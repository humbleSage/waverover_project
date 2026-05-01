import serial
import json
import time
from datetime import datetime
from contextlib import nullcontext
from pathlib import Path

# Waveshare General Driver Board is connected to the Pi's primary UART (ttyAMA0).
PORT = "/dev/ttyAMA0"
BAUD = 115200
TIMEOUT = 0.1

# Motor and test tuning parameters.
TEST_SPEED = 0.18
TEST_PIVOT_SPEED = TEST_SPEED * 1.4
TEST_DURATION = 3.0
SETTLE_TIME = 1.0
BETWEEN_TESTS = 1.0
MANUAL_FEEDBACK_TIME = 0.5

# Define the number of logs to keep. Old logs will be deleted when new ones are created.
MAX_LOGS = 10

# Remove old log files, keeping only the most recent MAX_LOGS files.
def cleanup_logs():
    log_files = sorted(Path(".").glob("rover_test_*.jsonl"))
    old_logs = log_files[:-MAX_LOGS]

    for log in old_logs:
        log.unlink()
        print(f"Deleted old log: {log}")

# Send the formatted JSON command to the rover, followed by a newline. Flush to ensure it's sent immediately.
def send(ser, cmd: dict) -> None:
    line = json.dumps(cmd) + "\n"
    print(f">>> {line.strip()}")
    ser.write(line.encode("utf-8"))
    ser.flush()

# Send a stop command to the rover (L=0, R=0) to ensure it halts.
def stop_rover(ser) -> None:
    send(ser, {"T": 1, "L": 0.0, "R": 0.0})

# Safely decode bytes to a UTF-8 string, replacing any invalid sequences and stripping whitespace.
def safe_decode(data: bytes) -> str:
    return data.decode("utf-8", errors = "replace").strip()

# Continuously read lines from the serial port for a specified duration, printing them with a phase prefix.
# If a log_file is provided, also write the raw lines to the log with timestamps and phase information.
def read_feedback_for(ser, duration: float, phase_name: str, log_file = None) -> None:
    end = time.monotonic() + duration
    while time.monotonic() < end:
        raw = ser.readline()
        if not raw:
            continue

        line = safe_decode(raw)
        print(f"<<< [{phase_name}] {line}")

        if log_file:
            timestamp = time.time()
            log_file.write(
                json.dumps({
                    "ts": timestamp,
                    "phase": phase_name,
                    "raw": line,
                })
                + "\n"
            )

# Run a single test phase by sending the specified motor commands, reading feedback for the duration,
# then stopping the rover and allowing it to settle before the next phase.
def run_phase(ser, name: str, left: float, right: float, duration: float, log_file = None) -> None:
    print(f"\n=== {name} ===")
    print(f"Command: L={left:.3f}, R={right:.3f}, Duration={duration:.1f}s")

    send(ser, {"T": 1, "L": left, "R": right})
    read_feedback_for(ser, duration, name, log_file = log_file)

    print(f"--- Stopping after {name} ---")
    stop_rover(ser)
    read_feedback_for(ser, SETTLE_TIME, f"{name}_settle", log_file = log_file)

    print(f"--- Pause {BETWEEN_TESTS:.1f}s ---")
    time.sleep(BETWEEN_TESTS)

def write_log(log_file, phase_name: str, raw: str) -> None:
    if not log_file:
        return
    
    log_file.write(
        json.dumps({
            "ts": time.time(),
            "phase": phase_name,
            "raw": raw,
        })
        + "\n"
    )

def send_manual_command(ser, log_file, name: str, left: float, right: float) -> None:
    send(ser, {"T": 1, "L": left, "R": right})
    write_log(log_file, "manual", name)
    read_feedback_for(ser, MANUAL_FEEDBACK_TIME, f"manual_{name}", log_file=log_file)

def run_manual_mode(ser, log_file = None) -> None:
    print("=== MANUAL MODE CONTROLS ===")
    print("w: FORWARD")
    print("s: REVERSE")
    print("a: SPIN LEFT")
    print("d: SPIN RIGHT")
    print("x: STOP")
    print("q: QUIT")

    while True:
        key = input("MANUAL >>> ").strip().lower()

        if key == "w":
            send_manual_command(ser, log_file, "forward", TEST_SPEED, TEST_SPEED)
        elif key == "s":
            send_manual_command(ser, log_file, "reverse", -TEST_SPEED, -TEST_SPEED)
        elif key == "a":
            send_manual_command(ser, log_file, "spin_left", -TEST_PIVOT_SPEED, TEST_PIVOT_SPEED)
        elif key == "d":
            send_manual_command(ser, log_file, "spin_right", TEST_PIVOT_SPEED, -TEST_PIVOT_SPEED)
        elif key == "x":
            send_manual_command(ser, log_file, "stop", 0.0, 0.0)
        elif key == "q":
            print("Exiting manual mode.")
            stop_rover(ser)
            write_log(log_file, "manual", "quit")
            break
        else:
            print(f"Unknown command: {key}.\nPlease use w/s/a/d/x/q.")

def main():
    ser = serial.Serial(PORT, BAUD, timeout = TIMEOUT)
    print(f"Opened {PORT} @ {BAUD}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"./logs/rover_test_{timestamp}.jsonl"

    print("Turning echo + continuous feedback on...")
    send(ser, {"T": 143, "cmd": 1})  # echo on
    send(ser, {"T": 131, "cmd": 1})  # continuous feedback on

    # Define the test phases with their respective motor commands.
    # Add new test phases here as needed, ensuring to give them unique names.
    phases = [
        ("forward", TEST_SPEED, TEST_SPEED),
        ("reverse", -TEST_SPEED, -TEST_SPEED),
        ("spin_left", -TEST_PIVOT_SPEED, TEST_PIVOT_SPEED),
        ("spin_right", TEST_PIVOT_SPEED, -TEST_PIVOT_SPEED),
    ]

    # Menu for selecting test mode. In LOOP mode, all phases will run.
    print("Please choose a test mode:")
    print("1. LOOP: Run all phases sequentially.")
    print("2. MANUAL: Run a single phase (for manual testing).")
    mode = input(">>> ").strip().lower()

    # Do NOT log every test. Enable logging only when necessary.
    save_logs = input("Save logs to file? (y/N) >>> ").strip().lower() == "y"

    if save_logs:
        print(f"Logging to {log_path}")
    else:
        print("Logging disabled.")

    try:
        # In LOOP mode, run through all defined phases sequentially.
        if mode == "1" or mode == "loop":
            if save_logs:
                log_context = open(log_path, "w", encoding = "utf-8")
            else:
                log_context = nullcontext(None)

            with log_context as log_file:
                print("\nStarting test loop in 3 seconds. Press Ctrl+C to stop early.\n")
                time.sleep(3.0)

                for name, left, right in phases:
                    run_phase(
                        ser,
                        name=name,
                        left=left,
                        right=right,
                        duration=TEST_DURATION,
                        log_file=log_file,
                    )

            if save_logs:
                print(f"\nTest loop complete. Logs saved to {log_path}")
                cleanup_logs()

        # In MANUAL mode, allow the user to select a single phase to run repeatedly until they stop it.
        elif mode == "2" or mode == "manual":
            if save_logs:
                log_context = open(log_path, "w", encoding = "utf-8")
            else:
                log_context = nullcontext(None)

            with log_context as log_file:
                run_manual_mode(ser, log_file = log_file)

            if save_logs:
                print(f"\nManual testing complete. Logs saved to {log_path}")
                cleanup_logs()

        else:
            print(f"Unknown mode: {mode}. Exiting.")

    # Press Ctrl+C to stop the test early.
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught. Stopping rover...")
        stop_rover(ser)
    
    finally:
        stop_rover(ser)
        time.sleep(0.5)
        print("Turning continuous feedback back off...")
        send(ser, {"T": 131, "cmd": 0})
        ser.close()
        print("Done.")

if __name__ == "__main__":
    main()