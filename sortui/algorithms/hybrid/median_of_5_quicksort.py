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

class MedianOf5Quicksort(SortAlgorithm):
    name = "Median-of-5 Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort with median-of-5 pivot."
    
    def get_invariant(self) -> str:
        return "Pivot is the median of 5 evenly-spaced elements; provides better pivot quality at cost of 6 comparisons per call."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            if hi - lo < 4:
                # Fallback to simple selection for small subarrays
                for i in range(lo, hi):
                    min_idx = i
                    for j in range(i+1, hi+1):
                        yield _base_frame(arr, highlighted=[min_idx, j], partition_bounds=(lo, hi))
                        if (arr[j] < arr[min_idx]) if ascending else (arr[j] > arr[min_idx]):
                            min_idx = j
                    if min_idx != i:
                        arr[i], arr[min_idx] = arr[min_idx], arr[i]
                        yield _base_frame(arr, swapped=[i, min_idx], partition_bounds=(lo, hi), operation="swap")
                return
                
            step = (hi - lo) // 4
            c_idx = [lo, lo+step, lo+2*step, lo+3*step, hi]
            yield _base_frame(arr, highlighted=c_idx, partition_bounds=(lo, hi), explanation="5 candidates selected", metadata={"candidates": 5, "pivot_quality": "high"})
            
            cands = [(arr[i], i) for i in c_idx]
            # Selection sort the 5 candidates
            for i in range(5):
                for j in range(i+1, 5):
                    yield _base_frame(arr, highlighted=[cands[i][1], cands[j][1]], partition_bounds=(lo, hi))
                    if (cands[j][0] < cands[i][0]) if ascending else (cands[j][0] > cands[i][0]):
                        cands[i], cands[j] = cands[j], cands[i]
            
            med_idx = cands[2][1]
            yield _base_frame(arr, highlighted=[med_idx], partition_bounds=(lo, hi), explanation="Median of 5 selected", metadata={"candidates": 5, "pivot_quality": "high"})
            
            arr[med_idx], arr[hi] = arr[hi], arr[med_idx]
            pivot = arr[hi]
            
            i_ptr = lo
            for j in range(lo, hi):
                yield _base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth)
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i_ptr], arr[j] = arr[j], arr[i_ptr]
                    if i_ptr != j:
                        yield _base_frame(arr, swapped=[i_ptr, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i_ptr += 1
            arr[i_ptr], arr[hi] = arr[hi], arr[i_ptr]
            yield _base_frame(arr, swapped=[i_ptr, hi], pivot_index=i_ptr, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            yield from _quick(lo, i_ptr - 1, depth + 1)
            yield from _quick(i_ptr + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

