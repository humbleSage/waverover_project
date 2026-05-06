# Wave Rover Project

Wave Rover is my first ROS 2 mobile robotics project. It serves as a development platform for learning teleoperation, sensing, testing workflows, drivetrain behavior, and semi-autonomous rover behavior.

The current goal is to turn this platform into a **semi-autonomous teleop scout**: a small rover that can be remotely driven for check-ins, telepresence, and environmental monitoring, with room to grow into more autonomous patrol behavior later.

## Project Vision

### Version 0

Wave Rover v0 is the working development baseline.

Current v0 focus:
- reliable manual teleop
- usable camera-based scout driving
- LiDAR-assisted obstacle blocking
- repeatable launch files
- documented safety and bring-up workflows
- drive/control tuning before moving to v1 features

### Version 1

Wave Rover v1 is intended to become a more polished:

- semi-autonomous teleop scout
- remote check-in rover, similar to a mobile security camera
- environmental monitoring platform
- testbed for control interfaces including laptop, game controller, smartphone, and VR/Quest

Likely v1 features include:
- Quest/VR-oriented viewing or control experiments
- richer scout interface ideas
- improved camera/perception hardware
- more polished drive controls
- whimsical scout features after the core platform is stable

### Version 2

Future goals for Wave Rover include:

- autonomous docking and charging
- scheduled patrol routes
- more persistent remote monitoring behavior
- improved autonomy and assisted-driving behavior

### Longer-Term Purpose

This project is also a gateway to designing and building a more robust **outdoor scout / patrol robot** over the next few months.

The current Wave Rover is not expected to be the final outdoor rover. It is the learning platform for developing the software, control, sensing, testing, and systems-engineering habits needed for that future platform.

## Current Status

Current development is focused on establishing a trustworthy mobility, teleoperation, sensing, and testing baseline.

Working baseline:

- ROS 2 workspace is up and running
- core rover packages are in progress under `src/`
- controller teleop is working
- manual driving with a PS5-style controller is working
- right-trigger throttle behavior is working
- `joy_to_cmdvel` publishes `/cmd_vel_raw`
- `obstacle_assist_node` filters `/cmd_vel_raw` and `/scan` into `/cmd_vel`
- `cmd_vel_to_serial` sends `/cmd_vel` to the rover hardware
- RPLIDAR publishes `/scan`
- LiDAR-assisted forward obstacle blocking is working
- Brio/uStreamer scout camera feed is working
- rover stops cleanly when controller/node commands stop arriving
- watchdog behavior has been tested and is currently acceptable
- automated motion testing is working
- a rover test harness exists under `tests/`
- basic forward / reverse / pivot motion tuning has begun
- multi-machine development workflow is working
- Linux laptop is the main Git/development machine
- rover Pi is the runtime/test target
- Mac mini is used for mission control, planning, and remote access
- Windows PC is available for future VR, simulation, Unity/Quest, and special-purpose tooling

## Current Architecture

### Control Pipeline

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

### Camera Pipeline

```
Logitech Brio
  ↓
uStreamer on rover Pi
  ↓
browser stream
```

#### Current camera URL:

`http://waverover.local:8080/stream?advance_headers=1`

The Brio camera feed is not currently handled through the ROS 2 image pipeline.

### LiDAR Pipeline

```
RPLIDAR A1
  ↓
rplidar_node
  ↓
/scan
  ↓
obstacle_assist_node and RViz
```

#### Known-good LiDAR baseline:
- Device path: `/dev/ttyUSB0`
- Frame ID: `laser`
- Approximate `/scan` rate: 7.9–8 Hz

## Repository Structure

```
waverover_project/
├── config/              # Configuration files
├── notes/               # Project notes, runbooks, safety notes, controller maps, references
├── src/                 # ROS 2 packages and project source
│   ├── rplidar_ros/
│   ├── waverover_base/
│   ├── waverover_control/
│   ├── waverover_safety/
│   └── waverover_project/
├── tests/               # Test scripts and motion test harnesses
├── build/               # ROS 2 workspace build artifacts (local, not source)
├── install/             # ROS 2 workspace install artifacts (local, not source)
└── log/                 # ROS 2 workspace log artifacts (local, not source)
```

## Documentation

Useful project notes live under `notes/`.

Current notes include or should include:
- `runbook.md` — known-good launch and operating steps
- `safety.md` — stop behavior, watchdog notes, LiDAR assist safety, and power-off safety
- `controller_map.md` — current controller mapping and reserved controls
- `bom.md` — living bill of materials
- future docs split — after v0, this project should likely move toward a structured docs/ folder or GitHub Pages-style documentation site

## Current Development Focus

Right now the project is focused on:
1. keeping manual teleop reliable and repeatable
2. keeping Scout Mode launch files working
3. documenting the known-good baseline
4. improving testability and development workflow
5. tuning speed, trim, throttle curve, and controller feel
6. preparing for later odometry, mapping, Quest/VR, and richer scout features

## Motion Testing

The current test workflow is meant to answer a simple but important question:

When the rover is commanded to move, what actually happens, and does it happen consistently enough to build on?

The current test harness supports repeatable motion phases such as:
- forward
- reverse
- spin left
- spin right

This stage is less about autonomy and more about creating a trustworthy motion baseline for later work like odometry, assisted driving, patrol logic, and remote operation.

## Known Findings So Far

Early findings from testing:
- low-speed straight motion is usable around the current test baseline
- pivot turns require more authority than straight motion
- pivot behavior is sensitive to floor traction
- surface conditions materially affect turning performance
- watchdog behavior affects motion testing if command updates stop
- controller teleop is now working well enough to serve as the current manual baseline
- the project has a usable testing harness and repeatable tuning workflow
- Brio/uStreamer is currently more reliable than the tested ROS 2 camera pipeline for human driving
- Brio field of view is limited and should not be considered the final camera solution
- LiDAR, uStreamer, teleop, and obstacle assist can run together from launch files
- the rover’s physical front corresponds to 180.0 degrees in the RPLIDAR scan frame
- Phase 3 LiDAR-assisted forward obstacle blocking works

## Near-Term Roadmap

### Phase 1 — Trustworthy Teleop Scout Base

Status: complete enough for current v0 baseline.

Completed:
- controller teleop works
- launch/run steps are documented
- safety behavior is documented
- controller map is documented
- `README` is being updated
- `BOM` exists as a living project document

### Phase 2 — Camera / Scout Mode

Status: complete enough for current v0 baseline.

Completed:
- Brio camera mounted and tested
- Pi sees the camera
- uStreamer browser feed works
- camera stream can be viewed from laptop/Mac
- rover can be driven while viewing the live camera feed
- direct uStreamer feed is preferred over ROS 2 camera streaming for current human driving

Known limitation:
- Brio field of view is narrow
- no more major camera work planned until the OAK-D Lite is in hand and mounted

### Phase 3 — LiDAR-Assisted Teleop / Obstacle Avoidance

Status: complete enough for current v0 baseline.

Completed:
- RPLIDAR launches cleanly
- `/scan` publishes at roughly 8 Hz
- scan data is visible in RViz
- LiDAR and teleop run together
- LiDAR, uStreamer, teleop, and obstacle assist coexist from launch files
- `obstacle_assist_node` filters `/cmd_vel_raw` into `/cmd_vel`
- forward motion is blocked when an obstacle is detected in the front LiDAR sector
- reverse and turning remain allowed
- front sector calibrated with `front_center_deg`: 180.0

Current known-good obstacle assist parameters:

```
front_center_deg: 180.0
front_half_width_deg: 25.0
stop_distance_m: 0.35
enable_speed_scaling: false
```

Speed scaling is intentionally not part of the Phase 3 closeout. Drive feel and tuning will be handled in the next phase.

### Phase 4 — Drive Feel / Controller Tuning

Next major phase before v1.

Goals:
- tune max linear speed
- tune max angular speed
- tune turn boost
- tune reverse speed
- tune throttle curve
- improve low-speed crawl behavior
- tune left/right trim
- refine obstacle assist thresholds
- test controller mode ideas
- explore possible DualSense rumble feedback when obstacle assist detects or blocks against an obstacle

Possible rumble behavior:
- light rumble when entering an obstacle warning range
- stronger pulse when forward motion is blocked
- use `/joy/set_feedback` if supported by the PS5 controller and ROS joy driver

### Phase 5 — Odometry / Encoder / Control

Odometry/control goals:
- reconfirm encoder counts are readable
- document current encoder wiring/status
- decide how encoder data enters ROS 2
- publish basic wheel/encoder data
- calculate left/right wheel distance
- publish rough /odom
- add odom -> base_link transform
- compare commanded motion vs observed motion

A ROS 2 odometry/control course may be used as a reference for this phase.

### Phase 6 — SLAM Readiness / First Mapping

Mapping goals:
- confirm `/scan` remains stable
- confirm static frame relationships are sane
- use odometry from Phase 5
- test SLAM Toolbox or another basic ROS 2 mapping path
- decide whether this platform is worth pushing further into SLAM/Nav2 or whether mapping should wait for a better platform

### Phase 7+ — VR / Quest Interface and Scout Features

Future interface goals:
- explore Quest/VR as a viewing or control interface
- decide whether VR is for viewing, driving, dashboard use, or all three
- only prototype VR control after normal teleop, camera scout mode, LiDAR assist, and drive tuning are stable
- explore additional scout features after the v0 core is trustworthy

### Physical Reliability / Fabrication Lane

Ongoing physical reliability goals:
- improve cable routing
- design small useful Fusion parts
- create simple mounts, spacers, or cable tie anchors
- revisit center-of-gravity/top-heavy concerns later
- possibly design a lower cable/ballast tray
- eventually design mounts for future camera/perception upgrades

## Notes

This repository is an active development workspace, not a finished package. Expect rapid changes, experiments, rough edges, and ongoing restructuring as the robot and workflow evolve.

## Documentation Note

I am learning robotics by building this project in real time, with help from ChatGPT and Codex for brainstorming, explanation, debugging, and documentation support.