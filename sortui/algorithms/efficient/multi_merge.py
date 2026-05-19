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

class MultiWayMergeSort(SortAlgorithm):
    name = "Multi-way Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log k log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Splits array into k runs and merges them."
    
    def get_invariant(self) -> str:
        return "A min-heap of size k holds the front elements of k sorted runs; the heap minimum is always the next output element."


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

            
        K_WAYS = max(3, min(8, n//10))
        if K_WAYS < 2: K_WAYS = 2
        
        run_size = (n + K_WAYS - 1) // K_WAYS
        runs = []
        for i in range(0, n, run_size):
            end = min(i + run_size, n)
            run = arr[i:end]
            run.sort(reverse=not ascending)
            runs.append(run)
            for j in range(i, end):
                arr[j] = run[j-i]
                yield _base_frame(arr, swapped=[j], operation="write")
                
        import heapq
        heap = []
        for i, r in enumerate(runs):
            if r:
                heapq.heappush(heap, (r[0] if ascending else -r[0], i, 0))
                
        idx = 0
        while heap:
            val, r_idx, elem_idx = heapq.heappop(heap)
            arr[idx] = runs[r_idx][elem_idx]
            heap_vals = [h[0] if ascending else -h[0] for h in heap]
            yield _base_frame(arr, swapped=[idx], aux_array=heap_vals, metadata={"k": K_WAYS, "heap_size": len(heap)}, operation="write")
            idx += 1
            if elem_idx + 1 < len(runs[r_idx]):
                next_val = runs[r_idx][elem_idx + 1]
                heapq.heappush(heap, (next_val if ascending else -next_val, r_idx, elem_idx + 1))
                
        yield done_frame(arr, self.name)

