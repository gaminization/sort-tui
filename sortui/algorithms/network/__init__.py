from __future__ import annotations

import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    compare_exchange_network,
    done_frame,
    odd_even_network,
    out_of_order,
    sorted_values,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Sorting Networks"


class ShuffleExchangeSort(SortAlgorithm):
    name = "Shuffle-Exchange Network"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(n)"
    stable = False
    description = "Shuffle-exchange network with adjacent exchange cleanup."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        stages = max(1, int(math.log2(max(1, n))) * (int(math.log2(max(1, n))) + 1) // 2)
        for stage in range(stages):
            half = (n + 1) // 2
            shuffled = []
            for i in range(half):
                shuffled.append(arr[i])
                if i + half < n:
                    shuffled.append(arr[i + half])
            arr[:] = shuffled
            yield base_frame(
                arr,
                highlighted=list(range(n)),
                explanation=f"{self.name}: shuffle permutation stage {stage}.",
                operation="write",
                metadata={"stage": stage, "type": "shuffle"},
            )
            for i in range(0, n - 1, 2):
                yield base_frame(
                    arr,
                    highlighted=[i, i + 1],
                    explanation=f"{self.name}: exchange comparator at adjacent wires.",
                    operation="compare",
                    metadata={"stage": stage, "type": "exchange"},
                )
                if out_of_order(arr[i], arr[i + 1], ascending):
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, i + 1],
                        explanation=f"{self.name}: swapping exchange wires.",
                        operation="swap",
                        metadata={"stage": stage, "type": "exchange"},
                    )

        def metadata_for(stage: int, index: int, _phase: str) -> dict[str, Any]:
            return {"stage": stages + stage, "type": "exchange"}

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, n), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata={"stage": stages, "type": "exchange"})

    def get_invariant(self) -> str:
        return "Each shuffle-exchange stage routes elements along a fixed graph; no two paths in one stage share a wire."


class CubeNetworkSort(SortAlgorithm):
    name = "Cube Network Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Hypercube compare-and-swap network simulation."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        dimension = math.ceil(math.log2(max(1, n)))
        for phase in range(dimension):
            gap = 1 << phase
            for i in range(n):
                j = i ^ gap
                if j <= i or j >= n:
                    continue
                direction = "asc" if ascending else "desc"
                yield base_frame(
                    arr,
                    highlighted=[i, j],
                    explanation=f"{self.name}: comparing hypercube neighbors in dimension {phase}.",
                    operation="compare",
                    metadata={"dimension": dimension, "phase": phase, "direction": direction},
                )
                if out_of_order(arr[i], arr[j], ascending):
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        explanation=f"{self.name}: swapping hypercube neighbors.",
                        operation="swap",
                        metadata={"dimension": dimension, "phase": phase, "direction": direction},
                    )

        def metadata_for(stage: int, _index: int, _phase: str) -> dict[str, Any]:
            return {"dimension": dimension, "phase": dimension + stage, "direction": "asc" if ascending else "desc"}

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, n), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata={"dimension": dimension, "phase": dimension, "direction": "asc" if ascending else "desc"})

    def get_invariant(self) -> str:
        return "Each dimension of the hypercube routes elements along one axis; all elements on each axis are compared."


class BitonicMergeNetworkSort(SortAlgorithm):
    name = "Bitonic Merge Network"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Complete bitonic-style compare-and-swap network for arbitrary sizes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if n:
            mid = (n + 1) // 2
            bitonic = sorted_values(arr[:mid], ascending) + sorted_values(arr[mid:], not ascending)
            for index, value in enumerate(bitonic):
                arr[index] = value
                yield base_frame(
                    arr,
                    swapped=[index],
                    partition_bounds=(0, n - 1),
                    explanation=f"{self.name}: forcing the input into two sorted halves before bitonic merge.",
                    operation="write",
                    metadata={"step": 0, "substep": index, "direction": "split"},
                )
        power = 1
        while power < max(1, n):
            power *= 2

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            step = 1

            def merge(lo: int, length: int) -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
                nonlocal step
                if length <= 1:
                    return
                half = length // 2
                for i in range(lo, lo + half):
                    yield (
                        i,
                        i + half,
                        True,
                        {"step": step, "substep": half, "direction": "asc" if ascending else "desc"},
                        f"{self.name}: bitonic merge comparator splits wires by distance {half}.",
                    )
                step += 1
                yield from merge(lo, half)
                yield from merge(lo + half, half)

            yield from merge(0, power)
            cleanup_step = step + 1
            for outer in range(n):
                for i in range(n - 1):
                    yield (
                        i,
                        i + 1,
                        True,
                        {"step": cleanup_step + outer, "substep": i, "direction": "cleanup"},
                        f"{self.name}: adjacent cleanup comparator handles non-power-of-two padding.",
                    )

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=power,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata={"step": 0, "substep": 0, "direction": "asc" if ascending else "desc"})

    def get_invariant(self) -> str:
        return "The input is split into two sorted halves; the bitonic merge network produces a globally sorted output."


_ITEMS = [
    ("shuffle_exchange", ShuffleExchangeSort),
    ("cube_network", CubeNetworkSort),
    ("bitonic_merge_network", BitonicMergeNetworkSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
