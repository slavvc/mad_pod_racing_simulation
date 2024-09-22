from typing import Optional, Generator
from subprocess import Popen, PIPE
from queue import Queue, Empty
from threading import Thread

from .messages import StrategyInput, StrategyOutput


class Strategy:
    class _StopCommand: pass
    _CoroutineType = Generator[StrategyOutput, StrategyInput | _StopCommand | None, None]
    
    def __init__(self, cmd_line: str):
        self.cmd_line = cmd_line
        self._coroutine: Optional[Strategy._CoroutineType] = None


    def _run(self, initial_state: StrategyInput) -> _CoroutineType:
        with Popen(
            self.cmd_line, shell=False,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        ) as proc:
            if proc.stdin is None or proc.stdout is None or proc.stderr is None:
                raise RuntimeError("failed to open pipes with the process")
            stderr_queue: Queue = Queue()
            stderr_reader = Thread(
                target=self._stderr_reader_target, 
                kwargs={'proc': proc, 'queue': stderr_queue}
            )
            stderr_reader.daemon = True
            stderr_reader.start()
            proc.stdin.write(initial_state.serialize())
            proc.stdin.flush()
            while True:
                proc.stdout.flush()
                proc.stderr.flush()
                raw_strategy_output = proc.stdout.readline()
                stderr_lines = self._read_queue(stderr_queue)
                strategy_output = StrategyOutput.deserialize(raw_strategy_output)
                strategy_output.message = '\n'.join(line.decode() for line in stderr_lines)
                strategy_input = yield strategy_output
                match strategy_input:
                    case StrategyInput():
                        proc.stdin.write(strategy_input.serialize())
                        proc.stdin.flush()
                    case Strategy._StopCommand():
                        break

            proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()
            proc.terminate()

    def _read_queue(self, queue: Queue) -> list[bytes]:
        result = []
        while True:
            try:
                result.append(queue.get_nowait())
            except Empty:
                break
        return result

    def _stderr_reader_target(self, proc: Popen, queue: Queue):
        if proc.stderr is not None:
            try:
                while line := proc.stderr.readline():
                    queue.put(line)
            except ValueError: pass
    
    def react(self, strategy_input: StrategyInput) -> StrategyOutput:
        if self._coroutine is None:
            self._coroutine = self._run(strategy_input)
            return self._coroutine.send(None)
        else:
            return self._coroutine.send(strategy_input)

    def stop(self):
        if self._coroutine is not None:
            try:
                self._coroutine.send(Strategy._StopCommand())
            except StopIteration: pass
            else:
                raise RuntimeError("couroutine did not stop")
