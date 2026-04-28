from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class ExchangeSort(SortAlgorithm):
    name = "Exchange Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = (
        "Compares each pair (i, j) where j > i and swaps if out of order. Simple but inefficient."
    )
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def cmp(a: int, b: int) -> bool:
            return a > b if ascending else a < b

        for i in range(n - 1):
            for j in range(i + 1, n):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[i, j],
                    explanation=f"Comparing arr[{i}]={arr[i]} and arr[{j}]={arr[j]}.",
                    operation="compare",
                )
                if cmp(arr[i], arr[j]):
                    arr[i], arr[j] = arr[j], arr[i]
                    yield SortFrame(
                        array=arr[:],
                        swapped=[i, j],
                        explanation=f"Swapping arr[{i}]={arr[i]} and arr[{j}]={arr[j]}.",
                        operation="swap",
                    )

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )
