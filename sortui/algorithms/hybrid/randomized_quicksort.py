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

class RandomizedQuicksort(SortAlgorithm):
    name = "Randomized Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort with random pivot selection."
    
    def get_invariant(self) -> str:
        return "Pivot is chosen uniformly at random; all elements left of pivot are <= pivot, all right are >= pivot after partition."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import random
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        yield _base_frame(arr, explanation="Starting Randomized Quicksort")
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            rand_idx = random.randint(lo, hi)
            yield _base_frame(arr, highlighted=[rand_idx], partition_bounds=(lo, hi), explanation="Selecting random pivot")
            arr[rand_idx], arr[hi] = arr[hi], arr[rand_idx]
            pivot = arr[hi]
            
            i = lo
            for j in range(lo, hi):
                yield _base_frame(arr, highlighted=[j, hi], pivot_index=hi, partition_bounds=(lo, hi), recursion_depth=depth, metadata={"pivot_value": pivot, "selection": "random"})
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    if i != j:
                        yield _base_frame(arr, swapped=[i, j], pivot_index=hi, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield _base_frame(arr, swapped=[i, hi], pivot_index=i, partition_bounds=(lo, hi), operation="swap", recursion_depth=depth)
            
            yield from _quick(lo, i - 1, depth + 1)
            yield from _quick(i + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

