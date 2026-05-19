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

class BidirectionalSelectionSort(SortAlgorithm):
    name = "Bidirectional Selection Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Finds min and max simultaneously."
    
    def get_invariant(self) -> str:
        return "Each pass simultaneously finds both the minimum and maximum of the unsorted region, placing both into final positions."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        left, right = 0, n - 1
        sorted_idx = []
        while left < right:
            min_idx, max_idx = left, left
            for i in range(left + 1, right + 1):
                yield _base_frame(arr, highlighted=[i, min_idx, max_idx], sorted_indices=sorted_idx)
                if out_of_order(arr[min_idx], arr[i], ascending):
                    min_idx = i
                elif out_of_order(arr[i], arr[max_idx], ascending):
                    max_idx = i
            if min_idx != left:
                arr[left], arr[min_idx] = arr[min_idx], arr[left]
                yield _base_frame(arr, swapped=[left, min_idx], sorted_indices=sorted_idx, operation="swap")
                if max_idx == left:
                    max_idx = min_idx
            if max_idx != right:
                arr[right], arr[max_idx] = arr[max_idx], arr[right]
                yield _base_frame(arr, swapped=[right, max_idx], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.extend([left, right])
            left += 1
            right -= 1
        yield done_frame(arr, self.name)

