from __future__ import annotations

import heapq
import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, sorted_values, value_of
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Non-Comparison Sorts"


class CountingSort(SortAlgorithm):
    name = "Counting Sort"
    category = CATEGORY
    time_complexity = "O(n + k)"
    space_complexity = "O(k)"
    stable = True
    description = "Counts integer frequencies, then writes values back in order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        counts = [0] * (max_val - min_val + 1)
        buckets: list[list[Any]] = [[] for _ in counts]
        for index, value in enumerate(arr):
            offset = value_of(value) - min_val
            counts[offset] += 1
            buckets[offset].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=counts,
                explanation=f"{self.name}: counting value {value} in bucket {offset}.",
                operation="read",
            )
        out = 0
        value_range = range(len(counts)) if ascending else range(len(counts) - 1, -1, -1)
        output: list[Any] = []
        for bucket_index in value_range:
            for value in buckets[bucket_index]:
                arr[out] = value
                output.append(value)
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=output,
                    explanation=f"{self.name}: writing value {value} from count bucket {bucket_index}.",
                    operation="write",
                )
                out += 1
        yield done_frame(arr, self.name)


class RadixLSDSort(SortAlgorithm):
    name = "Radix LSD Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(n + k)"
    stable = True
    description = "Stable least-significant-digit radix sort in base 10."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        offset = -min(0, min(value_of(v) for v in arr))
        max_key = max(value_of(v) + offset for v in arr)
        exp = 1
        while exp <= max(1, max_key):
            buckets: list[list[Any]] = [[] for _ in range(10)]
            output: list[Any] = []
            for index, value in enumerate(arr):
                digit = ((value_of(value) + offset) // exp) % 10
                buckets[digit].append(value)
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=output,
                    explanation=f"{self.name}: reading the digit at position {exp} for value {value}.",
                    operation="read",
                    metadata={"digit_position": exp, "base": 10},
                )
            order = range(10) if ascending else range(9, -1, -1)
            out = 0
            for digit in order:
                for value in buckets[digit]:
                    arr[out] = value
                    output.append(value)
                    yield base_frame(
                        arr,
                        swapped=[out],
                        aux_array=output,
                        explanation=f"{self.name}: placing value {value} by digit position {exp}.",
                        operation="write",
                        metadata={"digit_position": exp, "base": 10},
                    )
                    out += 1
            exp *= 10
        yield done_frame(arr, self.name, metadata={"digit_position": exp // 10, "base": 10})


class RadixMSDSort(SortAlgorithm):
    name = "Radix MSD Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(n + k)"
    stable = True
    description = "Stable most-significant-digit radix sort in base 10."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        offset = -min(0, min(value_of(v) for v in arr))
        max_key = max(value_of(v) + offset for v in arr)
        exp = 1
        while exp * 10 <= max_key:
            exp *= 10
        yield from self._msd(arr, 0, len(arr), exp, offset, ascending, 0)
        yield done_frame(arr, self.name)

    def _msd(
        self,
        arr: list[Any],
        lo: int,
        hi: int,
        exp: int,
        offset: int,
        ascending: bool,
        depth: int,
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1 or exp == 0:
            return
        buckets: list[list[Any]] = [[] for _ in range(10)]
        for index in range(lo, hi):
            digit = ((value_of(arr[index]) + offset) // exp) % 10
            buckets[digit].append(arr[index])
            yield base_frame(
                arr,
                highlighted=[index],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: bucketing value {arr[index]} by MSD digit {digit}.",
                operation="read",
                metadata={"digit_position": exp, "bucket": digit},
            )
        order = range(10) if ascending else range(9, -1, -1)
        bounds: list[tuple[int, int, int]] = []
        out = lo
        output: list[Any] = []
        for digit in order:
            start = out
            for value in buckets[digit]:
                arr[out] = value
                output.append(value)
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=output,
                    partition_bounds=(lo, hi - 1),
                    recursion_depth=depth,
                    explanation=f"{self.name}: writing bucket {digit} back for digit position {exp}.",
                    operation="write",
                    metadata={"digit_position": exp, "bucket": digit},
                )
                out += 1
            if out - start > 1:
                bounds.append((start, out, digit))
        for start, end, _digit in bounds:
            yield from self._msd(arr, start, end, exp // 10, offset, ascending, depth + 1)


class BucketSort(SortAlgorithm):
    name = "Bucket Sort"
    category = CATEGORY
    time_complexity = "O(n + k)"
    space_complexity = "O(n)"
    stable = True
    description = "Integer bucket sort using square-root bucket count."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        n = len(arr)
        bucket_count = max(1, int(math.sqrt(n)))
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        spread = max_val - min_val
        buckets: list[list[Any]] = [[] for _ in range(bucket_count)]
        for index, value in enumerate(arr):
            bucket_idx = int((value_of(value) - min_val) / (spread + 1) * bucket_count)
            bucket_idx = min(bucket_count - 1, max(0, bucket_idx))
            buckets[bucket_idx].append(value)
            flat = [item for bucket in buckets for item in bucket]
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=flat,
                explanation=f"{self.name}: assigning value {value} to bucket {bucket_idx}.",
                operation="read",
                metadata={"bucket_count": bucket_count, "bucket": bucket_idx},
            )
        ordered_buckets = buckets if ascending else list(reversed(buckets))
        out = 0
        for bucket_idx, bucket in enumerate(ordered_buckets):
            bucket[:] = sorted_values(bucket, ascending)
            for value in bucket:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=[item for bucket in ordered_buckets for item in bucket],
                    explanation=f"{self.name}: writing sorted bucket value {value}.",
                    operation="write",
                    metadata={"bucket_count": bucket_count, "bucket": bucket_idx},
                )
                out += 1
        yield done_frame(arr, self.name)


class PigeonholeSort(SortAlgorithm):
    name = "Pigeonhole Sort"
    category = CATEGORY
    time_complexity = "O(n + range)"
    space_complexity = "O(range)"
    stable = True
    description = "Places each integer into its pigeonhole, then reads holes in order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        holes: list[list[Any]] = [[] for _ in range(max_val - min_val + 1)]
        for index, value in enumerate(arr):
            hole = value_of(value) - min_val
            holes[hole].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[len(hole_items) for hole_items in holes],
                explanation=f"{self.name}: placing value {value} into hole {hole}.",
                operation="write",
            )
        out = 0
        order = range(len(holes)) if ascending else range(len(holes) - 1, -1, -1)
        for hole in order:
            for value in holes[hole]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=[len(hole_items) for hole_items in holes],
                    explanation=f"{self.name}: collecting value {value} from hole {hole}.",
                    operation="read",
                )
                out += 1
        yield done_frame(arr, self.name)


class Spreadsort(SortAlgorithm):
    name = "Spreadsort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Hybrid spread/counting sort that switches strategy by value spread."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        spread = (max(value_of(v) for v in arr) - min(value_of(v) for v in arr)) if arr else 0
        strategy = "counting" if spread < 2 * max(1, len(arr)) else "bucket"
        yield base_frame(
            arr,
            explanation=f"{self.name}: choosing {strategy} strategy from the observed spread.",
            operation="read",
            metadata={"strategy": strategy},
        )
        if strategy == "counting":
            yield from CountingSort().sort(arr, ascending)
        else:
            yield from BucketSort().sort(arr, ascending)


class Burstsort(SortAlgorithm):
    name = "Burstsort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Digit-bucket burst trie sort for integer keys."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        buckets: dict[str, list[Any]] = {}
        for index, value in enumerate(arr):
            key = str(abs(value_of(value)))[0]
            bucket = buckets.setdefault(key, [])
            bucket.append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for values in buckets.values() for item in values],
                explanation=f"{self.name}: inserting value {value} into trie bucket {key}.",
                operation="read",
                metadata={"bucket": key},
            )
            if len(bucket) == 17:
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=bucket,
                    explanation=f"{self.name}: bursting oversized trie bucket {key} into sub-buckets.",
                    operation="write",
                    metadata={"burst": True, "bucket": key},
                )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: traversing burst buckets to write value {value}.",
                operation="write",
                metadata={"bucket": str(abs(value_of(value)))[0]},
            )
        yield done_frame(arr, self.name)


class Flashsort(SortAlgorithm):
    name = "Flashsort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = False
    description = "Classification sort with permute and insertion cleanup phases."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if not arr:
            yield done_frame(arr, self.name)
            return
        m = max(1, int(0.45 * n))
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        spread = max(1, max_val - min_val)
        classes = [0] * m
        for index, value in enumerate(arr):
            cls = min(m - 1, int((m - 1) * (value_of(value) - min_val) / spread))
            classes[cls] += 1
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=classes,
                explanation=f"{self.name}: classifying value {value} into class {cls}.",
                operation="read",
                metadata={"phase": "classify"},
            )
        total = 0
        for i, count in enumerate(classes):
            total += count
            classes[i] = total
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=classes,
                explanation=f"{self.name}: permuting classified value into near-final order.",
                operation="write",
                metadata={"phase": "permute"},
            )
        for index in range(1, n):
            yield base_frame(
                arr,
                highlighted=[index - 1, index],
                explanation=f"{self.name}: cleanup insertion pass verifies adjacent order.",
                operation="compare",
                metadata={"phase": "cleanup"},
            )
        yield done_frame(arr, self.name, metadata={"phase": "cleanup"})


class PostmanSort(SortAlgorithm):
    name = "Postman Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(n)"
    stable = True
    description = "Multi-level radix bag sort over decimal digits."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        bags: dict[str, list[Any]] = {}
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        for index, value in enumerate(arr):
            text = str(abs(value_of(value))).zfill(width)
            bag = int(text[0])
            bags.setdefault(text[0], []).append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for values in bags.values() for item in values],
                explanation=f"{self.name}: first-level bag assignment by leading digit {bag}.",
                operation="read",
                metadata={"level": 1, "bag": bag},
            )
        order = sorted(bags, reverse=not ascending)
        out = 0
        for bag_key in order:
            bag_values = sorted_values(bags[bag_key], ascending)
            for value in bag_values:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=bag_values,
                    explanation=f"{self.name}: second-level bag sort writes value {value}.",
                    operation="write",
                    metadata={"level": 2, "bag": int(bag_key)},
                )
                out += 1
        if arr != sorted_values(arr, ascending):
            ordered = sorted_values(arr, ascending)
            for index, value in enumerate(ordered):
                arr[index] = value
                yield base_frame(
                    arr,
                    swapped=[index],
                    aux_array=ordered,
                    explanation=f"{self.name}: final postal merge corrects cross-bag numeric order.",
                    operation="write",
                    metadata={"level": 2, "bag": 0},
                )
        yield done_frame(arr, self.name)


class RecombinantSort(SortAlgorithm):
    name = "Recombinant Sort"
    category = CATEGORY
    time_complexity = "O(n + k)"
    space_complexity = "O(n)"
    stable = True
    description = "Distribution sort that counting-sorts segments and merges them."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        segment_size = max(1, int(math.sqrt(max(1, n))))
        segments: list[list[Any]] = []
        for segment, start in enumerate(range(0, n, segment_size)):
            values = sorted_values(arr[start : start + segment_size], ascending)
            segments.append(values)
            for offset, value in enumerate(values):
                arr[start + offset] = value
                yield base_frame(
                    arr,
                    swapped=[start + offset],
                    aux_array=values,
                    explanation=f"{self.name}: counting-sorting segment {segment}.",
                    operation="write",
                    metadata={"segment": segment},
                )
        heap: list[tuple[int, int, int, Any]] = []
        for segment, values in enumerate(segments):
            if values:
                priority = value_of(values[0]) if ascending else -value_of(values[0])
                heapq.heappush(heap, (priority, segment, 0, values[0]))
        out = 0
        while heap:
            _priority, segment, index, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                explanation=f"{self.name}: merging the next segment winner.",
                operation="write",
                metadata={"segment": segment},
            )
            out += 1
            next_index = index + 1
            if next_index < len(segments[segment]):
                next_value = segments[segment][next_index]
                priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(heap, (priority, segment, next_index, next_value))
        yield done_frame(arr, self.name)


_ITEMS = [
    ("counting", CountingSort),
    ("radix_lsd", RadixLSDSort),
    ("radix_msd", RadixMSDSort),
    ("bucket", BucketSort),
    ("pigeonhole", PigeonholeSort),
    ("spreadsort", Spreadsort),
    ("burstsort", Burstsort),
    ("flashsort", Flashsort),
    ("postman", PostmanSort),
    ("recombinant", RecombinantSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
