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

class CircleSort(SortAlgorithm):
    name = "Circle Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Compare mirrored pairs recursively."
    
    def get_invariant(self) -> str:
        return "Mirrored index pairs (lo, hi) are compared and swapped if out of order; the circle recursively halves until pairs meet."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        def _inner(lo: int, hi: int, depth: int) -> Generator[SortFrame, None, bool]:
            if lo >= hi: return False
            swapped = False
            high = hi
            low = lo
            mid = (high - low) // 2
            while lo < hi:
                yield _base_frame(arr, highlighted=[lo, hi], recursion_depth=depth, explanation="Comparing mirror pair")
                if out_of_order(arr[lo], arr[hi], ascending):
                    arr[lo], arr[hi] = arr[hi], arr[lo]
                    swapped = True
                    yield _base_frame(arr, swapped=[lo, hi], recursion_depth=depth, operation="swap")
                lo += 1
                hi -= 1
            if lo == hi:
                yield _base_frame(arr, highlighted=[lo, hi + 1], recursion_depth=depth)
                if out_of_order(arr[lo], arr[hi + 1], ascending):
                    arr[lo], arr[hi + 1] = arr[hi + 1], arr[lo]
                    swapped = True
                    yield _base_frame(arr, swapped=[lo, hi + 1], recursion_depth=depth, operation="swap")
            left_swapped = yield from _inner(low, low + mid, depth+1)
            right_swapped = yield from _inner(low + mid + 1, high, depth+1)
            return swapped or left_swapped or right_swapped
        
        while True:
            did_swap = yield from _inner(0, n-1, 0)
            if not did_swap:
                break
        yield done_frame(arr, self.name)
