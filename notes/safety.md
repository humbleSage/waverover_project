# Wave Rover Safety Guide

## Safety Note

Early tests are capped at 35% throttle.

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

## After Code Changes

- Test at low speed.
- Prefer wheels off floor first.
- Verify direction before floor driving.
- Verify that releasing the trigger stops motion.
- Verify that stopping nodes or losing commands stops the rover.

## Stop Immediately If

- Rover moves unexpectedly.
- Rover does not stop after trigger release.
- Steering/direction is wrong.
- Wheels spin unexpectedly at startup.
- ROS nodes/topics behave strangely.
- Network/controller behavior becomes unreliable.

## Watchdog / Command Loss Behavior

- The rover should stop when command messages stop arriving.
- If this behavior changes, treat it as a safety issue.
- Do not continue driving until stop behavior is confirmed again.

## Emergency Procedure

1. Release throttle.
2. Center left stick.
3. Pick up rover by the chassis only if safe.
4. Power off rover.
5. Kill ROS nodes if needed.
6. Diagnose before retrying.