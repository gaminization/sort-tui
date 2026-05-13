from __future__ import annotations

import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import value_of
from sortui.algorithms.base import SortAlgorithm, SortFrame


class OddEvenSort(SortAlgorithm):
    name = "Odd-Even Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Alternates between comparing odd-indexed and even-indexed pairs; parallelizable variant of bubble sort."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        power = 1
        while power < max(1, n):
            power *= 2
        sentinel = object()
        work: list[Any] = arr[:] + [sentinel] * (power - n)

        def priority(item: Any) -> float:
            if item is sentinel:
                return math.inf
            key = value_of(item)
            return key if ascending else -key

        def sync_array() -> None:
            arr[:] = [item for item in work if item is not sentinel]

        def visible_index(work_index: int) -> int | None:
            if work[work_index] is sentinel:
                return None
            return sum(1 for item in work[: work_index + 1] if item is not sentinel) - 1

        def compare_swap(i: int, j: int, gap: int, level: int) -> Generator[SortFrame, None, None]:
            highlighted = [idx for idx in (visible_index(i), visible_index(j)) if idx is not None]
            yield SortFrame(
                array=arr[:],
                highlighted=highlighted,
                explanation=f"Odd-even merge network: comparing wire {i} with wire {j} at gap {gap}.",
                operation="compare",
                metadata={"network": "odd_even_merge", "gap": gap, "level": level},
            )
            if priority(work[i]) > priority(work[j]):
                work[i], work[j] = work[j], work[i]
                sync_array()
                swapped = [idx for idx in (visible_index(i), visible_index(j)) if idx is not None]
                yield SortFrame(
                    array=arr[:],
                    swapped=swapped,
                    explanation=f"Odd-even merge network: swapping wires {i} and {j}.",
                    operation="swap",
                    metadata={"network": "odd_even_merge", "gap": gap, "level": level},
                )

        def odd_even_merge(lo: int, length: int, gap: int, level: int) -> Generator[SortFrame, None, None]:
            step = gap * 2
            if step < length:
                yield from odd_even_merge(lo, length, step, level + 1)
                yield from odd_even_merge(lo + gap, length, step, level + 1)
                for i in range(lo + gap, lo + length - gap, step):
                    yield from compare_swap(i, i + gap, gap, level)
            else:
                yield from compare_swap(lo, lo + gap, gap, level)

        def odd_even_merge_sort(lo: int, length: int, level: int) -> Generator[SortFrame, None, None]:
            if length <= 1:
                return
            half = length // 2
            yield from odd_even_merge_sort(lo, half, level + 1)
            yield from odd_even_merge_sort(lo + half, half, level + 1)
            yield from odd_even_merge(lo, length, 1, level)

        yield from odd_even_merge_sort(0, power, 0)

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))

    def get_invariant(self) -> str:
        return "After each odd-even merge stage, the covered wires form a sorted network segment."
