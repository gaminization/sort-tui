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

class TwoWayBubbleSort(SortAlgorithm):
    name = "Two-Way Bubble Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Bidirectional bubble sort variant."
    
    def get_invariant(self) -> str:
        return "Both ends of the unsorted region shrink each pass — forward pass bubbles largest right, backward pass bubbles smallest left."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        
        yield _base_frame(arr, explanation="Starting Two-Way Bubble Sort algorithm.")
        
        left, right = 0, n - 1
        sorted_idx = []
        while left < right:
            swapped_any = False
            for i in range(left, right):
                yield _base_frame(arr, highlighted=[i, i+1], sorted_indices=sorted_idx, explanation="Forward sweep")
                if out_of_order(arr[i], arr[i+1], ascending):
                    arr[i], arr[i+1] = arr[i+1], arr[i]
                    swapped_any = True
                    yield _base_frame(arr, swapped=[i, i+1], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.append(right)
            right -= 1
            if not swapped_any:
                break
            swapped_any = False
            for i in range(right, left, -1):
                yield _base_frame(arr, highlighted=[i-1, i], sorted_indices=sorted_idx, explanation="Backward sweep")
                if out_of_order(arr[i-1], arr[i], ascending):
                    arr[i-1], arr[i] = arr[i], arr[i-1]
                    swapped_any = True
                    yield _base_frame(arr, swapped=[i-1, i], sorted_indices=sorted_idx, operation="swap")
            sorted_idx.append(left)
            left += 1
            if not swapped_any:
                break
        sorted_idx.extend(range(left, right+1))
        yield done_frame(arr, self.name)

