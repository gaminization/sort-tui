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

class SwapSort(SortAlgorithm):
    name = "Swap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Counts smaller elements to find the exact sorted position."
    
    def get_invariant(self) -> str:
        return "For each index i, element arr[i] is placed into its correct final position by counting elements smaller than it."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        for i in range(n - 1):
            while True:
                count = 0
                for j in range(n):
                    if j == i: continue
                    yield _base_frame(arr, highlighted=[i, j], explanation=f"Counting elements smaller than arr[{i}]")
                    if (arr[j] < arr[i]) if ascending else (arr[j] > arr[i]):
                        count += 1
                if count == i:
                    break
                target = count
                while target < n and arr[target] == arr[i]:
                    if target == i:
                        break
                    target += 1
                if target == i:
                    break
                yield _base_frame(arr, highlighted=[i, target], explanation=f"Swapping to target position {target}")
                arr[i], arr[target] = arr[target], arr[i]
                yield _base_frame(arr, swapped=[i, target], operation="swap")
        yield done_frame(arr, self.name)

