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

class PingPongMergeSort(SortAlgorithm):
    name = "Ping-Pong Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Alternates src and dst buffers."
    
    def get_invariant(self) -> str:
        return "Sorted runs alternate between two buffers each pass; the active buffer and output buffer swap roles every merge pass."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        src = arr[:]
        dst = [0] * n
        width = 1
        pass_num = 0
        
        while width < n:
            buffer_name = "A" if pass_num % 2 == 0 else "B"
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n:
                    for k in range(l_start, l_end):
                        dst[k] = src[k]
                    continue
                    
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, aux_array=dst, metadata={"pass": pass_num, "buffer": buffer_name})
                    if not out_of_order(src[p1], src[p2], ascending):
                        dst[out] = src[p1]
                        p1 += 1
                    else:
                        dst[out] = src[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    dst[out] = src[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    dst[out] = src[p2]
                    p2 += 1
                    out += 1
                    
            src, dst = dst, src
            width *= 2
            pass_num += 1
            
        for i in range(n):
            arr[i] = src[i]
            yield _base_frame(arr, swapped=[i], operation="write")
                
        yield done_frame(arr, self.name)

