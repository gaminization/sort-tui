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

class SkewHeapSort(SortAlgorithm):
    name = "Skew Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Heapsort via a Skew Heap."
    
    def get_invariant(self) -> str:
        return "Skew merge always swaps left and right children of the root after each merge — no rank tracking needed."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 0})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 1})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 2})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 3})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 4})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 5})

            
        class SkewNode:
            def __init__(self, val, idx):
                self.val = val
                self.idx = idx
                self.left = None
                self.right = None
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if out_of_order(h1.val, h2.val, ascending):
                h1, h2 = h2, h1
                
            h1.right = merge(h1.right, h2)
            h1.left, h1.right = h1.right, h1.left
            return h1
            
        root = None
        for i in range(n):
            node = SkewNode(arr[i], i)
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"phase": "build", "merges": n})
            
        for i in range(n):
            min_val = root.val
            root = merge(root.left, root.right)
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"phase": "extract", "merges": n}, operation="write")
            
        yield done_frame(arr, self.name)

