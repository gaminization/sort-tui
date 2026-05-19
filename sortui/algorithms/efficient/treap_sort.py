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

class TreapSort(SortAlgorithm):
    name = "Treap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Sorts using a Treap."
    
    def get_invariant(self) -> str:
        return "Each node satisfies BST order on keys and heap order on random priorities; rotations maintain both properties."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import random
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class TreapNode:
            def __init__(self, val, priority):
                self.val = val
                self.priority = priority
                self.left = None
                self.right = None
                self.count = 1
                
        def right_rotate(y):
            x = y.left
            T2 = x.right
            x.right = y
            y.left = T2
            return x
            
        def left_rotate(x):
            y = x.right
            T2 = y.left
            y.left = x
            x.right = T2
            return y
            
        def insert(node, val, priority, frames_list):
            if not node:
                return TreapNode(val, priority)
                
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val, priority, frames_list)
                if node.left.priority > node.priority:
                    frames_list.append("right")
                    node = right_rotate(node)
            elif val == node.val:
                node.count += 1
                return node
            else:
                node.right = insert(node.right, val, priority, frames_list)
                if node.right.priority > node.priority:
                    frames_list.append("left")
                    node = left_rotate(node)
            return node
            
        root = None
        for i in range(n):
            p = random.random()
            frames_list = []
            root = insert(root, arr[i], p, frames_list)
            yield _base_frame(arr, highlighted=[i], metadata={"priority": p, "rotation": "none"})
            for rot in frames_list:
                yield _base_frame(arr, highlighted=[i], metadata={"priority": p, "rotation": rot})
                
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

