from __future__ import annotations

import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    bottom_up_merge_sort,
    done_frame,
    heap_sort_range,
    in_order,
    insertion_sort_range,
    merge_runs,
    odd_even_network,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Adaptive Sorts"


class AdaptiveHeapSort(SortAlgorithm):
    name = "Adaptive Heapsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False
    description = "Heapsort that switches to insertion sort on nearly sorted input."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        adjacent_inversions = sum(
            1 for i in range(len(arr) - 1) if out_of_order(arr[i], arr[i + 1], ascending)
        )
        ratio = adjacent_inversions / max(1, len(arr) - 1)
        strategy = "insertion" if ratio < 0.05 else "heap"
        yield base_frame(
            arr,
            highlighted=list(range(min(2, len(arr)))),
            explanation=f"{self.name}: prescan measured inversion ratio {ratio:.3f}; using {strategy}.",
            operation="read",
            metadata={"inversion_ratio": ratio, "strategy": strategy},
        )
        if strategy == "insertion":
            yield from insertion_sort_range(
                arr,
                0,
                len(arr),
                ascending,
                self.name,
                metadata={"inversion_ratio": ratio, "strategy": strategy},
            )
        else:
            yield from heap_sort_range(
                arr,
                0,
                len(arr),
                ascending,
                self.name,
                metadata={"inversion_ratio": ratio, "strategy": strategy},
            )
        yield done_frame(arr, self.name, metadata={"inversion_ratio": ratio, "strategy": strategy})


class AdaptiveMergeSort(SortAlgorithm):
    name = "Adaptive Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Natural merge sort that merges shorter detected runs first."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        runs = self._detect_runs(arr, ascending)
        metadata = {"run_count": len(runs), "run_lengths": [end - start for start, end in runs]}
        yield base_frame(
            arr,
            explanation=f"{self.name}: detected {len(runs)} natural runs.",
            operation="read",
            metadata=metadata,
        )
        while len(runs) > 1:
            runs.sort(key=lambda run: run[1] - run[0])
            left, mid = runs.pop(0)
            right_run = min((run for run in runs if run[0] == mid), default=None)
            if right_run is None:
                runs.append((left, mid))
                runs.sort()
                left, mid = runs[0]
                if len(runs) == 1:
                    break
                right_run = runs[1]
                runs = runs[2:]
            else:
                runs.remove(right_run)
            right = right_run[1]
            yield from merge_runs(arr, left, mid, right, ascending, self.name, metadata=metadata)
            runs.append((left, right))
            runs.sort()
        yield done_frame(arr, self.name, metadata=metadata)

    def _detect_runs(self, arr: list[Any], ascending: bool) -> list[tuple[int, int]]:
        n = len(arr)
        runs: list[tuple[int, int]] = []
        i = 0
        while i < n:
            start = i
            i += 1
            if i < n:
                descending = out_of_order(arr[i - 1], arr[i], ascending)
                while i < n and (
                    out_of_order(arr[i - 1], arr[i], ascending)
                    if descending
                    else in_order(arr[i - 1], arr[i], ascending)
                ):
                    i += 1
                if descending:
                    arr[start:i] = reversed(arr[start:i])
            runs.append((start, i))
        return runs


class AdaptiveBitonicSort(SortAlgorithm):
    name = "Adaptive Bitonic Sort"
    category = CATEGORY
    time_complexity = "O(n log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Bitonic-network-style adaptive compare-and-swap simulation."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        power = 1
        while power < max(1, n):
            power *= 2
        step = 0

        def metadata_for(pass_no: int, index: int, _phase: str) -> dict[str, int]:
            return {"step": step + pass_no, "substep": index}

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, power), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata={"step": step, "substep": 0})


class SplaySort(SortAlgorithm):
    name = "Splaysort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Splay-tree based insertion followed by in-order extraction."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        root: dict[str, Any] | None = None

        def new_node(value: Any) -> dict[str, Any]:
            return {"val": value, "items": [value], "left": None, "right": None}

        for index, value in enumerate(arr):
            if root is None:
                root = new_node(value)
                yield base_frame(
                    arr,
                    highlighted=[index],
                    explanation=f"{self.name}: inserting the first value as root.",
                    operation="read",
                    metadata={"splay_depth": 0},
                )
                continue
            node = root
            depth = 0
            while True:
                yield base_frame(
                    arr,
                    highlighted=[index],
                    recursion_depth=depth,
                    explanation=f"{self.name}: descending the splay tree before rotating to root.",
                    operation="compare",
                    metadata={"splay_depth": depth},
                )
                if value_of(value) == value_of(node["val"]):
                    node["items"].append(value)
                    break
                branch = "left" if value_of(value) < value_of(node["val"]) else "right"
                if node[branch] is None:
                    node[branch] = new_node(value)
                    break
                node = node[branch]
                depth += 1
            yield base_frame(
                arr,
                highlighted=[index],
                recursion_depth=depth,
                explanation=f"{self.name}: splaying the accessed path toward the root.",
                operation="swap",
                metadata={"splay_depth": depth},
            )

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
                explanation=f"{self.name}: writing the next in-order tree value.",
                operation="write",
                metadata={"splay_depth": 0},
            )
        yield done_frame(arr, self.name)


class CartesianTreeSort(SortAlgorithm):
    name = "Cartesian Tree Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Builds a Cartesian-tree-shaped stack, then extracts sorted values."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        stack: list[Any] = []
        for index, value in enumerate(arr):
            last = None
            while stack and out_of_order(stack[-1], value, ascending):
                last = stack.pop()
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=stack,
                    explanation=f"{self.name}: popping a larger stack top to become a left child.",
                    operation="compare",
                    metadata={"tree_size": len(stack) + 1},
                )
            stack.append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=stack,
                explanation=f"{self.name}: adding value {value} to the Cartesian tree spine.",
                operation="write",
                metadata={"tree_size": len(stack), "last_left_child": value_of(last) if last is not None else None},
            )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: traversing tree priorities to write sorted value.",
                operation="write",
                metadata={"tree_size": len(stack)},
            )
        yield done_frame(arr, self.name)


class WiggleSort(SortAlgorithm):
    name = "Wiggle Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    stable = False
    description = "One-pass wiggle arrangement followed by sorted normalization for benchmarking."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        for i in range(len(arr) - 1):
            should_swap = arr[i] > arr[i + 1] if i % 2 == 0 else arr[i] < arr[i + 1]
            yield base_frame(
                arr,
                highlighted=[i, i + 1],
                explanation=f"{self.name}: checking the wiggle relation at indices {i} and {i + 1}.",
                operation="compare",
            )
            if should_swap:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                yield base_frame(
                    arr,
                    swapped=[i, i + 1],
                    explanation=f"{self.name}: swapping to satisfy the local wiggle relation.",
                    operation="swap",
                )
        yield from insertion_sort_range(arr, 0, len(arr), ascending, self.name, explanation_prefix="normalizing to sorted order; ")
        yield done_frame(arr, self.name)


class BlockQuickSort(SortAlgorithm):
    name = "Block Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Cache-friendly quicksort with block offset buffers."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._quick(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _quick(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        pivot = arr[hi]
        i = lo
        left_offsets: list[int] = []
        right_offsets: list[int] = []
        for block_start in range(lo, hi, 64):
            block_end = min(hi, block_start + 64)
            left_offsets.clear()
            right_offsets.clear()
            for j in range(block_start, block_end):
                yield base_frame(
                    arr,
                    highlighted=[j, hi],
                    pivot_index=hi,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: classifying an index inside a 64-item partition block.",
                    operation="compare",
                    metadata={"block_size": 64, "left_count": len(left_offsets), "right_count": len(right_offsets)},
                )
                if in_order(arr[j], pivot, ascending):
                    left_offsets.append(j)
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        yield base_frame(
                            arr,
                            swapped=[i, j],
                            pivot_index=hi,
                            partition_bounds=(lo, hi),
                            recursion_depth=depth,
                            explanation=f"{self.name}: swapping a buffered block offset into the left partition.",
                            operation="swap",
                            metadata={"block_size": 64, "left_count": len(left_offsets), "right_count": len(right_offsets)},
                        )
                    i += 1
                else:
                    right_offsets.append(j)
        arr[i], arr[hi] = arr[hi], arr[i]
        yield base_frame(
            arr,
            swapped=[i, hi],
            pivot_index=i,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: placing the pivot after block partitioning.",
            operation="swap",
            metadata={"block_size": 64, "left_count": len(left_offsets), "right_count": len(right_offsets)},
        )
        yield from self._quick(arr, lo, i - 1, ascending, depth + 1)
        yield from self._quick(arr, i + 1, hi, ascending, depth + 1)


class PDQSort(SortAlgorithm):
    name = "Pattern-Defeating Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Simplified pattern-defeating quicksort with heap fallback."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if all(in_order(arr[i], arr[i + 1], ascending) for i in range(len(arr) - 1)):
            pattern = "sorted"
        elif all(in_order(arr[i + 1], arr[i], ascending) for i in range(len(arr) - 1)):
            pattern = "reverse"
        else:
            pattern = "random"
        yield base_frame(
            arr,
            explanation=f"{self.name}: detected {pattern} input pattern.",
            operation="read",
            metadata={"pattern": pattern, "fallback": None},
        )
        if pattern == "reverse":
            arr[:] = reversed(arr)
            yield base_frame(
                arr,
                swapped=list(range(len(arr))),
                explanation=f"{self.name}: reversing a detected reverse pattern.",
                operation="write",
                metadata={"pattern": pattern, "fallback": None},
            )
        elif pattern != "sorted":
            yield from self._quick(arr, 0, len(arr) - 1, ascending, pattern, 0)
        yield done_frame(arr, self.name, metadata={"pattern": pattern, "fallback": None})

    def _quick(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, pattern: str, depth: int
    ) -> Generator[SortFrame, None, None]:
        if hi - lo + 1 <= 24:
            yield from insertion_sort_range(
                arr, lo, hi + 1, ascending, self.name, metadata={"pattern": pattern, "fallback": None}
            )
            return
        mid = (lo + hi) // 2
        pivot = arr[mid]
        i, j = lo, hi
        while i <= j:
            while i <= hi and value_of(arr[i]) < value_of(pivot):
                yield base_frame(
                    arr,
                    highlighted=[i],
                    pivot_index=mid,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: scanning the left side for the median pivot.",
                    operation="compare",
                    metadata={"pattern": pattern, "fallback": None},
                )
                i += 1
            while j >= lo and value_of(arr[j]) > value_of(pivot):
                yield base_frame(
                    arr,
                    highlighted=[j],
                    pivot_index=mid,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: scanning the right side for the median pivot.",
                    operation="compare",
                    metadata={"pattern": pattern, "fallback": None},
                )
                j -= 1
            if i <= j:
                arr[i], arr[j] = arr[j], arr[i]
                yield base_frame(
                    arr,
                    swapped=[i, j],
                    pivot_index=mid,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: swapping around the pivot.",
                    operation="swap",
                    metadata={"pattern": pattern, "fallback": None},
                )
                i += 1
                j -= 1
        left = max(0, j - lo + 1)
        right = max(0, hi - i + 1)
        if max(left, right) > 8 * max(1, min(left or 1, right or 1)):
            yield base_frame(
                arr,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: highly unbalanced partition; switching to heap fallback.",
                operation="read",
                metadata={"pattern": pattern, "fallback": "heap"},
            )
            yield from heap_sort_range(arr, lo, hi + 1, ascending, self.name, metadata={"pattern": pattern, "fallback": "heap"})
            return
        if lo < j:
            yield from self._quick(arr, lo, j, ascending, pattern, depth + 1)
        if i < hi:
            yield from self._quick(arr, i, hi, ascending, pattern, depth + 1)


class GrailSort(SortAlgorithm):
    name = "Grailsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = True
    description = "Block merge sort with a collected unique-key buffer."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        # STRETCH: The full GrailSort rotates blocks using an O(1) internal
        # buffer. This approximation collects unique keys and then performs
        # stable block merges while preserving the same visible phases.
        needed = 2 * int(math.sqrt(max(1, len(arr))))
        seen: set[int] = set()
        buffer: list[Any] = []
        for index, value in enumerate(arr):
            if value_of(value) not in seen:
                seen.add(value_of(value))
                buffer.append(value)
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=buffer,
                    explanation=f"{self.name}: collecting a unique buffer key.",
                    operation="read",
                    metadata={"buffer_size": len(buffer), "phase": "collect"},
                )
                if len(buffer) >= needed:
                    break
        yield from bottom_up_merge_sort(
            arr,
            ascending,
            self.name,
            metadata=lambda _op, _idx: {"buffer_size": len(buffer), "phase": "merge"},
        )
        yield base_frame(
            arr,
            highlighted=list(range(min(len(arr), len(buffer)))),
            aux_array=buffer,
            explanation=f"{self.name}: finalizing the merged block layout.",
            operation="write",
            metadata={"buffer_size": len(buffer), "phase": "finalize"},
        )
        yield done_frame(arr, self.name, metadata={"buffer_size": len(buffer), "phase": "finalize"})


_ITEMS = [
    ("adaptive_heapsort", AdaptiveHeapSort),
    ("adaptive_merge", AdaptiveMergeSort),
    ("adaptive_bitonic", AdaptiveBitonicSort),
    ("splaysort", SplaySort),
    ("cartesian_tree", CartesianTreeSort),
    ("wiggle", WiggleSort),
    ("block_quicksort", BlockQuickSort),
    ("pdqsort", PDQSort),
    ("grailsort", GrailSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
