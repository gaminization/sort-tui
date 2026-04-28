from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class InsertionSort(SortAlgorithm):
    name = "Insertion Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Builds sorted array one item at a time by inserting each element into its correct position."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def cmp(a: int, b: int) -> bool:
            """Return True when a should move right of b."""
            return a > b if ascending else a < b

        for i in range(1, n):
            key = arr[i]
            j = i - 1
            yield SortFrame(
                array=arr[:],
                highlighted=[i],
                sorted_indices=list(range(i)),
                explanation=f"Picking arr[{i}]={key} to insert into sorted portion.",
                operation="read",
            )
            while j >= 0:
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, j + 1],
                    sorted_indices=list(range(i)),
                    explanation=f"Comparing arr[{j}]={arr[j]} with key={key}, shifting if out of order.",
                    operation="compare",
                )
                if not cmp(arr[j], key):
                    break
                arr[j + 1] = arr[j]
                yield SortFrame(
                    array=arr[:],
                    swapped=[j, j + 1],
                    sorted_indices=list(range(i)),
                    explanation=f"Shifting arr[{j}]={arr[j]} one position right.",
                    operation="write",
                )
                j -= 1
            arr[j + 1] = key
            yield SortFrame(
                array=arr[:],
                swapped=[j + 1],
                sorted_indices=list(range(i + 1)),
                explanation=f"Inserted key={key} at position {j + 1}.",
                operation="write",
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
        return "arr[0..i] is always a sorted permutation of the first i+1 elements."
