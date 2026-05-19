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

class NintherQuicksort(SortAlgorithm):
    name = "Ninther Quicksort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort using Tukey's ninther pivot selection."
    
    def get_invariant(self) -> str:
        return "Pivot is Tukey's ninther: median of three medians of three triples — 9 elements examined, extremely robust pivot."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
            
        def _median3(i, j, k):
            a, b, c = arr[i], arr[j], arr[k]
            yield _base_frame(arr, highlighted=[i, j, k], explanation="Median of triple")
            if (a < b) if ascending else (a > b):
                if (b < c) if ascending else (b > c): return j
                elif (a < c) if ascending else (a > c): return k
                else: return i
            else:
                if (a < c) if ascending else (a > c): return i
                elif (b < c) if ascending else (b > c): return k
                else: return j
                
        def _quick(lo, hi, depth):
            if lo >= hi: return
            if hi - lo < 8:
                # insertion fallback
                for i in range(lo+1, hi+1):
                    val = arr[i]
                    j = i
                    while j > lo:
                        yield _base_frame(arr, highlighted=[j, j-1])
                        if out_of_order(arr[j-1], val, ascending):
                            arr[j] = arr[j-1]
                            yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                            j -= 1
                        else: break
                    arr[j] = val
                return
                
            step = (hi - lo) // 8
            yield _base_frame(arr, highlighted=[lo, lo+step, lo+2*step, lo+3*step, lo+4*step, lo+5*step, lo+6*step, lo+7*step, hi], metadata={"candidates": 9, "method": "tukey_ninther"})
            
            m1 = yield from _median3(lo, lo+step, lo+2*step)
            m2 = yield from _median3(lo+3*step, lo+4*step, lo+5*step)
            m3 = yield from _median3(lo+6*step, lo+7*step, hi)
            med_idx = yield from _median3(m1, m2, m3)
            
            yield _base_frame(arr, highlighted=[med_idx], explanation="Median of medians selected")
            arr[med_idx], arr[hi] = arr[hi], arr[med_idx]
            pivot = arr[hi]
            
            i_ptr = lo
            for j in range(lo, hi):
                yield _base_frame(arr, highlighted=[j, hi], pivot_index=hi)
                if (arr[j] <= pivot) if ascending else (arr[j] >= pivot):
                    arr[i_ptr], arr[j] = arr[j], arr[i_ptr]
                    if i_ptr != j:
                        yield _base_frame(arr, swapped=[i_ptr, j], pivot_index=hi, operation="swap")
                    i_ptr += 1
            arr[i_ptr], arr[hi] = arr[hi], arr[i_ptr]
            yield _base_frame(arr, swapped=[i_ptr, hi], pivot_index=i_ptr, operation="swap")
            
            yield from _quick(lo, i_ptr - 1, depth + 1)
            yield from _quick(i_ptr + 1, hi, depth + 1)
            
        yield from _quick(0, n - 1, 0)
        yield done_frame(arr, self.name)

