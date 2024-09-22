from __future__ import annotations
from typing import Optional, Literal, Tuple
from dataclasses import dataclass

@dataclass
class StrategyInput:
    pod_pos: Tuple[int, int]
    checkpoint_pos: Tuple[int, int]
    checkpoint_dist: int
    checkpoint_angle: int
    enemy_pos: Tuple[int, int]

    def serialize(self) -> bytes:
        return (
            f'{self.pod_pos[0]} {self.pod_pos[1]} '
            f'{self.checkpoint_pos[0]} {self.checkpoint_pos[1]} '
            f'{self.checkpoint_dist} {self.checkpoint_angle}\n'
            f'{self.enemy_pos[0]} {self.enemy_pos[1]}\n'
        ).encode()

@dataclass
class StrategyOutput:
    target_pos: Tuple[int, int]
    thrust: int | Literal['BOOST']
    message: Optional[str] = None

    @classmethod
    def deserialize(cls, message: bytes) -> StrategyOutput:
        xs = message.decode(errors='ignore').split()
        if len(xs) != 3:
            raise ValueError('wrong number of arguments')
        x, y = [int(a) for a in xs[:2]]
        thrust: int | Literal['BOOST']
        if xs[2] == 'BOOST':
            thrust = 'BOOST'
        else:
            thrust = int(xs[2])
        return StrategyOutput(
            target_pos=(x, y),
            thrust=thrust
        )
