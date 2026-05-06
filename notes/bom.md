# Wave Rover BOM

This is a living bill of materials for the Wave Rover project. It tracks installed parts, test equipment, development machines, and planned upgrades.

Current project status:
- Scout Mode v0 is working with PS5 controller teleop, Brio/uStreamer video, RPLIDAR, and LiDAR-assisted forward obstacle blocking.
- Current command pipeline is `/cmd_vel_raw → obstacle_assist_node → /cmd_vel`.
- Next major work is drive/controller tuning before v1 features.

Status labels:

- **Installed** — currently on the rover or in active use
- **Available** — owned and available, but not currently installed
- **Planned** — intended future addition
- **TBD** — not selected yet

---

## Core Platform

| Item | Status | Notes |
|---|---|---|
| Waveshare Wave Rover | Installed | Base rover platform |
| Accessory mounting plate | Installed | Used for mounting compute/sensors |
| Stock chassis hardware | Installed | Screws, plates, standoffs, and frame parts |

---

## Compute

| Item | Status | Notes |
|---|---|---|
| Raspberry Pi 4 | Installed | Rover brain / ROS 2 runtime target |
| MicroSD card | Installed | Pi system storage |
| Linux laptop | Active | Main Git/development machine |
| Mac mini | Active | Mission control / remote access / general workflow |
| Windows PC | Available | Future VR, simulation, Unity/Quest, and special-purpose tooling |

---

## Control Interfaces

| Item | Status | Notes |
|---|---|---|
| PS5-style controller / DualSense | Active | Current manual teleop controller; possible future rumble feedback through `/joy/set_feedback` |
| Laptop keyboard/terminal control | Active | Used for SSH, ROS commands, and testing |
| Meta Quest 3S | Available | Future viewing/control interface; likely v1 feature, not part of current v0 baseline |
| Smartphone interface | Planned | Possible future control/viewing interface |

---

## Sensors

| Item | Status | Notes |
|---|---|---|
| RPLIDAR A1 | Installed | Publishes `/scan`; used for RViz testing and LiDAR-assisted obstacle avoidance |
| Logitech Brio Ultra-HD Pro | Installed | Current scout camera; streamed through uStreamer outside ROS 2; usable but limited FOV |
| OAK-D Lite | Planned | Future smart vision camera; can provide RGB video, stereo depth, and onboard CV/AI experiments |
| Encoder motors | Partially installed | Two installed, one per side, for future odometry experiments |
| IMU | TBD | Not currently confirmed/selected |
| Environmental sensors | Planned | Possible future monitoring use case |

---

## Motion / Drivetrain

| Item | Status | Notes |
|---|---|---|
| Stock Wave Rover motors | Partially replaced | Some stock motors remain installed |
| Encoder motors | Partially installed | Installed for left/right encoder feedback experiments |
| Stock wheels/tires | Installed | Current mobility baseline |
| Future traction upgrades | Planned | For later outdoor/security rover concepts |

---

## Power

| Item | Status | Notes |
|---|---|---|
| 18650 cells | Installed | Rover power system |
| Onboard Wave Rover power system | Installed | Includes charge/use power handling |
| Power switch | Installed | Physical hard-stop option |
| Battery monitoring | Available | Wave Rover platform includes power/current monitoring capability |

---

## Fabrication / Mounting

| Item | Status | Notes |
|---|---|---|
| LiDAR mount | Installed | Working for Phase 3; may need anti-twist/stability improvement later |
| Brio camera mount | Installed | Current scout camera mounting; FOV is limited, future camera/mount likely needed |
| Cable management parts | Planned | Future printed anchors/tie-downs |
| Lower cable/ballast tray | Planned | Possible future Fusion part |
| Small spacers/standoffs | Planned | Useful first fabrication practice parts |
| Future OAK-D Lite mount | Planned | Needed after OAK-D Lite is in hand and mounted |

---

## Software / ROS 2 Packages

| Item | Status | Notes |
|---|---|---|
| ROS 2 Jazzy | Installed | Current ROS 2 environment |
| `waverover_base` | Active | Includes serial bridge / rover hardware interface and Pi-side scout launch |
| `waverover_control` | Active | Includes controller teleop mapping; publishes `/cmd_vel_raw` for assisted teleop |
| `waverover_safety` | Active | Includes `obstacle_assist_node`; filters `/cmd_vel_raw` + `/scan` into `/cmd_vel` |
| `rplidar_ros` | Active | LiDAR driver package; publishes `/scan` from RPLIDAR A1 |
| `uStreamer` | Active | Streams Brio camera feed outside ROS 2 at port 8080 |
| Motion test harness | Active | Located under `tests/` |
| Runbook / safety / controller notes | Active | Located under `notes/` |

---

## Development / Test Equipment

| Item | Status | Notes |
|---|---|---|
| SSH access | Active | Used for rover Pi control and maintenance |
| Remote desktop access | Active | Used across development machines |
| GitHub repo | Active | Project source backup and sync |
| RViz | Available | Used for LiDAR and robot visualization |
| Gazebo / simulation tools | Available | Future simulation/testing lane |

---

## Planned / Future Upgrades

| Item | Status | Notes |
|---|---|---|
| Drive feel / controller tuning phase | Planned | Next major phase; tune speed, trim, throttle curve, turn behavior, and controller feel |
| DualSense rumble feedback | Planned | Possible tuning-phase feature; rumble when obstacle assist detects or blocks against an obstacle |
| Odometry publishing | Planned | Future encoder/control phase; publish `/odom` and eventually `odom → base_link` |
| Improved physical cable routing | Planned | Reliability improvement |
| Center-of-gravity improvements | Planned | Rover may be top-heavy; revisit later |
| OAK-D Lite integration | Planned | Future camera/perception upgrade; no more major camera work until it is in hand and mounted |
| VR/Quest interface | Planned | Likely v1 feature after v0 tuning and core rover behavior are stable |
| Smartphone interface | Planned | Possible future control/viewing interface |
| Outdoor scout platform | Planned | Longer-term, more rugged security/exploration rover |
| Environmental monitoring | Planned | Possible future use case after core scout behavior is stable |