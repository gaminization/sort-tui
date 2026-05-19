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

class IterativeMergeSort(SortAlgorithm):
    name = "Iterative Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Bottom-up merge sort."
    
    def get_invariant(self) -> str:
        return "Bottom-up: all subarrays of size 2^pass are sorted; pass number is always floor(log2(current_merge_size))."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 0})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 1})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 2})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 3})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 4})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 5})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 6})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 7})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 8})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 9})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 10})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 11})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 12})

            
        aux = [0] * n
        width = 1
        pass_num = 0
        
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), aux_array=aux, metadata={"width": width, "pass": pass_num})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        aux[out] = arr[p1]
                        p1 += 1
                    else:
                        aux[out] = arr[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    aux[out] = arr[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    aux[out] = arr[p2]
                    p2 += 1
                    out += 1
                    
                for k in range(l_start, r_end):
                    arr[k] = aux[k]
                    yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end-1), aux_array=aux, metadata={"width": width, "pass": pass_num}, operation="write")
            width *= 2
            pass_num += 1
            
        yield done_frame(arr, self.name)

