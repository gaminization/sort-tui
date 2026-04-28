from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class SelectionSort(SortAlgorithm):
    name = "Selection Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Finds the minimum element and places it at the beginning, repeatedly."
    worst_case_input = "random"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def better(a: int, b: int) -> bool:
            return a < b if ascending else a > b

        sorted_so_far: List[int] = []

        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, min_idx],
                    sorted_indices=sorted_so_far[:],
                    explanation=f"Comparing arr[{j}]={arr[j]} with current min arr[{min_idx}]={arr[min_idx]}.",
                    operation="compare",
                )
                if better(arr[j], arr[min_idx]):
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                yield SortFrame(
                    array=arr[:],
                    swapped=[i, min_idx],
                    sorted_indices=sorted_so_far[:],
                    explanation=f"Swapping arr[{i}]={arr[i]} and arr[{min_idx}]={arr[min_idx]}.",
                    operation="swap",
                )
            else:
                yield SortFrame(
                    array=arr[:],
                    swapped=[i],
                    sorted_indices=sorted_so_far[:],
                    explanation=f"Index {i} already holds the selected value for this pass.",
                    operation="swap",
                )
            sorted_so_far.append(i)

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        import random

        arr = list(range(1, size + 1))
        random.shuffle(arr)
        return arr

    def get_invariant(self) -> str:
        return "arr[0..i] contains the i smallest elements in their final positions."
