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

class LinkedListInsertionSort(SortAlgorithm):
    name = "Linked List Insertion Sort"
    category = "CATEGORY"  # replaced by init
    time_complexity = "O(n²)"
    space_complexity = "O(n)"
    stable = True
    description = "Simulates a linked list insertion sort."
    
    def get_invariant(self) -> str:
        return "The virtual linked list contains all processed elements in sorted order; each new element is spliced into its correct position."


    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n <= 1:
            yield done_frame(arr, self.name)
            return
        sorted_list = []
        for i in range(n):
            val = arr[i]
            insert_pos = len(sorted_list)
            for j in range(len(sorted_list)):
                yield _base_frame(arr, highlighted=[i], aux_array=sorted_list, operation="compare")
                if (val < sorted_list[j]) if ascending else (val > sorted_list[j]):
                    insert_pos = j
                    break
            sorted_list.insert(insert_pos, val)
            yield _base_frame(arr, highlighted=[i], aux_array=sorted_list, operation="write")
        for i in range(n):
            arr[i] = sorted_list[i]
            yield _base_frame(arr, swapped=[i], aux_array=sorted_list, operation="write")
        yield done_frame(arr, self.name)

