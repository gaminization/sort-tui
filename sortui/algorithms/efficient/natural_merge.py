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

class NaturalMergeSort(SortAlgorithm):
    name = "Natural Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Natural runs are detected and used directly."
    
    def get_invariant(self) -> str:
        return "Natural runs (existing ascending sequences) are detected and used directly; only run boundaries are merged, never internal."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        aux = [0] * n
        
        while True:
            # Phase 1: Detect runs
            runs = []
            i = 0
            while i < n:
                start = i
                yield _base_frame(arr, highlighted=[i], metadata={"phase": "detect", "run_count": n})
                while i < n - 1:
                    yield _base_frame(arr, highlighted=[i, i+1], metadata={"phase": "detect", "run_count": n})
                    if not out_of_order(arr[i], arr[i+1], ascending):
                        i += 1
                    else:
                        break
                runs.append((start, i + 1))
                i += 1
                
            if len(runs) <= 1:
                break
                
            # Phase 2: Merge adjacent runs
            new_runs = []
            for j in range(0, len(runs), 2):
                if j + 1 < len(runs):
                    l_start, l_end = runs[j]
                    r_start, r_end = runs[j+1]
                    
                    p1, p2, out = l_start, r_start, l_start
                    while p1 < l_end and p2 < r_end:
                        yield _base_frame(arr, highlighted=[p1, p2], partition_bounds=(l_start, r_end - 1), aux_array=aux)
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
                        yield _base_frame(arr, swapped=[k], partition_bounds=(l_start, r_end - 1), aux_array=aux, operation="write")
                    new_runs.append((l_start, r_end))
                else:
                    new_runs.append(runs[j])
            runs = new_runs
            
        yield done_frame(arr, self.name)

