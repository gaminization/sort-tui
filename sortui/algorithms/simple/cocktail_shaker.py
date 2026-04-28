from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame


class CocktailShakerSort(SortAlgorithm):
    name = "Cocktail Shaker Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Bidirectional bubble sort: bubbles elements in both forward and backward passes."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        lo, hi = 0, n - 1
        sorted_indices: List[int] = []

        def cmp(a: int, b: int) -> bool:
            return a > b if ascending else a < b

        while lo < hi:
            swapped = False

            # Forward pass: bubble largest unsorted element to hi
            for j in range(lo, hi):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, j + 1],
                    sorted_indices=sorted_indices[:],
                    explanation=f"Forward pass: comparing arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                    operation="compare",
                )
                if cmp(arr[j], arr[j + 1]):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    yield SortFrame(
                        array=arr[:],
                        swapped=[j, j + 1],
                        sorted_indices=sorted_indices[:],
                        explanation=f"Swapping arr[{j}]={arr[j]} and arr[{j + 1}]={arr[j + 1]}.",
                        operation="swap",
                    )

            sorted_indices.append(hi)
            hi -= 1

            if not swapped:
                break

            swapped = False

            # Backward pass: bubble smallest unsorted element to lo
            for j in range(hi, lo, -1):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j - 1, j],
                    sorted_indices=sorted_indices[:],
                    explanation=f"Backward pass: comparing arr[{j - 1}]={arr[j - 1]} and arr[{j}]={arr[j]}.",
                    operation="compare",
                )
                if cmp(arr[j - 1], arr[j]):
                    arr[j - 1], arr[j] = arr[j], arr[j - 1]
                    swapped = True
                    yield SortFrame(
                        array=arr[:],
                        swapped=[j - 1, j],
                        sorted_indices=sorted_indices[:],
                        explanation=f"Swapping arr[{j - 1}]={arr[j - 1]} and arr[{j}]={arr[j]}.",
                        operation="swap",
                    )

            sorted_indices.append(lo)
            lo += 1

            if not swapped:
                break

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_invariant(self) -> str:
        return "Elements outside [lo..hi] are in their final sorted positions."
