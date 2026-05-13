from __future__ import annotations

import json


class TimeTravelEngine:
    """Buffers generator output so the user can step forward and backward."""


    def __init__(self, algorithm, array, ascending: bool = True):
        self._history: list = []
        self._gen = algorithm.sort(list(array), ascending)
        self._pos = -1
        self._done = False
        self.max_history = 50_000

    def advance(self):
        if self._pos < len(self._history) - 1:
            self._pos += 1
            return self._history[self._pos]
        if self._done:
            return None
        try:
            frame = next(self._gen)
            if len(self._history) < self.max_history:
                self._history.append(frame)
            self._pos = len(self._history) - 1
            return frame
        except StopIteration:
            self._done = True
            return None

    def rewind(self):
        if self._pos > 0:
            self._pos -= 1
            return self._history[self._pos]
        return None

    def seek(self, pos: int):
        while len(self._history) <= pos and not self._done:
            frame = self.advance()
            if frame is None:
                break
        if pos < len(self._history):
            self._pos = pos
            return self._history[self._pos]
        return None

    def current(self):
        if 0 <= self._pos < len(self._history):
            return self._history[self._pos]
        return None

    @property
    def position(self) -> int:
        return self._pos

    @property
    def buffered(self) -> int:
        return len(self._history)

    @property
    def is_done(self) -> bool:
        return self._done

    def jump_to_next_swap(self):
        while True:
            f = self.advance()
            if f is None:
                return None
            if f.operation == "swap":
                return f

    def jump_to_prev_swap(self):
        pos = self._pos - 1
        while pos >= 0:
            if self._history[pos].operation == "swap":
                self._pos = pos
                return self._history[pos]
            pos -= 1
        return None

    def export_history(self, path: str) -> None:
        from sortui.export import frame_to_dict

        with open(path, "w", encoding="utf-8") as fh:
            json.dump([frame_to_dict(f) for f in self._history], fh)

    @classmethod
    def load_replay(cls, path: str) -> "TimeTravelEngine":
        from sortui.export import load_frames

        obj = cls.__new__(cls)
        obj._done = True
        obj._history = load_frames(path)
        obj._pos = -1
        obj._gen = iter([])
        obj.max_history = len(obj._history)
        return obj
