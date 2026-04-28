from __future__ import annotations

import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, odd_even_network, out_of_order
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


class BitonicMergeNetworkSort(SortAlgorithm):
    name = "Bitonic Merge Network"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Complete bitonic-style compare-and-swap network for arbitrary sizes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def metadata_for(step: int, index: int, _phase: str) -> dict[str, Any]:
            return {"step": step, "substep": index, "direction": "asc" if ascending else "desc"}

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, n), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata={"step": 0, "substep": 0, "direction": "asc" if ascending else "desc"})


_ITEMS = [
    ("shuffle_exchange", ShuffleExchangeSort),
    ("cube_network", CubeNetworkSort),
    ("bitonic_merge_network", BitonicMergeNetworkSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
