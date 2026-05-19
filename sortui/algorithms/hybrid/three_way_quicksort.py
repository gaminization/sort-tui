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

class ThreeWayQuicksort(SortAlgorithm):
    name = "Three-Way Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Bentley-McIlroy 3-way quicksort."
    
    def get_invariant(self) -> str:
        return "Bentley-McIlroy: lt and gt pointers partition into <pivot, ==pivot, >pivot; equal elements are never moved again."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[lo]
            lt, i, gt = lo, lo + 1, hi
            while i <= gt:
                yield _base_frame(arr, highlighted=[i], partition_bounds=(lt, gt), recursion_depth=depth, metadata={"lt": lt, "gt": gt, "i": i})
                if (arr[i] < pivot) if ascending else (arr[i] > pivot):
                    arr[lt], arr[i] = arr[i], arr[lt]
                    yield _base_frame(arr, swapped=[lt, i], partition_bounds=(lt, gt), operation="swap", recursion_depth=depth)
                    lt += 1
                    i += 1
                elif (arr[i] > pivot) if ascending else (arr[i] < pivot):
                    arr[i], arr[gt] = arr[gt], arr[i]
                    yield _base_frame(arr, swapped=[i, gt], partition_bounds=(lt, gt), operation="swap", recursion_depth=depth)
                    gt -= 1
                else:
                    i += 1
                    
            yield from _quick(lo, lt - 1, depth + 1)
            yield from _quick(gt + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

