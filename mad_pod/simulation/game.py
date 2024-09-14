from __future__ import annotations
import vector
import numpy as np
from dataclasses import dataclass

from ..constants import WORLD_H, WORLD_W, CHECKPOINT_RADIUS
from .pod_physics import Pods, Pod, PodControl
from .utils import get_relative_angle
from ..strategy_communication.messages import StrategyInput, StrategyOutput
from ..visualization.data import VisualizationData, PodVisualizationData

@dataclass
class Game:
    pods: Pods
    checkpoints: list[vector.VectorObject2D]
    pods_next_checkpoint: list[int]
    pods_laps: list[int]

    @classmethod
    def create(cls, number_of_pods: int, number_of_checkpoints: int) -> Game:
        if number_of_checkpoints < 2:
            raise RuntimeError("number_of_checkpoints must be >= 2")
        if number_of_pods < 1:
            raise RuntimeError("number_of_pods must be >= 1")
        checkpoints = []
        for i in range(number_of_checkpoints):
            x = np.random.randint(int(WORLD_W*0.1), int(WORLD_W*0.9))
            y = np.random.randint(int(WORLD_H*0.1), int(WORLD_H*0.9))
            checkpoints.append(vector.obj(x=x, y=y))
        pods = Pods()
        for i in range(number_of_pods):
            pods.add(Pod(
                pos=checkpoints[0],
                vel=vector.obj(x=0, y=0),
                ang=0
            ))
        return Game(
            pods=pods,
            checkpoints=checkpoints,
            pods_next_checkpoint=[1]*number_of_pods,
            pods_laps=[3]*number_of_pods
        )

    def get_strategy_input(self, pod_number: int) -> StrategyInput:
        pod = self.pods[pod_number]
        checkpoint_pos = self.checkpoints[self.pods_next_checkpoint[pod_number]]
        pod_pos = pod.pos
        checkpoint_vect: vector.VectorObject2D = checkpoint_pos - pod_pos # type: ignore
        checkpoint_dist = checkpoint_vect.rho
        checkpoint_angle = get_relative_angle(checkpoint_vect.phi, pod.ang)
        if len(self.pods) >= 2:
            enemy_pod = self.pods[(pod_number + 1) % len(self.pods)]
            enemy_pos = enemy_pod.pos
        else:
            enemy_pos = vector.obj(x=0, y=0)

        return StrategyInput(
            pod_pos=(int(pod_pos.x), int(pod_pos.y)),
            checkpoint_pos=(int(checkpoint_pos.x), int(checkpoint_pos.y)),
            checkpoint_dist=int(checkpoint_dist),
            checkpoint_angle=int(np.degrees(checkpoint_angle)),
            enemy_pos=(int(enemy_pos.x), int(enemy_pos.y))
        )

    @dataclass
    class ResultWin:
        pod_number: int

    class ResultContinue:
        pass

    def step(self, strategy_outputs: list[StrategyOutput]) -> Game.ResultWin | Game.ResultContinue:
        if len(strategy_outputs) != len(self.pods):
            raise RuntimeError("number of strategy outputs is not equal to number of pods")
        pod_controls = []
        for pod, strategy_output in zip(self.pods, strategy_outputs):
            target_angle = (vector.VectorObject2D.from_xy(*strategy_output.target_pos) - pod.pos).rho
            match strategy_output.thrust:
                case 'BOOST':
                    thrust = 200.0
                case int(x):
                    thrust = float(x)
            pod_control = PodControl(
                thrust=thrust,
                target_angle=np.degrees(target_angle)
            )
            pod_controls.append(pod_control)
        
        self.pods.move(pod_controls=pod_controls)

        for i, pod in enumerate(self.pods):
            checkpoint = self.checkpoints[self.pods_next_checkpoint[i]]
            checkpoint_dist = (checkpoint - pod.pos).rho
            if checkpoint_dist <= CHECKPOINT_RADIUS:
                self.pods_next_checkpoint[i] += 1
                if self.pods_next_checkpoint[i] == len(self.checkpoints):
                    self.pods_next_checkpoint[i] = 0
                    self.pods_laps[i] -= 1
                    if self.pods_laps[i] == 0:
                        return Game.ResultWin(i)
        
        return Game.ResultContinue()
        
    def get_visualization_data(self) -> VisualizationData:
        return VisualizationData(
            checkpoints=self.checkpoints,
            pods=[
                PodVisualizationData(
                    pos=vector.obj(x=pod.pos.x, y=pod.pos.y),
                    ang=pod.ang
                )
                for pod in self.pods
            ]
        )
