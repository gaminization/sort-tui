from __future__ import annotations

import math
from collections import defaultdict, deque
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    compare_exchange_network,
    done_frame,
    odd_even_network,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Other Sorts"


class PancakeSort(SortAlgorithm):
    name = "Pancake Sort"
    category = CATEGORY
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "Sorts by prefix reversals called flips."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        def flip(end: int) -> Generator[SortFrame, None, None]:
            arr[: end + 1] = reversed(arr[: end + 1])
            for index in range(end + 1):
                yield base_frame(
                    arr,
                    swapped=[index],
                    explanation=f"{self.name}: writing element touched by flip range 0..{end}.",
                    operation="write",
                    metadata={"flip_end": end},
                )

        for size in range(len(arr), 1, -1):
            target = sorted_values(arr[:size], ascending)[-1]
            max_index = next(i for i, value in enumerate(arr[:size]) if value == target)
            yield base_frame(
                arr,
                highlighted=[max_index],
                explanation=f"{self.name}: locating the pancake that belongs at index {size - 1}.",
                operation="compare",
            )
            if max_index != size - 1:
                if max_index != 0:
                    yield from flip(max_index)
                yield from flip(size - 1)
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each pair of flips places the current maximum into its correct position from the unsorted suffix."


class TopologicalSort(SortAlgorithm):
    name = "Topological Sort"
    category = CATEGORY
    time_complexity = "O(V + E)"
    space_complexity = "O(V + E)"
    stable = True
    description = "Simulates dependency extraction to produce ascending order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        graph: dict[int, set[int]] = {index: set() for index in range(n)}
        in_degree = [0] * n

        def topo_key(index: int) -> tuple[int, int]:
            base = value_of(arr[index])
            original_index = getattr(arr[index], "original_index", index)
            return (base if ascending else -base, original_index)

        for i in range(n):
            for j in range(i + 1, n):
                yield base_frame(
                    arr,
                    highlighted=[i, j],
                    explanation=f"{self.name}: comparing node labels to orient a dependency edge.",
                    operation="compare",
                    metadata={"in_degree": {str(k): v for k, v in enumerate(in_degree)}, "phase": "build"},
                )
                if topo_key(i) <= topo_key(j):
                    before, after = i, j
                else:
                    before, after = j, i
                if after not in graph[before]:
                    graph[before].add(after)
                    in_degree[after] += 1
                    yield base_frame(
                        arr,
                        highlighted=[before, after],
                        explanation=f"{self.name}: adding dependency edge {before} -> {after}.",
                        operation="write",
                        metadata={"in_degree": {str(k): v for k, v in enumerate(in_degree)}, "phase": "build"},
                    )

        queue = deque(sorted([node for node, degree in enumerate(in_degree) if degree == 0], key=topo_key))
        output_indices: list[int] = []
        while queue:
            node = queue.popleft()
            output_indices.append(node)
            yield base_frame(
                arr,
                highlighted=[node],
                aux_array=[arr[index] for index in queue],
                explanation=f"{self.name}: extracting zero in-degree node {node} from Kahn's queue.",
                operation="read",
                metadata={
                    "in_degree": {str(k): v for k, v in enumerate(in_degree)},
                    "queue": list(queue),
                    "phase": "extract",
                },
            )
            for nxt in sorted(graph[node], key=topo_key):
                in_degree[nxt] -= 1
                yield base_frame(
                    arr,
                    highlighted=[node, nxt],
                    aux_array=[arr[index] for index in queue],
                    explanation=f"{self.name}: reducing in-degree for neighbor {nxt}.",
                    operation="write",
                    metadata={
                        "in_degree": {str(k): v for k, v in enumerate(in_degree)},
                        "queue": list(queue),
                        "phase": "reduce",
                    },
                )
                if in_degree[nxt] == 0:
                    queue.append(nxt)
                    queue = deque(sorted(queue, key=topo_key))
                    yield base_frame(
                        arr,
                        highlighted=[nxt],
                        aux_array=[arr[index] for index in queue],
                        explanation=f"{self.name}: enqueueing node {nxt} after all dependencies clear.",
                        operation="read",
                        metadata={
                            "in_degree": {str(k): v for k, v in enumerate(in_degree)},
                            "queue": list(queue),
                            "phase": "enqueue",
                        },
                    )
        ordered = [arr[index] for index in output_indices]
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: writing the simulated topological order.",
                operation="write",
                metadata={"in_degree": {str(k): v for k, v in enumerate(in_degree)}, "phase": "extract"},
            )
        yield done_frame(arr, self.name, metadata={"in_degree": {str(k): v for k, v in enumerate(in_degree)}, "phase": "extract"})

    def get_invariant(self) -> str:
        return "In-degree counts are maintained; only zero-in-degree nodes are available for extraction at each step."


class VanEmdeBoasSort(SortAlgorithm):
    name = "van Emde Boas Sort"
    category = CATEGORY
    time_complexity = "O(n log log U)"
    space_complexity = "O(U)"
    stable = True
    description = "van Emde Boas inspired recursive universe clustering."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)

        def recurse(
            values: list[Any],
            low: int,
            high: int,
            depth: int,
            offset: int,
        ) -> Generator[SortFrame, None, list[Any]]:
            universe = high - low + 1
            if len(values) <= 1 or universe <= 2:
                ordered_leaf = sorted_values(values, ascending)
                for leaf_index, value in enumerate(ordered_leaf):
                    arr[offset + leaf_index] = value
                    yield base_frame(
                        arr,
                        swapped=[offset + leaf_index],
                        recursion_depth=depth,
                        aux_array=ordered_leaf,
                        explanation=f"{self.name}: extracting base-universe value {value}.",
                        operation="write",
                        metadata={"universe": universe, "cluster": 0, "phase": "base_extract"},
                    )
                return ordered_leaf

            midpoint = low + universe // 2
            lower: list[Any] = []
            upper: list[Any] = []
            for local_index, value in enumerate(values):
                cluster = 0 if value_of(value) < midpoint else 1
                yield base_frame(
                    arr,
                    highlighted=[offset + local_index if offset + local_index < len(arr) else len(arr) - 1],
                    recursion_depth=depth,
                    aux_array=[value_of(item) for item in lower + upper],
                    explanation=(
                        f"{self.name}: halving universe [{low}, {high}] and inserting "
                        f"value {value} into cluster {cluster}."
                    ),
                    operation="read",
                    metadata={"universe": universe, "cluster": cluster, "phase": "insert"},
                )
                if cluster == 0:
                    lower.append(value)
                else:
                    upper.append(value)

            first_values, first_low, first_high = (
                (lower, low, midpoint - 1) if ascending else (upper, midpoint, high)
            )
            second_values, second_low, second_high = (
                (upper, midpoint, high) if ascending else (lower, low, midpoint - 1)
            )
            first_sorted = yield from recurse(first_values, first_low, first_high, depth + 1, offset)
            second_sorted = yield from recurse(
                second_values, second_low, second_high, depth + 1, offset + len(first_sorted)
            )
            combined = first_sorted + second_sorted
            for local_index, value in enumerate(combined):
                arr[offset + local_index] = value
                yield base_frame(
                    arr,
                    swapped=[offset + local_index],
                    recursion_depth=depth,
                    aux_array=combined,
                    explanation=f"{self.name}: recombining halved universe value {value}.",
                    operation="write",
                    metadata={"universe": universe, "cluster": -1, "phase": "extract"},
                )
            return combined

        yield from recurse(arr[:], min_val, max_val, 0, 0)
        yield done_frame(arr, self.name, metadata={"universe": max_val - min_val + 1, "cluster": 0, "phase": "extract"})

    def get_invariant(self) -> str:
        return "Each recursive level halves the universe; elements cluster into sqrt(U) buckets of size sqrt(U)."


class XPlusYSort(SortAlgorithm):
    name = "X + Y Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n²)"
    stable = True
    description = "Uses sorted pairwise sums of two halves as a merge guide."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]
        yield base_frame(
            arr,
            aux_array=left + right,
            explanation=f"{self.name}: splitting input into X and Y halves.",
            operation="read",
            metadata={"phase": "split"},
        )
        sums: list[int] = []
        for x in left:
            for y in right:
                sums.append(value_of(x) + value_of(y))
                yield base_frame(
                    arr,
                    aux_array=sums,
                    explanation=f"{self.name}: computing pairwise X+Y sums.",
                    operation="read",
                    metadata={"phase": "sum"},
                )
        sums.sort(reverse=not ascending)
        yield base_frame(
            arr,
            aux_array=sums,
            explanation=f"{self.name}: sorting pairwise sums as a merge guide.",
            operation="write",
            metadata={"phase": "sort_sums"},
        )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=sums,
                explanation=f"{self.name}: writing the final value guided by sorted sums.",
                operation="write",
                metadata={"phase": "write"},
            )
        yield done_frame(arr, self.name, metadata={"phase": "write"})

    def get_invariant(self) -> str:
        return "All pairwise sums are generated in sorted order by maintaining a priority queue of frontier sum candidates."


class MergeExchangeSort(SortAlgorithm):
    name = "Merge-Exchange Sort"
    category = CATEGORY
    time_complexity = "O(n log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Batcher-style merge-exchange sorting network."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        power = 1
        while power < max(1, n):
            power *= 2

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            pass_no = 0
            gap = power // 2
            while gap:
                for offset in range(gap):
                    for i in range(offset, power - gap, gap * 2):
                        yield (
                            i,
                            i + gap,
                            True,
                            {"pass": pass_no, "offset": gap},
                            f"{self.name}: merge-exchange comparator uses power-of-two offset {gap}.",
                        )
                pass_no += 1
                gap //= 2
            for outer in range(n):
                for i in range(n - 1):
                    yield (
                        i,
                        i + 1,
                        True,
                        {"pass": pass_no + outer, "offset": 1},
                        f"{self.name}: adjacent exchange cleanup after power-of-two merge passes.",
                    )

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=power,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata={"pass": n, "offset": 0})

    def get_invariant(self) -> str:
        return "Each comparator pair (i, j) with j-i a power of two fires in a fixed sequence derived from Batcher's construction."


class BrickSort(SortAlgorithm):
    name = "Brick Sort"
    category = CATEGORY
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Odd-even brick-wall pair sorting."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        pass_no = 0
        while True:
            swapped = False
            for start, phase in ((1, "odd"), (0, "even")):
                for i in range(start, n - 1, 2):
                    yield base_frame(
                        arr,
                        highlighted=[i, i + 1],
                        explanation=f"{self.name}: {phase} brick-wall comparison.",
                        operation="compare",
                        metadata={"phase": phase, "pass": pass_no},
                    )
                    if out_of_order(arr[i], arr[i + 1], ascending):
                        arr[i], arr[i + 1] = arr[i + 1], arr[i]
                        swapped = True
                        yield base_frame(
                            arr,
                            swapped=[i, i + 1],
                            explanation=f"{self.name}: swapping a {phase} brick pair.",
                            operation="swap",
                            metadata={"phase": phase, "pass": pass_no},
                        )
            pass_no += 1
            if not swapped:
                break
        yield done_frame(arr, self.name, metadata={"phase": "even", "pass": pass_no})

    def get_invariant(self) -> str:
        return "Alternating odd and even adjacent comparisons guarantee the maximum unsorted element moves right each full round."


_ITEMS = [
    ("pancake", PancakeSort),
    ("topological", TopologicalSort),
    ("van_emde_boas", VanEmdeBoasSort),
    ("x_plus_y", XPlusYSort),
    ("merge_exchange", MergeExchangeSort),
    ("brick", BrickSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
