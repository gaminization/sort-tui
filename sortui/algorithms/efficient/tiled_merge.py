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

class TiledMergeSort(SortAlgorithm):
    name = "Tiled Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Sorts tiles before merging."
    
    def get_invariant(self) -> str:
        return "Each tile of size sqrt(n) is sorted before cross-tile merges begin; tile boundaries remain visible throughout."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        import math
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        TILE_SIZE = max(4, int(math.sqrt(n)))
        aux = [0] * n
        
        # Phase 1: sort each tile with insertion sort
        for start in range(0, n, TILE_SIZE):
            end = min(start + TILE_SIZE, n)
            for i in range(start + 1, end):
                val = arr[i]
                j = i
                while j > start:
                    yield _base_frame(arr, highlighted=[j, j-1], partition_bounds=(start, end-1), metadata={"tile_size": TILE_SIZE, "phase": "tile"})
                    if out_of_order(arr[j-1], val, ascending):
                        arr[j] = arr[j-1]
                        yield _base_frame(arr, swapped=[j, j-1], partition_bounds=(start, end-1), metadata={"tile_size": TILE_SIZE, "phase": "tile"}, operation="swap")
                        j -= 1
                    else:
                        break
                arr[j] = val
                
        # Phase 2: merge tiles in passes
        width = TILE_SIZE
        while width < n:
            for i in range(0, n, 2 * width):
                l_start = i
                l_end = min(i + width, n)
                r_start = l_end
                r_end = min(i + 2 * width, n)
                
                if r_start >= n: continue
                
                p1, p2, out = l_start, r_start, l_start
                while p1 < l_end and p2 < r_end:
                    yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end-1), metadata={"tile_size": TILE_SIZE, "phase": "merge"})
                    if not out_of_order(arr[p1], arr[p2], ascending):
                        aux[out] = arr[p1]
                        p1 += 1
                    else:
                        aux[out] = arr[p2]
                        p2 += 1
                    out += 1
                    
                while p1 < l_end:
                    aux[out] = arr[p1]
                    p1 += 1
                    out += 1
                while p2 < r_end:
                    aux[out] = arr[p2]
                    p2 += 1
                    out += 1
                    
                for k in range(l_start, r_end):
                    arr[k] = aux[k]
                    yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end-1), metadata={"tile_size": TILE_SIZE, "phase": "merge"}, operation="write")
            width *= 2
            
        yield done_frame(arr, self.name)

