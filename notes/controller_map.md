# Wave Rover Controller Map

## Current Controller Mode

Manual teleop using PS5-style controller through ROS 2 joy input.

## Motion Controls

| Control | Function | Notes |
|---|---|---|
| Left stick up/down | Forward / reverse | Primary drive axis |
| Left stick left/right | Turn left / right | Primary steering axis |
| Right trigger | Throttle / speed scaling | Released = stopped or low/no throttle; pressed = more speed |

## Current Safety Behavior

- Releasing throttle or left stick should stop commanded motion.
- If controller/node commands stop arriving, watchdog stops rover.
- Power-off remains final physical stop option.

## Future Mappings

| Control | Possible function |
|---|---|
| Left trigger | Pull-to-listen |
| L1/R1 | Mode switching or speed profile |
| Face buttons | Lights, snapshot, push-to-talk, behavior toggles |

## DualSense/PS5 Controller Map (0-Indexed)

### Axes
| Axis | Control | Input | Range |
|---|---|---|---|
| axes[0] | left stick horizontal | left -> right | +1.0 -> -1.0 |
| axes[1] | left stick vertical | forward/up -> back/down  | +1.0 -> -1.0 |
| axes[2] | right stick horizontal | left -> right | +1.0 -> -1.0 |
| axes[3] | right stick vertical | up -> down | +1.0 -> -1.0|
| axes[4] | left trigger | released -> pressed | 0.0 -> -1.0 |
| axes[5] | right trigger | released -> pressed | 0.0 -> -1.0 |

### Buttons
| Button Index | Label |
|---|---|
| buttons[0] | X |
| buttons[1] | Circle |
| buttons[2] | Square |
| buttons[3] | Triangle |
| buttons[9] | L1 |
| buttons[10] | R1 |

### Current Intended Control Scheme

| Input | Mapping |
|---|---|
| Left stick vertical | forward / reverse |
| Left stick horizontal | turn left / right |
| Right trigger | throttle / speed scale |
| Right stick | unused / reserved |
| L1/R1 | reserved for mode/speed profile |
| Face buttons | reserved for lights/snapshot/PTT/behavior toggles |
| Left trigger | reserved for pull-to-listen |