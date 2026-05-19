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

class FibonacciHeapSort(SortAlgorithm):
    name = "Fibonacci Heap Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Heapsort via a Fibonacci Heap."
    
    def get_invariant(self) -> str:
        return "Trees are lazily consolidated; marked nodes have lost one child since becoming non-root — cascading cuts maintain O(log n) rank."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        yield _base_frame(arr, highlighted=[], explanation="Initialising Fibonacci heap", metadata={"init_step": 0})
        yield _base_frame(arr, highlighted=[], explanation="Initialising Fibonacci heap", metadata={"init_step": 1})
        yield _base_frame(arr, highlighted=[], explanation="Initialising Fibonacci heap", metadata={"init_step": 2})


        class FibNode:
            def __init__(self, val):
                self.val = val
                self.degree = 0
                self.parent = None
                self.child = None
                self.left = self
                self.right = self
                self.marked = False
                
        def insert_node(min_node, node):
            if not min_node:
                return node
            node.left = min_node
            node.right = min_node.right
            min_node.right.left = node
            min_node.right = node
            if out_of_order(min_node.val, node.val, ascending):
                return node
            return min_node
            
        def link(y, x):
            y.left.right = y.right
            y.right.left = y.left
            y.parent = x
            if not x.child:
                x.child = y
                y.left = y
                y.right = y
            else:
                y.left = x.child
                y.right = x.child.right
                x.child.right.left = y
                x.child.right = y
            x.degree += 1
            y.marked = False
            
        def consolidate(min_node):
            D = int(math.log(n) * 2) + 1
            A = [None] * D
            nodes = []
            curr = min_node
            if curr:
                nodes.append(curr)
                curr = curr.right
                while curr != min_node:
                    nodes.append(curr)
                    curr = curr.right
                    
            for w in nodes:
                x = w
                d = x.degree
                while A[d] != None:
                    y = A[d]
                    if out_of_order(x.val, y.val, ascending):
                        x, y = y, x
                    link(y, x)
                    A[d] = None
                    d += 1
                A[d] = x
                
            new_min = None
            for i in range(D):
                if A[i]:
                    A[i].left = A[i]
                    A[i].right = A[i]
                    new_min = insert_node(new_min, A[i])
            return new_min
            
        min_node = None
        for i in range(n):
            node = FibNode(arr[i])
            min_node = insert_node(min_node, node)
            yield _base_frame(arr, highlighted=[i], metadata={"trees": n, "marked": n, "phase": "insert"})
            
        for i in range(n):
            z = min_node
            if z:
                curr = z.child
                children = []
                if curr:
                    children.append(curr)
                    curr = curr.right
                    while curr != z.child:
                        children.append(curr)
                        curr = curr.right
                for child in children:
                    child.parent = None
                    min_node = insert_node(min_node, child)
                    
                z.left.right = z.right
                z.right.left = z.left
                if z == z.right:
                    min_node = None
                else:
                    min_node = z.right
                    min_node = consolidate(min_node)
                    
                arr[i] = z.val
                yield _base_frame(arr, swapped=[i], metadata={"trees": n, "marked": n, "phase": "extract"}, operation="write")
                
        yield done_frame(arr, self.name)

