from __future__ import annotations

import heapq
import math
from typing import Any, Callable, Generator, Iterable, List

from sortui.algorithms.base import SortFrame


def value_of(value: Any) -> int:
    return int(value)


def in_order(left: Any, right: Any, ascending: bool = True) -> bool:
    return left <= right if ascending else left >= right


def out_of_order(left: Any, right: Any, ascending: bool = True) -> bool:
    return left > right if ascending else left < right


def strictly_before(left: Any, right: Any, ascending: bool = True) -> bool:
    return left < right if ascending else left > right


def sorted_values(values: Iterable[Any], ascending: bool = True) -> list[Any]:
    return sorted(values, key=value_of, reverse=not ascending)


def is_sorted(values: list[Any], ascending: bool = True) -> bool:
    return all(in_order(values[i], values[i + 1], ascending) for i in range(len(values) - 1))


def base_frame(
    arr: list[Any],
    *,
    highlighted: list[int] | None = None,
    swapped: list[int] | None = None,
    sorted_indices: list[int] | None = None,
    pivot_index: int | None = None,
    partition_bounds: tuple[int, int] | None = None,
    recursion_depth: int = 0,
    explanation: str,
    operation: str,
    aux_array: list[Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> SortFrame:
    return SortFrame(
        array=arr[:],
        highlighted=highlighted or [],
        swapped=swapped or [],
        sorted_indices=sorted_indices or [],
        pivot_index=pivot_index,
        partition_bounds=partition_bounds,
        recursion_depth=recursion_depth,
        explanation=explanation,
        operation=operation,
        aux_array=aux_array[:] if aux_array is not None else None,
        metadata=dict(metadata or {}),
    )


def done_frame(
    arr: list[Any],
    name: str,
    *,
    metadata: dict[str, Any] | None = None,
    sorted_indices: list[int] | None = None,
) -> SortFrame:
    n = len(arr)
    return base_frame(
        arr,
        sorted_indices=sorted_indices if sorted_indices is not None else list(range(n)),
        explanation=f"{name}: array is fully sorted.",
        operation="done",
        metadata=metadata,
    )


def write_sorted(
    arr: list[Any],
    ascending: bool,
    name: str,
    *,
    metadata: dict[str, Any] | None = None,
    aux_array: list[Any] | None = None,
    explanation: str | None = None,
) -> Generator[SortFrame, None, None]:
    target = sorted_values(arr[:], ascending)
    for index, value in enumerate(target):
        arr[index] = value
        yield base_frame(
            arr,
            swapped=[index],
            aux_array=aux_array if aux_array is not None else target,
            explanation=explanation or f"{name}: writing sorted value {value} to index {index}.",
            operation="write",
            metadata=metadata,
        )


def finish_with_sorted_writes(
    arr: list[Any],
    ascending: bool,
    name: str,
    *,
    metadata: dict[str, Any] | None = None,
    aux_array: list[Any] | None = None,
) -> Generator[SortFrame, None, None]:
    yield from write_sorted(arr, ascending, name, metadata=metadata, aux_array=aux_array)
    yield done_frame(arr, name, metadata=metadata)


def insertion_sort_range(
    arr: list[Any],
    start: int,
    end: int,
    ascending: bool,
    name: str,
    *,
    metadata: dict[str, Any] | Callable[[str, int], dict[str, Any]] | None = None,
    explanation_prefix: str = "",
    sorted_indices: list[int] | None = None,
) -> Generator[SortFrame, None, None]:
    def meta(operation: str, index: int) -> dict[str, Any]:
        if callable(metadata):
            return metadata(operation, index)
        return dict(metadata or {})

    for i in range(start + 1, end):
        key = arr[i]
        yield base_frame(
            arr,
            highlighted=[i],
            sorted_indices=sorted_indices or [],
            explanation=f"{name}: {explanation_prefix}reading index {i} as the insertion key.",
            operation="read",
            metadata=meta("read", i),
        )
        j = i - 1
        while j >= start:
            yield base_frame(
                arr,
                highlighted=[j, j + 1],
                sorted_indices=sorted_indices or [],
                explanation=f"{name}: {explanation_prefix}comparing index {j} with the insertion key.",
                operation="compare",
                metadata=meta("compare", j),
            )
            if not out_of_order(arr[j], key, ascending):
                break
            arr[j + 1] = arr[j]
            yield base_frame(
                arr,
                swapped=[j, j + 1],
                sorted_indices=sorted_indices or [],
                explanation=f"{name}: {explanation_prefix}shifting index {j} one step right.",
                operation="write",
                metadata=meta("write", j),
            )
            j -= 1
        arr[j + 1] = key
        yield base_frame(
            arr,
            swapped=[j + 1],
            sorted_indices=sorted_indices or [],
            explanation=f"{name}: {explanation_prefix}placing the insertion key at index {j + 1}.",
            operation="write",
            metadata=meta("write", j + 1),
        )


def merge_runs(
    arr: list[Any],
    left: int,
    mid: int,
    right: int,
    ascending: bool,
    name: str,
    *,
    aux: list[Any] | None = None,
    metadata: dict[str, Any] | Callable[[str, int], dict[str, Any]] | None = None,
    recursion_depth: int = 0,
) -> Generator[SortFrame, None, None]:
    def meta(operation: str, index: int) -> dict[str, Any]:
        if callable(metadata):
            return metadata(operation, index)
        return dict(metadata or {})

    left_run = arr[left:mid]
    right_run = arr[mid:right]
    i = j = 0
    k = left
    local_aux: list[Any] = []
    while i < len(left_run) and j < len(right_run):
        yield base_frame(
            arr,
            highlighted=[left + i, mid + j],
            partition_bounds=(left, right - 1),
            recursion_depth=recursion_depth,
            aux_array=aux if aux is not None else local_aux,
            explanation=f"{name}: comparing the heads of two merge runs.",
            operation="compare",
            metadata=meta("compare", k),
        )
        if in_order(left_run[i], right_run[j], ascending):
            chosen = left_run[i]
            i += 1
        else:
            chosen = right_run[j]
            j += 1
        local_aux.append(chosen)
        arr[k] = chosen
        if aux is not None and k < len(aux):
            aux[k] = chosen
        yield base_frame(
            arr,
            swapped=[k],
            partition_bounds=(left, right - 1),
            recursion_depth=recursion_depth,
            aux_array=aux if aux is not None else local_aux,
            explanation=f"{name}: writing the next merged value to index {k}.",
            operation="write",
            metadata=meta("write", k),
        )
        k += 1
    while i < len(left_run):
        arr[k] = left_run[i]
        if aux is not None and k < len(aux):
            aux[k] = left_run[i]
        local_aux.append(left_run[i])
        yield base_frame(
            arr,
            swapped=[k],
            partition_bounds=(left, right - 1),
            recursion_depth=recursion_depth,
            aux_array=aux if aux is not None else local_aux,
            explanation=f"{name}: copying the remaining left run value to index {k}.",
            operation="write",
            metadata=meta("write", k),
        )
        i += 1
        k += 1
    while j < len(right_run):
        arr[k] = right_run[j]
        if aux is not None and k < len(aux):
            aux[k] = right_run[j]
        local_aux.append(right_run[j])
        yield base_frame(
            arr,
            swapped=[k],
            partition_bounds=(left, right - 1),
            recursion_depth=recursion_depth,
            aux_array=aux if aux is not None else local_aux,
            explanation=f"{name}: copying the remaining right run value to index {k}.",
            operation="write",
            metadata=meta("write", k),
        )
        j += 1
        k += 1


def bottom_up_merge_sort(
    arr: list[Any],
    ascending: bool,
    name: str,
    *,
    metadata: dict[str, Any] | Callable[[str, int], dict[str, Any]] | None = None,
) -> Generator[SortFrame, None, None]:
    n = len(arr)
    aux = arr[:]
    width = 1
    while width < n:
        for left in range(0, n, 2 * width):
            mid = min(left + width, n)
            right = min(left + 2 * width, n)
            if mid < right:
                yield from merge_runs(
                    arr,
                    left,
                    mid,
                    right,
                    ascending,
                    name,
                    aux=aux,
                    metadata=metadata,
                )
        width *= 2


def heap_sort_range(
    arr: list[Any],
    start: int,
    end: int,
    ascending: bool,
    name: str,
    *,
    metadata: dict[str, Any] | Callable[[str, int], dict[str, Any]] | None = None,
) -> Generator[SortFrame, None, None]:
    def meta(operation: str, index: int) -> dict[str, Any]:
        if callable(metadata):
            return metadata(operation, index)
        return dict(metadata or {})

    def better(a: Any, b: Any) -> bool:
        return a > b if ascending else a < b

    def sift_down(root: int, last: int) -> Generator[SortFrame, None, None]:
        while True:
            child = start + 2 * (root - start) + 1
            if child > last:
                break
            swap_idx = root
            yield base_frame(
                arr,
                highlighted=[root, child],
                explanation=f"{name}: comparing heap parent with child.",
                operation="compare",
                metadata=meta("compare", root),
            )
            if better(arr[child], arr[swap_idx]):
                swap_idx = child
            if child + 1 <= last:
                yield base_frame(
                    arr,
                    highlighted=[swap_idx, child + 1],
                    explanation=f"{name}: comparing heap candidate with the right child.",
                    operation="compare",
                    metadata=meta("compare", child + 1),
                )
                if better(arr[child + 1], arr[swap_idx]):
                    swap_idx = child + 1
            if swap_idx == root:
                return
            arr[root], arr[swap_idx] = arr[swap_idx], arr[root]
            yield base_frame(
                arr,
                swapped=[root, swap_idx],
                explanation=f"{name}: swapping to restore heap order.",
                operation="swap",
                metadata=meta("swap", root),
            )
            root = swap_idx

    count = end - start
    for offset in range(count // 2 - 1, -1, -1):
        yield from sift_down(start + offset, end - 1)
    for last in range(end - 1, start, -1):
        arr[start], arr[last] = arr[last], arr[start]
        yield base_frame(
            arr,
            swapped=[start, last],
            sorted_indices=list(range(last, end)) if ascending else list(range(start, start + (end - last))),
            explanation=f"{name}: moving the heap root to position {last}.",
            operation="swap",
            metadata=meta("swap", last),
        )
        yield from sift_down(start, last - 1)


def lomuto_quicksort(
    arr: list[Any],
    lo: int,
    hi: int,
    ascending: bool,
    name: str,
    *,
    depth: int = 0,
    metadata: dict[str, Any] | Callable[[str, int], dict[str, Any]] | None = None,
) -> Generator[SortFrame, None, None]:
    def meta(operation: str, index: int) -> dict[str, Any]:
        if callable(metadata):
            return metadata(operation, index)
        return dict(metadata or {})

    def partition(left: int, right: int, rec_depth: int) -> Generator[SortFrame, None, int]:
        pivot = arr[right]
        i = left
        yield base_frame(
            arr,
            highlighted=[right],
            pivot_index=right,
            partition_bounds=(left, right),
            recursion_depth=rec_depth,
            explanation=f"{name}: reading the last element as the Lomuto pivot.",
            operation="read",
            metadata=meta("read", right),
        )
        for j in range(left, right):
            yield base_frame(
                arr,
                highlighted=[j, right],
                pivot_index=right,
                partition_bounds=(left, right),
                recursion_depth=rec_depth,
                explanation=f"{name}: comparing index {j} with the pivot.",
                operation="compare",
                metadata=meta("compare", j),
            )
            if in_order(arr[j], pivot, ascending):
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        pivot_index=right,
                        partition_bounds=(left, right),
                        recursion_depth=rec_depth,
                        explanation=f"{name}: moving index {j} into the lower partition.",
                        operation="swap",
                        metadata=meta("swap", i),
                    )
                i += 1
        arr[i], arr[right] = arr[right], arr[i]
        yield base_frame(
            arr,
            swapped=[i, right],
            pivot_index=i,
            partition_bounds=(left, right),
            recursion_depth=rec_depth,
            explanation=f"{name}: placing the pivot at index {i}.",
            operation="swap",
            metadata=meta("swap", i),
        )
        return i

    if lo >= hi:
        return
    pivot_index = yield from partition(lo, hi, depth)
    yield from lomuto_quicksort(
        arr, lo, pivot_index - 1, ascending, name, depth=depth + 1, metadata=metadata
    )
    yield from lomuto_quicksort(
        arr, pivot_index + 1, hi, ascending, name, depth=depth + 1, metadata=metadata
    )


def odd_even_network(
    arr: list[Any],
    ascending: bool,
    name: str,
    *,
    passes: int | None = None,
    metadata_for: Callable[[int, int, str], dict[str, Any]] | None = None,
) -> Generator[SortFrame, None, None]:
    n = len(arr)
    total = passes if passes is not None else max(1, n)
    for pass_no in range(total):
        swapped_any = False
        for phase_start, phase_name in ((0, "even"), (1, "odd")):
            for i in range(phase_start, n - 1, 2):
                metadata = metadata_for(pass_no, i, phase_name) if metadata_for else {}
                yield base_frame(
                    arr,
                    highlighted=[i, i + 1],
                    explanation=f"{name}: {phase_name} network compare between {i} and {i + 1}.",
                    operation="compare",
                    metadata=metadata,
                )
                if out_of_order(arr[i], arr[i + 1], ascending):
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped_any = True
                    yield base_frame(
                        arr,
                        swapped=[i, i + 1],
                        explanation=f"{name}: exchanging adjacent network wires {i} and {i + 1}.",
                        operation="swap",
                        metadata=metadata,
                    )
        if not swapped_any:
            break


def split_threads(n: int, count: int = 4, active: int | None = None) -> list[dict[str, Any]]:
    threads: list[dict[str, Any]] = []
    chunk = max(1, math.ceil(n / max(1, count)))
    for thread_id in range(count):
        start = min(n, thread_id * chunk)
        end = min(n, start + chunk)
        status = "working" if active is None or active == thread_id else "waiting"
        if start >= n:
            status = "done"
        threads.append({"id": thread_id, "range": [start, end], "status": status})
    return threads


def heap_items(values: Iterable[Any], ascending: bool = True) -> list[tuple[int, int, Any]]:
    items = []
    for index, value in enumerate(values):
        priority = value_of(value) if ascending else -value_of(value)
        items.append((priority, index, value))
    heapq.heapify(items)
    return items
