from __future__ import annotations
import math
from typing import Generator, List, Any
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms._helpers import base_frame, done_frame
from sortui.algorithms._helpers import out_of_order, value_of, is_sorted, in_order



def _base_frame(arr, **kwargs):
    kwargs.setdefault('explanation', 'Sorting step')
    kwargs.setdefault('operation', 'compare')
    return base_frame(arr, **kwargs)

class OptimizedBubbleSort(SortAlgorithm):
    name = "Optimized Bubble Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Bubble sort that tracks the last swap index."
    
    def get_invariant(self) -> str:
        return "last_swap tracks the rightmost swap position; elements beyond last_swap are confirmed sorted and never re-examined."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        end = n
        sorted_idx = []
        while end > 1:
            new_end = 0
            for i in range(1, end):
                yield _base_frame(arr, highlighted=[i-1, i], sorted_indices=sorted_idx, partition_bounds=(0, end), explanation="Scanning unsorted region")
                if out_of_order(arr[i-1], arr[i], ascending):
                    arr[i-1], arr[i] = arr[i], arr[i-1]
                    new_end = i
                    yield _base_frame(arr, swapped=[i-1, i], sorted_indices=sorted_idx, partition_bounds=(0, end), operation="swap")
            for j in range(new_end, end):
                if j not in sorted_idx:
                    sorted_idx.append(j)
            end = new_end
        sorted_idx.extend(range(0, end))
        yield done_frame(arr, self.name)

