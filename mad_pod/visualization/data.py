from dataclasses import dataclass

from ..vector import Vector


class VisualizationStopCommand: pass

@dataclass
class PodVisualizationData:
    pos: Vector
    ang: float

@dataclass
class VisualizationData:
    checkpoints: list[Vector]
    pods: list[PodVisualizationData]
