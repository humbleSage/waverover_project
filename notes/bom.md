# Wave Rover BOM

This is a living bill of materials for the Wave Rover project. It tracks installed parts, test equipment, development machines, and planned upgrades.

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
| PS5-style controller / DualSense | Active | Current manual teleop controller |
| Laptop keyboard/terminal control | Active | Used for SSH, ROS commands, and testing |
| Meta Quest 3S | Planned | Future viewing/control interface; not part of current baseline |
| Smartphone interface | Planned | Possible future control/viewing interface |

---

## Sensors

| Item | Status | Notes |
|---|---|---|
| RPLIDAR A1 | Installed | Publishes `/scan`; used for LiDAR/RViz testing |
| Basic webcam | Installed | Current placeholder scout camera for simple video streaming |
| OAK-D Lite | Planned | Future smart vision camera; can provide RGB video, stereo depth, and onboard CV/AI experiments |
| Encoder motors | Partially installed | Two installed, one per side, for odometry experiments |
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
| LiDAR mount | Installed | May need anti-twist/stability improvement later |
| Cable management parts | Planned | Future printed anchors/tie-downs |
| Lower cable/ballast tray | Planned | Possible future Fusion part |
| Small spacers/standoffs | Planned | Useful first fabrication practice parts |
| Camera mount | TBD | Needed for scout mode; pan-tilt removed from near-term plan |

---

## Software / ROS 2 Packages

| Item | Status | Notes |
|---|---|---|
| ROS 2 Jazzy | Installed | Current ROS 2 environment |
| `waverover_base` | Active | Includes serial bridge / rover hardware interface |
| `waverover_control` | Active | Includes controller-to-`/cmd_vel` teleop mapping |
| `rplidar_ros` | Active | LiDAR driver package |
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
| Basic camera stream | Planned | Next scout-mode milestone |
| VR/Quest interface | Planned | Only after normal teleop + camera scout mode are stable |
| Odometry publishing | Planned | Future encoder/control phase |
| Assisted obstacle behavior | Planned | First simple autonomy behavior |
| Improved physical cable routing | Planned | Reliability improvement |
| Center-of-gravity improvements | Planned | Rover may be top-heavy; revisit later |
| Outdoor scout platform | Planned | Longer-term, more rugged security/exploration rover |
| OAK-D Lite integration | Planned | Future camera/perception upgrade after basic webcam streaming works |