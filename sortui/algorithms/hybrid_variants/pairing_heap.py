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

class PairingHeapSort(SortAlgorithm):
    name = "Pairing Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Heapsort via a Pairing Heap."
    
    def get_invariant(self) -> str:
        return "Each node's value is >= all values in its subtrees; the two-pass pairing on delete-min preserves the heap property."


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

            
        class PairingNode:
            def __init__(self, val):
                self.val = val
                self.subheaps = []
                
        def merge(h1, h2):
            if not h1: return h2
            if not h2: return h1
            if not out_of_order(h1.val, h2.val, ascending):
                h1.subheaps.append(h2)
                return h1
            else:
                h2.subheaps.append(h1)
                return h2
                
        def two_pass_merge(subheaps):
            if not subheaps: return None
            if len(subheaps) == 1: return subheaps[0]
            
            merged_pairs = []
            for i in range(0, len(subheaps), 2):
                if i + 1 < len(subheaps):
                    merged_pairs.append(merge(subheaps[i], subheaps[i+1]))
                else:
                    merged_pairs.append(subheaps[i])
                    
            res = merged_pairs[-1]
            for i in range(len(merged_pairs) - 2, -1, -1):
                res = merge(res, merged_pairs[i])
            return res
            
        # Phase 1: Build pairing heap
        root = None
        for i in range(n):
            node = PairingNode(arr[i])
            root = merge(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"heap_size": n, "phase": "build"}, explanation="Insert element")
            
        # Phase 2: Extract min
        for i in range(n):
            min_val = root.val
            root = two_pass_merge(root.subheaps)
            arr[i] = min_val
            yield _base_frame(arr, swapped=[i], metadata={"heap_size": n, "phase": "extract"}, operation="write")
            
        yield done_frame(arr, self.name)

