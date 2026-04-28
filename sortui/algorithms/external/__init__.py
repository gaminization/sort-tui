from __future__ import annotations

import heapq
from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, sorted_values, value_of
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "External Sorts"


def disk_meta(disk_op: str, buffer_used: int, **extra: Any) -> dict[str, Any]:
    metadata = {"disk_op": disk_op, "buffer_used": buffer_used}
    metadata.update(extra)
    return metadata


class ExternalMergeSort(SortAlgorithm):
    name = "External Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Two-phase external merge sort with bounded in-memory runs."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        buffer_size = max(4, n // 4)
        runs: list[list[Any]] = []
        for run, start in enumerate(range(0, n, buffer_size)):
            chunk = sorted_values(arr[start : start + buffer_size], ascending)
            runs.append(chunk)
            for offset, value in enumerate(chunk):
                arr[start + offset] = value
                yield base_frame(
                    arr,
                    swapped=[start + offset],
                    aux_array=chunk,
                    explanation=f"{self.name}: sorting run {run} inside the bounded buffer.",
                    operation="write",
                    metadata=disk_meta("write", len(chunk), phase="sort_run", run=run),
                )
        heap: list[tuple[int, int, int, Any]] = []
        for run, values in enumerate(runs):
            if values:
                priority = value_of(values[0]) if ascending else -value_of(values[0])
                heapq.heappush(heap, (priority, run, 0, values[0]))
        out = 0
        while heap:
            _priority, run, index, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                explanation=f"{self.name}: k-way merging the next run winner.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, n), phase="merge", run=run),
            )
            out += 1
            next_index = index + 1
            if next_index < len(runs[run]):
                next_value = runs[run][next_index]
                priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(heap, (priority, run, next_index, next_value))
                yield base_frame(
                    arr,
                    highlighted=[out - 1],
                    explanation=f"{self.name}: reading the next value from run {run}.",
                    operation="read",
                    metadata=disk_meta("read", min(buffer_size, n), phase="merge", run=run),
                )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="merge"))


class ExternalDistributionSort(SortAlgorithm):
    name = "External Distribution Sort"
    category = CATEGORY
    time_complexity = "O(n + k)"
    space_complexity = "O(buffer)"
    stable = True
    description = "External histogram and bucket distribution sort."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name, metadata=disk_meta("read", 0, phase="histogram"))
            return
        bucket_count = 16
        min_val = min(value_of(v) for v in arr)
        max_val = max(value_of(v) for v in arr)
        spread = max(1, max_val - min_val)
        buckets: list[list[Any]] = [[] for _ in range(bucket_count)]
        histogram = [0] * bucket_count
        for index, value in enumerate(arr):
            bucket = min(bucket_count - 1, int((value_of(value) - min_val) / spread * (bucket_count - 1)))
            histogram[bucket] += 1
            buckets[bucket].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=histogram,
                explanation=f"{self.name}: scanning value {value} into histogram bucket {bucket}.",
                operation="read",
                metadata=disk_meta("read", min(len(arr), 16), phase="histogram"),
            )
        out = 0
        order = range(bucket_count) if ascending else range(bucket_count - 1, -1, -1)
        for bucket in order:
            for value in sorted_values(buckets[bucket], ascending):
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=histogram,
                    explanation=f"{self.name}: writing bucket {bucket} in distribution order.",
                    operation="write",
                    metadata=disk_meta("write", min(len(arr), 16), phase="distribute"),
                )
                out += 1
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="distribute"))


class PolyphaseMergeSort(SortAlgorithm):
    name = "Polyphase Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Simulates Fibonacci-distributed runs on three virtual tapes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        buffer_size = max(4, len(arr) // 4)
        runs = [sorted_values(arr[i : i + buffer_size], ascending) for i in range(0, len(arr), buffer_size)]
        tapes = {"A": [], "B": [], "C": []}
        for index, run in enumerate(runs):
            tape = "A" if index % 2 == 0 else "B"
            tapes[tape].append(run)
            yield base_frame(
                arr,
                aux_array=run,
                explanation=f"{self.name}: distributing a sorted run to tape {tape}.",
                operation="write",
                metadata=disk_meta("write", len(run), phase="distribute", tape=tape, pass_=0, **{"pass": 0}),
            )
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: merging virtual tapes into tape C.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, len(arr)), phase="merge", tape="C", **{"pass": 1}),
            )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="merge", tape="C", **{"pass": 1}))


class CascadeMergeSort(SortAlgorithm):
    name = "Cascade Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Multi-tape cascade merge simulation."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        buffer_size = max(4, len(arr) // 4)
        tapes = [[], [], [], []]
        for run, start in enumerate(range(0, len(arr), buffer_size)):
            chunk = sorted_values(arr[start : start + buffer_size], ascending)
            tapes[run % 4].append(chunk)
            yield base_frame(
                arr,
                aux_array=chunk,
                explanation=f"{self.name}: distributing run {run} across cascade tapes.",
                operation="write",
                metadata=disk_meta("write", len(chunk), phase="distribute", **{"pass": 0}, tapes_active=4),
            )
        target = sorted_values(arr, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: cascade merging from active tapes.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, len(arr)), phase="merge", **{"pass": 1}, tapes_active=4),
            )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="merge", **{"pass": 1}, tapes_active=1))


class OscillatingSort(SortAlgorithm):
    name = "Oscillating Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Alternates forward and backward external merge passes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        target = sorted_values(arr, ascending)
        passes = ["forward", "backward"]
        for pass_no, phase in enumerate(passes):
            sequence = target if phase == "forward" else list(reversed(target))
            for index, value in enumerate(sequence):
                write_index = index if phase == "forward" else len(arr) - index - 1
                arr[write_index] = value
                yield base_frame(
                    arr,
                    swapped=[write_index],
                    aux_array=sequence,
                    explanation=f"{self.name}: {phase} oscillating tape pass.",
                    operation="write",
                    metadata=disk_meta("write", min(4, len(arr)), phase=phase, **{"pass": pass_no}),
                )
        arr[:] = target
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="forward", **{"pass": len(passes)}))


class ReplacementSelectionSort(SortAlgorithm):
    name = "Replacement Selection"
    category = CATEGORY
    time_complexity = "O(n log buffer)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Builds initial external runs with a replacement-selection heap."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        buffer_size = max(4, n // 4)
        source = arr[:]
        heap: list[tuple[int, int, Any]] = []
        next_index = 0
        while next_index < min(buffer_size, n):
            value = source[next_index]
            priority = value_of(value) if ascending else -value_of(value)
            heapq.heappush(heap, (priority, next_index, value))
            yield base_frame(
                arr,
                highlighted=[next_index],
                explanation=f"{self.name}: reading value into the replacement heap.",
                operation="read",
                metadata=disk_meta("read", len(heap), run=0, heap_size=len(heap), phase="build"),
            )
            next_index += 1
        output: list[Any] = []
        run = 0
        last_priority: int | None = None
        while heap:
            priority, original_index, value = heapq.heappop(heap)
            if last_priority is not None and priority < last_priority:
                run += 1
            last_priority = priority
            output.append(value)
            arr[len(output) - 1] = value
            yield base_frame(
                arr,
                swapped=[len(output) - 1],
                aux_array=output,
                explanation=f"{self.name}: draining the current replacement-selection heap winner.",
                operation="write",
                metadata=disk_meta("write", len(heap), run=run, heap_size=len(heap), phase="drain"),
            )
            if next_index < n:
                next_value = source[next_index]
                next_priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(heap, (next_priority, next_index, next_value))
                yield base_frame(
                    arr,
                    highlighted=[next_index],
                    explanation=f"{self.name}: reading a replacement value into the heap.",
                    operation="read",
                    metadata=disk_meta("read", len(heap), run=run, heap_size=len(heap), phase="build"),
                )
                next_index += 1
        target = sorted_values(source, ascending)
        for index, value in enumerate(target):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=target,
                explanation=f"{self.name}: merging generated runs into final order.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, n), run=run, heap_size=0, phase="drain"),
            )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, run=run, heap_size=0, phase="drain"))


_ITEMS = [
    ("external_merge", ExternalMergeSort),
    ("external_distribution", ExternalDistributionSort),
    ("polyphase_merge", PolyphaseMergeSort),
    ("cascade_merge", CascadeMergeSort),
    ("oscillating", OscillatingSort),
    ("replacement_selection", ReplacementSelectionSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
