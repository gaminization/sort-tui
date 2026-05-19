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

class DiagonalSort(SortAlgorithm):
    name = "Diagonal Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Sorts elements conceptually arranged in a matrix by diagonals."
    
    def get_invariant(self) -> str:
        return "All elements in each completed diagonal strip are sorted relative to their diagonal neighbors."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        w = int(math.ceil(math.sqrt(n)))
        diagonals = {}
        for i in range(n):
            d = (i % w) - (i // w)
            diagonals.setdefault(d, []).append(i)
            
        for d, indices in diagonals.items():
            for i in range(1, len(indices)):
                val = arr[indices[i]]
                j = i
                while j > 0:
                    yield _base_frame(arr, highlighted=indices, metadata={"diagonal": d, "width": w})
                    if out_of_order(arr[indices[j-1]], val, ascending):
                        arr[indices[j]] = arr[indices[j-1]]
                        yield _base_frame(arr, swapped=[indices[j], indices[j-1]], metadata={"diagonal": d, "width": w}, operation="swap")
                        j -= 1
                    else:
                        break
                arr[indices[j]] = val
        
        # Final pass to fully sort the array
        for i in range(1, n):
            val = arr[i]
            j = i
            while j > 0:
                yield _base_frame(arr, highlighted=[j, j-1])
                if out_of_order(arr[j-1], val, ascending):
                    arr[j] = arr[j-1]
                    yield _base_frame(arr, swapped=[j, j-1], operation="swap")
                    j -= 1
                else:
                    break
            arr[j] = val
        yield done_frame(arr, self.name)
