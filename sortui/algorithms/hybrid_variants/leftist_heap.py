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

class LeftistHeapSort(SortAlgorithm):
    name = "Leftist Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Heapsort via a Leftist Heap."
    
    def get_invariant(self) -> str:
        return "The right spine length (s-value) is always <= log2(n+1); merges always happen along the right spine."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 0})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 1})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 2})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 3})

            
        class LeftistNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.s_value = 1
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if out_of_order(h1.val, h2.val, ascending):
                h1, h2 = h2, h1
                
            h1.right = merge(h1.right, h2)
            
            left_s = h1.left.s_value if h1.left else 0
            right_s = h1.right.s_value if h1.right else 0
            
            if left_s < right_s:
                h1.left, h1.right = h1.right, h1.left
                
            h1.s_value = (h1.right.s_value if h1.right else 0) + 1
            return h1
            
        root = None
        for i in range(n):
            node = LeftistNode(arr[i])
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"s_value": root.s_value, "right_spine_len": n})
            
        for i in range(n):
            min_val = root.val
            root = merge(root.left, root.right)
            s_val = root.s_value if root else 0
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"s_value": s_val, "right_spine_len": n}, operation="write")
            
        yield done_frame(arr, self.name)

