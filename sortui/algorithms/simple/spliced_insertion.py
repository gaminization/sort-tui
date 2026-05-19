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

class SplicedInsertionSort(SortAlgorithm):
    name = "Spliced Insertion Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Explicit splice-out and splice-in insertion sort."
    
    def get_invariant(self) -> str:
        return "arr[0..i] are sorted; element at i was spliced out of position j and spliced back in at its correct sorted position."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        for i in range(1, n):
            yield _base_frame(arr, highlighted=[i], explanation="Splice-out selected")
            val = arr[i]
            yield _base_frame(arr, highlighted=[i], operation="read", explanation="Element removed")
            j = i
            while j > 0:
                yield _base_frame(arr, highlighted=[j-1, j], explanation="Compare")
                if out_of_order(arr[j-1], val, ascending):
                    arr[j] = arr[j-1]
                    yield _base_frame(arr, swapped=[j, j-1], operation="write")
                    j -= 1
                else:
                    break
            arr[j] = val
            yield _base_frame(arr, swapped=[j], operation="write", explanation="Element spliced in")
        yield done_frame(arr, self.name)

