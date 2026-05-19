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

class IterativeQuicksort(SortAlgorithm):
    name = "Iterative Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Iterative quicksort using an explicit stack."
    
    def get_invariant(self) -> str:
        return "An explicit stack holds (lo, hi) subarray bounds; the stack depth never exceeds log2(n) with tail-call optimization."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising explicit stack", metadata={"init": True})
            
        stack = [(0, n - 1)]
        while stack:
            lo, hi = stack.pop()
            depth = len(stack)
            if lo >= hi: continue
            
            pivot = arr[hi]
            i = lo
            for j in range(lo, hi):
                yield _base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth, metadata={"stack_depth": depth, "stack": stack})
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    if i != j:
                        yield _base_frame(arr, swapped=[i, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield _base_frame(arr, swapped=[i, hi], pivot_index=i, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            if i - 1 - lo > hi - i - 1:
                stack.append((lo, i - 1))
                stack.append((i + 1, hi))
            else:
                stack.append((i + 1, hi))
                stack.append((lo, i - 1))
                
        yield done_frame(arr, self.name)

