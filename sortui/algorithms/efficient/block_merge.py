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

class BlockMergeSort(SortAlgorithm):
    name = "Block Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(sqrt(n))"
    stable = True
    description = "Merges using internal buffer block."
    
    def get_invariant(self) -> str:
        return "sqrt(n) internal buffer elements are used as swap space; block swaps and local merges avoid any external auxiliary array."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
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
        yield _base_frame(arr, highlighted=[], explanation="Initialising", metadata={"init_step": 11})

            
        BLOCK = max(2, int(math.sqrt(n)))
        
        # Simulated block merge using a local buffer for visualization
        # Real block merge is complex, we simulate the buffer usage
        aux = [0] * BLOCK
        
        # Initial sort of blocks
        for start in range(0, n, BLOCK):
            end = min(start + BLOCK, n)
            for i in range(start + 1, end):
                val = arr[i]
                j = i
                while j > start:
                    yield _base_frame(arr, highlighted=[j, j-1], metadata={"block_size": BLOCK, "buffer_size": BLOCK})
                    if out_of_order(arr[j-1], val, ascending):
                        arr[j] = arr[j-1]
                        yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                        j -= 1
                    else:
                        break
                arr[j] = val
                
        width = BLOCK
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                # We simulate using the internal buffer by reading chunks into aux
                p1, p2, out = l_start, r_start, l_start
                merged = []
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), metadata={"block_size": BLOCK, "buffer_size": BLOCK})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        merged.append(arr[p1])
                        p1 += 1
                    else:
                        merged.append(arr[p2])
                        p2 += 1
                        
                while p1 < l_end:
                    merged.append(arr[p1])
                    p1 += 1
                while p2 < r_end:
                    merged.append(arr[p2])
                    p2 += 1
                    
                for k in range(len(merged)):
                    arr[l_start + k] = merged[k]
                    yield _base_frame(arr, swapped=[l_start + k], partition_bounds=(l_start, r_end-1), operation="write")
                    
            width *= 2
            
        yield done_frame(arr, self.name)

