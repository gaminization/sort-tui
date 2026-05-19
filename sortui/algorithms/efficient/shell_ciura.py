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

class ShellCiuraSort(SortAlgorithm):
    name = "Shellsort (Ciura Gaps)"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n^(4/3))"
    space_complexity = "O(1)"
    stable = False
    description = "Shellsort using the optimal Ciura gap sequence."
    
    def get_invariant(self) -> str:
        return "The array is h-sorted for all gap values used so far in Ciura's sequence [701,301,132,57,23,10,4,1]."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        gaps = [701, 301, 132, 57, 23, 10, 4, 1]
        for gap in gaps:
            if gap >= n and gap != 1: continue
            for i in range(gap, n):
                temp = arr[i]
                j = i
                while j >= gap:
                    yield _base_frame(arr, highlighted=[j, j-gap], metadata={"gap": gap}, explanation="Ciura gap compare")
                    if out_of_order(arr[j-gap], temp, ascending):
                        arr[j] = arr[j-gap]
                        yield _base_frame(arr, swapped=[j, j-gap], metadata={"gap": gap}, operation="swap")
                        j -= gap
                    else:
                        break
                arr[j] = temp
                if j != i:
                    yield _base_frame(arr, swapped=[j], metadata={"gap": gap}, operation="write")
        yield done_frame(arr, self.name)

