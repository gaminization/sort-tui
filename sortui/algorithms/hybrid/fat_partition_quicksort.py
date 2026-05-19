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

class FatPartitionQuicksort(SortAlgorithm):
    name = "Fat Partition Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Dutch national flag partition quicksort."
    
    def get_invariant(self) -> str:
        return "Three regions: arr[lo..p1-1] < pivot, arr[p1..p2] == pivot, arr[p2+1..hi] > pivot after each partition."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _quick(lo, hi, depth):
            if lo >= hi: return
            pivot = arr[hi]
            i, j, k = lo, lo, hi
            while j <= k:
                yield _base_frame(arr, highlighted=[j], partition_bounds=(i, k), recursion_depth=depth, metadata={"equal_count": k-i+1, "regions": 3})
                if (arr[j] < pivot) if ascending else (arr[j] > pivot):
                    arr[i], arr[j] = arr[j], arr[i]
                    yield _base_frame(arr, swapped=[i, j], partition_bounds=(i, k), operation="swap", recursion_depth=depth)
                    i += 1
                    j += 1
                elif (arr[j] > pivot) if ascending else (arr[j] < pivot):
                    arr[j], arr[k] = arr[k], arr[j]
                    yield _base_frame(arr, swapped=[j, k], partition_bounds=(i, k), operation="swap", recursion_depth=depth)
                    k -= 1
                else:
                    j += 1
                    
            yield from _quick(lo, i - 1, depth + 1)
            yield from _quick(k + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

