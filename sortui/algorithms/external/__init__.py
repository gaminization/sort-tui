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


def stable_external_sorted(values: list[Any], ascending: bool) -> list[Any]:
    if ascending:
        return sorted(values, key=lambda value: (value_of(value), getattr(value, "original_index", 0)))
    return sorted(values, key=lambda value: (-value_of(value), getattr(value, "original_index", 0)))


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

    def get_invariant(self) -> str:
        return "Each merge pass reduces the number of sorted runs by half; run length doubles after each complete pass."


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
        source = arr[:]
        bucket_count = 16
        min_val = min(value_of(v) for v in source)
        max_val = max(value_of(v) for v in source)
        spread = max(1, max_val - min_val)
        buckets: list[list[Any]] = [[] for _ in range(bucket_count)]
        histogram = [0] * bucket_count
        for index, value in enumerate(source):
            bucket = min(bucket_count - 1, int((value_of(value) - min_val) / spread * (bucket_count - 1)))
            histogram[bucket] += 1
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=histogram,
                explanation=f"{self.name}: scanning value {value} into histogram bucket {bucket}.",
                operation="read",
                metadata=disk_meta("read", min(len(arr), 16), phase="histogram", bucket=bucket),
            )

        for index, value in enumerate(source):
            bucket = min(bucket_count - 1, int((value_of(value) - min_val) / spread * (bucket_count - 1)))
            buckets[bucket].append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[item for bucket_values in buckets for item in bucket_values],
                explanation=f"{self.name}: writing value {value} to external bucket run {bucket}.",
                operation="write",
                metadata=disk_meta("write", len(buckets[bucket]), phase="distribute", bucket=bucket),
            )

        for bucket, values in enumerate(buckets):
            for i in range(1, len(values)):
                key = values[i]
                yield base_frame(
                    arr,
                    aux_array=values[:],
                    explanation=f"{self.name}: reading external bucket {bucket} into memory for run sorting.",
                    operation="read",
                    metadata=disk_meta("read", len(values), phase="sort_bucket", bucket=bucket),
                )
                j = i - 1
                while j >= 0:
                    yield base_frame(
                        arr,
                        aux_array=values[:],
                        explanation=f"{self.name}: comparing inside external bucket {bucket}.",
                        operation="compare",
                        metadata=disk_meta("read", len(values), phase="sort_bucket", bucket=bucket),
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
                        explanation=f"{self.name}: writing a shifted bucket-run value.",
                        operation="write",
                        metadata=disk_meta("write", len(values), phase="sort_bucket", bucket=bucket),
                    )
                    j -= 1
                values[j + 1] = key
                yield base_frame(
                    arr,
                    aux_array=values[:],
                    explanation=f"{self.name}: writing key into sorted bucket run {bucket}.",
                    operation="write",
                    metadata=disk_meta("write", len(values), phase="sort_bucket", bucket=bucket),
                )

        heap: list[tuple[int, int, int, Any]] = []
        order = range(bucket_count) if ascending else range(bucket_count - 1, -1, -1)
        for order_index, bucket in enumerate(order):
            if buckets[bucket]:
                value = buckets[bucket][0]
                heapq.heappush(heap, (order_index, 0, bucket, value))
                yield base_frame(
                    arr,
                    aux_array=buckets[bucket],
                    explanation=f"{self.name}: loading bucket {bucket} head for external merge.",
                    operation="read",
                    metadata=disk_meta("read", len(buckets[bucket]), phase="merge_load", bucket=bucket),
                )

        out = 0
        while heap:
            _order_index, index, bucket, value = heapq.heappop(heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                aux_array=buckets[bucket],
                explanation=f"{self.name}: merging bucket {bucket} winner to output.",
                operation="write",
                metadata=disk_meta("write", min(len(arr), 16), phase="merge", bucket=bucket),
            )
            out += 1
            next_index = index + 1
            if next_index < len(buckets[bucket]):
                next_value = buckets[bucket][next_index]
                order_index = list(order).index(bucket)
                heapq.heappush(heap, (order_index, next_index, bucket, next_value))
                yield base_frame(
                    arr,
                    aux_array=buckets[bucket],
                    explanation=f"{self.name}: reading next value from bucket {bucket}.",
                    operation="read",
                    metadata=disk_meta("read", len(buckets[bucket]), phase="merge", bucket=bucket),
                )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="distribute"))

    def get_invariant(self) -> str:
        return "Each distribution pass assigns elements to buckets by value range; buckets are merged in sorted order."


class PolyphaseMergeSort(SortAlgorithm):
    name = "Polyphase Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Simulates Fibonacci-distributed runs on three virtual tapes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        buffer_size = max(4, n // 5)
        runs = [stable_external_sorted(arr[i : i + buffer_size], ascending) for i in range(0, n, buffer_size)]
        tapes: dict[str, list[list[Any]]] = {"A": [], "B": [], "C": []}
        fib_slots = ["A", "B", "A", "C", "B", "A", "C", "B"]
        for index, run in enumerate(runs):
            tape = fib_slots[index % len(fib_slots)]
            tapes[tape].append(run)
            for offset, value in enumerate(run):
                arr[min(n - 1, index * buffer_size + offset)] = value
                yield base_frame(
                    arr,
                    swapped=[min(n - 1, index * buffer_size + offset)],
                    aux_array=run,
                    explanation=f"{self.name}: Fibonacci-distributing sorted run {index} to tape {tape}.",
                    operation="write",
                    metadata=disk_meta("write", len(run), phase="distribute", tape=tape, **{"pass": 0}),
                )

        pass_no = 1
        while sum(len(run_list) for run_list in tapes.values()) > 1:
            nonempty = [(sum(len(run) for run in run_list), tape) for tape, run_list in tapes.items() if run_list]
            nonempty.sort()
            _size_a, tape_a = nonempty[0]
            _size_b, tape_b = nonempty[1] if len(nonempty) > 1 else nonempty[0]
            target_tape = next(tape for tape in tapes if tape not in {tape_a, tape_b})
            run_a = tapes[tape_a].pop(0)
            run_b = tapes[tape_b].pop(0) if tapes[tape_b] else []
            merged = stable_external_sorted(run_a + run_b, ascending)
            tapes[target_tape].append(merged)
            for index, value in enumerate(merged):
                arr[index] = value
                yield base_frame(
                    arr,
                    swapped=[index],
                    aux_array=merged,
                    explanation=(
                        f"{self.name}: absorbing shortest tape {tape_a} with {tape_b} "
                        f"into tape {target_tape}."
                    ),
                    operation="write",
                    metadata=disk_meta(
                        "write", min(buffer_size, len(merged)), phase="merge", tape=target_tape, **{"pass": pass_no}
                    ),
                )
            pass_no += 1

        final_run = next((run_list[0] for run_list in tapes.values() if run_list), [])
        for index, value in enumerate(final_run):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=final_run,
                explanation=f"{self.name}: writing final polyphase tape output.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, n), phase="final", tape="C", **{"pass": pass_no}),
            )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="merge", tape="C", **{"pass": pass_no}))

    def get_invariant(self) -> str:
        return "Runs are distributed across tapes in Fibonacci proportions; each merge phase absorbs the shortest tape."


class CascadeMergeSort(SortAlgorithm):
    name = "Cascade Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Multi-tape cascade merge simulation."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        buffer_size = max(4, n // 6)
        tapes: list[list[list[Any]]] = [[], [], [], []]
        fibonacci_pattern = [3, 2, 1, 0, 3, 1, 2, 0]
        for run, start in enumerate(range(0, n, buffer_size)):
            chunk = stable_external_sorted(arr[start : start + buffer_size], ascending)
            tape_index = fibonacci_pattern[run % len(fibonacci_pattern)]
            tapes[tape_index].append(chunk)
            for offset, value in enumerate(chunk):
                arr[start + offset] = value
                yield base_frame(
                    arr,
                    swapped=[start + offset],
                    aux_array=chunk,
                    explanation=f"{self.name}: distributing run {run} to high-order cascade tape {tape_index}.",
                    operation="write",
                    metadata=disk_meta("write", len(chunk), phase="distribute", **{"pass": 0}, tapes_active=4),
                )

        pass_no = 1
        while sum(len(tape) for tape in tapes) > 1:
            active_indices = [index for index, tape in enumerate(tapes) if tape]
            high_to_low = sorted(active_indices, reverse=True)
            carry: list[Any] = []
            for tape_index in high_to_low:
                run = tapes[tape_index].pop(0)  # type: ignore[assignment]
                carry = stable_external_sorted(carry + run, ascending)  # type: ignore[operator, assignment]
                for index, value in enumerate(carry):
                    arr[index] = value
                    yield base_frame(
                        arr,
                        swapped=[index],
                        aux_array=carry,
                        explanation=f"{self.name}: cascading merge wave through tape {tape_index}.",
                        operation="write",
                        metadata=disk_meta(
                            "write",
                            min(buffer_size, len(carry)),
                            phase="merge",
                            **{"pass": pass_no},
                            tapes_active=len(active_indices),
                        ),
                    )
            tapes[0].append(carry)
            pass_no += 1

        final = next((tape[0] for tape in tapes if tape), [])
        for index, value in enumerate(final):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=final,
                explanation=f"{self.name}: writing final cascade tape output.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, n), phase="final", **{"pass": pass_no}, tapes_active=1),
            )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="merge", **{"pass": pass_no}, tapes_active=1))

    def get_invariant(self) -> str:
        return "Initial runs are distributed in cascading proportions; merge waves propagate from the highest-order tape down."


class OscillatingSort(SortAlgorithm):
    name = "Oscillating Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(buffer)"
    stable = True
    description = "Alternates forward and backward external merge passes."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        width = 1
        pass_no = 0
        buffer_size = max(4, n // 4)
        while width < n:
            phase = "forward" if pass_no % 2 == 0 else "backward"
            starts = list(range(0, n, 2 * width))
            if phase == "backward":
                starts.reverse()
            for left in starts:
                mid = min(left + width, n)
                right = min(left + 2 * width, n)
                if mid >= right:
                    continue
                left_run = arr[left:mid]
                right_run = arr[mid:right]
                i = j = 0
                merged: list[Any] = []
                while i < len(left_run) and j < len(right_run):
                    yield base_frame(
                        arr,
                        highlighted=[left + i, mid + j],
                        partition_bounds=(left, right - 1),
                        aux_array=merged,
                        explanation=f"{self.name}: {phase} pass compares run heads.",
                        operation="compare",
                        metadata=disk_meta("read", min(buffer_size, right - left), phase=phase, **{"pass": pass_no}),
                    )
                    if (
                        value_of(left_run[i]) <= value_of(right_run[j])
                        if ascending
                        else value_of(left_run[i]) >= value_of(right_run[j])
                    ):
                        merged.append(left_run[i])
                        i += 1
                    else:
                        merged.append(right_run[j])
                        j += 1
                while i < len(left_run):
                    merged.append(left_run[i])
                    i += 1
                    yield base_frame(
                        arr,
                        partition_bounds=(left, right - 1),
                        aux_array=merged,
                        explanation=f"{self.name}: {phase} pass reads a remaining left-run value.",
                        operation="read",
                        metadata=disk_meta("read", min(buffer_size, right - left), phase=phase, **{"pass": pass_no}),
                    )
                while j < len(right_run):
                    merged.append(right_run[j])
                    j += 1
                    yield base_frame(
                        arr,
                        partition_bounds=(left, right - 1),
                        aux_array=merged,
                        explanation=f"{self.name}: {phase} pass reads a remaining right-run value.",
                        operation="read",
                        metadata=disk_meta("read", min(buffer_size, right - left), phase=phase, **{"pass": pass_no}),
                    )
                write_positions = range(left, right)
                if phase == "backward":
                    write_positions = reversed(list(write_positions))  # type: ignore[assignment]
                    merged_to_write = list(reversed(merged))
                else:
                    merged_to_write = merged
                for write_index, value in zip(write_positions, merged_to_write):
                    arr[write_index] = value
                    yield base_frame(
                        arr,
                        swapped=[write_index],
                        partition_bounds=(left, right - 1),
                        aux_array=merged,
                        explanation=f"{self.name}: {phase} pass writes merged tape value.",
                        operation="write",
                        metadata=disk_meta("write", min(buffer_size, right - left), phase=phase, **{"pass": pass_no}),
                    )
            width *= 2
            pass_no += 1
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, phase="forward", **{"pass": pass_no}))

    def get_invariant(self) -> str:
        return "Merge direction alternates each pass; runs from opposing directions meet and merge at the center tape."


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
        runs: list[list[Any]] = []
        current_run: list[Any] = []
        frozen: list[tuple[int, int, Any]] = []
        run = 0
        last_priority: int | None = None
        while heap or frozen:
            if not heap:
                runs.append(current_run)
                yield base_frame(
                    arr,
                    aux_array=current_run,
                    explanation=f"{self.name}: closing run {run} and thawing frozen records.",
                    operation="write",
                    metadata=disk_meta("write", len(current_run), run=run, heap_size=0, phase="close_run"),
                )
                run += 1
                heap = frozen
                heapq.heapify(heap)
                frozen = []
                current_run = []
                last_priority = None
                continue
            priority, original_index, value = heapq.heappop(heap)
            last_priority = priority
            current_run.append(value)
            arr[min(n - 1, sum(len(run_values) for run_values in runs) + len(current_run) - 1)] = value
            yield base_frame(
                arr,
                swapped=[min(n - 1, sum(len(run_values) for run_values in runs) + len(current_run) - 1)],
                aux_array=current_run,
                explanation=f"{self.name}: draining the current replacement-selection heap winner.",
                operation="write",
                metadata=disk_meta("write", len(heap), run=run, heap_size=len(heap), phase="drain"),
            )
            if next_index < n:
                next_value = source[next_index]
                next_priority = value_of(next_value) if ascending else -value_of(next_value)
                if last_priority is None or next_priority >= last_priority:
                    heapq.heappush(heap, (next_priority, next_index, next_value))
                    phase = "replace_current"
                    heap_size = len(heap)
                else:
                    frozen.append((next_priority, next_index, next_value))
                    phase = "freeze_next_run"
                    heap_size = len(frozen)
                yield base_frame(
                    arr,
                    highlighted=[next_index],
                    aux_array=[item[2] for item in heap] + [item[2] for item in frozen],
                    explanation=(
                        f"{self.name}: replacement value {next_value} "
                        f"{'stays in this run' if phase == 'replace_current' else 'freezes for the next run'}."
                    ),
                    operation="read",
                    metadata=disk_meta("read", heap_size, run=run, heap_size=heap_size, phase=phase),
                )
                next_index += 1
        if current_run:
            runs.append(current_run)
            yield base_frame(
                arr,
                aux_array=current_run,
                explanation=f"{self.name}: closing final generated run {run}.",
                operation="write",
                metadata=disk_meta("write", len(current_run), run=run, heap_size=0, phase="close_run"),
            )

        merge_heap: list[tuple[int, int, int, int, Any]] = []
        for run_index, run_values in enumerate(runs):
            if run_values:
                value = run_values[0]
                priority = value_of(value) if ascending else -value_of(value)
                heapq.heappush(
                    merge_heap,
                    (priority, getattr(value, "original_index", 0), run_index, 0, value),
                )
                yield base_frame(
                    arr,
                    aux_array=run_values,
                    explanation=f"{self.name}: loading run {run_index} head into merge heap.",
                    operation="read",
                    metadata=disk_meta("read", len(merge_heap), run=run_index, heap_size=len(merge_heap), phase="merge_load"),
                )
        out = 0
        while merge_heap:
            _priority, _original_index, run_index, value_index, value = heapq.heappop(merge_heap)
            arr[out] = value
            yield base_frame(
                arr,
                swapped=[out],
                aux_array=[item[4] for item in merge_heap],
                explanation=f"{self.name}: merging generated replacement-selection runs.",
                operation="write",
                metadata=disk_meta("write", min(buffer_size, n), run=run_index, heap_size=len(merge_heap), phase="merge"),
            )
            out += 1
            next_value_index = value_index + 1
            if next_value_index < len(runs[run_index]):
                next_value = runs[run_index][next_value_index]
                priority = value_of(next_value) if ascending else -value_of(next_value)
                heapq.heappush(
                    merge_heap,
                    (priority, getattr(next_value, "original_index", 0), run_index, next_value_index, next_value),
                )
                yield base_frame(
                    arr,
                    aux_array=runs[run_index],
                    explanation=f"{self.name}: advancing run {run_index} during final merge.",
                    operation="read",
                    metadata=disk_meta("read", len(merge_heap), run=run_index, heap_size=len(merge_heap), phase="merge_advance"),
                )
        yield done_frame(arr, self.name, metadata=disk_meta("write", 0, run=len(runs), heap_size=0, phase="merge"))

    def get_invariant(self) -> str:
        return "The heap always contains the candidates for the current run; out-of-run values are frozen for the next run."


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
