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

class BinomialHeapSort(SortAlgorithm):
    name = "Binomial Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Heapsort via a Binomial Heap."
    
    def get_invariant(self) -> str:
        return "The heap is a forest of binomial trees B_k where each B_k has exactly 2^k nodes and satisfies the min-heap property."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising Binomial heap", metadata={"init_step": 0})

        class BinomialNode:
            def __init__(self, val):
                self.val = val
                self.degree = 0
                self.parent = None
                self.child = None
                self.sibling = None
                
        def link(y, z):
            y.parent = z
            y.sibling = z.child
            z.child = y
            z.degree += 1
            
        def merge_trees(h1, h2):
            if not h1: return h2
            if not h2: return h1
            res = None
            curr = None
            p1, p2 = h1, h2
            while p1 and p2:
                if p1.degree <= p2.degree:
                    node = p1
                    p1 = p1.sibling
                else:
                    node = p2
                    p2 = p2.sibling
                if not res:
                    res = node
                else:
                    curr.sibling = node
                curr = node
            if p1: curr.sibling = p1
            if p2: curr.sibling = p2
            return res
            
        def union(h1, h2):
            if not h1: return h2
            if not h2: return h1
            h = merge_trees(h1, h2)
            prev = None
            x = h
            next_x = x.sibling
            while next_x:
                if x.degree != next_x.degree or (next_x.sibling and next_x.sibling.degree == x.degree):
                    prev = x
                    x = next_x
                elif not out_of_order(x.val, next_x.val, ascending):
                    x.sibling = next_x.sibling
                    link(next_x, x)
                else:
                    if not prev:
                        h = next_x
                    else:
                        prev.sibling = next_x
                    link(x, next_x)
                    x = next_x
                next_x = x.sibling
            return h
            
        root = None
        for i in range(n):
            node = BinomialNode(arr[i])
            root = union(root, node)
            yield _base_frame(arr, highlighted=[i], metadata={"forest_size": n}, explanation="Insert and union")
            
        for i in range(n):
            # Find min
            min_node = root
            min_prev = None
            curr = root
            prev = None
            while curr:
                if out_of_order(min_node.val, curr.val, ascending):
                    min_node = curr
                    min_prev = prev
                prev = curr
                curr = curr.sibling
                
            if not min_prev:
                root = min_node.sibling
            else:
                min_prev.sibling = min_node.sibling
                
            child = min_node.child
            rev_child = None
            while child:
                next_child = child.sibling
                child.sibling = rev_child
                child.parent = None
                rev_child = child
                child = next_child
                
            root = union(root, rev_child)
            arr[i] = min_node.val
            yield _base_frame(arr, swapped=[i], metadata={"forest_size": n}, operation="write")
            
        yield done_frame(arr, self.name)

