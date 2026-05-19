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

class SpaghettiSort(SortAlgorithm):
    name = "Spaghetti Sort (Simulation)"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(n)"
    stable = False
    description = "Simulates finding the tallest rod in a bundle."
    
    def get_invariant(self) -> str:
        return "Rods of length proportional to each value are held vertically; the tallest rod found in each pass goes next."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        bundle = [(val, idx) for idx, val in enumerate(arr)]
        output = []
        target_idx = n - 1 if ascending else 0
        step = -1 if ascending else 1
        while bundle:
            max_idx = 0
            for i in range(1, len(bundle)):
                yield _base_frame(arr, highlighted=[bundle[max_idx][1], bundle[i][1]], aux_array=[b[0] for b in bundle], explanation="Scanning bundle for longest rod")
                if bundle[i][0] > bundle[max_idx][0]:
                    max_idx = i
            val, orig_idx = bundle.pop(max_idx)
            yield _base_frame(arr, highlighted=[orig_idx], operation="read", aux_array=[b[0] for b in bundle], explanation="Extracting tallest rod")
            arr[target_idx] = val
            yield _base_frame(arr, swapped=[target_idx], operation="write", aux_array=[b[0] for b in bundle], explanation="Writing to output")
            target_idx += step
        yield done_frame(arr, self.name)

