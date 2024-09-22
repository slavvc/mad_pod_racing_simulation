import math

def get_relative_angle(angle: float, reference: float) -> float:
    return (angle + math.pi - reference) % (2 * math.pi) - math.pi

def clamp(x: float, a: float, b: float) -> float:
    return min(max(x, a), b)

def degrees(rad: float) -> float:
    return rad * 180 / math.pi