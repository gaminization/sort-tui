from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class BubbleSort(SortAlgorithm):
    name = "Bubble Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Repeatedly steps through the list, compares adjacent elements, and swaps them if in wrong order."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        sorted_so_far: List[int] = []

        def cmp(a: int, b: int) -> bool:
            """Return True when a and b are in the wrong order."""
            return a > b if ascending else a < b

        for i in range(n):
            swapped_any = False

            for j in range(0, n - i - 1):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, j + 1],
                    sorted_indices=sorted_so_far[:],
                    explanation=f"Comparing arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                    operation="compare",
                )

                if cmp(arr[j], arr[j + 1]):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped_any = True
                    yield SortFrame(
                        array=arr[:],
                        swapped=[j, j + 1],
                        sorted_indices=sorted_so_far[:],
                        explanation=f"Swapping arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                        operation="swap",
                    )

            sorted_so_far.append(n - i - 1)

            if not swapped_any:
                # No swap occurred — the rest of the array is already sorted.
                sorted_so_far = list(range(n))
                break

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))

    def get_invariant(self) -> str:
        return "After pass i, the largest i elements are in their final positions."
