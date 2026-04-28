from __future__ import annotations

import math
from collections import defaultdict, deque
from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, odd_even_network, out_of_order, sorted_values, value_of
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


class TopologicalSort(SortAlgorithm):
    name = "Topological Sort"
    category = CATEGORY
    time_complexity = "O(V + E)"
    space_complexity = "O(V + E)"
    stable = True
    description = "Simulates dependency extraction to produce ascending order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        graph: dict[int, set[int]] = defaultdict(set)
        in_degree: dict[int, int] = {value_of(v): 0 for v in arr}
        for i in range(len(arr) - 1):
            a, b = value_of(arr[i]), value_of(arr[i + 1])
            yield base_frame(
                arr,
                highlighted=[i, i + 1],
                explanation=f"{self.name}: building a dependency between adjacent labels when ordered.",
                operation="compare",
                metadata={"in_degree": dict(in_degree), "phase": "build"},
            )
            if a < b:
                graph[a].add(b)
                in_degree[b] = in_degree.get(b, 0) + 1
        queue = deque(sorted([node for node, degree in in_degree.items() if degree == 0]))
        while queue:
            node = queue.popleft()
            yield base_frame(
                arr,
                highlighted=[],
                explanation=f"{self.name}: extracting zero in-degree label {node}.",
                operation="read",
                metadata={"in_degree": dict(in_degree), "phase": "extract"},
            )
            for nxt in graph[node]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: writing the simulated topological order.",
                operation="write",
                metadata={"in_degree": dict(in_degree), "phase": "extract"},
            )
        yield done_frame(arr, self.name, metadata={"in_degree": dict(in_degree), "phase": "extract"})


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
        universe = max_val - min_val + 1
        cluster_size = max(1, int(math.sqrt(universe)))
        clusters: dict[int, list[Any]] = defaultdict(list)
        for index, value in enumerate(arr):
            cluster = (value_of(value) - min_val) // cluster_size
            clusters[cluster].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for values in clusters.values() for item in values],
                explanation=f"{self.name}: inserting value {value} into universe cluster {cluster}.",
                operation="write",
                metadata={"universe": universe, "cluster": cluster, "phase": "insert"},
            )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            cluster = (value_of(value) - min_val) // cluster_size
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: extracting value from cluster {cluster}.",
                operation="read",
                metadata={"universe": universe, "cluster": cluster, "phase": "extract"},
            )
        yield done_frame(arr, self.name, metadata={"universe": universe, "cluster": 0, "phase": "extract"})


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


class MergeExchangeSort(SortAlgorithm):
    name = "Merge-Exchange Sort"
    category = CATEGORY
    time_complexity = "O(n log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Batcher-style merge-exchange sorting network."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        def metadata_for(pass_no: int, index: int, _phase: str) -> dict[str, int]:
            return {"pass": pass_no, "offset": index}

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, len(arr)), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata={"pass": len(arr), "offset": 0})


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
