from __future__ import annotations
from dataclasses import dataclass
from numbers import Number

import math


@dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other: Vector) -> Vector:
        return Vector(x=self.x + other.x, y=self.y + other.y)
    
    def __sub__(self, other: Vector) -> Vector:
        return Vector(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: float) -> Vector:
        return Vector(x=self.x * other, y=self.y * other)
    
    def __rmul__(self, other: float) -> Vector:
        return self * other

    def __truediv__(self, other: float) -> Vector:
        return Vector(x=self.x / other, y=self.y / other)
    
    @property
    def rho(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def phi(self) -> float:
        return math.atan2(self.y, self.x)
    
    def rotate(self, angle: float) -> Vector:
        sin = math.sin(angle)
        cos = math.cos(angle)
        return Vector(
            x=cos * self.x - sin * self.y,
            y=sin * self.x + cos * self.y
        )