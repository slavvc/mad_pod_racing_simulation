import argparse
from threading import Thread
from queue import Queue

from ..simulation.game import Game
from ..simulation.play import play, PlayResult
from ..strategy_communication.communication import Strategy
from ..visualization.data import VisualizationData, VisualizationStopCommand
from ..visualization.gltk import visualize_game

def run_vis1_gltk(cmdline: str):
    queue: Queue[VisualizationData | VisualizationStopCommand] = Queue()
    play_thread = Thread(target=run1, args=[cmdline, queue])
    play_thread.daemon = False
    play_thread.start()
    visualize_game(queue)

def run1(cmdline, queue=None):
    strategy = Strategy(cmdline)
    game = Game.create(1, 4)
    res =  play(game, [strategy], 500, queue)
    match res:
        case PlayResult.Limit():
            print("Step limit reached")
        case PlayResult.Win(pod_number):
            print(f"pod #{pod_number} won")
    queue.put(VisualizationStopCommand())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd1')
    parser.add_argument('--vis', choices=['gltk'], required=False)
    args = parser.parse_args()
    if args.vis is not None:
        run_vis1_gltk(args.cmd1)
    else:
        run1(args.cmd1)

if __name__ == '__main__':
    main()