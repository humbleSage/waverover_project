# Wave Rover Runbook
This document contains known-good bring-up steps for Wave Rover teleop and LiDAR.

---

## Project Workflow Notes

Current workflow rules:
- The robo-dev laptop is the main development machine.
- The rover Pi is a runtime/test target only.
- Do not do local development on the Pi.
- If anything is created on the Pi during testing, copy it back to the laptop/Mac before any pull, reset, sync, or deploy.
- GitHub is for backup/sharing.
- Avoid nested Git repositories or accidental submodules inside project folders.
- Before major Git operations, make a dated folder backup.

---

## PS5 Controller Teleop Bring-Up

### Goal
Drive the Wave Rover with a PS5-style controller through the custom ROS 2 stack.

### Pre-flight
- Power on the Wave Rover.
- Connect the PS5 controller to the Linux laptop.
- Make sure the laptop and rover Pi are on the same network.
- Open:
  - 1 terminal/SSH session to the rover Pi
  - 2 terminals on the Linux laptop

### Terminal Layout
| Machine | Terminal | Purpose |
|---|---|---|
| Rover Pi | Terminal 1 | Run serial bridge: `/cmd_vel` → rover hardware |
| Laptop | Terminal 1 | Run controller input node: controller → `/joy` |
| Laptop | Terminal 2 | Run custom teleop node: `/joy` → `/cmd_vel` |

---

### 1. On the Rover Pi — Start Serial Bridge

SSH into the rover Pi if needed:

```
ssh humblesage@waverover.local
```

Then run:

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_base cmd_vel_to_serial
```

Expected result:
- Bridge node starts.
- Pi is listening for `/cmd_vel`.
- Incoming velocity commands can be converted to rover serial commands.

### 2. On Laptop Terminal 1 — Start Controller Input

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run joy game_controller_node
```

Expected result:
- Controller input node starts.
- `/joy` is being published.

Optional check:

`ros2 topic echo /joy`

### 3. On Laptop Terminal 2 — Start Custom Teleop Mapping

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_control joy_to_cmdvel
```

Expected result:
- Custom mapping node starts.
- `/joy` is converted into `/cmd_vel`.

Optional check:

`ros2 topic echo /cmd_vel`

### 4. Drive

Current control behavior:

| Control | Function |
|---|---|
| Left stick | Direction / steering |
| Right trigger | Throttle / speed scaling |
| No trigger | No movement |

Safety behavior:
- Releasing the right trigger should stop commanded motion.
- Releasing the left stick should stop commanded motion.
- If controller/node commands stop arriving, the watchdog should stop the rover.
- Physical power-off remains the final stop option.

### 5. Troubleshooting Teleop

Check active topics

`ros2 topic list`

Expected topics include:

```
/joy
/cmd_vel
```

#### If `/joy` is missing or dead

Check that the controller input node is running:

`ros2 run joy game_controller_node`

Possible causes:
- Controller is not connected.
- Controller is connected to the wrong machine.
- `game_controller_node` is not running.
- ROS environment is not sourced on the laptop.

#### If `/joy` works but `/cmd_vel` is missing or dead

Check that the custom mapping node is running:

`ros2 run waverover_control joy_to_cmdvel`

Possible causes:
- `joy_to_cmdvel` is not running.
- Workspace is not sourced.
- Package was not rebuilt after changes.
- Controller mapping issue.

#### If `/cmd_vel` works but rover does not move

Check that the Pi bridge is running:

`ros2 run waverover_base cmd_vel_to_serial`

Possible causes:
- Pi bridge is not running.
- Serial port issue.
- Rover power issue.
- Watchdog is stopping motion.
- Wrong ROS domain/network issue.
- Motor command is below the movement threshold.

### 6. Shutdown Teleop

Stop nodes with `Ctrl+C` in each terminal.

Recommended shutdown order:

1. Stop `joy_to_cmdvel` on the laptop.
2. Stop `game_controller_node` on the laptop.
3. Stop `cmd_vel_to_serial` on the rover Pi.
4. Power off the rover if finished testing.

## Ultra-short Teleop Version

### Rover Pi

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_base cmd_vel_to_serial
```

### Laptop Terminal 1

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run joy game_controller_node
```

### Laptop Terminal 2

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_control joy_to_cmdvel
```

---

## LiDAR Bring-Up

### Goal

Get the RPLIDAR online, publishing `/scan`, and ready for testing.

### Pre-check

- Rover Pi is powered and reachable over SSH.
- LiDAR is physically plugged in.
- USB connection is seated firmly.
- ROS 2 shell is sourced.

### 1. SSH into Rover Pi

`ssh humblesage@waverover.local`

Or use the IP address if needed.

### 2. Source ROS 2 and Workspace

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
```

### 3. Check That the LiDAR Is Detected

```
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
lsusb
```

Expected result:
- Usually `/dev/ttyUSB0`
- Sometimes `/dev/ttyACM0`

If nothing appears:
- Unplug/replug LiDAR.
- Check cable/USB seating.
- Rerun the commands.

### 4. Launch the LiDAR Node

If the device is `/dev/ttyUSB0`:

```
ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyUSB0
```

If the device is `/dev/ttyACM0`:

```
ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyACM0
```

Expected result:
- LiDAR node starts.
- Terminal remains running.
- LiDAR begins publishing scan data.

### 5. Verify `/scan` in Another Terminal

Open a second terminal/SSH session and run:

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 topic list | grep scan
ros2 topic echo /scan --once
```

Expected result:
- `/scan` exists.
- One scan message prints.

### 6. Optional Sanity Checks

```
ros2 topic info /scan
ros2 node list
```

### 7. Troubleshooting LiDAR

#### If `/scan` does not appear

Try:

`ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null`

Then:
- Confirm the device path again.
- Unplug/replug LiDAR.
- Relaunch the LiDAR node.

#### If still broken:

Check recent USB/system messages:

`sudo dmesg | tail -n 50`

#### Common gotchas
- Do not launch RViz/view launch files on the headless Pi.
- Missing device is often a cable/USB seating problem.
- Confirm `/dev/ttyUSB0` vs `/dev/ttyACM0`.
- If replugging fixed it before, try that first.

### Success Condition

LiDAR is up when:
- Device path exists.
- Launch command stays running.
- `/scan` appears.
- `/scan` echoes one message.

### Shutdown LiDAR

In the LiDAR terminal:

`Ctrl+C`

### Current Known-Good LiDAR Baseline

- LiDAR device path: `/dev/ttyUSB0`
- Launch command:

`ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyUSB0`

- /scan appears: Yes
- Approximate /scan rate: 7.9 Hz
- Warnings/errors: None observed

---

## ROS 2 Brio Webcam Bring-Up

### Goal

Publish the mounted Logitech Brio camera as a ROS 2 image stream and view it from the laptop.

### Current Status

The mounted Brio camera is detected as `/dev/video0`.

The earlier placeholder webcam worked but had poor image quality and high latency. The Brio camera gives a much better image and tolerable latency for slow indoor scouting.

Motion was tested first and worked as a browser stream, but latency was too high for comfortable teleop. Motion is now disabled so it does not grab `/dev/video0` at boot.

### On the Rover Pi — Start Brio Camera Node

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash

ros2 run usb_cam usb_cam_node_exe --ros-args \
  -p video_device:=/dev/video0 \
  -p image_width:=640 \
  -p image_height:=480 \
  -p framerate:=15.0 \
  -p pixel_format:=mjpeg2rgb
```

Expected result:
- `usb_cam` starts successfully.
- `/image_raw` is published.
- `/image_raw/compressed` is available.
- `/camera_info` is available.

If mjpeg2rgb does not work, check supported formats:

`ros2 run usb_cam usb_cam_node_exe --ros-args -p pixel_format:="test"`

### On the Laptop — View Camera Feed

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash

ros2 run image_view image_view --ros-args \
  -r image:=/image_raw \
  -p image_transport:=compressed
```

Expected result:
- A viewer window opens on the laptop.
- The rover camera feed is visible.
- Latency is usable enough for slow indoor testing.

### Useful Checks

```
ros2 topic list
ros2 topic hz /image_raw
ros2 topic hz /image_raw/compressed
```
### Observed Brio Test Rate
- Camera feed is currently about 15 FPS.

Notes / Gotchas
- Do not run Motion at the same time as `usb_cam`; it may grab `/dev/video0`.
- Motion service has been disabled with: `sudo systemctl disable motion`.
- Viewing `/image_raw/compressed` directly may hang.
- Use `/image_raw` with `image_transport:=compressed` instead.
- The Brio is currently the working Scout Mode camera.

---

## Scout Mode v0 — Teleop + Brio Camera

### Goal

Drive the Wave Rover with the PS5-style controller while viewing the mounted Brio camera feed from the laptop.

### Current Status

Scout Mode v0 is working.

- Brio camera is physically mounted.
- Camera is slightly off-center, but the view is usable.
- Image quality is much better than the original placeholder webcam.
- Latency is tolerable for slow indoor scouting.
- Camera feed is currently about 15 FPS.
- Camera view feels roughly comparable in latency to the Enabot Rola Mini.

### Rover Pi Terminal 1 — Start Serial Bridge

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_base cmd_vel_to_serial
```

### Rover Pi Terminal 2 — Start Brio Camera

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash

ros2 run usb_cam usb_cam_node_exe --ros-args \
  -p video_device:=/dev/video0 \
  -p image_width:=640 \
  -p image_height:=480 \
  -p framerate:=15.0 \
  -p pixel_format:=mjpeg2rgb
```

#### If mjpeg2rgb does not work, check supported formats:

`ros2 run usb_cam usb_cam_node_exe --ros-args -p pixel_format:="test"`

### Laptop Terminal 1 — Start Controller Input

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run joy game_controller_node
```

### Laptop Terminal 2 — Start Custom Teleop Mapping

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 run waverover_control joy_to_cmdvel
```

### Laptop Terminal 3 — View Camera Feed

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash

ros2 run image_view image_view --ros-args \
  -r image:=/image_raw \
  -p image_transport:=compressed
  ```

### Safety Notes
- Drive slowly while using camera view.
- Confirm rover orientation before moving.
- Keep the camera cable away from wheels.
- Keep throttle low until the view/latency feels predictable.
- Teleop override and stop behavior should remain the safety baseline.

### Success Condition

Scout Mode v0 is working when:
- Controller teleop works.
- Brio camera publishes through ROS 2.
- Laptop can view the camera feed.
- Rover can be driven slowly while watching the live camera view.

---

## Scout Mode v0 Launch Files

### Goal

Start Scout Mode v0 with one launch command on the rover Pi and one launch command on the laptop.

### Current Status

Scout Mode v0 launch files are working.

The Pi-side launch file starts:

- `cmd_vel_to_serial`
- `usb_cam_node_exe` for the mounted Brio camera

The laptop-side launch file starts:

- `game_controller_node`
- `joy_to_cmdvel`
- `image_view` using compressed image transport

### Rover Pi — Start Scout Runtime

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 launch waverover_base scout_pi_launch.py
```

#### Expected result:
- Serial bridge starts.
- Brio camera starts.
- /image_raw publishes.
- /image_raw/compressed publishes.
- Rover is ready to receive /cmd_vel.

### Laptop — Start Scout Operator Stack

```
source /opt/ros/jazzy/setup.bash
source ~/robot_ws/install/setup.bash
ros2 launch waverover_control scout_laptop_launch.py
```

#### Expected result:

- Controller node starts.
- Custom teleop mapping node starts.
- Camera viewer opens.
- Controller commands publish to /cmd_vel.

#### Success Condition

Scout Mode v0 launch files are working when:
- Pi launch starts the serial bridge and Brio camera.
- Laptop launch starts controller input, teleop mapping, and camera viewer.
- Camera feed is visible on the laptop.
- Rover can be driven slowly while watching the live camera feed.
- Releasing throttle stops the rover.

### Scout + LiDAR Coexistence Baseline

Scout Mode and LiDAR can run together.

Observed working stack:

- Pi launch: `ros2 launch waverover_base scout_pi_launch.py`
- LiDAR launch: `ros2 launch rplidar_ros rplidar_a1_launch.py serial_port:=/dev/ttyUSB0`
- Laptop launch: `ros2 launch waverover_control scout_laptop_launch.py`
- `/scan` publishes
- Brio camera publishes
- Controller teleop remains functional

Known issue to investigate:

- Connection/viewing reliability degrades during combined Scout + LiDAR testing.
- Cause is not yet confirmed.
- Possible causes include Wi-Fi/network instability, Pi CPU load, USB bandwidth, image streaming overhead, or combined sensor load.