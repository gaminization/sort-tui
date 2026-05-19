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

class OptimizedPatienceSort(SortAlgorithm):
    name = "Patience Sort (Optimized)"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Patience sort using binary search for pile placement."
    
    def get_invariant(self) -> str:
        return "Each pile's top is the smallest in that pile; binary search finds the leftmost pile whose top >= current card."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        piles = []
        for i in range(n):
            val = arr[i]
            left, right = 0, len(piles)
            while left < right:
                mid = (left + right) // 2
                yield _base_frame(arr, highlighted=[i], metadata={"pile_count": len(piles), "search": "binary", "mid": mid})
                if (piles[mid][-1] > val) if ascending else (piles[mid][-1] < val):
                    right = mid
                else:
                    left = mid + 1
            if left == len(piles):
                piles.append([val])
            else:
                piles[left].append(val)
        
        # Merge piles
        import heapq
        heap = []
        for i, p in enumerate(piles):
            heapq.heappush(heap, (p[-1] if ascending else -p[-1], i))
        
        for i in range(n):
            _, p_idx = heapq.heappop(heap)
            val = piles[p_idx].pop()
            if piles[p_idx]:
                heapq.heappush(heap, (piles[p_idx][-1] if ascending else -piles[p_idx][-1], p_idx))
            arr[i] = val
            yield _base_frame(arr, swapped=[i], operation="write")
        yield done_frame(arr, self.name)

