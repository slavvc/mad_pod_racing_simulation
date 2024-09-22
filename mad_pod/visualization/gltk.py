from typing import Optional
from dataclasses import dataclass, field

import tkinter as tk
from pyopengltk import OpenGLFrame # type: ignore
from OpenGL.GL import * # type: ignore
import moderngl

from queue import Queue
import time
import math

from .data import VisualizationData, PodVisualizationData, VisualizationStopCommand
from ..constants import WORLD_H, WORLD_W, CHECKPOINT_RADIUS
from ..utils import degrees


@dataclass
class VisualizationState:
    prev_frame: Optional[VisualizationData] = None
    last_frame: Optional[VisualizationData] = None
    frame_started_time: float = field(default_factory=lambda: time.time())


class GlFrame(OpenGLFrame):
    def __init__(
        self, *args, 
        data_queue: Queue[VisualizationData | VisualizationStopCommand], 
        factor: float, 
        frame_duration: float,
        label: tk.Label,
        **kwargs
    ):
        self.data_queue = data_queue
        self.data_queue_exhausted = False
        self.factor = factor
        self.frame_duration = frame_duration
        self.label = label
        super().__init__(*args, **kwargs)
        self.state = VisualizationState()

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
    
    def _calc_k(self) -> float:
        dt = time.time() - self.state.frame_started_time
        k = min(1, dt / self.frame_duration)
        return k

    def _calc_data(self) -> VisualizationData:
        def queue_get(old_val):
            if self.data_queue_exhausted:
                return old_val
            match x := self.data_queue.get():
                case VisualizationStopCommand():
                    self.data_queue_exhausted = True
                    return old_val
                case VisualizationData():
                    return x

        if self.state.prev_frame is None:
            self.state.prev_frame = queue_get(self.state.prev_frame)
            self.state.last_frame = queue_get(self.state.last_frame)
            self.state.frame_started_time = time.time()
        elif self._calc_k() == 1:
            self.state.prev_frame = self.state.last_frame
            self.state.last_frame = queue_get(self.state.last_frame)
            self.state.frame_started_time = time.time()
        
        k = self._calc_k()

        if self.state.last_frame is None or self.state.prev_frame is None:
            raise RuntimeError("unreachable")

        return VisualizationData(
            checkpoints=self.state.last_frame.checkpoints,
            pods=[
                PodVisualizationData(
                    pos=podb.pos * k + poda.pos * (1 - k),
                    ang=podb.ang * k + poda.ang * (1 - k)
                )
                for poda, podb 
                in zip(self.state.prev_frame.pods, self.state.last_frame.pods)
            ]
        )

    def redraw(self):       

        data = self._calc_data()
        report=(
            f"ang = {degrees(data.pods[0].ang):.1f} ∈ [{degrees(self.state.prev_frame.pods[0].ang):.1f}, {degrees(self.state.last_frame.pods[0].ang):.1f}]"
        )
        self.label.config(text=report)

        # print(f"vis: {data}")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glColor3f(0.0,0.0,0.0)
        glPointSize(CHECKPOINT_RADIUS * 2 * self.factor)
        glBegin(GL_POINTS)
        for checkpoint in data.checkpoints:
            glVertex2f(checkpoint.x * self.factor , checkpoint.y * self.factor)
        glEnd()

        glColor3f(0.0,0.0,1.0)
        glPointSize(200 * self.factor)
        glBegin(GL_POINTS)
        for pod in data.pods:
            glVertex2f(pod.pos.x * self.factor, pod.pos.y * self.factor)
        glEnd()
        
        glColor3f(1.0,0.0,0.0)
        # glLineWidth(3)
        glBegin(GL_LINES)
        for pod in data.pods:
            glVertex2f(pod.pos.x * self.factor, pod.pos.y * self.factor)
            r = 300 * self.factor
            dx = r * math.cos(pod.ang)
            dy = r * math.sin(pod.ang)
            glVertex2f(pod.pos.x * self.factor + dx, pod.pos.y * self.factor + dy)
        glEnd()

        glFlush()

def visualize_game(data: Queue[VisualizationData | VisualizationStopCommand], window_scale: float = 1/5, frame_duration: float = 0.3):
    root = tk.Tk()
    label = tk.Label(root, text="label")
    label.pack()
    frame = GlFrame(
        root,
        data_queue=data,
        factor=window_scale,
        frame_duration=frame_duration,
        label=label,
        width=int(WORLD_W * window_scale), 
        height=int(WORLD_H * window_scale)
    )
    frame.pack(fill=tk.BOTH, expand=tk.YES)
    frame.animate = 1

    root.mainloop()
