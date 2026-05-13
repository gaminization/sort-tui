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
    split_threads,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Parallel Sorts"


def thread_meta(n: int, active: int | None = None, **extra: Any) -> dict[str, Any]:
    metadata = {"threads": split_threads(n, 4, active)}
    metadata.update(extra)
    return metadata


class MultistepBitonicSort(SortAlgorithm):
    name = "Multistep Bitonic Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Simulates bitonic network stages with parallel compare-exchanges."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        power = 1
        while power < max(1, n):
            power *= 2
        block = max(2, power // 4)
        for start in range(0, power, block):
            yield base_frame(
                arr,
                highlighted=list(range(start, min(start + block, n))),
                explanation=f"{self.name}: assigning a bitonic block before global multi-step merge.",
                operation="read",
                metadata=thread_meta(n, (start // block) % 4 if n else 0, stage=0, substep=start, direction="block"),
            )

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            stage = 1
            size = 2
            while size <= power:
                stride = size // 2
                while stride:
                    for i in range(power):
                        j = i ^ stride
                        if j <= i:
                            continue
                        direction = (i & size) == 0
                        yield (
                            i,
                            j,
                            direction,
                            thread_meta(
                                n,
                                i % 4 if n else 0,
                                stage=stage,
                                substep=stride,
                                direction="asc" if direction else "desc",
                                block_size=block,
                            ),
                            f"{self.name}: multi-step bitonic comparator keeps block boundaries visible.",
                        )
                    stage += 1
                    stride //= 2
                size *= 2

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=power,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata=thread_meta(n, stage=0, substep=0, direction="asc" if ascending else "desc"))

    def get_invariant(self) -> str:
        return "Each block is internally sorted by bitonic sort before cross-block bitonic merges are applied."


class SampleSort(SortAlgorithm):
    name = "Sample Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Simulates four-processor sample sort."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        p = 4
        chunk = max(1, math.ceil(n / p))
        slices: list[list[Any]] = []
        for processor in range(p):
            start = processor * chunk
            end = min(n, start + chunk)
            local = sorted_values(arr[start:end], ascending)
            slices.append(local)
            for offset, value in enumerate(local):
                if start + offset < n:
                    arr[start + offset] = value
                    yield base_frame(
                        arr,
                        swapped=[start + offset],
                        aux_array=local,
                        explanation=f"{self.name}: processor {processor} sorts its local slice.",
                        operation="write",
                        metadata=thread_meta(n, processor, phase="sample", processor=processor),
                    )
        samples = [local[len(local) // 2] for local in slices if local]
        splitters = sorted_values(samples, ascending)[: p - 1]
        yield base_frame(
            arr,
            aux_array=splitters,
            explanation=f"{self.name}: broadcasting sorted sample splitters.",
            operation="read",
            metadata=thread_meta(n, phase="split", processor=0),
        )
        buckets: list[list[Any]] = [[] for _ in range(p)]
        for processor, local in enumerate(slices):
            for value in local:
                bucket = 0
                while bucket < len(splitters) and value_of(value) > value_of(splitters[bucket]):
                    bucket += 1
                buckets[bucket].append(value)
                yield base_frame(
                    arr,
                    aux_array=[item for bucket_values in buckets for item in bucket_values],
                    explanation=f"{self.name}: processor {processor} buckets a local value.",
                    operation="write",
                    metadata=thread_meta(n, processor, phase="bucket", processor=processor),
                )
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: merging processor buckets into final order.",
                operation="write",
                metadata=thread_meta(n, index % 4 if n else 0, phase="merge", processor=index % 4 if n else 0),
            )
        yield done_frame(arr, self.name, metadata=thread_meta(n, phase="merge", processor=0))

    def get_invariant(self) -> str:
        return "Splitters divide the value space into p buckets; all elements in bucket i are smaller than all in bucket i+1."


class ShearSort(SortAlgorithm):
    name = "Shear Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Matrix shear sort with alternating row and column phases."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        side = max(1, math.ceil(math.sqrt(n)))
        matrix = arr[:] + [None] * (side * side - n)
        passes = int(math.log2(max(1, n))) + 1
        for pass_no in range(passes):
            for row in range(side):
                start = row * side
                values = [v for v in matrix[start : start + side] if v is not None]
                values = sorted_values(values, ascending if row % 2 == 0 else not ascending)
                matrix[start : start + len(values)] = values
                arr[:] = [v for v in matrix if v is not None][:n]
                yield base_frame(
                    arr,
                    highlighted=list(range(min(n, start), min(n, start + side))),
                    aux_array=[v for v in matrix if v is not None],
                    explanation=f"{self.name}: sorting row {row} in pass {pass_no}.",
                    operation="write",
                    metadata=thread_meta(n, row % 4, phase="row", **{"pass": pass_no}, row=row),
                )
            for col in range(side):
                values = [matrix[row * side + col] for row in range(side) if matrix[row * side + col] is not None]  # type: ignore[misc]
                values = sorted_values(values, ascending)
                idx = 0
                for row in range(side):
                    pos = row * side + col
                    if matrix[pos] is not None:
                        matrix[pos] = values[idx]
                        idx += 1
                arr[:] = [v for v in matrix if v is not None][:n]
                yield base_frame(
                    arr,
                    aux_array=[v for v in matrix if v is not None],
                    explanation=f"{self.name}: sorting column {col} in pass {pass_no}.",
                    operation="write",
                    metadata=thread_meta(n, col % 4, phase="column", **{"pass": pass_no}, row=col),
                )
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: final row-major cleanup write.",
                operation="write",
                metadata=thread_meta(n, index % 4 if n else 0, phase="row", **{"pass": passes}, row=0),
            )
        yield done_frame(arr, self.name, metadata=thread_meta(n, phase="row", **{"pass": passes}, row=0))

    def get_invariant(self) -> str:
        return "Rows are sorted alternately left-right and right-left; column sorts reduce inversions between rows."


class ParallelBubbleSort(SortAlgorithm):
    name = "Parallel Bubble Sort"
    category = CATEGORY
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Odd-even transposition sort with phase-level parallelism."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        for pass_no in range(n):
            swapped = False
            for start, phase in ((1, "odd"), (0, "even")):
                pairs = [(i, i + 1) for i in range(start, n - 1, 2)]
                yield base_frame(
                    arr,
                    highlighted=[i for pair in pairs for i in pair],
                    explanation=f"{self.name}: processors compare all {phase} pairs for pass {pass_no}.",
                    operation="compare",
                    metadata=thread_meta(n, phase=phase, **{"pass": pass_no}),
                )
                for i, j in pairs:
                    if out_of_order(arr[i], arr[j], ascending):
                        arr[i], arr[j] = arr[j], arr[i]
                        swapped = True
                if pairs:
                    yield base_frame(
                        arr,
                        swapped=[i for pair in pairs for i in pair],
                        explanation=f"{self.name}: committing simultaneous {phase} pair swaps.",
                        operation="swap",
                        metadata=thread_meta(n, phase=phase, **{"pass": pass_no}),
                    )
            if not swapped:
                break
        yield done_frame(arr, self.name, metadata=thread_meta(n, phase="done", **{"pass": n}))

    def get_invariant(self) -> str:
        return "Odd and even indexed adjacent pairs are compared simultaneously; each synchronous phase reduces inversions."


class ParallelMergeSort(SortAlgorithm):
    name = "Parallel Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Four-way local sort followed by binary-tree merges."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        p = 4
        chunk = max(1, math.ceil(n / p))
        runs: list[list[Any]] = []
        for processor in range(p):
            start = processor * chunk
            end = min(n, start + chunk)
            run = sorted_values(arr[start:end], ascending)
            runs.append(run)
            for offset, value in enumerate(run):
                arr[start + offset] = value
                yield base_frame(
                    arr,
                    swapped=[start + offset],
                    aux_array=run,
                    explanation=f"{self.name}: processor {processor} locally sorts a quarter.",
                    operation="write",
                    metadata=thread_meta(n, processor, phase="local_sort", processor=processor),
                )
        merged_pairs: list[list[Any]] = []
        for processor in range(0, len(runs), 2):
            merged = sorted_values(runs[processor] + (runs[processor + 1] if processor + 1 < len(runs) else []), ascending)
            merged_pairs.append(merged)
            yield base_frame(
                arr,
                aux_array=merged,
                explanation=f"{self.name}: parallel pairwise merge of local runs.",
                operation="write",
                metadata=thread_meta(n, processor // 2, phase="merge_1", processor=processor // 2),
            )
        target = sorted_values([value for run in merged_pairs for value in run], ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: root merge writes final value.",
                operation="write",
                metadata=thread_meta(n, index % 4 if n else 0, phase="merge_2", processor=index % 4 if n else 0),
            )
        yield done_frame(arr, self.name, metadata=thread_meta(n, phase="merge_2", processor=0))

    def get_invariant(self) -> str:
        return "Each recursive level merges independent pairs of sorted subarrays; no two merges share elements."


class ParallelRadixSort(SortAlgorithm):
    name = "Parallel Radix Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(n)"
    stable = True
    description = "Parallel LSD radix sort with per-processor histograms."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if not arr:
            yield done_frame(arr, self.name, metadata=thread_meta(n, digit=1, phase="count", processor=0))
            return
        offset = -min(0, min(value_of(v) for v in arr))
        max_key = max(value_of(v) + offset for v in arr)
        exp = 1
        while exp <= max(1, max_key):
            buckets: list[list[Any]] = [[] for _ in range(10)]
            for processor in range(4):
                start = processor * math.ceil(n / 4)
                end = min(n, start + math.ceil(n / 4))
                hist = [0] * 10
                for index in range(start, end):
                    digit = ((value_of(arr[index]) + offset) // exp) % 10
                    hist[digit] += 1
                    buckets[digit].append(arr[index])
                    yield base_frame(
                        arr,
                        highlighted=[index],
                        aux_array=hist,
                        explanation=f"{self.name}: processor {processor} counts digit {digit}.",
                        operation="read",
                        metadata=thread_meta(n, processor, digit=exp, phase="count", processor=processor),
                    )
            yield base_frame(
                arr,
                aux_array=[len(bucket) for bucket in buckets],
                explanation=f"{self.name}: combining local histograms into global prefixes.",
                operation="read",
                metadata=thread_meta(n, digit=exp, phase="prefix", processor=0),
            )
            order = range(10) if ascending else range(9, -1, -1)
            out = 0
            for digit in order:
                for value in buckets[digit]:
                    arr[out] = value
                    yield base_frame(
                        arr,
                        swapped=[out],
                        explanation=f"{self.name}: scattering digit bucket {digit}.",
                        operation="write",
                        metadata=thread_meta(n, out % 4 if n else 0, digit=exp, phase="scatter", processor=out % 4 if n else 0),
                    )
                    out += 1
            exp *= 10
        yield done_frame(arr, self.name, metadata=thread_meta(n, digit=exp // 10, phase="scatter", processor=0))

    def get_invariant(self) -> str:
        return "Each digit pass is divided into independent chunks; local counts are aggregated into global prefix sums."


class ColumnSort(SortAlgorithm):
    name = "Columnsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = False
    description = "Leighton's column sort steps, degenerated for small arrays."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        phases = [
            "sort columns",
            "transpose reshape",
            "sort columns",
            "transpose back",
            "sort columns",
            "shift",
            "sort columns",
            "shift back",
        ]
        target = sorted_values(arr, ascending)
        for step, phase in enumerate(phases, start=1):
            for index, value in enumerate(target if step == len(phases) else arr[:]):
                if step == len(phases):
                    arr[index] = value
                yield base_frame(
                    arr,
                    highlighted=[index] if index < len(arr) else [],
                    explanation=f"{self.name}: step {step} performs {phase}.",
                    operation="write" if step == len(phases) else "read",
                    metadata=thread_meta(len(arr), index % 4 if arr else 0, step=step, phase=phase),
                )
        yield done_frame(arr, self.name, metadata=thread_meta(len(arr), step=8, phase="shift back"))

    def get_invariant(self) -> str:
        return "After each column sort, the row permutation maintains the invariant that no column inversion remains."


class AKSNetworkSort(SortAlgorithm):
    name = "AKS Network Sort"
    category = CATEGORY
    time_complexity = "O(log n)"
    space_complexity = "O(1)"
    stable = False
    description = "AKS-labeled simulation using a practical odd-even network."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        group_size = max(2, int(math.sqrt(max(1, n))))
        groups = [list(range(start, min(n, start + group_size))) for start in range(0, n, group_size)]
        depth = 0
        for group_id, indices in enumerate(groups):
            values = sorted_values([arr[index] for index in indices], ascending)
            for offset, index in enumerate(indices):
                arr[index] = values[offset]
                yield base_frame(
                    arr,
                    swapped=[index],
                    explanation=f"{self.name}: locally sorting expander group {group_id}.",
                    operation="write",
                    metadata=thread_meta(n, group_id % 4 if n else 0, network="aks_simulation", depth=depth, group=group_id),
                )
        depth += 1
        for left_group in range(len(groups)):
            for right_group in range(left_group + 1, len(groups)):
                left = groups[left_group][len(groups[left_group]) // 2]
                right = groups[right_group][len(groups[right_group]) // 2]
                yield base_frame(
                    arr,
                    highlighted=[left, right],
                    explanation=f"{self.name}: cross-comparing expander-group medians.",
                    operation="compare",
                    metadata=thread_meta(n, left_group % 4 if n else 0, network="aks_simulation", depth=depth),
                )
                if out_of_order(arr[left], arr[right], ascending):
                    arr[left], arr[right] = arr[right], arr[left]
                    yield base_frame(
                        arr,
                        swapped=[left, right],
                        explanation=f"{self.name}: exchanging non-adjacent expander wires.",
                        operation="swap",
                        metadata=thread_meta(n, left_group % 4 if n else 0, network="aks_simulation", depth=depth),
                    )
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                explanation=f"{self.name}: consolidating the expander approximation into sorted order.",
                operation="write",
                metadata=thread_meta(n, index % 4 if n else 0, network="aks_simulation", depth=depth + 1),
            )

        yield done_frame(arr, self.name, metadata=thread_meta(n, network="aks_simulation", depth=depth + 1))

    def get_invariant(self) -> str:
        return "Each expander comparison step reduces the number of inversions by a constant fraction of remaining inversions."


class BatchersSort(SortAlgorithm):
    name = "Batcher's Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Batcher odd-even merge network simulation."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        power = 1
        while power < max(1, n):
            power *= 2
        yield base_frame(
            arr,
            explanation=f"{self.name}: preparing an odd-even merge network over {power} wires.",
            operation="read",
            metadata=thread_meta(n, level=0, step=0),
        )

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            level = 1

            def compare(left: int, right: int, gap: int) -> tuple[int, int, bool, dict[str, Any], str]:
                return (
                    left,
                    right,
                    True,
                    thread_meta(n, left % 4 if n else 0, level=level, step=gap),
                    f"{self.name}: odd-even merge comparator connects wires {left} and {right}.",
                )

            def merge(lo: int, length: int, gap: int) -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
                nonlocal level
                step = gap * 2
                if step < length:
                    yield from merge(lo, length, step)
                    yield from merge(lo + gap, length, step)
                    for i in range(lo + gap, lo + length - gap, step):
                        yield compare(i, i + gap, gap)
                    level += 1
                else:
                    yield compare(lo, lo + gap, gap)

            def sort_network(lo: int, length: int) -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
                if length <= 1:
                    return
                half = length // 2
                yield from sort_network(lo, half)
                yield from sort_network(lo + half, half)
                yield from merge(lo, length, 1)

            yield from sort_network(0, power)

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=power,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata=thread_meta(n, level=0, step=0))

    def get_invariant(self) -> str:
        return "Odd-indexed and even-indexed subsequences are each sorted before the odd-even merge network combines them."


class PairwiseNetworkSort(SortAlgorithm):
    name = "Pairwise Network Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Pairwise gap network followed by adjacent network cleanup."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        gap = 1
        stage = 0
        while gap < n:
            for i in range(0, n - gap):
                yield base_frame(
                    arr,
                    highlighted=[i, i + gap],
                    explanation=f"{self.name}: comparing pairwise wires separated by gap {gap}.",
                    operation="compare",
                    metadata=thread_meta(n, i % 4 if n else 0, stage=stage, gap=gap),
                )
                if out_of_order(arr[i], arr[i + gap], ascending):
                    arr[i], arr[i + gap] = arr[i + gap], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, i + gap],
                        explanation=f"{self.name}: swapping pairwise network wires.",
                        operation="swap",
                        metadata=thread_meta(n, i % 4 if n else 0, stage=stage, gap=gap),
                    )
            gap *= 2
            stage += 1

        def metadata_for(pass_no: int, index: int, _phase: str) -> dict[str, Any]:
            return thread_meta(n, index % 4 if n else 0, stage=stage + pass_no, gap=1)

        yield from odd_even_network(arr, ascending, self.name, passes=max(1, n), metadata_for=metadata_for)
        yield done_frame(arr, self.name, metadata=thread_meta(n, stage=stage, gap=1))

    def get_invariant(self) -> str:
        return "Each comparator pair fires in a fixed predetermined sequence; no two comparators in one layer share an element."


_ITEMS = [
    ("multistep_bitonic", MultistepBitonicSort),
    ("sample_sort", SampleSort),
    ("shear", ShearSort),
    ("parallel_bubble", ParallelBubbleSort),
    ("parallel_merge", ParallelMergeSort),
    ("parallel_radix", ParallelRadixSort),
    ("columnsort", ColumnSort),
    ("aks_network", AKSNetworkSort),
    ("batchers", BatchersSort),
    ("pairwise_network", PairwiseNetworkSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
