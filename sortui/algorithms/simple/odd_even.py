from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class OddEvenSort(SortAlgorithm):
    name = "Odd-Even Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Alternates between comparing odd-indexed and even-indexed pairs; parallelizable variant of bubble sort."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        is_sorted = False

        def cmp(a: int, b: int) -> bool:
            return a > b if ascending else a < b

        while not is_sorted:
            is_sorted = True
            for start in (1, 0):
                phase_name = "Odd" if start == 1 else "Even"
                for j in range(start, n - 1, 2):
                    yield SortFrame(
                        array=arr[:],
                        highlighted=[j, j + 1],
                        explanation=f"{phase_name} phase: comparing arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                        operation="compare",
                    )
                    if cmp(arr[j], arr[j + 1]):
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        is_sorted = False
                        yield SortFrame(
                            array=arr[:],
                            swapped=[j, j + 1],
                            explanation=f"Swapping arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                            operation="swap",
                        )

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))

    def get_invariant(self) -> str:
        return "After each full pass (even + odd phase), at least one more element is in its final position."
