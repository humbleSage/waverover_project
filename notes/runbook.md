# Wave Rover Runbook

This document contains known-good bring-up steps for Wave Rover teleop, LiDAR-assisted obstacle avoidance, Brio/uStreamer scout camera streaming, and current launch-file workflows.

Current normal driving mode is Scout Mode v0 with LiDAR-assisted teleop:

```text
PS5 controller
  ↓
game_controller_node
  ↓
/joy
  ↓
joy_to_cmdvel
  ↓
/cmd_vel_raw
  ↓
obstacle_assist_node + /scan
  ↓
/cmd_vel
  ↓
cmd_vel_to_serial
  ↓
Wave Rover motors
```

The Brio camera feed is handled outside ROS 2 through uStreamer.

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

## Legacy / Manual PS5 Controller Teleop Bring-Up

> Note: This is now a legacy/manual baseline. The current normal driving path uses LiDAR-assisted teleop, where `joy_to_cmdvel` publishes `/cmd_vel_raw`, `obstacle_assist_node` filters it, and `cmd_vel_to_serial` receives `/cmd_vel`.

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
| Rover Pi | Terminal 1 | Run serial bridge: `/cmd_vel` → rover hardware |
| Rover Pi | Terminal 2 | Run obstacle assist: `/cmd_vel_raw` + `/scan` → `/cmd_vel` |
| Laptop | Terminal 1 | Run controller input node: controller → `/joy` |
| Laptop | Terminal 2 | Run custom teleop node: `/joy` → `/cmd_vel_raw` |

---

### 1. On the Rover Pi — Start Serial Bridge

SSH into the rover Pi if needed:

```
ssh humblesage@waverover.local
```

Then run:

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 run waverover_base cmd_vel_to_serial
```

Expected result:
- Bridge node starts.
- Pi is listening for `/cmd_vel`.
- Incoming velocity commands can be converted to rover serial commands.

### 2. On Laptop Terminal 1 — Start Controller Input

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
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
source ~/waverover_ws/install/setup.bash
ros2 run waverover_control joy_to_cmdvel
```

Expected result:
- Custom mapping node starts.
- `/joy` is converted into `/cmd_vel_raw`.
- `obstacle_assist_node` filters `/cmd_vel_raw` into `/cmd_vel`.

Optional checks:

`ros2 topic echo /cmd_vel_raw`

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
/cmd_vel_raw
/cmd_vel
/scan
```

#### If `/joy` is missing or dead

Check that the controller input node is running:

`ros2 run joy game_controller_node`

Possible causes:
- Controller is not connected.
- Controller is connected to the wrong machine.
- `game_controller_node` is not running.
- ROS environment is not sourced on the laptop.

#### If `/joy` works but `/cmd_vel_raw` is missing or dead

Check that the custom mapping node is running:

`ros2 run waverover_control joy_to_cmdvel`

Possible causes:
- `joy_to_cmdvel` is not running.
- Workspace is not sourced.
- Package was not rebuilt after changes.
- Controller mapping issue.
- `joy_to_cmdvel` should publish `/cmd_vel_raw`, not `/cmd_vel`, in the assisted teleop pipeline.

#### If `/cmd_vel_raw` works but `/cmd_vel` is missing or dead

Check that obstacle assist is running:

`ros2 run waverover_safety obstacle_assist_node`

Possible causes:
- `obstacle_assist_node` is not running.
- `/scan` is missing or LiDAR is not running.
- Workspace is not sourced.
- `waverover_safety` was not rebuilt after changes.

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
source ~/waverover_ws/install/setup.bash
ros2 run waverover_base cmd_vel_to_serial
```

### Laptop Terminal 1

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 run joy game_controller_node
```

### Laptop Terminal 2

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
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
source ~/waverover_ws/install/setup.bash
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
source ~/waverover_ws/install/setup.bash
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

---

## LiDAR-Assisted Teleop / Obstacle Avoidance

### Goal

Use the RPLIDAR to block forward motion when an obstacle is too close in front of the rover.

This is the current Phase 3 known-good driving safety layer.

### Current Status

LiDAR-assisted teleop v0.1 is working.

Current behavior:
- Forward motion is blocked when an obstacle is detected in the front LiDAR sector.
- Reverse remains allowed.
- Turning remains allowed.
- This lets the rover back away or rotate out of trouble.

### Current Control Pipeline

```
PS5 controller
  ↓
game_controller_node
  ↓
/joy
  ↓
joy_to_cmdvel
  ↓
/cmd_vel_raw
  ↓
obstacle_assist_node
  + /scan from RPLIDAR
  ↓
/cmd_vel
  ↓
cmd_vel_to_serial
  ↓
Wave Rover motors
```

### Important Topic Change

`joy_to_cmdvel` now publishes to:

`/cmd_vel_raw`

It does not publish directly to /cmd_vel in the assisted teleop pipeline.

`cmd_vel_to_serial` still listens to:

`/cmd_vel`

The obstacle assist node sits between them.

### Obstacle Assist Node

#### Package:

`waverover_safety`

#### Executable:

`obstacle_assist_node`

#### Subscriptions:

- `/cmd_vel_raw`
- `/scan`

#### Publication:

- `/cmd_vel`

### Known-Good Parameters

- front_center_deg: 180.0
- front_half_width_deg: 25.0
- stop_distance_m: 0.35
- slow_distance_m: 0.70
- enable_speed_scaling: false
- enabled: true
- debug_sectors: false

The Wave Rover’s physical front corresponds to 180.0 degrees in the RPLIDAR scan frame.

Speed scaling exists in the node, but is intentionally disabled for Phase 3 closeout. Drive feel and tuning will be handled in the next tuning phase.

### Manual Obstacle Assist Command

If testing manually on the rover Pi:

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash

ros2 run waverover_safety obstacle_assist_node
```

### Debug Sector Mode

Use this only when recalibrating LiDAR direction:

`ros2 run waverover_safety obstacle_assist_node --ros-args -p debug_sectors:=true`

### Wiring Checks

#### Check topics:

`ros2 topic list | grep cmd_vel`

#### Expected:

```
/cmd_vel
/cmd_vel_raw
```

#### Check command pipeline:

```
ros2 topic info /cmd_vel_raw
ros2 topic info /cmd_vel
```

#### Expected when both Pi and laptop launch files are running:

```
/cmd_vel_raw:
  Publisher count: 1
  Subscription count: 1

/cmd_vel:
  Publisher count: 1
  Subscription count: 1
```

#### Expected wiring:
- `/cmd_vel_raw` publisher: `joy_to_cmdvel`
- `/cmd_vel_raw` subscriber: `obstacle_assist_node`
- `/cmd_vel` publisher: `obstacle_assist_node`
- `/cmd_vel` subscriber: `cmd_vel_to_serial`

### Physical Test

Use low speed.

| Test | Expected Result |
|---|---|
| No obstacle in front, drive forward | Rover moves forward |
| Obstacle in front, drive forward | Forward motion is blocked |
| Obstacle in front, reverse | Rover backs away |
| Obstacle in front, turn | Rover turns |
| Obstacle on side only, drive forward | Forward motion is allowed |

### Known-Good Phase 3 Result

- `/scan` publishes while driving.
- `/scan` rate is approximately 8 Hz.
- RViz displays the scan.
- LiDAR, uStreamer, obstacle assist, and teleop coexist.
- Pi launcher starts `rplidar_node`, `obstacle_assist_node`, `cmd_vel_to_serial`, and uStreamer successfully.
- Final obstacle behavior test passed.

---

## Brio / uStreamer Scout Camera Bring-Up

### Goal

Run the mounted Logitech Brio as a reliable human-driving scout camera outside the ROS 2 image pipeline.

The Brio feed is used for live driving view. It does not currently publish camera images into ROS 2.

### Current Status

The mounted Brio camera is detected as `/dev/video0`.

The Brio works best as a direct MJPEG browser stream using `uStreamer`.

Current known-good camera architecture:

- ROS 2 handles rover control, LiDAR, and robot state.
- uStreamer handles the Brio scout camera feed.
- Browser view is used as the driver camera.
- The Brio is usable as the current scout camera, but field of view is limited.
- The Brio is not considered the final long-term camera.

### Known-Good uStreamer Command

On the rover Pi:

```
ustreamer \
  --device=/dev/video0 \
  --format=MJPEG \
  --resolution=640x480 \
  --desired-fps=30 \
  --host=0.0.0.0 \
  --port=8080 \
  --drop-same-frames=0
```

### Viewer URLs

#### Preferred:

```
http://waverover.local:8080/stream?advance_headers=1
```

#### Alternate:

```
http://waverover.local:8080/stream?advance_headers=1&dual_final_frames=1
```

### Expected Result

- Browser stream opens.
- Video stays alive while driving.
- Latency is good enough for slow indoor scouting.
- Pi CPU/GPU load remains low.
- No ROS camera topics are expected from uStreamer.

### Current Driving Test Result

Brio via uStreamer has been tested while driving.

#### Observed result:

- Stream stayed alive: Yes
- Latency: Good
- Freezes: None observed
- Broken-pipe disconnects: None observed
- Control remained responsive: Yes
- Lighting issues: None observed in the test environment
- Drivability: Safely drivable even under full throttle
- Main limitation: field of view is narrow / not ideal

#### Notes / Gotchas

- Do not run usb_cam, v4l2_camera, Motion, or another camera service at the same time as uStreamer.
- Motion was previously tested but had too much latency and is disabled.
- The ROS 2 webcam path was useful for learning, but is no longer the preferred Scout Mode camera path.
- The Brio is currently a temporary reliable scout camera, not the final camera.
- Future scout camera should have a wider field of view.

### Stop Camera Stream

In the uStreamer terminal:

`Ctrl+C`

Or kill any existing uStreamer process:

`pkill -f ustreamer`

---

## Legacy ROS 2 Brio Camera Notes

### Status

The ROS 2 Brio camera path is currently considered legacy/debug only.

The Brio hardware can stream well directly through V4L2/uStreamer, but the tested ROS camera paths were unreliable or inefficient for the driving camera feed.

### Observed issues:

- usb_cam dropped to very low frame rates.
- v4l2_camera could request MJPG but did not publish MJPG cleanly in this setup.
- ROS image transport added unnecessary overhead for the human-driving camera feed.
- Direct uStreamer MJPEG streaming is currently much more reliable.

### Previous ROS 2 Camera Command


```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash

ros2 run usb_cam usb_cam_node_exe --ros-args \
  -p video_device:=/dev/video0 \
  -p image_width:=640 \
  -p image_height:=480 \
  -p framerate:=15.0 \
  -p pixel_format:=mjpeg2rgb
```

### Previous Laptop Viewer Command

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash

ros2 run image_view image_view --ros-args \
  -r image:=/image_raw \
  -p image_transport:=compressed
```

### Useful Diagnostic Checks

```
v4l2-ctl -d /dev/video0 --list-formats-ext
v4l2-ctl -d /dev/video0 --list-ctrls
ros2 topic hz /image_raw
ros2 topic hz /image_raw/compressed
vcgencmd get_throttled
vcgencmd measure_temp
```

### Known Brio FOV/control note:

`zoom_absolute min=100 max=500 default=100 value=100`

The Brio is already at minimum Linux-exposed zoom, so the remaining field-of-view limitation is not fixable through v4l2-ctl zoom controls.

---

## Scout Mode v0 — Teleop + Brio/uStreamer Camera

### Goal

Drive the Wave Rover with the PS5-style controller while viewing the mounted Brio camera feed in a browser.

### Current Status

Scout Mode v0 is working.

### Current architecture:

- Rover control runs through ROS 2.
- Controller commands publish to `/cmd_vel_raw`.
- `obstacle_assist_node` filters `/cmd_vel_raw` using `/scan`.
- Filtered drive commands publish to `/cmd_vel`.
- `cmd_vel_to_serial` sends `/cmd_vel` to the rover hardware.
- Brio camera feed runs through uStreamer outside ROS 2.
- Browser is used as the driver camera view.
- RPLIDAR publishes `/scan`.

### Rover Pi Terminal 1 — Start Scout Runtime

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 launch waverover_base scout_pi_launch.py
```

#### Current Pi launch starts:

- `rplidar_node`
- `obstacle_assist_node`
- `cmd_vel_to_serial`
- uStreamer Brio camera feed

### Browser — Open Camera Feed

#### Preferred:

`http://waverover.local:8080/stream?advance_headers=1`

#### Alternate:

`http://waverover.local:8080/stream?advance_headers=1&dual_final_frames=1`

### Laptop Terminal — Start Scout Operator Stack

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 launch waverover_control scout_laptop_launch.py
```

#### Current laptop launch starts:

- `game_controller_node`
- `joy_to_cmdvel`

`joy_to_cmdvel` publishes `/cmd_vel_raw` for the assisted teleop pipeline.

### Safety Notes

- Drive slowly while using camera view.
- Confirm rover orientation before moving.
- Keep the camera cable away from wheels.
- Keep throttle low until the view/latency feels predictable.
- Teleop override and stop behavior should remain the safety baseline.
- Physical power-off remains the final stop option.

### Success Condition

#### Scout Mode v0 is working when:

- Pi launch starts the serial bridge and uStreamer camera feed.
- Browser can view the Brio stream.
- Laptop launch starts controller input and teleop mapping.
- Controller teleop works.
- Rover can be driven slowly while watching the live browser camera view.
- Releasing throttle stops the rover.
- `/scan` is publishing.
- `/cmd_vel_raw` and `/cmd_vel` are both present.
- Obstacle assist blocks forward motion when an obstacle is directly in front.

---

## Scout Mode v0 Launch Files

### Goal

Start Scout Mode v0 with one launch command on the rover Pi and one launch command on the laptop.

### Current Status

Scout Mode v0 launch files are working.

The Pi-side launch file starts:

- rplidar_node
- obstacle_assist_node
- cmd_vel_to_serial
- uStreamer for the mounted Brio camera

The laptop-side launch file starts:

- game_controller_node
- joy_to_cmdvel

The camera is viewed separately in a browser.

### Rover Pi — Start Scout Runtime

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 launch waverover_base scout_pi_launch.py
```

#### Expected result:

- Serial bridge starts.
- uStreamer starts.
- Browser stream becomes available at port 8080.
- Rover is ready to receive `/cmd_vel_raw` from the laptop.
- Obstacle assist publishes filtered `/cmd_vel` for the motor bridge.

### Laptop — Start Scout Operator Stack

```
source /opt/ros/jazzy/setup.bash
source ~/waverover_ws/install/setup.bash
ros2 launch waverover_control scout_laptop_launch.py
```

#### Expected result:

- Controller node starts.
- Custom teleop mapping node starts.
- Controller commands publish to `/cmd_vel_raw`.
- Obstacle assist filters `/cmd_vel_raw` into `/cmd_vel`.
- No image_view window opens.

### Browser — Start Driver View

`http://waverover.local:8080/stream?advance_headers=1`

---

---

## Scout + LiDAR + Obstacle Assist Baseline

Scout Mode, LiDAR, obstacle assist, and the Brio/uStreamer camera can run together from launch files.

### Observed working stack:

- Pi launch: `ros2 launch waverover_base scout_pi_launch.py`
- Laptop launch: `ros2 launch waverover_control scout_laptop_launch.py`
- Browser camera view: `http://waverover.local:8080/stream?advance_headers=1`

### Current Pi launch starts:

- `rplidar_node`
- `obstacle_assist_node`
- `cmd_vel_to_serial`
- uStreamer Brio camera feed

### Current laptop launch starts:

- `game_controller_node`
- `joy_to_cmdvel`

### Current topic pipeline:

```
/joy
  ↓
joy_to_cmdvel
  ↓
/cmd_vel_raw
  ↓
obstacle_assist_node + /scan
  ↓
/cmd_vel
  ↓
cmd_vel_to_serial
```

### Current result:

- uStreamer Brio camera feed stays alive.
- `/scan` publishes.
- `/cmd_vel_raw` publishes from laptop teleop.
- obstacle_assist_node publishes `/cmd_vel`.
- Controller teleop remains functional.
- Rover is safely drivable.
- Forward motion is blocked when an obstacle is directly in front.
- Reverse and turning remain available.
- Main remaining camera limitation is field of view.

### Known-good LiDAR baseline:

- Device path: `/dev/ttyUSB0`
- Approximate `/scan` rate: 7.9–8 Hz
- Frame ID: `laser`
- Warnings/errors: None observed during baseline test

### Known-good obstacle assist baseline:

```
front_center_deg: 180.0
front_half_width_deg: 25.0
stop_distance_m: 0.35
enable_speed_scaling: false
```

---

## Current Known Issues / TODO

### Phase 4 Drive Feel / Controller Tuning

Next major phase before v1.

Planned tuning topics:
- Max linear speed
- Max angular speed
- Turn boost
- Reverse speed
- Throttle curve
- Low-speed crawl behavior
- Left/right trim
- Obstacle assist thresholds
- Controller mode ideas
- Possible DualSense rumble feedback when obstacle assist detects or blocks against an obstacle

Initial rumble idea:
- Light rumble when entering obstacle warning range.
- Stronger pulse when forward motion is blocked.
- Use `/joy/set_feedback` if supported by the PS5 controller and ROS joy driver.

### Brio Field of View

The current Brio camera is usable for scout driving, but its field of view is limited.

#### Current status:

- Brio zoom is already at minimum using Linux-exposed controls.
- FOV is usable for now.
- Brio is not the final camera.
- Future scout camera should be wider.

### Pi Time Synchronization

The rover Pi time synchronization needs follow-up.

#### Observed issue:

- systemd-timesyncd is active but not synchronizing.
- Manual time correction allowed GitHub HTTPS/Git operations to work.
- Time sync failure may be due to NTP server, network, router/firewall, or DNS issues.

#### TODO:

- Fix Pi NTP/time sync later.
- Until fixed, check time before Git HTTPS operations.

#### Useful checks:

```
timedatectl
systemctl status systemd-timesyncd --no-pager
```

### Planned Headlights / Light Bar

A small RC light bar/headlight is planned.

#### Initial rules:

- Verify input voltage range.
- Verify current draw if available.
- Identify power wires vs control/signal wire.
- Test off-robot first.
- Confirm rover battery board output before connecting.
- Do not power LEDs from Pi GPIO.
- ROS/GPIO control comes later.

### Post-v0 Documentation Cleanup

After v0 is complete, split this runbook into a structured `docs/` folder or GitHub Pages site.

Likely structure:
- Quick Start
- Architecture
- Scout Mode Bring-Up
- LiDAR / Obstacle Assist
- Camera Streaming
- Controller Mapping
- Troubleshooting
- Phase Notes