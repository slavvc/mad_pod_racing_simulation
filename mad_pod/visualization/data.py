from dataclasses import dataclass

import vector


class VisualizationStopCommand: pass

@dataclass
class PodVisualizationData:
    pos: vector.VectorObject2D
    ang: float

@dataclass
class VisualizationData:
    checkpoints: list[vector.VectorObject2D]
    pods: list[PodVisualizationData]
