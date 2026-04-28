from __future__ import annotations

import heapq
import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    bottom_up_merge_sort,
    done_frame,
    heap_items,
    heap_sort_range,
    in_order,
    insertion_sort_range,
    merge_runs,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Efficient Sorts"


class MergeSort(SortAlgorithm):
    name = "Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Bottom-up stable merge sort with explicit auxiliary writes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from bottom_up_merge_sort(arr, ascending, self.name)
        yield done_frame(arr, self.name)


class InPlaceMergeSort(SortAlgorithm):
    name = "In-place Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = True
    description = "Recursive merge sort with adjacent-rotation in-place merge."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def merge(left: int, mid: int, right: int, depth: int) -> Generator[SortFrame, None, None]:
            i, j = left, mid
            while i < j and j < right:
                yield base_frame(
                    arr,
                    highlighted=[i, j],
                    partition_bounds=(left, right - 1),
                    recursion_depth=depth,
                    explanation=f"{self.name}: comparing the front of two in-place runs.",
                    operation="compare",
                )
                if in_order(arr[i], arr[j], ascending):
                    i += 1
                    continue
                for k in range(j, i, -1):
                    arr[k], arr[k - 1] = arr[k - 1], arr[k]
                    yield base_frame(
                        arr,
                        swapped=[k - 1, k],
                        partition_bounds=(left, right - 1),
                        recursion_depth=depth,
                        explanation=f"{self.name}: rotating the smaller right-run value left.",
                        operation="swap",
                    )
                i += 1
                j += 1
                mid += 1

        def sort_rec(left: int, right: int, depth: int) -> Generator[SortFrame, None, None]:
            if right - left <= 1:
                return
            mid = (left + right) // 2
            yield from sort_rec(left, mid, depth + 1)
            yield from sort_rec(mid, right, depth + 1)
            yield from merge(left, mid, right, depth)

        yield from sort_rec(0, n, 0)
        yield done_frame(arr, self.name)


class QuickSort(SortAlgorithm):
    name = "Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Lomuto quicksort using the last element as pivot."
    worst_case_input = "sorted"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._quick(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _quick(
        self, arr: List[int], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        pivot = arr[hi]
        i = lo
        yield base_frame(
            arr,
            highlighted=[hi],
            pivot_index=hi,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: reading the last element as pivot.",
            operation="read",
        )
        for j in range(lo, hi):
            yield base_frame(
                arr,
                highlighted=[j, hi],
                pivot_index=hi,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing index {j} with the pivot.",
                operation="compare",
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
                        explanation=f"{self.name}: moving index {j} into the pivot's left partition.",
                        operation="swap",
                    )
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        yield base_frame(
            arr,
            swapped=[i, hi],
            pivot_index=i,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: placing the pivot at index {i}.",
            operation="swap",
        )
        yield from self._quick(arr, lo, i - 1, ascending, depth + 1)
        yield from self._quick(arr, i + 1, hi, ascending, depth + 1)

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size))


class HeapSort(SortAlgorithm):
    name = "Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Binary max-heap for ascending order, min-heap for descending order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from heap_sort_range(arr, 0, len(arr), ascending, self.name)
        yield done_frame(arr, self.name)


class ShellSort(SortAlgorithm):
    name = "Shell Sort"
    category = CATEGORY
    time_complexity = "O(n^(3/2))"
    space_complexity = "O(1)"
    stable = False
    description = "Gapped insertion sort using the Ciura gap sequence."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        gaps = [gap for gap in [701, 301, 132, 57, 23, 10, 4, 1] if gap < len(arr)]
        if len(arr) > 1 and 1 not in gaps:
            gaps.append(1)
        for gap in gaps:
            for i in range(gap, len(arr)):
                key = arr[i]
                yield base_frame(
                    arr,
                    highlighted=[i],
                    explanation=f"{self.name}: reading index {i} for gapped insertion with gap {gap}.",
                    operation="read",
                    metadata={"gap": gap},
                )
                j = i
                while j >= gap:
                    yield base_frame(
                        arr,
                        highlighted=[j - gap, j],
                        explanation=f"{self.name}: comparing values with gap {gap}.",
                        operation="compare",
                        metadata={"gap": gap},
                    )
                    if not out_of_order(arr[j - gap], key, ascending):
                        break
                    arr[j] = arr[j - gap]
                    yield base_frame(
                        arr,
                        swapped=[j - gap, j],
                        explanation=f"{self.name}: shifting by the current gap {gap}.",
                        operation="write",
                        metadata={"gap": gap},
                    )
                    j -= gap
                arr[j] = key
                yield base_frame(
                    arr,
                    swapped=[j],
                    explanation=f"{self.name}: placing the saved value after gap {gap} insertion.",
                    operation="write",
                    metadata={"gap": gap},
                )
        yield done_frame(arr, self.name)

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))


class CombSort(SortAlgorithm):
    name = "Comb Sort"
    category = CATEGORY
    time_complexity = "O(n²/2^p)"
    space_complexity = "O(1)"
    stable = False
    description = "Bubble sort with a shrinking comparison gap."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        gap = len(arr)
        sorted_pass = False
        while not sorted_pass:
            gap = max(1, int(gap / 1.3))
            sorted_pass = gap == 1
            for i in range(0, len(arr) - gap):
                j = i + gap
                yield base_frame(
                    arr,
                    highlighted=[i, j],
                    explanation=f"{self.name}: comparing values at shrinking gap {gap}.",
                    operation="compare",
                    metadata={"gap": gap},
                )
                if out_of_order(arr[i], arr[j], ascending):
                    arr[i], arr[j] = arr[j], arr[i]
                    sorted_pass = False
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        explanation=f"{self.name}: swapping values separated by gap {gap}.",
                        operation="swap",
                        metadata={"gap": gap},
                    )
        yield done_frame(arr, self.name)


class TreeSort(SortAlgorithm):
    name = "Tree Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Binary search tree insertion followed by in-order traversal."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        root: dict[str, Any] | None = None

        def new_node(value: Any) -> dict[str, Any]:
            return {"val": value, "items": [value], "left": None, "right": None}

        for index, value in enumerate(arr):
            yield base_frame(
                arr,
                highlighted=[index],
                explanation=f"{self.name}: reading value {value} before tree insertion.",
                operation="read",
            )
            if root is None:
                root = new_node(value)
                continue
            node = root
            depth = 0
            while True:
                yield base_frame(
                    arr,
                    highlighted=[index],
                    recursion_depth=depth,
                    explanation=f"{self.name}: comparing {value} with tree node {node['val']}.",
                    operation="compare",
                )
                if value_of(value) == value_of(node["val"]):
                    node["items"].append(value)
                    break
                branch = "left" if strictly_tree_before(value, node["val"], ascending=True) else "right"
                if node[branch] is None:
                    node[branch] = new_node(value)
                    break
                node = node[branch]
                depth += 1

        ordered: list[Any] = []

        def traverse(node: dict[str, Any] | None) -> None:
            if node is None:
                return
            first, second = ("left", "right") if ascending else ("right", "left")
            traverse(node[first])
            ordered.extend(node["items"])
            traverse(node[second])

        traverse(root)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                explanation=f"{self.name}: writing the next in-order tree value to index {index}.",
                operation="write",
                aux_array=ordered,
            )
        yield done_frame(arr, self.name)


def strictly_tree_before(left: Any, right: Any, ascending: bool = True) -> bool:
    return value_of(left) < value_of(right) if ascending else value_of(left) > value_of(right)


class TournamentSort(SortAlgorithm):
    name = "Tournament Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Complete tournament tree that repeatedly extracts the winning leaf."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n == 0:
            yield done_frame(arr, self.name)
            return
        size = 1
        while size < n:
            size *= 2
        infinity = float("inf")
        tree: list[tuple[float, int]] = [(infinity, -1)] * (2 * size)
        priorities = [(value_of(v) if ascending else -value_of(v), i) for i, v in enumerate(arr)]
        for i, item in enumerate(priorities):
            tree[size + i] = item
            yield base_frame(
                arr,
                highlighted=[i],
                aux_array=[idx for _priority, idx in tree if idx >= 0],
                explanation=f"{self.name}: placing index {i} into a tournament leaf.",
                operation="read",
            )
        for i in range(size - 1, 0, -1):
            yield base_frame(
                arr,
                highlighted=[idx for _priority, idx in (tree[2 * i], tree[2 * i + 1]) if idx >= 0],
                explanation=f"{self.name}: comparing two children to bubble a winner upward.",
                operation="compare",
            )
            tree[i] = min(tree[2 * i], tree[2 * i + 1])
        original = arr[:]
        for out in range(n):
            _priority, winner = tree[1]
            arr[out] = original[winner]
            yield base_frame(
                arr,
                swapped=[out, winner],
                explanation=f"{self.name}: writing tournament winner from original index {winner}.",
                operation="write",
            )
            pos = size + winner
            tree[pos] = (infinity, -1)
            pos //= 2
            while pos:
                yield base_frame(
                    arr,
                    highlighted=[idx for _priority, idx in (tree[2 * pos], tree[2 * pos + 1]) if idx >= 0],
                    explanation=f"{self.name}: replaying matches after removing the winner.",
                    operation="compare",
                )
                tree[pos] = min(tree[2 * pos], tree[2 * pos + 1])
                pos //= 2
        yield done_frame(arr, self.name)


class BlockSort(SortAlgorithm):
    name = "Block Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "WikiSort-style simplification: insertion-sort blocks, then merge blocks."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        block = max(1, int(math.sqrt(max(1, n))))
        for start in range(0, n, block):
            end = min(n, start + block)
            yield from insertion_sort_range(
                arr,
                start,
                end,
                ascending,
                self.name,
                metadata={"block_size": block, "block": start // block},
                explanation_prefix=f"sorting block {start // block}; ",
            )
        width = block
        while width < n:
            for left in range(0, n, 2 * width):
                mid = min(left + width, n)
                right = min(left + 2 * width, n)
                if mid < right:
                    yield from merge_runs(
                        arr,
                        left,
                        mid,
                        right,
                        ascending,
                        self.name,
                        metadata={"block_size": block},
                    )
            width *= 2
        yield done_frame(arr, self.name)


class SmoothSort(SortAlgorithm):
    name = "Smoothsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Leonardo heap sort visualization."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        # STRETCH: This keeps the Leonardo-number build/extract annotations but
        # uses a binary heap restore internally instead of a full weak Leonardo
        # heap forest.
        leonardo = [1, 1]
        while leonardo[-1] < max(1, len(arr)):
            leonardo.append(leonardo[-1] + leonardo[-2] + 1)
        for i in range(len(arr)):
            yield base_frame(
                arr,
                highlighted=[i],
                explanation=f"{self.name}: adding index {i} to the Leonardo heap forest.",
                operation="read",
                metadata={"leonardo": [x for x in leonardo if x <= i + 1]},
            )
        yield from heap_sort_range(
            arr,
            0,
            len(arr),
            ascending,
            self.name,
            metadata=lambda _op, _idx: {"leonardo": [x for x in leonardo if x <= len(arr)]},
        )
        yield done_frame(arr, self.name)


class PatienceSort(SortAlgorithm):
    name = "Patience Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Deals values into patience piles, then heap-merges pile tops."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        piles: list[list[tuple[Any, int]]] = []
        for index, value in enumerate(arr):
            placed = False
            for pile_index, pile in enumerate(piles):
                top_value = pile[-1][0]
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=[pile[-1][0] for pile in piles],
                    explanation=f"{self.name}: comparing card {value} with pile {pile_index}'s top.",
                    operation="compare",
                    metadata={"pile": pile_index},
                )
                if (top_value > value) if ascending else (top_value < value):
                    pile.append((value, index))
                    placed = True
                    yield base_frame(
                        arr,
                        highlighted=[index],
                        aux_array=[pile[-1][0] for pile in piles],
                        explanation=f"{self.name}: dealing card {value} onto pile {pile_index}.",
                        operation="write",
                        metadata={"pile": pile_index},
                    )
                    break
            if not placed:
                piles.append([(value, index)])
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=[pile[-1][0] for pile in piles],
                    explanation=f"{self.name}: starting a new patience pile for card {value}.",
                    operation="write",
                    metadata={"pile": len(piles) - 1},
                )

        heap: list[tuple[int, int, int, Any]] = []
        for pile_index, pile in enumerate(piles):
            if pile:
                top, original_index = pile.pop()
                priority = value_of(top) if ascending else -value_of(top)
                heapq.heappush(heap, (priority, original_index, pile_index, top))
        out = 0
        while heap:
            _priority, _original_index, pile_index, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                aux_array=[pile[-1][0] for pile in piles if pile],
                explanation=f"{self.name}: writing the next heap-merged pile value.",
                operation="write",
                metadata={"pile": pile_index},
            )
            out += 1
            if piles[pile_index]:
                top, original_index = piles[pile_index].pop()
                priority = value_of(top) if ascending else -value_of(top)
                heapq.heappush(heap, (priority, original_index, pile_index, top))
        yield done_frame(arr, self.name)


class CubeSort(SortAlgorithm):
    name = "Cube Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Adaptive merge sort that detects monotone runs."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        runs: list[tuple[int, int]] = []
        i = 0
        while i < n:
            start = i
            i += 1
            if i == n:
                runs.append((start, i))
                break
            descending = out_of_order(arr[i - 1], arr[i], ascending)
            while i < n and (
                out_of_order(arr[i - 1], arr[i], ascending) if descending else in_order(arr[i - 1], arr[i], ascending)
            ):
                yield base_frame(
                    arr,
                    highlighted=[i - 1, i],
                    explanation=f"{self.name}: scanning a natural run.",
                    operation="compare",
                    metadata={"run_count": len(runs) + 1},
                )
                i += 1
            if descending:
                arr[start:i] = reversed(arr[start:i])
                yield base_frame(
                    arr,
                    swapped=list(range(start, i)),
                    explanation=f"{self.name}: reversing a descending natural run.",
                    operation="write",
                    metadata={"run_count": len(runs) + 1},
                )
            runs.append((start, i))
        while len(runs) > 1:
            new_runs: list[tuple[int, int]] = []
            for idx in range(0, len(runs), 2):
                if idx + 1 == len(runs):
                    new_runs.append(runs[idx])
                    continue
                left, mid = runs[idx][0], runs[idx][1]
                right = runs[idx + 1][1]
                yield from merge_runs(
                    arr,
                    left,
                    mid,
                    right,
                    ascending,
                    self.name,
                    metadata={"run_count": len(runs)},
                )
                new_runs.append((left, right))
            runs = new_runs
        yield done_frame(arr, self.name)


class LibrarySort(SortAlgorithm):
    name = "Library Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Gapped insertion sort using None sentinels as shelf gaps."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        values: list[Any] = []
        shelf: list[Any | None] = [None] * max(2, len(arr) * 2)
        for index, value in enumerate(arr):
            lo, hi = 0, len(values)
            steps = 0
            while lo < hi:
                mid = (lo + hi) // 2
                steps += 1
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=shelf,
                    explanation=f"{self.name}: binary searching the gapped shelf for {value}.",
                    operation="compare",
                    metadata={"binary_search_steps": steps},
                )
                if in_order(values[mid], value, ascending):
                    lo = mid + 1
                else:
                    hi = mid
            values.insert(lo, value)
            if 2 * len(values) >= len(shelf):
                shelf = [None] * (len(shelf) * 2)
            shelf = [None] * max(2, len(values) * 2)
            for pos, existing in enumerate(values):
                shelf[2 * pos] = existing
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=shelf,
                explanation=f"{self.name}: inserting {value} into the shelf and rebalancing gaps.",
                operation="write",
                metadata={"binary_search_steps": steps},
            )
        for index, value in enumerate(values):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=shelf,
                explanation=f"{self.name}: compacting shelf value into array index {index}.",
                operation="write",
            )
        yield done_frame(arr, self.name)


_ITEMS = [
    ("merge", MergeSort),
    ("merge_inplace", InPlaceMergeSort),
    ("quicksort", QuickSort),
    ("heapsort", HeapSort),
    ("shellsort", ShellSort),
    ("comb", CombSort),
    ("tree_sort", TreeSort),
    ("tournament", TournamentSort),
    ("block", BlockSort),
    ("smooth", SmoothSort),
    ("patience", PatienceSort),
    ("cube_sort", CubeSort),
    ("library_sort", LibrarySort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
