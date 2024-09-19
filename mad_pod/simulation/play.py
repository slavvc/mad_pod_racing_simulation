from typing import Optional
from dataclasses import dataclass
from queue import Queue

from .game import Game
from ..strategy_communication.communication import Strategy
from ..strategy_communication.messages import StrategyInput
from ..visualization.data import VisualizationData

class PlayResult:
    @dataclass
    class Win:
        pod_number: int

    class Limit:
        pass

def play(
    game: Game, 
    strategies: list[Strategy], 
    step_limit: int = 1000, 
    visualization_data: Optional[Queue[VisualizationData]] = None
) -> PlayResult.Win | PlayResult.Limit:
    if len(game.pods) != len(strategies):
        raise RuntimeError("number of pods and strategies must match")
    try:
        if visualization_data is not None:
            visualization_data.put(game.get_visualization_data())
        states = [game.get_strategy_input(i) for i in range(len(strategies))]
        for i in range(step_limit):
            print(f"step {i}")
            strategy_outputs = [strategy.react(state) for strategy, state in zip(strategies, states)]
            print(strategy_outputs)
            step_result = game.step(strategy_outputs)
            if visualization_data is not None:
                visualization_data.put(game.get_visualization_data())
            match step_result:
                case Game.ResultWin(n):
                    return PlayResult.Win(n)
                case Game.ResultContinue():
                    states = [game.get_strategy_input(i) for i in range(len(strategies))]
            print(states)
    finally:
        for strategy in strategies:
            strategy.stop()
    
    return PlayResult.Limit()