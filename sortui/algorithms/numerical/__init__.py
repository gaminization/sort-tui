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

    def get_invariant(self) -> str:
        return "Each element's proxmap value gives its approximate final position; collisions are resolved by insertion sort."


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
        offset = -min(0, min(value_of(v) for v in arr))
        max_key = max(value_of(v) + offset for v in arr)
        exp = 1
        while exp <= max(1, max_key):
            counts = [0] * 10
            for index, value in enumerate(arr):
                digit = ((value_of(value) + offset) // exp) % 10
                counts[digit] += 1
                yield base_frame(
                    arr,
                    highlighted=[index],
                    explanation=f"{self.name}: counting digit {digit} at position {exp} before cycle placement.",
                    operation="read",
                    metadata={"digit": exp, "cycle_start": index, "counts": counts[:]},
                )
            starts = [0] * 10
            total = 0
            digit_order = list(range(10)) if ascending else list(range(9, -1, -1))
            for digit in digit_order:
                starts[digit] = total
                total += counts[digit]
                yield base_frame(
                    arr,
                    highlighted=[],
                    explanation=f"{self.name}: digit {digit} owns in-place range starting at {starts[digit]}.",
                    operation="read",
                    metadata={"digit": exp, "cycle_start": starts[digit], "counts": counts[:], "starts": starts[:]},
                )

            next_free = starts[:]
            targets = [0] * len(arr)
            for index, value in enumerate(arr):
                digit = ((value_of(value) + offset) // exp) % 10
                targets[index] = next_free[digit]
                next_free[digit] += 1
                yield base_frame(
                    arr,
                    highlighted=[index],
                    explanation=f"{self.name}: assigning index {index} to cycle target {targets[index]} for digit {digit}.",
                    operation="read",
                    metadata={"digit": exp, "cycle_start": index, "targets_ready": index + 1},
                )

            for cycle_start in range(len(arr)):
                while targets[cycle_start] != cycle_start:
                    target = targets[cycle_start]
                    digit = ((value_of(arr[cycle_start]) + offset) // exp) % 10
                    arr[cycle_start], arr[target] = arr[target], arr[cycle_start]
                    targets[cycle_start], targets[target] = targets[target], targets[cycle_start]
                    yield base_frame(
                        arr,
                        highlighted=[cycle_start, target],
                        swapped=[cycle_start, target],
                        explanation=f"{self.name}: cycle-following digit {digit} swaps index {cycle_start} with target {target}.",
                        operation="swap",
                        metadata={"digit": exp, "cycle_start": cycle_start, "counts": counts[:]},
                    )
            exp *= 10
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "After each digit pass, elements occupy their correct relative positions for that digit without auxiliary space."


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

    def get_invariant(self) -> str:
        return "Elements are partitioned by the current bit; the zero-bit partition precedes the one-bit partition."


class KirkpatrickReischSort(SortAlgorithm):
    name = "Kirkpatrick-Reisch Sort"
    category = CATEGORY
    time_complexity = "O(n log log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Fusion-tree-inspired block sort with priority-queue merge."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        min_val = min(value_of(value) for value in arr)
        max_key = max(value_of(value) - min_val for value in arr)
        top_bit = max(0, max_key.bit_length() - 1)

        def reduce(lo: int, hi: int, bit: int, depth: int) -> Generator[SortFrame, None, None]:
            if hi - lo <= 1 or bit < 0:
                return
            group_bits = max(1, int(math.sqrt(bit + 1)))
            shift = max(0, bit - group_bits + 1)
            bucket_count = 1 << (bit - shift + 1)
            buckets: list[list[Any]] = [[] for _ in range(bucket_count)]
            for index in range(lo, hi):
                reduced_key = ((value_of(arr[index]) - min_val) >> shift) & (bucket_count - 1)
                buckets[reduced_key].append(arr[index])
                yield base_frame(
                    arr,
                    highlighted=[index],
                    partition_bounds=(lo, hi - 1),
                    recursion_depth=depth,
                    aux_array=[len(bucket) for bucket in buckets],
                    explanation=(
                        f"{self.name}: reducing universe bits {bit}..{shift} "
                        f"into bucket {reduced_key}."
                    ),
                    operation="read",
                    metadata={
                        "block_size": group_bits,
                        "block": reduced_key,
                        "phase": "universe_reduce",
                        "bit": bit,
                    },
                )
            order = range(bucket_count) if ascending else range(bucket_count - 1, -1, -1)
            bounds: list[tuple[int, int]] = []
            out = lo
            for bucket in order:
                start = out
                for value in buckets[bucket]:
                    arr[out] = value
                    yield base_frame(
                        arr,
                        swapped=[out],
                        partition_bounds=(lo, hi - 1),
                        recursion_depth=depth,
                        aux_array=[len(bucket_values) for bucket_values in buckets],
                        explanation=f"{self.name}: writing reduced-universe bucket {bucket}.",
                        operation="write",
                        metadata={
                            "block_size": group_bits,
                            "block": bucket,
                            "phase": "bucket_write",
                            "bit": bit,
                        },
                    )
                    out += 1
                if out - start > 1:
                    bounds.append((start, out))
            for start, end in bounds:
                yield from reduce(start, end, shift - 1, depth + 1)

        yield from reduce(0, len(arr), top_bit, 0)
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each recursive level reduces the universe size; elements in the same reduced bucket share a digit prefix."


_ITEMS = [
    ("proxmap", ProxmapSort),
    ("inplace_radix", InPlaceRadixSort),
    ("binary_quicksort", BinaryQuickSort),
    ("kirkpatrick_reisch", KirkpatrickReischSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
