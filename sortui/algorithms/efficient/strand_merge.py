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

class StrandMergeSort(SortAlgorithm):
    name = "Strand Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Extracts maximal ascending subsequences."
    
    def get_invariant(self) -> str:
        return "Each extracted strand is a maximal ascending subsequence; strands are merged via priority queue until one strand remains."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        strands = []
        unprocessed = arr[:]
        
        # Phase 1: extract strands
        while unprocessed:
            strand = [unprocessed.pop(0)]
            i = 0
            while i < len(unprocessed):
                yield _base_frame(arr, highlighted=[n - len(unprocessed) + i], aux_array=strand, metadata={"strand_count": n, "phase": "extract"})
                if not out_of_order(strand[-1], unprocessed[i], ascending):
                    strand.append(unprocessed.pop(i))
                else:
                    i += 1
            strands.append(strand)
            
        # Phase 2: merge strands using heapq
        import heapq
        heap = []
        for i, s in enumerate(strands):
            heapq.heappush(heap, (s[0] if ascending else -s[0], i, 0))
            
        idx = 0
        while heap:
            val, s_idx, elem_idx = heapq.heappop(heap)
            arr[idx] = strands[s_idx][elem_idx]
            yield _base_frame(arr, swapped=[idx], metadata={"strand_count": n, "phase": "merge"}, operation="write")
            idx += 1
            if elem_idx + 1 < len(strands[s_idx]):
                next_val = strands[s_idx][elem_idx + 1]
                heapq.heappush(heap, (next_val if ascending else -next_val, s_idx, elem_idx + 1))
                
        yield done_frame(arr, self.name)

