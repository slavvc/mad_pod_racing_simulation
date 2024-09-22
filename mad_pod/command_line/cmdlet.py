from typing import Optional
import argparse
from threading import Thread
from queue import Queue

from ..simulation.game import Game
from ..simulation.play import play, PlayResult
from ..strategy_communication.communication import Strategy
from ..visualization.data import VisualizationData, VisualizationStopCommand
from ..visualization.gltk import visualize_game

def run_vis1_gltk(
    cmdline: str, 
    step_limit: int = 500, 
    window_scale: float = 1/5, 
    frame_duration: float = 0.3
):
    queue: Queue[VisualizationData | VisualizationStopCommand] = Queue()
    play_thread = Thread(target=run1, args=[cmdline, queue, step_limit])
    play_thread.daemon = False
    play_thread.start()
    visualize_game(queue, window_scale, frame_duration)

def run1(
    cmdline: str, 
    queue: Optional[Queue[VisualizationData | VisualizationStopCommand]] = None, 
    step_limit: int = 500
):
    strategy = Strategy(cmdline)
    game = Game.create(1, 4)
    match queue:
        case None:
            vis_cb = None
        case _:
            def vis_cb(data: VisualizationData):
                queue.put(data)
    res =  play(game, [strategy], step_limit, vis_cb)
    match res:
        case PlayResult.Limit():
            print("Step limit reached")
        case PlayResult.Win(pod_number):
            print(f"pod #{pod_number} won")
    if queue is not None:
        queue.put(VisualizationStopCommand())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd1', required=True)
    parser.add_argument('--vis', choices=['gltk'])
    parser.add_argument('--vis-scale', type=float)
    parser.add_argument('--vis-frame-duration', type=float)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    limit = 500 if args.limit is None else args.limit
    window_scale = 1/5 if args.vis_scale is None else args.vis_scale
    frame_duration = 0.3 if args.vis_frame_duration is None else args.vis_frame_duration
    if args.vis is not None:
        run_vis1_gltk(
            args.cmd1, 
            step_limit=limit, 
            window_scale=window_scale, 
            frame_duration=frame_duration
        )
    else:
        run1(args.cmd1, step_limit=limit)

if __name__ == '__main__':
    main()