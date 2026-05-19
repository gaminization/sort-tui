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

class GravitySortSimulation(SortAlgorithm):
    name = "Gravity Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n·max)"
    space_complexity = "O(n·max)"
    stable = False
    description = "Simulates falling beads."
    
    def get_invariant(self) -> str:
        return "Each column's bead count equals the number of elements whose value is >= that column's row index after each gravity pass."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        if not ascending:
            arr.reverse()
        max_val = max(arr)
        if max_val == 0:
            yield done_frame(arr, self.name)
            return
        beads = [[0]*max_val for _ in range(n)]
        for i in range(n):
            for j in range(arr[i]):
                beads[i][j] = 1
        for j in range(max_val):
            yield _base_frame(arr, highlighted=[], explanation=f"Gravity pass for column {j}", aux_array=[sum(row) for row in beads])
            sum_col = sum(beads[i][j] for i in range(n))
            for i in range(n):
                beads[i][j] = 1 if i >= n - sum_col else 0
            for i in range(n):
                arr[i] = sum(beads[i])
            yield _base_frame(arr, operation="write", explanation="Beads settled")
        if not ascending:
            arr.reverse()
        yield done_frame(arr, self.name)

