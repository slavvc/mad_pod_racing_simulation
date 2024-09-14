import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

def s(x):
    x = max(0, min(1, x))
    return 3*x*x-2*x*x*x

boost_used = False
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"

    thrust_dist = s(next_checkpoint_dist * 0.00025)
    thrust_angle = s((90 - abs(next_checkpoint_angle)) * 0.015)
    thrust = int(100 * thrust_dist * thrust_angle)

    use_boost = not boost_used and abs(next_checkpoint_angle) < 10 and next_checkpoint_dist >= 5000
    if use_boost:
        boost_used = True

    print(f"{next_checkpoint_dist}, {next_checkpoint_angle}; {thrust_dist}, {thrust_angle}", file=sys.stderr, flush=True)
    print(f"{next_checkpoint_x} {next_checkpoint_y} {'BOOST' if use_boost else thrust}")
