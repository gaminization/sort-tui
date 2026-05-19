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

class HoareQuicksort(SortAlgorithm):
    name = "Hoare Partition Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort with Hoare partition scheme."
    
    def get_invariant(self) -> str:
        return "Two pointers i and j move inward from opposite ends; all elements left of i are <= pivot, right of j are >= pivot."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[lo + (hi - lo) // 2]
            i, j = lo - 1, hi + 1
            while True:
                i += 1
                while (arr[i] < pivot) if ascending else (arr[i] > pivot):
                    yield _base_frame(arr, highlighted=[min(max(i, 0), n-1), min(max(j, 0), n-1)], recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                    i += 1
                j -= 1
                while (arr[j] > pivot) if ascending else (arr[j] < pivot):
                    yield _base_frame(arr, highlighted=[min(max(i, 0), n-1), min(max(j, 0), n-1)], recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                    j -= 1
                    
                if i >= j:
                    p_idx = j
                    break
                arr[i], arr[j] = arr[j], arr[i]
                yield _base_frame(arr, swapped=[i, j], operation="swap", recursion_depth=depth, metadata={"pivot_pos": -1, "scheme": "hoare"})
                
            yield from _quick(lo, p_idx, depth + 1)
            yield from _quick(p_idx + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

