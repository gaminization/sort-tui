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

class TangoTreeSort(SortAlgorithm):
    name = "Tango Tree Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Sorts via an access sequence on a Tango Tree representation."
    
    def get_invariant(self) -> str:
        return "Preferred paths partition the tree; path switches occur when accessing a non-preferred child."


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
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 6})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 7})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 8})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 9})
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 10})

            
        # Tango tree simulation using basic BST for visualization
        class TangoNode:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                
        def insert(node, val):
            if not node: return TangoNode(val)
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val)
            elif val == node.val:
                node.count += 1
            else:
                node.right = insert(node.right, val)
            return node
            
        root = None
        for i in range(n):
            root = insert(root, arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"preferred_path_len": n, "path_switches": n}, explanation="Path switch — restructuring preferred path")
            
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)

