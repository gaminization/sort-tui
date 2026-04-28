from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class GnomeSort(SortAlgorithm):
    name = "Gnome Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = (
        "Like insertion sort but moves elements to their correct position by swapping backwards."
    )
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        pos = 0

        def cmp(a: int, b: int) -> bool:
            return a > b if ascending else a < b

        while pos < n:
            if pos == 0:
                pos += 1
            else:
                yield SortFrame(
                    array=arr[:],
                    highlighted=[pos - 1, pos],
                    explanation=f"Comparing arr[{pos - 1}]={arr[pos - 1]} and arr[{pos}]={arr[pos]}.",
                    operation="compare",
                )
                if cmp(arr[pos - 1], arr[pos]):
                    arr[pos - 1], arr[pos] = arr[pos], arr[pos - 1]
                    yield SortFrame(
                        array=arr[:],
                        swapped=[pos - 1, pos],
                        explanation=f"Swapping arr[{pos - 1}]={arr[pos - 1]} and arr[{pos}]={arr[pos]}, stepping back.",
                        operation="swap",
                    )
                    pos -= 1
                else:
                    pos += 1

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_invariant(self) -> str:
        return "All elements before pos are in sorted order."
