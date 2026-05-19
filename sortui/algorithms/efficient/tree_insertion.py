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

class TreeInsertionSort(SortAlgorithm):
    name = "Tree Insertion Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Builds a BST and traverses it."
    
    def get_invariant(self) -> str:
        return "The BST contains all elements seen so far; its inorder traversal yields them in sorted order at every step."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        
        class Node:
            def __init__(self, val):
                self.val = val
                self.left = None
                self.right = None
                self.count = 1
                
        root = None
        for i in range(n):
            val = arr[i]
            if root is None:
                root = Node(val)
                yield _base_frame(arr, highlighted=[i], metadata={"phase": "insert", "tree_size": i+1}, explanation="Insert root")
            else:
                curr = root
                while True:
                    yield _base_frame(arr, highlighted=[i], metadata={"phase": "insert", "tree_size": i+1}, operation="compare")
                    if (val < curr.val) if ascending else (val > curr.val):
                        if curr.left is None:
                            curr.left = Node(val)
                            break
                        curr = curr.left
                    elif val == curr.val:
                        curr.count += 1
                        break
                    else:
                        if curr.right is None:
                            curr.right = Node(val)
                            break
                        curr = curr.right
        
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, highlighted=[idx], metadata={"phase": "extract", "tree_size": n}, operation="write")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)

