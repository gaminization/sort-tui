from __future__ import annotations

import heapq
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    done_frame,
    heap_sort_range,
    in_order,
    merge_runs,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from
from sortui.algorithms.hybrid_variants.d_ary_heap import DAryHeapSort
from sortui.algorithms.hybrid_variants.pairing_heap import PairingHeapSort
from sortui.algorithms.hybrid_variants.skew_heap import SkewHeapSort
from sortui.algorithms.hybrid_variants.leftist_heap import LeftistHeapSort
from sortui.algorithms.hybrid_variants.binomial_heap import BinomialHeapSort
from sortui.algorithms.hybrid_variants.fibonacci_heap import FibonacciHeapSort

CATEGORY = "Hybrid Variants"


class WeakHeapSort(SortAlgorithm):
    name = "Weak Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Weak-heap visualization with flag-bit combine operations."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        flags = [0] * len(arr)
        for i in range(len(arr) - 1, 0, -1):
            parent = (i - 1) // 2
            yield base_frame(
                arr,
                highlighted=[parent, i],
                explanation=f"{self.name}: combining weak-heap node {i} with its parent.",
                operation="compare",
                metadata={"flags": flags[:]},
            )
            if out_of_order(arr[parent], arr[i], ascending):
                arr[parent], arr[i] = arr[i], arr[parent]
                flags[i] ^= 1
                yield base_frame(
                    arr,
                    swapped=[parent, i],
                    explanation=f"{self.name}: toggling a weak-heap reverse bit after combine.",
                    operation="swap",
                    metadata={"flags": flags[:]},
                )
        yield from heap_sort_range(arr, 0, len(arr), ascending, self.name, metadata={"flags": flags[:]})
        yield done_frame(arr, self.name, metadata={"flags": flags[:]})

    def get_invariant(self) -> str:
        return "Each merge step maintains the weak-heap property: every right-spine child is <= its grandparent."


class BottomUpHeapSort(SortAlgorithm):
    name = "Bottom-Up Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Heapsort with bottom-up sift-down annotations."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def better(left: Any, right: Any) -> bool:
            return value_of(left) > value_of(right) if ascending else value_of(left) < value_of(right)

        def sift_bottom_up(root: int, end: int) -> Generator[SortFrame, None, None]:
            if root > end:
                return
            displaced = arr[root]
            hole = root
            yield base_frame(
                arr,
                highlighted=[root],
                explanation=f"{self.name}: lifting the root value out and opening a heap hole.",
                operation="read",
                metadata={"phase": "sift_down_to_leaf"},
            )
            while 2 * hole + 1 <= end:
                child = 2 * hole + 1
                right = child + 1
                if right <= end:
                    yield base_frame(
                        arr,
                        highlighted=[child, right],
                        explanation=f"{self.name}: choosing the better child while descending to a leaf.",
                        operation="compare",
                        metadata={"phase": "sift_down_to_leaf"},
                    )
                    if better(arr[right], arr[child]):
                        child = right
                arr[hole] = arr[child]
                yield base_frame(
                    arr,
                    swapped=[hole, child],
                    explanation=f"{self.name}: moving a child up while the heap hole travels downward.",
                    operation="write",
                    metadata={"phase": "sift_down_to_leaf"},
                )
                hole = child
            while hole > root:
                parent = (hole - 1) // 2
                yield base_frame(
                    arr,
                    highlighted=[parent, hole],
                    explanation=f"{self.name}: testing whether the displaced value should sift back upward.",
                    operation="compare",
                    metadata={"phase": "sift_up"},
                )
                if better(displaced, arr[parent]):
                    arr[hole] = arr[parent]
                    yield base_frame(
                        arr,
                        swapped=[parent, hole],
                        explanation=f"{self.name}: moving a parent down as the displaced value sifts up.",
                        operation="write",
                        metadata={"phase": "sift_up"},
                    )
                    hole = parent
                else:
                    break
            arr[hole] = displaced
            yield base_frame(
                arr,
                swapped=[hole],
                explanation=f"{self.name}: placing the displaced value into the final heap hole.",
                operation="write",
                metadata={"phase": "sift_up"},
            )

        for start in range(n // 2 - 1, -1, -1):
            yield from sift_bottom_up(start, n - 1)
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            yield base_frame(
                arr,
                swapped=[0, end],
                explanation=f"{self.name}: extracting the heap root before bottom-up repair.",
                operation="swap",
                metadata={"phase": "extract"},
            )
            yield from sift_bottom_up(0, end - 1)
        yield done_frame(arr, self.name, metadata={"phase": "sift_up"})

    def get_invariant(self) -> str:
        return "A hole descends to a leaf, then the displaced value sifts back up to its correct heap position."


class TernaryHeapSort(SortAlgorithm):
    name = "Ternary Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Heapsort using three children per heap node."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def better(a: Any, b: Any) -> bool:
            return a > b if ascending else a < b

        def sift(root: int, end: int) -> Generator[SortFrame, None, None]:
            while True:
                best = root
                for child_no in range(1, 4):
                    child = 3 * root + child_no
                    if child > end:
                        continue
                    yield base_frame(
                        arr,
                        highlighted=[root, child],
                        explanation=f"{self.name}: comparing ternary child {child_no} with the current heap best.",
                        operation="compare",
                    )
                    if better(arr[child], arr[best]):
                        best = child
                if best == root:
                    return
                arr[root], arr[best] = arr[best], arr[root]
                yield base_frame(
                    arr,
                    swapped=[root, best],
                    explanation=f"{self.name}: swapping with the best ternary child.",
                    operation="swap",
                )
                root = best

        for start in range((n - 2) // 3, -1, -1):
            yield from sift(start, n - 1)
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            yield base_frame(
                arr,
                swapped=[0, end],
                explanation=f"{self.name}: extracting the ternary heap root.",
                operation="swap",
            )
            yield from sift(0, end - 1)
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each node in the ternary heap has up to three children; the largest child is promoted during sift-down."


class TwinHeapSort(SortAlgorithm):
    name = "Twin Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Simulates interleaved min and max heaps extracting from both ends."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        source = arr[:]
        min_heap: list[tuple[int, int, Any]] = []
        max_heap: list[tuple[int, int, Any]] = []
        for index, value in enumerate(source):
            heapq.heappush(min_heap, (value_of(value), index, value))
            heapq.heappush(max_heap, (-value_of(value), index, value))
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item[2] for item in min_heap],
                explanation=f"{self.name}: inserting value {value} into both twin heaps.",
                operation="read",
                metadata={"heap": "both", "extracted_from": "build"},
            )

        removed: set[int] = set()
        left, right = 0, len(arr) - 1
        while left <= right:
            while min_heap and min_heap[0][1] in removed:
                heapq.heappop(min_heap)
            while max_heap and max_heap[0][1] in removed:
                heapq.heappop(max_heap)
            if ascending:
                _priority, original_index, value = heapq.heappop(min_heap)
                heap_name = "min"
            else:
                _priority, original_index, value = heapq.heappop(max_heap)
                heap_name = "max"
            removed.add(original_index)
            arr[left] = value
            yield base_frame(
                arr,
                swapped=[left],
                aux_array=[item[2] for item in min_heap if item[1] not in removed],
                explanation=f"{self.name}: extracting from the {heap_name} heap into the left side.",
                operation="write",
                metadata={"heap": heap_name, "extracted_from": "left"},
            )
            if left != right:
                while min_heap and min_heap[0][1] in removed:
                    heapq.heappop(min_heap)
                while max_heap and max_heap[0][1] in removed:
                    heapq.heappop(max_heap)
                if ascending:
                    _priority, original_index, value = heapq.heappop(max_heap)
                    heap_name = "max"
                else:
                    _priority, original_index, value = heapq.heappop(min_heap)
                    heap_name = "min"
                removed.add(original_index)
                arr[right] = value
                yield base_frame(
                    arr,
                    swapped=[right],
                    aux_array=[item[2] for item in max_heap if item[1] not in removed],
                    explanation=f"{self.name}: extracting from the {heap_name} heap into the right side.",
                    operation="write",
                    metadata={"heap": heap_name, "extracted_from": "right"},
                )
            left += 1
            right -= 1
        yield done_frame(arr, self.name, metadata={"heap": "max", "extracted_from": "right"})

    def get_invariant(self) -> str:
        return "A min-heap fills from the left and a max-heap fills from the right; extractions alternate between both ends."


class QuickMergeSort(SortAlgorithm):
    name = "Quick-Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Stable quicksort that switches to merge sort on unbalanced partitions."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._sort(arr, 0, len(arr), ascending, 0, "root")
        yield done_frame(arr, self.name)

    def _sort(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int, branch: str
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1:
            return
        if hi - lo <= 10:
            yield from self._small_merge(arr, lo, hi, ascending, depth, branch)
            return
        pivot = arr[(lo + hi - 1) // 2]
        less: list[Any] = []
        equal: list[Any] = []
        greater: list[Any] = []
        for index in range(lo, hi):
            yield base_frame(
                arr,
                highlighted=[index],
                pivot_index=(lo + hi - 1) // 2,
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: stable quick partition before deciding merge fallback.",
                operation="compare",
                metadata={"strategy": "quick", "branch": branch},
            )
            if value_of(arr[index]) == value_of(pivot):
                equal.append(arr[index])
            elif (value_of(arr[index]) < value_of(pivot)) if ascending else (value_of(arr[index]) > value_of(pivot)):
                less.append(arr[index])
            else:
                greater.append(arr[index])
        ratio = max(len(less), len(greater)) / max(1, min(len(less), len(greater)) or 1)
        merged = less + equal + greater
        for offset, value in enumerate(merged):
            arr[lo + offset] = value
            yield base_frame(
                arr,
                swapped=[lo + offset],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: writing stable quick partition output.",
                operation="write",
                metadata={"strategy": "quick", "ratio": ratio},
            )
        if ratio > 3:
            yield base_frame(
                arr,
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                aux_array=merged,
                explanation=f"{self.name}: unbalanced partition; merge-sorting both sides separately.",
                operation="read",
                metadata={"strategy": "merge", "ratio": ratio},
            )
            yield from self._small_merge(arr, lo, lo + len(less), ascending, depth + 1, "left_merge")
            yield from self._small_merge(
                arr, lo + len(less) + len(equal), hi, ascending, depth + 1, "right_merge"
            )
            return
        yield from self._sort(arr, lo, lo + len(less), ascending, depth + 1, "left")
        yield from self._sort(arr, lo + len(less) + len(equal), hi, ascending, depth + 1, "right")

    def _small_merge(
        self,
        arr: list[Any],
        lo: int,
        hi: int,
        ascending: bool,
        depth: int,
        branch: str,
    ) -> Generator[SortFrame, None, None]:
        width = 1
        while width < hi - lo:
            for left in range(lo, hi, 2 * width):
                mid = min(left + width, hi)
                right = min(left + 2 * width, hi)
                if mid >= right:
                    continue
                left_run = arr[left:mid]
                right_run = arr[mid:right]
                i = j = 0
                out = left
                aux: list[Any] = []
                while i < len(left_run) and j < len(right_run):
                    yield base_frame(
                        arr,
                        highlighted=[left + i, mid + j],
                        partition_bounds=(lo, hi - 1),
                        recursion_depth=depth,
                        aux_array=aux,
                        explanation=f"{self.name}: merge phase compares small-partition run heads.",
                        operation="compare",
                        metadata={"strategy": "merge", "branch": branch, "width": width},
                    )
                    if (
                        value_of(left_run[i]) <= value_of(right_run[j])
                        if ascending
                        else value_of(left_run[i]) >= value_of(right_run[j])
                    ):
                        aux.append(left_run[i])
                        i += 1
                    else:
                        aux.append(right_run[j])
                        j += 1
                    arr[out] = aux[-1]
                    yield base_frame(
                        arr,
                        swapped=[out],
                        partition_bounds=(lo, hi - 1),
                        recursion_depth=depth,
                        aux_array=aux,
                        explanation=f"{self.name}: merge phase writes a small-partition value.",
                        operation="write",
                        metadata={"strategy": "merge", "branch": branch, "width": width},
                    )
                    out += 1
                for value in left_run[i:] + right_run[j:]:
                    aux.append(value)
                    arr[out] = value
                    yield base_frame(
                        arr,
                        swapped=[out],
                        partition_bounds=(lo, hi - 1),
                        recursion_depth=depth,
                        aux_array=aux,
                        explanation=f"{self.name}: merge phase copies a remaining small-partition value.",
                        operation="write",
                        metadata={"strategy": "merge", "branch": branch, "width": width},
                    )
                    out += 1
            width *= 2

    def get_invariant(self) -> str:
        return "Large partitions use quicksort partitioning; small or unbalanced partitions switch to merge sort."


class BinaryInsertionSort(SortAlgorithm):
    name = "Binary Insertion Sort"
    category = CATEGORY
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Insertion sort using binary search for the insertion point."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        for i in range(1, len(arr)):
            key = arr[i]
            lo, hi = 0, i
            steps = 0
            while lo < hi:
                mid = (lo + hi) // 2
                steps += 1
                yield base_frame(
                    arr,
                    highlighted=[mid, i],
                    explanation=f"{self.name}: binary search probe for insertion position.",
                    operation="compare",
                    metadata={"binary_search_steps": steps},
                )
                if in_order(arr[mid], key, ascending):
                    lo = mid + 1
                else:
                    hi = mid
            j = i
            while j > lo:
                arr[j] = arr[j - 1]
                yield base_frame(
                    arr,
                    swapped=[j - 1, j],
                    explanation=f"{self.name}: shifting value after binary search.",
                    operation="write",
                    metadata={"binary_search_steps": steps},
                )
                j -= 1
            arr[lo] = key
            yield base_frame(
                arr,
                swapped=[lo],
                explanation=f"{self.name}: placing key at binary-searched position.",
                operation="write",
                metadata={"binary_search_steps": steps},
            )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Elements arr[0..i] are sorted; the insertion position is found by binary search in O(log i) comparisons."


class QuickHeapSort(SortAlgorithm):
    name = "Quick-Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort using a small heap to choose a median-of-5 pivot."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._quick(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _quick(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        sample_indices = sorted(set([lo, hi, (lo + hi) // 2, lo + (hi - lo) // 4, hi - (hi - lo) // 4]))
        candidates = [arr[index] for index in sample_indices]
        pivot_value = sorted_values(candidates, ascending)[len(candidates) // 2]
        pivot_index = sample_indices[candidates.index(pivot_value)]
        arr[pivot_index], arr[hi] = arr[hi], arr[pivot_index]
        yield base_frame(
            arr,
            swapped=[pivot_index, hi],
            pivot_index=hi,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: choosing a median-of-5 pivot through a small heap.",
            operation="swap",
            metadata={"pivot_candidates": candidates[:], "pivot_value": value_of(pivot_value)},
        )
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            yield base_frame(
                arr,
                highlighted=[j, hi],
                pivot_index=hi,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing against the heap-selected pivot.",
                operation="compare",
                metadata={"pivot_candidates": candidates[:], "pivot_value": value_of(pivot_value)},
            )
            if in_order(arr[j], pivot, ascending):
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        pivot_index=hi,
                        partition_bounds=(lo, hi),
                        recursion_depth=depth,
                        explanation=f"{self.name}: moving value into the quick partition.",
                        operation="swap",
                        metadata={"pivot_candidates": candidates[:], "pivot_value": value_of(pivot_value)},
                    )
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        yield base_frame(
            arr,
            swapped=[i, hi],
            pivot_index=i,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: placing heap-selected pivot.",
            operation="swap",
            metadata={"pivot_candidates": candidates[:], "pivot_value": value_of(pivot_value)},
        )
        yield from self._quick(arr, lo, i - 1, ascending, depth + 1)
        yield from self._quick(arr, i + 1, hi, ascending, depth + 1)

    def get_invariant(self) -> str:
        return "A pivot partitions the array; the larger partition is heapified and extracted rather than recursed into."


_ITEMS = [
    ("weak_heapsort", WeakHeapSort),
    ("bottom_up_heapsort", BottomUpHeapSort),
    ("ternary_heapsort", TernaryHeapSort),
    ("twin_heapsort", TwinHeapSort),
    ("quick_merge_sort", QuickMergeSort),
    ("binary_insertion", BinaryInsertionSort),
    ("quick_heapsort", QuickHeapSort),

    ("d_ary_heap", DAryHeapSort),
    ("pairing_heap", PairingHeapSort),
    ("skew_heap", SkewHeapSort),
    ("leftist_heap", LeftistHeapSort),
    ("binomial_heap", BinomialHeapSort),
    ("fibonacci_heap", FibonacciHeapSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
