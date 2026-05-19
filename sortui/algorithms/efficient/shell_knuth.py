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

class ShellKnuthSort(SortAlgorithm):
    name = "Shellsort (Knuth Gaps)"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n^(3/2))"
    space_complexity = "O(1)"
    stable = False
    description = "Shellsort using the Knuth gap sequence."
    
    def get_invariant(self) -> str:
        return "The array is h-sorted for all gaps in the Knuth sequence 1,4,13,40,121,... (3k+1) used so far."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        h = 1
        while h < n // 3:
            h = 3 * h + 1
        while h > 0:
            for i in range(h, n):
                temp = arr[i]
                j = i
                while j >= h:
                    yield _base_frame(arr, highlighted=[j, j-h], metadata={"gap": h, "formula": "3k+1"})
                    if out_of_order(arr[j-h], temp, ascending):
                        arr[j] = arr[j-h]
                        yield _base_frame(arr, swapped=[j, j-h], metadata={"gap": h, "formula": "3k+1"}, operation="swap")
                        j -= h
                    else:
                        break
                arr[j] = temp
                if j != i:
                    yield _base_frame(arr, swapped=[j], metadata={"gap": h, "formula": "3k+1"}, operation="write")
            h //= 3
        yield done_frame(arr, self.name)

