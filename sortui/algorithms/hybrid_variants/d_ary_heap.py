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

class DAryHeapSort(SortAlgorithm):
    name = "D-ary Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log_d n)"
    space_complexity = "O(1)"
    stable = False
    description = "Heapsort with a 4-ary heap."
    
    def get_invariant(self) -> str:
        return "Each node has exactly d=4 children; parent at i has children at d*i+1 through d*i+d, maintaining max-d-heap property."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        D = 4
        
        def sift_down(start: int, end: int):
            root = start
            while True:
                child = D * root + 1
                if child > end:
                    break
                
                swap = root
                for c in range(child, min(child + D, end + 1)):
                    yield _base_frame(arr, highlighted=[swap, c], metadata={"d": D, "phase": "heapify"})
                    if out_of_order(arr[c], arr[swap], ascending):
                        swap = c
                        
                if swap == root:
                    break
                arr[root], arr[swap] = arr[swap], arr[root]
                yield _base_frame(arr, swapped=[root, swap], operation="swap", metadata={"d": D, "phase": "heapify"})
                root = swap
                
        # Build heap
        for i in range((n - 2) // D, -1, -1):
            yield from sift_down(i, n - 1)
            
        # Extract max
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            yield _base_frame(arr, swapped=[0, i], operation="swap", metadata={"d": D, "phase": "extract"})
            yield from sift_down(0, i - 1)
            
        yield done_frame(arr, self.name)

