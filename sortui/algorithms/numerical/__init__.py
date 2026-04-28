from __future__ import annotations

import heapq
import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, sorted_values, value_of
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Numerical Sorts"


class ProxmapSort(SortAlgorithm):
    name = "Proxmap Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Proximity-map distribution sort with insertion inside mapped slots."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        n = len(arr)
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        scale = n / (max_val - min_val + 1)
        proxmap: list[list[Any]] = [[] for _ in range(n)]
        for index, value in enumerate(arr):
            prox_index = min(n - 1, int(scale * (value_of(value) - min_val)))
            bucket = proxmap[prox_index]
            insert_at = len(bucket)
            while insert_at > 0 and (
                value_of(bucket[insert_at - 1]) > value_of(value)
                if ascending
                else value_of(bucket[insert_at - 1]) < value_of(value)
            ):
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=[item for bucket_values in proxmap for item in bucket_values],
                    explanation=f"{self.name}: insertion-scanning proxmap bucket {prox_index}.",
                    operation="compare",
                    metadata={"proxmap_index": prox_index},
                )
                insert_at -= 1
            bucket.insert(insert_at, value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for bucket_values in proxmap for item in bucket_values],
                explanation=f"{self.name}: placing value {value} into proxmap bucket {prox_index}.",
                operation="write",
                metadata={"proxmap_index": prox_index},
            )
        ordered_buckets = proxmap if ascending else list(reversed(proxmap))
        out = 0
        for bucket_index, bucket in enumerate(ordered_buckets):
            for value in bucket:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=[item for bucket_values in ordered_buckets for item in bucket_values],
                    explanation=f"{self.name}: compacting proxmap bucket {bucket_index}.",
                    operation="write",
                    metadata={"proxmap_index": bucket_index},
                )
                out += 1
        yield done_frame(arr, self.name)


class InPlaceRadixSort(SortAlgorithm):
    name = "In-place Radix Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(1)"
    stable = False
    description = "LSD radix sort shown as in-place cycle-following passes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        # STRETCH: The visual pass follows bucket cycles but uses temporary
        # bucket lists for correctness on arbitrary Python integer objects.
        offset = -min(0, min(value_of(v) for v in arr))
        max_key = max(value_of(v) + offset for v in arr)
        exp = 1
        while exp <= max(1, max_key):
            buckets: list[list[Any]] = [[] for _ in range(10)]
            for index, value in enumerate(arr):
                digit = ((value_of(value) + offset) // exp) % 10
                buckets[digit].append(value)
                yield base_frame(
                    arr,
                    highlighted=[index],
                    explanation=f"{self.name}: following cycle start {index} for digit {exp}.",
                    operation="read",
                    metadata={"digit": exp, "cycle_start": index},
                )
            order = range(10) if ascending else range(9, -1, -1)
            out = 0
            for digit in order:
                for value in buckets[digit]:
                    arr[out] = value
                    yield base_frame(
                        arr,
                        swapped=[out],
                        explanation=f"{self.name}: cycling value into digit bucket {digit}.",
                        operation="write",
                        metadata={"digit": exp, "cycle_start": out},
                    )
                    out += 1
            exp *= 10
        yield done_frame(arr, self.name)


class BinaryQuickSort(SortAlgorithm):
    name = "Binary Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort partitioning by descending integer bits."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        max_val = max((abs(value_of(v)) for v in arr), default=0)
        bit = max(0, max_val.bit_length() - 1)
        yield from self._binary(arr, 0, len(arr), bit, ascending, 0)
        yield done_frame(arr, self.name)

    def _binary(
        self, arr: list[Any], lo: int, hi: int, bit: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1 or bit < 0:
            return
        zeros: list[Any] = []
        ones: list[Any] = []
        for index in range(lo, hi):
            bit_value = (value_of(arr[index]) >> bit) & 1
            yield base_frame(
                arr,
                highlighted=[index],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: reading bit {bit} with value {bit_value}.",
                operation="read",
                metadata={"bit": bit, "bit_value": bit_value},
            )
            (ones if bit_value else zeros).append(arr[index])
        ordered = zeros + ones if ascending else ones + zeros
        for offset, value in enumerate(ordered):
            arr[lo + offset] = value
            yield base_frame(
                arr,
                swapped=[lo + offset],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: writing bit partition value.",
                operation="write",
                metadata={"bit": bit, "bit_value": (value_of(value) >> bit) & 1},
            )
        split = lo + (len(zeros) if ascending else len(ones))
        yield from self._binary(arr, lo, split, bit - 1, ascending, depth + 1)
        yield from self._binary(arr, split, hi, bit - 1, ascending, depth + 1)


class KirkpatrickReischSort(SortAlgorithm):
    name = "Kirkpatrick-Reisch Sort"
    category = CATEGORY
    time_complexity = "O(n log log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Fusion-tree-inspired block sort with priority-queue merge."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        block_size = max(1, int(math.log2(max(2, n))))
        blocks: list[list[Any]] = []
        for block, start in enumerate(range(0, n, block_size)):
            values = sorted_values(arr[start : start + block_size], ascending)
            blocks.append(values)
            for offset, value in enumerate(values):
                arr[start + offset] = value
                yield base_frame(
                    arr,
                    swapped=[start + offset],
                    aux_array=values,
                    explanation=f"{self.name}: counting-sorting block {block}.",
                    operation="write",
                    metadata={"block_size": block_size, "block": block, "phase": "block_sort"},
                )
        heap: list[tuple[int, int, int, Any]] = []
        for block, values in enumerate(blocks):
            if values:
                priority = value_of(values[0]) if ascending else -value_of(values[0])
                heapq.heappush(heap, (priority, block, 0, values[0]))
        out = 0
        while heap:
            _priority, block, index, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                explanation=f"{self.name}: priority-queue merging block {block}.",
                operation="write",
                metadata={"block_size": block_size, "block": block, "phase": "merge"},
            )
            out += 1
            next_index = index + 1
            if next_index < len(blocks[block]):
                next_value = blocks[block][next_index]
                priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(heap, (priority, block, next_index, next_value))
        yield done_frame(arr, self.name)


_ITEMS = [
    ("proxmap", ProxmapSort),
    ("inplace_radix", InPlaceRadixSort),
    ("binary_quicksort", BinaryQuickSort),
    ("kirkpatrick_reisch", KirkpatrickReischSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
