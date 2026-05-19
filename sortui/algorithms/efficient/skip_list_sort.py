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

class SkipListSort(SortAlgorithm):
    name = "Skip List Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n log n)"
    stable = True
    description = "Sorts using a randomized Skip List."
    
    def get_invariant(self) -> str:
        return "Each element appears in level 0; each higher level contains a geometrically shrinking random subset of level below."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math, random
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

            
        MAX_LEVELS = max(2, int(math.log2(n+1))+1)
        
        class SkipNode:
            def __init__(self, val, level):
                self.val = val
                self.forward = [None] * (level + 1)
                
        head = SkipNode(float('-inf') if ascending else float('inf'), MAX_LEVELS)
        
        for i in range(n):
            val = arr[i]
            update = [None] * (MAX_LEVELS + 1)
            curr = head
            
            for l in range(MAX_LEVELS, -1, -1):
                while curr.forward[l] and not out_of_order(curr.forward[l].val, val, ascending):
                    curr = curr.forward[l]
                update[l] = curr
                
            level = 0
            while random.random() < 0.5 and level < MAX_LEVELS:
                level += 1
                
            yield _base_frame(arr, highlighted=[i], metadata={"levels": MAX_LEVELS, "element_level": level, "current_level": 0})
            
            node = SkipNode(val, level)
            for l in range(level + 1):
                node.forward[l] = update[l].forward[l]
                update[l].forward[l] = node
                
        curr = head.forward[0]
        idx = 0
        while curr:
            arr[idx] = curr.val
            yield _base_frame(arr, swapped=[idx], operation="write")
            idx += 1
            curr = curr.forward[0]
            
        yield done_frame(arr, self.name)

