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

class TapeMergeSort(SortAlgorithm):
    name = "Tape Merge Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Simulates 4-tape merge sort."
    
    def get_invariant(self) -> str:
        return "Two virtual input tapes hold sorted runs alternately; each merge pass reads both tapes and writes to two output tapes."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        tapes = [[], [], [], []]
        
        # Initial distribution
        for i in range(n):
            tapes[i % 2].append(arr[i])
            yield _base_frame(arr, highlighted=[i], metadata={"tape_A": len(tapes[0]), "tape_B": len(tapes[1]), "tape_C": len(tapes[2]), "tape_D": len(tapes[3]), "pass": 0})
            
        run_size = 1
        pass_num = 1
        
        while True:
            tapes[2] = []
            tapes[3] = []
            
            i, j = 0, 0
            out_idx = 0
            
            while i < len(tapes[0]) or j < len(tapes[1]):
                l_start = i
                l_end = min(i + run_size, len(tapes[0]))
                r_start = j
                r_end = min(j + run_size, len(tapes[1]))
                
                while i < l_end and j < r_end:
                    yield _base_frame(arr, metadata={"tape_A": len(tapes[0]), "tape_B": len(tapes[1]), "tape_C": len(tapes[2]), "tape_D": len(tapes[3]), "pass": pass_num})
                    if not out_of_order(tapes[0][i], tapes[1][j], ascending):
                        tapes[2 + out_idx % 2].append(tapes[0][i])
                        i += 1
                    else:
                        tapes[2 + out_idx % 2].append(tapes[1][j])
                        j += 1
                        
                while i < l_end:
                    tapes[2 + out_idx % 2].append(tapes[0][i])
                    i += 1
                while j < r_end:
                    tapes[2 + out_idx % 2].append(tapes[1][j])
                    j += 1
                    
                out_idx += 1
                
            tapes[0], tapes[1] = tapes[2], tapes[3]
            run_size *= 2
            pass_num += 1
            
            if len(tapes[1]) == 0:
                break
                
        for i in range(n):
            arr[i] = tapes[0][i]
            yield _base_frame(arr, swapped=[i], operation="write")
            
        yield done_frame(arr, self.name)

