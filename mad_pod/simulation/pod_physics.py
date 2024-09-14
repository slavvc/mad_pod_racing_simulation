import vector
import numpy as np
from dataclasses import dataclass, field

from ..constants import POD_ROTATION_SPEED, POD_SPEED_REDUCTION
from .utils import get_relative_angle


@dataclass
class PodControl:
    thrust: float
    target_angle: float

@dataclass
class Pod:
    pos: vector.VectorObject2D
    vel: vector.VectorObject2D
    ang: float

@dataclass
class Pods:
    pods: list[Pod] = field(default_factory=lambda: [])

    def add(self, pod: Pod):
        self.pods.append(pod)
    
    def __getitem__(self, i: int) -> Pod:
        return self.pods[i]
    
    def __len__(self):
        return len(self.pods)
    
    def __iter__(self):
        return iter(self.pods)
    
    def move(self, pod_controls: list[PodControl]):
        if len(self.pods) != len(pod_controls):
            raise RuntimeError("number of pod_controls must be equal to number of pods")
        for pod, pod_control in zip(self.pods, pod_controls):
            relative_angle = get_relative_angle(pod_control.target_angle, pod.ang)
            pod.ang += np.clip(relative_angle, -POD_ROTATION_SPEED, POD_ROTATION_SPEED)
            pod.vel += pod_control.thrust * vector.obj(x=1, y=0).rotateZ(pod.ang)
            pod.pos += pod.vel
            pod.vel *= POD_SPEED_REDUCTION
        
