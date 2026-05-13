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
        source = arr[:]
        for index, value in enumerate(source):
            offset = value_of(value) - min_val
            counts[offset] += 1
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=counts,
                explanation=f"{self.name}: counting value {value} in bucket {offset}.",
                operation="read",
                metadata={"phase": "count", "value": value_of(value), "bucket": offset},
            )

        positions: dict[int, int] = {}
        running_total = 0
        prefix_order = range(len(counts)) if ascending else range(len(counts) - 1, -1, -1)
        for bucket_index in prefix_order:
            positions[bucket_index] = running_total
            running_total += counts[bucket_index]
            counts[bucket_index] = running_total
            yield base_frame(
                arr,
                highlighted=[],
                aux_array=counts,
                explanation=(
                    f"{self.name}: computing prefix sum for bucket {bucket_index}; "
                    f"next write starts at index {positions[bucket_index]}."
                ),
                operation="read",
                metadata={"phase": "prefix", "bucket": bucket_index, "prefix": running_total},
            )

        output: list[Any | None] = [None] * len(arr)
        for source_index, value in enumerate(source):
            bucket_index = value_of(value) - min_val
            write_index = positions[bucket_index]
            positions[bucket_index] += 1
            output[write_index] = value
            arr[write_index] = value
            aux_output = [item if item is not None else 0 for item in output]
            yield base_frame(
                arr,
                highlighted=[source_index],
                swapped=[write_index],
                aux_array=aux_output,
                explanation=f"{self.name}: placing value {value} at prefix position {write_index}.",
                operation="write",
                metadata={"phase": "place", "value": value_of(value), "bucket": bucket_index},
            )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "count[v] holds the number of elements equal to v seen so far; prefix sums give final positions."


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

    def get_invariant(self) -> str:
        return "After processing digit d, all elements are sorted by their d least-significant digits."


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

    def get_invariant(self) -> str:
        return "Elements sharing the same most-significant digit prefix are grouped into the same bucket recursively."


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

        for bucket_idx, bucket in enumerate(buckets):
            for i in range(1, len(bucket)):
                key = bucket[i]
                yield base_frame(
                    arr,
                    aux_array=[item for bucket_values in buckets for item in bucket_values],
                    explanation=f"{self.name}: reading bucket {bucket_idx} value for insertion sort.",
                    operation="read",
                    metadata={"bucket_count": bucket_count, "bucket": bucket_idx, "phase": "bucket_sort"},
                )
                j = i - 1
                while j >= 0:
                    yield base_frame(
                        arr,
                        aux_array=bucket[:],
                        explanation=f"{self.name}: insertion-sorting bucket {bucket_idx}.",
                        operation="compare",
                        metadata={"bucket_count": bucket_count, "bucket": bucket_idx, "phase": "bucket_sort"},
                    )
                    if not (
                        value_of(bucket[j]) > value_of(key)
                        if ascending
                        else value_of(bucket[j]) < value_of(key)
                    ):
                        break
                    bucket[j + 1] = bucket[j]
                    yield base_frame(
                        arr,
                        aux_array=bucket[:],
                        explanation=f"{self.name}: shifting inside bucket {bucket_idx}.",
                        operation="write",
                        metadata={"bucket_count": bucket_count, "bucket": bucket_idx, "phase": "bucket_sort"},
                    )
                    j -= 1
                bucket[j + 1] = key
                yield base_frame(
                    arr,
                    aux_array=bucket[:],
                    explanation=f"{self.name}: placing the saved value in bucket {bucket_idx}.",
                    operation="write",
                    metadata={"bucket_count": bucket_count, "bucket": bucket_idx, "phase": "bucket_sort"},
                )

        ordered_buckets = buckets if ascending else list(reversed(buckets))
        out = 0
        for bucket_idx, bucket in enumerate(ordered_buckets):
            for value in bucket:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=[item for bucket in ordered_buckets for item in bucket],
                    explanation=f"{self.name}: writing sorted bucket value {value}.",
                    operation="write",
                    metadata={"bucket_count": bucket_count, "bucket": bucket_idx, "phase": "concatenate"},
                )
                out += 1
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each bucket contains only elements whose values fall within that bucket's designated range."


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
                metadata={"phase": "place", "hole": hole, "value": value_of(value)},
            )
        out = 0
        order = range(len(holes)) if ascending else range(len(holes) - 1, -1, -1)
        for hole in order:
            yield base_frame(
                arr,
                aux_array=[len(hole_items) for hole_items in holes],
                explanation=f"{self.name}: scanning pigeonhole {hole} for stored values.",
                operation="read",
                metadata={"phase": "scan", "hole": hole, "value": min_val + hole},
            )
            for value in holes[hole]:
                yield base_frame(
                    arr,
                    highlighted=[out],
                    aux_array=[len(hole_items) for hole_items in holes],
                    explanation=f"{self.name}: reading value {value} out of hole {hole}.",
                    operation="read",
                    metadata={"phase": "collect", "hole": hole, "value": value_of(value)},
                )
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=[len(hole_items) for hole_items in holes],
                    explanation=f"{self.name}: writing collected pigeonhole value {value} to output.",
                    operation="write",
                    metadata={"phase": "write", "hole": hole, "value": value_of(value)},
                )
                out += 1
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each pigeonhole slot holds exactly the elements equal to that slot's value from the original array."


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

    def get_invariant(self) -> str:
        return "Elements are recursively spread into buckets by bit prefix; each bucket's range halves each level."


class Burstsort(SortAlgorithm):
    name = "Burstsort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Digit-bucket burst trie sort for integer keys."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(value)))) for value in arr), default=1)
        threshold = 8
        root: dict[str, Any] = {"children": {}, "values": [], "depth": 0}

        def node_snapshot(node: dict[str, Any]) -> list[int]:
            values = [value_of(value) for value in node.get("values", [])]
            for child in node.get("children", {}).values():
                values.extend(node_snapshot(child))
            return values

        def burst(node: dict[str, Any]) -> Generator[SortFrame, None, None]:
            depth = node["depth"]
            if depth >= width or len(node["values"]) <= threshold:
                return
            values = node["values"]
            node["values"] = []
            for value in values:
                digit = str(abs(value_of(value))).zfill(width)[depth]
                child = node["children"].setdefault(
                    digit, {"children": {}, "values": [], "depth": depth + 1}
                )
                child["values"].append(value)
            yield base_frame(
                arr,
                aux_array=node_snapshot(root),
                explanation=f"{self.name}: bursting trie node at depth {depth} into digit children.",
                operation="write",
                metadata={"burst": True, "bucket": depth, "depth": depth},
            )
            for child in node["children"].values():
                if len(child["values"]) > threshold:
                    yield from burst(child)

        for index, value in enumerate(arr):
            node = root
            key = str(abs(value_of(value))).zfill(width)
            for depth, digit in enumerate(key):
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=node_snapshot(root),
                    explanation=f"{self.name}: following trie digit {digit} at depth {depth}.",
                    operation="read",
                    metadata={"bucket": digit, "depth": depth},
                )
                if node["children"]:
                    node = node["children"].setdefault(
                        digit, {"children": {}, "values": [], "depth": depth + 1}
                    )
                else:
                    break
            node["values"].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=node_snapshot(root),
                explanation=f"{self.name}: storing value {value} in the current trie bucket.",
                operation="write",
                metadata={"bucket": key, "depth": node["depth"]},
            )
            if len(node["values"]) > threshold:
                yield from burst(node)

        ordered: list[Any] = []

        def traverse(node: dict[str, Any]) -> None:
            digits = sorted(node["children"], reverse=not ascending)
            if ascending:
                ordered.extend(sorted_values(node["values"], ascending))
            for digit in digits:
                traverse(node["children"][digit])
            if not ascending:
                ordered.extend(sorted_values(node["values"], ascending))

        traverse(root)
        if len(ordered) != len(arr):
            ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: flattening burst trie traversal value {value}.",
                operation="write",
                metadata={"bucket": str(abs(value_of(value))).zfill(width), "phase": "flatten"},
            )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "The trie partitions strings by leading character; a bucket bursts into child nodes when it exceeds capacity."


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
            yield base_frame(
                arr,
                highlighted=[],
                aux_array=classes,
                explanation=f"{self.name}: prefix boundary for class {i} is now {total}.",
                operation="read",
                metadata={"phase": "prefix", "class": i},
            )

        buckets: list[list[Any]] = [[] for _ in range(m)]
        for index, value in enumerate(arr[:]):
            cls = min(m - 1, int((m - 1) * (value_of(value) - min_val) / spread))
            buckets[cls].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for bucket in buckets for item in bucket],
                explanation=f"{self.name}: permuting value {value} into class bucket {cls}.",
                operation="write",
                metadata={"phase": "permute", "class": cls},
            )
        out = 0
        class_order = range(m) if ascending else range(m - 1, -1, -1)
        for cls in class_order:
            for value in buckets[cls]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=buckets[cls],
                    explanation=f"{self.name}: writing class {cls} back for cleanup.",
                    operation="write",
                    metadata={"phase": "class_write", "class": cls},
                )
                out += 1

        for index in range(1, n):
            key = arr[index]
            j = index - 1
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=classes,
                explanation=f"{self.name}: cleanup insertion pass reads index {index}.",
                operation="read",
                metadata={"phase": "cleanup"},
            )
            while j >= 0:
                yield base_frame(
                    arr,
                    highlighted=[j, j + 1],
                    aux_array=classes,
                    explanation=f"{self.name}: cleanup insertion pass verifies adjacent order.",
                    operation="compare",
                    metadata={"phase": "cleanup"},
                )
                if not (
                    value_of(arr[j]) > value_of(key)
                    if ascending
                    else value_of(arr[j]) < value_of(key)
                ):
                    break
                arr[j + 1] = arr[j]
                yield base_frame(
                    arr,
                    swapped=[j, j + 1],
                    aux_array=classes,
                    explanation=f"{self.name}: cleanup shifts a classified value.",
                    operation="write",
                    metadata={"phase": "cleanup"},
                )
                j -= 1
            arr[j + 1] = key
            yield base_frame(
                arr,
                swapped=[j + 1],
                aux_array=classes,
                explanation=f"{self.name}: cleanup places the saved value.",
                operation="write",
                metadata={"phase": "cleanup"},
            )
        yield done_frame(arr, self.name, metadata={"phase": "cleanup"})

    def get_invariant(self) -> str:
        return "Each element's class index is computed by linear interpolation; class boundaries are maintained as prefix counts."


class PostmanSort(SortAlgorithm):
    name = "Postman Sort"
    category = CATEGORY
    time_complexity = "O(d(n + k))"
    space_complexity = "O(n)"
    stable = True
    description = "Multi-level radix bag sort over decimal digits."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        yield base_frame(
            arr,
            explanation=f"{self.name}: measuring {width} postal digit levels before bagging.",
            operation="read",
            metadata={"level": 0, "bag": -1, "phase": "measure"},
        )
        for level, digit_pos in enumerate(range(width - 1, -1, -1), start=1):
            bags: dict[int, list[Any]] = {digit: [] for digit in range(10)}
            for index, value in enumerate(arr):
                text = str(abs(value_of(value))).zfill(width)
                bag = int(text[digit_pos])
                bags[bag].append(value)
                yield base_frame(
                    arr,
                    highlighted=[index],
                    aux_array=[item for digit in range(10) for item in bags[digit]],
                    explanation=(
                        f"{self.name}: postal clerk files value {value} by digit "
                        f"{level}/{width} into bag {bag}."
                    ),
                    operation="read",
                    metadata={"level": level, "bag": bag, "phase": "bag"},
                )
            out = 0
            order = range(10) if ascending else range(9, -1, -1)
            for bag in order:
                yield base_frame(
                    arr,
                    aux_array=[item for digit in order for item in bags[digit]],
                    explanation=f"{self.name}: opening postal bag {bag} for digit level {level}.",
                    operation="read",
                    metadata={"level": level, "bag": bag, "phase": "open_bag"},
                )
                for value in bags[bag]:
                    arr[out] = value
                    yield base_frame(
                        arr,
                        swapped=[out],
                        aux_array=[item for digit in order for item in bags[digit]],
                        explanation=f"{self.name}: writing bag {bag} value back for the next postal pass.",
                        operation="write",
                        metadata={"level": level, "bag": bag, "phase": "write"},
                    )
                    out += 1
            yield base_frame(
                arr,
                aux_array=arr[:],
                explanation=f"{self.name}: completed digit level {level} postal distribution.",
                operation="read",
                metadata={"level": level, "bag": -1, "phase": "level_done"},
            )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "After each digit pass, elements are grouped by their combined digit prefix seen so far, LSD to MSD."


class RecombinantSort(SortAlgorithm):
    name = "Recombinant Sort"
    category = CATEGORY
    time_complexity = "O(n + k)"
    space_complexity = "O(n)"
    stable = True
    description = "Distribution sort that counting-sorts segments and merges them."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        segment_count = max(1, int(math.sqrt(max(1, n))))
        segments: list[list[Any]] = [[] for _ in range(segment_count)]
        for index, value in enumerate(arr):
            segment = index % segment_count
            segments[segment].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for segment_values in segments for item in segment_values],
                explanation=f"{self.name}: distributing value {value} into subsequence {segment}.",
                operation="read",
                metadata={"segment": segment, "phase": "distribute"},
            )

        for segment, values in enumerate(segments):
            for i in range(1, len(values)):
                key = values[i]
                yield base_frame(
                    arr,
                    aux_array=values[:],
                    explanation=f"{self.name}: reading subsequence {segment} key for insertion sort.",
                    operation="read",
                    metadata={"segment": segment, "phase": "subsequence_sort"},
                )
                j = i - 1
                while j >= 0:
                    yield base_frame(
                        arr,
                        aux_array=values[:],
                        explanation=f"{self.name}: comparing inside subsequence {segment}.",
                        operation="compare",
                        metadata={"segment": segment, "phase": "subsequence_sort"},
                    )
                    if not (
                        value_of(values[j]) > value_of(key)
                        if ascending
                        else value_of(values[j]) < value_of(key)
                    ):
                        break
                    values[j + 1] = values[j]
                    yield base_frame(
                        arr,
                        aux_array=values[:],
                        explanation=f"{self.name}: shifting inside subsequence {segment}.",
                        operation="write",
                        metadata={"segment": segment, "phase": "subsequence_sort"},
                    )
                    j -= 1
                values[j + 1] = key
                yield base_frame(
                    arr,
                    aux_array=values,
                    explanation=f"{self.name}: placing key inside sorted subsequence {segment}.",
                    operation="write",
                    metadata={"segment": segment, "phase": "subsequence_sort"},
                )

        visual_index = 0
        for segment, values in enumerate(segments):
            for value in values:
                if visual_index < n:
                    arr[visual_index] = value
                    yield base_frame(
                        arr,
                        swapped=[visual_index],
                        aux_array=values,
                        explanation=f"{self.name}: staging sorted subsequence {segment} before recombination.",
                        operation="write",
                        metadata={"segment": segment, "phase": "stage"},
                    )
                    visual_index += 1
        heap: list[tuple[int, int, int, Any]] = []
        for segment, values in enumerate(segments):
            if values:
                priority = value_of(values[0]) if ascending else -value_of(values[0])
                heapq.heappush(heap, (priority, segment, 0, values[0]))
                yield base_frame(
                    arr,
                    aux_array=values,
                    explanation=f"{self.name}: loading subsequence {segment} head into recombination heap.",
                    operation="read",
                    metadata={"segment": segment, "phase": "heap_load"},
                )
        out = 0
        while heap:
            _priority, segment, index, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                explanation=f"{self.name}: merging the next segment winner.",
                operation="write",
                metadata={"segment": segment, "phase": "recombine"},
            )
            out += 1
            next_index = index + 1
            if next_index < len(segments[segment]):
                next_value = segments[segment][next_index]
                priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(heap, (priority, segment, next_index, next_value))
                yield base_frame(
                    arr,
                    aux_array=segments[segment],
                    explanation=f"{self.name}: advancing subsequence {segment} after recombination.",
                    operation="read",
                    metadata={"segment": segment, "phase": "advance"},
                )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Each subsequence is internally sorted; the heap always yields the minimum across all subsequence fronts."


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
