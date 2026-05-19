from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame



def _base_frame(arr, **kwargs):
    kwargs.setdefault('explanation', 'Sorting step')
    kwargs.setdefault('operation', 'compare')
    return base_frame(arr, **kwargs)

class CycleSort(SortAlgorithm):
    name = "Cycle Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Minimises writes by cycling elements to their final positions."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        writes = 0

        def before(a: int, b: int) -> bool:
            return a < b if ascending else a > b

        for cycle_start in range(n - 1):
            item = arr[cycle_start]
            pos = cycle_start

            for i in range(cycle_start + 1, n):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[cycle_start, i],
                    explanation=f"Counting values that belong before {item}; checking index {i}.",
                    operation="compare",
                )
                if before(arr[i], item):
                    pos += 1

            if pos == cycle_start:
                continue

            while pos < n and arr[pos] == item:
                yield SortFrame(
                    array=arr[:],
                    highlighted=[pos],
                    explanation=f"Skipping duplicate value at index {pos} before writing the cycle item.",
                    operation="compare",
                )
                pos += 1

            if pos >= n:
                continue

            arr[pos], item = item, arr[pos]
            writes += 1
            yield SortFrame(
                array=arr[:],
                swapped=[pos],
                explanation=f"Writing the cycle item into position {pos}. Total writes: {writes}.",
                operation="write",
                metadata={"writes": writes},
            )

            while pos != cycle_start:
                pos = cycle_start
                for i in range(cycle_start + 1, n):
                    yield SortFrame(
                        array=arr[:],
                        highlighted=[cycle_start, i],
                        explanation=f"Finding the next position for displaced value {item}.",
                        operation="compare",
                    )
                    if before(arr[i], item):
                        pos += 1

                while pos < n and arr[pos] == item:
                    yield SortFrame(
                        array=arr[:],
                        highlighted=[pos],
                        explanation=f"Skipping duplicate value at index {pos} before continuing the cycle.",
                        operation="compare",
                    )
                    pos += 1

                if pos >= n:
                    break

                arr[pos], item = item, arr[pos]
                writes += 1
                yield SortFrame(
                    array=arr[:],
                    swapped=[pos],
                    explanation=f"Continuing the cycle with a write to position {pos}. Total writes: {writes}.",
                    operation="write",
                    metadata={"writes": writes},
                )

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"Array is fully sorted. Total writes: {writes}.",
            operation="done",
            metadata={"writes": writes},
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))

    def get_invariant(self) -> str:
        return "Each completed cycle places at least one value into its final position."
