from dataclasses import dataclass
from typing import List, Optional

import tkinter
import subprocess
import numpy as np
import time

from pyopengltk import OpenGLFrame
from OpenGL.GL import *


PLAYER_ROTATION_SPEED = 18 / 180 * np.pi
WORLD_W = 16000
WORLD_H = 9000
CHECKPOINT_RADIUS = 600

def clamp(x: float, a: float, b: float) -> float:
    return min(b, max(a, x))

@dataclass
class Player:
    pos: np.ndarray
    vel: np.ndarray
    ang: float

    def move(self, thrust, target_angle):
        self.ang += clamp(target_angle - self.ang, -PLAYER_ROTATION_SPEED, PLAYER_ROTATION_SPEED)
        self.vel += thrust * np.array([np.cos(self.ang), np.sin(self.ang)])
        self.pos += self.vel
        self.vel *= 0.85

@dataclass
class Game:
    player: Player
    checkpoints: List[np.ndarray]
    next_checkpoint: int
    laps: int

    def get_state(self):
        checkpoint = self.checkpoints[self.next_checkpoint]
        vector = checkpoint - self.player.pos
        distance_to_checkpoint = np.linalg.norm(vector)
        angle_to_checkpoint = (np.arctan2(vector[1], vector[0]) - self.player.ang)
        return (
            self.player.pos[0], self.player.pos[1], 
            checkpoint[0], checkpoint[1], 
            int(distance_to_checkpoint), int(angle_to_checkpoint*180/np.pi)
        )

    def step(self, strategy_decision):
        target_x, target_y, thrust = strategy_decision
        target = np.array([target_x, target_y]).astype(np.float32)
        vector = target - self.player.pos
        target_angle = np.arctan2(vector[1], vector[0])
        
        thrust = 200 if thrust == 'BOOST' else thrust
        self.player.move(thrust, target_angle)

        checkpoint = self.checkpoints[self.next_checkpoint]
        distance = np.linalg.norm(checkpoint - self.player.pos)
        if distance <= CHECKPOINT_RADIUS:
            self.next_checkpoint = self.next_checkpoint + 1
            if self.next_checkpoint == len(self.checkpoints):
                self.next_checkpoint = 0
                self.laps -= 1
                if self.laps == 0:
                    return True
        return False

def make_game() -> Game:
    checkpoints = []
    for i in range(4):
        x = np.random.randint(WORLD_W*0.1, WORLD_W*0.9)
        y = np.random.randint(WORLD_H*0.1, WORLD_H*0.9)
        checkpoints.append(np.array([x, y]).astype(np.float32))
    return Game(
        Player(
            checkpoints[0].copy(),
            np.zeros(2),
            0
        ), 
        checkpoints, 0,
        3
    )

def play_strat():
    with subprocess.Popen(
        ["python", "strat.py"], 
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    ) as proc:
        game = make_game()
        for i in range(5000):
            yield game

            state = game.get_state()
            strat_input = b' '.join(str(int(x)).encode() for x in state)
            print(strat_input)
            proc.stdin.write(strat_input+b'\n')
            proc.stdin.write(b"0 0\n")
            proc.stdin.flush()
            strat_output = proc.stdout.readline()
            print(strat_output)
            strat_output = strat_output.split()
            target = tuple(int(x) for x in strat_output[:2])
            thrust = 'BOOST' if strat_output[2] == b'BOOST' else int(strat_output[2])
            finished = game.step(target + (thrust,))
            if finished:
                break
        print(f"finished in {i} steps")

def play_strat_tk():
    root = tkinter.Tk()
    delay = 200
    factor = 20
    canvas = tkinter.Canvas(root, width=WORLD_W/factor, height=WORLD_H/factor)
    canvas.pack()

    states = play_strat()
    init_state = next(states)

    for checkpoint in init_state.checkpoints:
        xy = checkpoint / factor
        canvas.create_oval(xy[0]-300/factor, xy[1]-300/factor, xy[0]+300/factor, xy[1]+300/factor)
    
    pos = init_state.player.pos / factor
    ang = init_state.player.ang * 180 / np.pi
    player = canvas.create_oval(pos[0]-100/factor, pos[1]-100/factor, pos[0]+100/factor, pos[1]+100/factor, fill='blue')
    player_ang = canvas.create_arc(pos[0]-100/factor, pos[1]-100/factor, pos[0]+100/factor, pos[1]+100/factor, start=ang-1, extent=2, outline='red')

    def frame():
        nonlocal player, player_ang
        state = next(states, None)
        if state is None:
            return
        pos = state.player.pos / factor
        ang = state.player.ang * 180 / np.pi
        canvas.delete(player)
        canvas.delete(player_ang)
        player = canvas.create_oval(pos[0]-100/factor, pos[1]-100/factor, pos[0]+100/factor, pos[1]+100/factor, fill='blue')
        player_ang = canvas.create_arc(pos[0]-100/factor, pos[1]-100/factor, pos[0]+100/factor, pos[1]+100/factor, start=-ang-1, extent=2, outline='red')
        root.after(delay, frame)


    root.after(delay, frame)
    root.mainloop()


class GlFrame(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.a_state: Optional[Game] = None
        self.b_state: Optional[Game] = None
        self.t = 0
        self.factor = 1
        self.delay = 1
        self._prev_time = 0

    def initgl(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(1.0,1.0,1.0,1.0)

        # setup projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        # setup identity model view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_POINT_SMOOTH)

        self.prev_time = time.time()
        
    def redraw(self):
        dt = time.time() - self.prev_time
        self.t = min(1, dt / self.delay)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.a_state is not None:
            checkpoints = np.array(self.a_state['checkpoints']) / self.factor
            pos = self.a_state['pos'] / self.factor
            ang = self.a_state['ang']
            if self.b_state is not None:
                a_checkpoints = np.array(self.a_state['checkpoints'])
                a_pos = self.a_state['pos']
                a_ang = self.a_state['ang']
                b_checkpoints = np.array(self.b_state['checkpoints'])
                b_pos = self.b_state['pos']
                b_ang = self.b_state['ang']
                checkpoints = ((b_checkpoints-a_checkpoints)*self.t + a_checkpoints) / self.factor
                pos = ((b_pos-a_pos)*self.t + a_pos) / self.factor
                ang = (b_ang-a_ang)*self.t + a_ang

            glColor3f(0.0,0.0,0.0)
            glPointSize(CHECKPOINT_RADIUS*2/self.factor)
            glBegin(GL_POINTS)
            for checkpoint in checkpoints:
                glVertex2f(checkpoint[0], checkpoint[1])
            glEnd()

            glColor3f(0.0,0.0,1.0)
            glPointSize(200/self.factor)
            glBegin(GL_POINTS)
            # print(pos)
            glVertex2f(pos[0], pos[1])
            glEnd()
            
            glColor3f(1.0,0.0,0.0)
            # glLineWidth(3)
            glBegin(GL_LINES)
            glVertex2f(pos[0], pos[1])
            r = 300/self.factor
            dx = r*np.cos(ang)
            dy = r*np.sin(ang)
            glVertex2f(pos[0]+dx, pos[1]+dy)
            glEnd()

        glFlush()

def play_strat_gl():
    def _make_state(game: Game):
        return {
            'pos': game.player.pos.copy(),
            'ang': game.player.ang,
            'checkpoints': game.checkpoints
        }


    root = tkinter.Tk()
    factor = 20
    delay = 0.3
    frame = GlFrame(root, width=WORLD_W/factor, height=WORLD_H/factor)
    frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)
    
    states = play_strat()
    init_state = next(states)
    a_state = _make_state(init_state)
    
    frame.a_state = a_state
    frame.delay = delay
    frame.factor = factor
    frame.animate = 1

    def update():
        # print(frame.a_state, frame.b_state)
        new_state = next(states, None)
        if new_state is None:
            return
        if frame.b_state is not None:
            frame.a_state = frame.b_state
        frame.b_state = _make_state(new_state)
        frame.t = 0
        frame.prev_time = time.time()
        # print(frame.a_state, frame.b_state)
        root.after(int(delay*1000), update)

    root.after(int(delay*1000), update)

    root.mainloop()

if __name__ == "__main__":
    # for g in play_strat():
    #     pass

    # play_strat_tk()
    play_strat_gl()
