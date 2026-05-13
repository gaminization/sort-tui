from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sortui.algorithms.base import SortFrame


@dataclass
class SortStats:
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    frames: int = 0
    start_time: float = field(default_factory=time.time)

    def elapsed_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    def update(self, frame: "SortFrame") -> None:
        self.frames += 1
        op = frame.operation
        if op == "compare":
            self.comparisons += 1
        elif op == "swap":
            self.swaps += 1
        elif op == "write":
            self.writes += 1

    def reset(self) -> None:
        self.comparisons = 0
        self.swaps = 0
        self.writes = 0
        self.frames = 0
        self.start_time = time.time()
