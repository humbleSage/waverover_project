# Wave Rover Safety Guide

## Safety Note

Early tests are capped at low throttle.

LiDAR obstacle assist is a helper, not a guarantee. Always drive as if the rover can still miss an obstacle, lose network, misunderstand direction, or behave unexpectedly.

## Current Normal Safety Stack

Current Scout Mode v0 command pipeline:

```
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
motors
```

The obstacle assist node currently blocks forward motion when an obstacle is detected in the front LiDAR sector.

### Current limits:

- Reverse is still allowed.
- Turning is still allowed.
- Side/rear obstacles are not blocked.
- Low objects, reflective objects, thin objects, pets, cables, fabric, and fast motion may not be detected reliably.
- The Brio camera has limited field of view.
- Physical power-off remains the final stop option.

## Normal Stop

- Release right trigger.
- Center left stick.
- Confirm rover stops.

## Immediate Stop
- Release throttle.
- Center left stick.
- Pick up rover by the chassis only if safe.
- Keep fingers clear of wheels.
- Set rover down safely.

## Hard Stop

- Release throttle.
- Pick up rover by the chassis if needed and safe.
- Power off rover.
- Stop ROS nodes if needed.
- Do not restart until the issue is understood.

## Before Driving

- Use open floor space.
- Keep away from stairs, pets, cables, drinks, and edges.
- Start at low throttle.
- Confirm controller, network, and robot are connected.
- Confirm rover orientation before moving.
- Confirm the rover has room to stop or be picked up safely.
- Confirm the camera feed is live if driving by camera.
- Confirm LiDAR is running if relying on obstacle assist.

## Assisted Teleop Checks

#### Before assisted driving, confirm:

`ros2 topic list | grep -E "scan|cmd_vel"`

#### Expected topics:

```
/scan
/cmd_vel_raw
/cmd_vel
```

#### Check topic wiring:

```
ros2 topic info /cmd_vel_raw
ros2 topic info /cmd_vel
```

#### Expected:
- `/cmd_vel_raw` has a publisher from `joy_to_cmdvel`.
- `/cmd_vel_raw` has a subscriber from `obstacle_assist_node`.
- `/cmd_vel` has a publisher from `obstacle_assist_node`.
- `/cmd_vel` has a subscriber from `cmd_vel_to_serial`.

#### Do not drive if:
- `/scan` is missing.
- `/cmd_vel_raw` is missing.
- `/cmd_vel` is missing.
- Multiple unexpected publishers are sending to `/cmd_vel`.
- Obstacle assist is expected but not running.

### Obstacle Assist Test

Before relying on obstacle assist after code or launch changes:
1. Place an obstacle directly in front of the rover.
2. Apply very low forward throttle.
3. Confirm forward motion is blocked.
4. Confirm reverse still works.
5. Confirm turning still works.
6. Move obstacle to the side.
7. Confirm forward motion is not falsely blocked.

Known-good Phase 3 parameters:

```
front_center_deg: 180.0
front_half_width_deg: 25.0
stop_distance_m: 0.35
enable_speed_scaling: false
```

### After Code Changes
- Test at low speed.
- Prefer wheels off floor first.
- Verify direction before floor driving.
- Verify that releasing the trigger stops motion.
- Verify that stopping nodes or losing commands stops the rover.
- Verify /cmd_vel_raw → obstacle_assist_node → /cmd_vel wiring before assisted driving.
- Re-test obstacle assist behavior if LiDAR, teleop, launch files, or command topics changed.

### Stop Immediately If
- Rover moves unexpectedly.
- Rover does not stop after trigger release.
- Steering/direction is wrong.
- Wheels spin unexpectedly at startup.
- ROS nodes/topics behave strangely.
- Network/controller behavior becomes unreliable.
- Obstacle assist blocks constantly or fails to block a clear front obstacle.
- Camera feed freezes while driving by camera.
- LiDAR stops publishing while relying on obstacle assist.

### Watchdog / Command Loss Behavior
- The rover should stop when command messages stop arriving.
- If this behavior changes, treat it as a safety issue.
- Do not continue driving until stop behavior is confirmed again.

### Emergency Procedure
1. Release throttle.
2. Center left stick.
3. Pick up rover by the chassis only if safe.
4. Power off rover.
5. Kill ROS nodes if needed.
6. Diagnose before retrying.