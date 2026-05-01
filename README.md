# Wave Rover Project

Wave Rover is my first ROS 2 mobile robotics project. It serves as a development platform for learning teleoperation, sensing, testing workflows, drivetrain behavior, and semi-autonomous rover behavior.

The current goal is to turn this platform into a **semi-autonomous teleop scout**: a small rover that can be remotely driven for check-ins, telepresence, and environmental monitoring, with room to grow into more autonomous patrol behavior later.

## Project Vision

### Version 1

Wave Rover v1 is intended to become a:

- semi-autonomous teleop scout
- remote check-in rover, similar to a mobile security camera
- environmental monitoring platform
- testbed for control interfaces including laptop, game controller, and eventually smartphone or VR

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

Current development is focused on establishing a trustworthy mobility, teleoperation, and testing baseline.

Working baseline:

- ROS 2 workspace is up and running
- core rover packages are in progress under `src/`
- controller teleop is working
- manual driving with a PS5-style controller is working
- right-trigger throttle behavior is working
- rover stops cleanly when controller/node commands stop arriving
- watchdog behavior has been tested and is currently acceptable
- automated motion testing is working
- a rover test harness exists under `tests/`
- basic forward / reverse / pivot motion tuning has begun
- multi-machine development workflow is working
- Linux laptop is the main Git/development machine
- Pi systems are used as hardware test targets

## Repository Structure
```
waverover_project/
├── config/              # Configuration files
├── notes/               # Project notes, runbooks, safety notes, controller maps, references
├── src/                 # ROS 2 packages and project source
│   ├── rplidar_ros/
│   ├── waverover_base/
│   ├── waverover_control/
│   └── waverover_project/
├── tests/               # Test scripts and motion test harnesses
├── build/               # ROS 2 workspace build artifacts (local, not source)
├── install/             # ROS 2 workspace install artifacts (local, not source)
└── log/                 # ROS 2 workspace log artifacts (local, not source)
```

## Documentation

Useful project notes live under ```notes/```.

Current notes include or should include:
* runbook.md — known-good launch and operating steps
* safety.md — stop behavior, watchdog notes, and power-off safety
* controller_map.md — current controller mapping and reserved controls
* bom.md — living bill of materials, currently incomplete

## Current Development Focus

Right now the project is focused on:
1. keeping manual teleop reliable and repeatable
2. documenting the known-good baseline
3. improving testability and development workflow
4. understanding encoder and drivetrain behavior
5. preparing for camera-based scout mode
6. building toward remote scouting and environmental monitoring use cases

## Motion Testing

The current test workflow is meant to answer a simple but important question:

When the rover is commanded to move, what actually happens, and does it happen consistently enough to build on?

The current test harness supports repeatable motion phases such as:
* forward
* reverse
* spin left
* spin right

This stage is less about autonomy and more about creating a trustworthy motion baseline for later work like odometry, assisted driving, patrol logic, and remote operation.

## Known Findings So Far

Early findings from testing:
* low-speed straight motion is usable around the current test baseline
* pivot turns require more authority than straight motion
* pivot behavior is sensitive to floor traction
* surface conditions materially affect turning performance
* watchdog behavior affects motion testing if command updates stop
* controller teleop is now working well enough to serve as the current manual baseline
* the project has a usable testing harness and repeatable tuning workflow

## Near-Term Roadmap

### Phase 1 — Trustworthy Teleop Scout Base

Current Phase 1 status:
* controller teleop works
* launch/run steps are documented
* safety behavior is documented
* controller map is documented
* README up to date
* BOM stub still needs to be started

### Phase 2 — Camera / Scout Mode

Next scout-mode goals:
* attach and test a basic webcam
* confirm the Pi sees the camera
* get a basic camera stream working
* view camera feed from laptop or Mac
* drive the rover while viewing the live camera feed

Pan-tilt is intentionally removed from the near-term plan because the rover is already somewhat top-heavy.

### Phase 3 — LiDAR / RViz / Sensor Awareness

Sensor goals:
* confirm LiDAR still launches cleanly
* confirm `/scan` publishes
* run teleop and LiDAR together
* view live scan data in RViz
* clean up robot frames and URDF as needed

### Phase 4 — Odometry / Encoder / Control

Odometry/control goals:
* reconfirm encoder counts are readable
* document current encoder wiring/status
* decide how encoder data enters ROS 2
* publish basic wheel/encoder data
* calculate left/right wheel distance
* publish rough `/odom`
* add `odom -> base_link` transform
* compare commanded motion vs observed motion

A ROS 2 odometry/control course may be used as a reference for this phase.

### Phase 5 — Assisted Behavior

Early assisted-driving goals:
* choose one simple assisted behavior
* add obstacle warning, speed clamp, or stop behavior
* make sure teleop override always wins
* test at low speed
* document assumptions and limitations

### Phase 6 — VR / Quest Interface

Future interface goals:
* explore Quest/VR as a viewing or control interface
* decide whether VR is for viewing, driving, dashboard use, or all three
* only prototype VR control after normal teleop and camera scout mode are stable

### Phase 7 — Fabrication / Physical Reliability

Physical reliability goals:

* improve cable routing
* design small useful Fusion parts
* create simple mounts, spacers, or cable tie anchors
* revisit center-of-gravity/top-heavy concerns later
* possibly design a lower cable/ballast tray

## Notes

This repository is an active development workspace, not a finished package. Expect rapid changes, experiments, rough edges, and ongoing restructuring as the robot and workflow evolve.

## Documentation Note

I am learning robotics by building this project in real time, with help from ChatGPT and Codex for brainstorming, explanation, debugging, and documentation support.