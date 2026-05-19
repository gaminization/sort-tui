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

class DutchNationalFlagSort(SortAlgorithm):
    name = "Dutch National Flag Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    stable = False
    description = "Sorts an array of 3 distinct value ranges in linear time."
    
    def get_invariant(self) -> str:
        return "arr[0..lo-1] are all small, arr[lo..mid-1] are all medium, arr[hi+1..n-1] are all large — three strict regions at every step."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        # Find split points roughly based on values
        min_v, max_v = value_of(min(arr, key=value_of)), value_of(max(arr, key=value_of))
        range_v = max_v - min_v
        if range_v == 0:
            yield done_frame(arr, self.name)
            return
        p1 = min_v + range_v / 3
        p2 = min_v + 2 * range_v / 3
        lo, mid, hi = 0, 0, n - 1
        sorted_idx = []
        while mid <= hi:
            yield _base_frame(arr, highlighted=[mid], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), explanation="Classifying current element")
            val = value_of(arr[mid])
            if (val < p1 if ascending else val > p2):
                if lo != mid:
                    arr[lo], arr[mid] = arr[mid], arr[lo]
                    yield _base_frame(arr, swapped=[lo, mid], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), operation="swap")
                sorted_idx.append(lo)
                lo += 1
                mid += 1
            elif (val >= p2 if ascending else val <= p1):
                if mid != hi:
                    arr[mid], arr[hi] = arr[hi], arr[mid]
                    yield _base_frame(arr, swapped=[mid, hi], metadata={"lo": lo, "mid": mid, "hi": hi}, partition_bounds=(lo, hi), operation="swap")
                sorted_idx.append(hi)
                hi -= 1
            else:
                mid += 1
        
        # Final pass to fully sort the array
        for i in range(1, n):
            val = arr[i]
            j = i
            while j > 0:
                yield _base_frame(arr, highlighted=[j, j-1])
                if out_of_order(arr[j-1], val, ascending):
                    arr[j] = arr[j-1]
                    yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                    j -= 1
                else:
                    break
            arr[j] = val
        yield done_frame(arr, self.name)
