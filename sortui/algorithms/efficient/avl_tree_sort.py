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

class AVLTreeSort(SortAlgorithm):
    name = "AVL Tree Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Sorts using an AVL tree."
    
    def get_invariant(self) -> str:
        return "Every AVL node's left and right subtree heights differ by at most 1; rotations restore this after every insertion."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        class AVLNode:
            def __init__(self, val, idx):
                self.val = val
                self.idx = idx
                self.left = None
                self.right = None
                self.height = 1
                self.count = 1
                
        def get_height(node):
            return node.height if node else 0
            
        def get_balance(node):
            return get_height(node.left) - get_height(node.right) if node else 0
            
        def right_rotate(y, frames_list):
            x = y.left
            T2 = x.right
            x.right = y
            y.left = T2
            y.height = 1 + max(get_height(y.left), get_height(y.right))
            x.height = 1 + max(get_height(x.left), get_height(x.right))
            frames_list.append(("LL", y.idx, x.idx))
            return x
            
        def left_rotate(x, frames_list):
            y = x.right
            T2 = y.left
            y.left = x
            x.right = T2
            x.height = 1 + max(get_height(x.left), get_height(x.right))
            y.height = 1 + max(get_height(y.left), get_height(y.right))
            frames_list.append(("RR", x.idx, y.idx))
            return y
            
        def insert(node, val, idx, frames_list):
            if not node:
                return AVLNode(val, idx)
                
            if (val < node.val) if ascending else (val > node.val):
                node.left = insert(node.left, val, idx, frames_list)
            elif val == node.val:
                node.count += 1
                return node
            else:
                node.right = insert(node.right, val, idx, frames_list)
                
            node.height = 1 + max(get_height(node.left), get_height(node.right))
            balance = get_balance(node)
            
            if balance > 1 and ((val < node.left.val) if ascending else (val > node.left.val)):
                return right_rotate(node, frames_list)
            if balance < -1 and ((val > node.right.val) if ascending else (val < node.right.val)):
                return left_rotate(node, frames_list)
            if balance > 1 and ((val > node.left.val) if ascending else (val < node.left.val)):
                node.left = left_rotate(node.left, frames_list)
                return right_rotate(node, frames_list)
            if balance < -1 and ((val < node.right.val) if ascending else (val > node.right.val)):
                node.right = right_rotate(node.right, frames_list)
                return left_rotate(node, frames_list)
                
            return node
            
        root = None
        for i in range(n):
            frames_list = []
            root = insert(root, arr[i], i, frames_list)
            yield _base_frame(arr, highlighted=[i], metadata={"rotation": "none", "balance_factor": n, "tree_size": n}, explanation="Insert node")
            for rot in frames_list:
                yield _base_frame(arr, swapped=[rot[1], rot[2]], metadata={"rotation": rot[0], "balance_factor": n, "tree_size": n}, operation="swap", explanation="Rebalance via rotation")
                
        idx = 0
        def inorder(node) -> Generator[SortFrame, None, None]:
            nonlocal idx
            if not node: return
            yield from inorder(node.left)
            for _ in range(node.count):
                arr[idx] = node.val
                yield _base_frame(arr, swapped=[idx], operation="write", explanation="Writing sorted element")
                idx += 1
            yield from inorder(node.right)
            
        yield from inorder(root)
        yield done_frame(arr, self.name)

