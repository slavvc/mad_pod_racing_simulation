import math

def get_relative_angle(angle: float, reference: float) -> float:
    return (angle + math.pi - reference) % (2 * math.pi) - math.pi