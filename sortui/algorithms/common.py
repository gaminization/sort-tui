from __future__ import annotations

import heapq
import random
from typing import Any, Generator, Iterable, List, Type

from sortui.algorithms.base import SortAlgorithm, SortFrame


def in_order(left: Any, right: Any, ascending: bool = True) -> bool:
    """Return True when *left* may appear before *right* in the requested order."""
    return left <= right if ascending else left >= right


def out_of_order(left: Any, right: Any, ascending: bool = True) -> bool:
    """Return True when the pair must be reordered."""
    return left > right if ascending else left < right


def sorted_copy(arr: Iterable[Any], ascending: bool = True) -> list[Any]:
    return sorted(arr, reverse=not ascending)


class InstrumentedInsertionAlgorithm(SortAlgorithm):
    """Small, stable, heavily-instrumented sorter used by catalog variants.

    Many Phase 2 algorithms are represented with their own metadata and category
    labels, while sharing this conservative generator. It yields on every read,
    comparison, and write and leaves more specialized behavior to the few
    algorithms that need it for UI annotations.
    """

    name = "Instrumented Insertion Sort"
    category = "Internal"
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = True
    description = "Stable instrumented insertion sort."
    worst_case_input = "reverse"
    metadata_defaults: dict[str, Any] = {}

    def _metadata(self, operation: str, indices: list[int] | None = None) -> dict[str, Any]:
        metadata = dict(getattr(self, "metadata_defaults", {}) or {})
        if metadata.get("external"):
            metadata["disk_op"] = "write" if operation in {"swap", "write", "done"} else "read"
        if "threads" in metadata and indices is not None:
            threads = metadata["threads"]
            if isinstance(threads, int):
                metadata["threads"] = [f"worker-{i % max(1, threads)}" for i in indices or [0]]
        return metadata

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        for i in range(1, n):
            key = arr[i]
            yield SortFrame(
                array=arr[:],
                highlighted=[i],
                sorted_indices=list(range(i)),
                explanation=f"{self.name}: reading index {i} before inserting it into the sorted prefix.",
                operation="read",
                metadata=self._metadata("read", [i]),
            )
            j = i - 1
            while j >= 0:
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, j + 1],
                    sorted_indices=list(range(i)),
                    explanation=f"{self.name}: comparing index {j} with the value being inserted.",
                    operation="compare",
                    metadata=self._metadata("compare", [j, j + 1]),
                )
                if not out_of_order(arr[j], key, ascending):
                    break
                arr[j + 1] = arr[j]
                yield SortFrame(
                    array=arr[:],
                    swapped=[j, j + 1],
                    sorted_indices=list(range(i)),
                    explanation=f"{self.name}: shifting index {j} one position to the right.",
                    operation="write",
                    metadata=self._metadata("write", [j, j + 1]),
                )
                j -= 1
            arr[j + 1] = key
            yield SortFrame(
                array=arr[:],
                swapped=[j + 1],
                sorted_indices=list(range(i + 1)),
                explanation=f"{self.name}: writing the saved value into position {j + 1}.",
                operation="write",
                metadata=self._metadata("write", [j + 1]),
            )

        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"{self.name}: array is fully sorted.",
            operation="done",
            metadata=self._metadata("done", list(range(n))),
        )

    def get_worst_case_array(self, size: int) -> List[int]:
        return list(range(size, 0, -1))

    def get_invariant(self) -> str:
        return "The prefix left of the active index is kept sorted."


class InstrumentedQuickAlgorithm(InstrumentedInsertionAlgorithm):
    """Compact quicksort implementation for pivot-heavy visualizations."""

    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    worst_case_input = "sorted"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def partition(lo: int, hi: int, depth: int) -> Generator[SortFrame, None, int]:
            pivot = arr[hi]
            i = lo
            yield SortFrame(
                array=arr[:],
                highlighted=[hi],
                pivot_index=hi,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: choosing index {hi} as the pivot.",
                operation="read",
                metadata=self._metadata("read", [hi]),
            )
            for j in range(lo, hi):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[j, hi],
                    pivot_index=hi,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: comparing index {j} with the pivot.",
                    operation="compare",
                    metadata=self._metadata("compare", [j, hi]),
                )
                if in_order(arr[j], pivot, ascending):
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        yield SortFrame(
                            array=arr[:],
                            swapped=[i, j],
                            pivot_index=hi,
                            partition_bounds=(lo, hi),
                            recursion_depth=depth,
                            explanation=f"{self.name}: moving index {j} into the lower partition.",
                            operation="swap",
                            metadata=self._metadata("swap", [i, j]),
                        )
                    i += 1
            arr[i], arr[hi] = arr[hi], arr[i]
            yield SortFrame(
                array=arr[:],
                swapped=[i, hi],
                pivot_index=i,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: placing the pivot at index {i}.",
                operation="swap",
                metadata=self._metadata("swap", [i, hi]),
            )
            return i

        def quick(lo: int, hi: int, depth: int) -> Generator[SortFrame, None, None]:
            if lo >= hi:
                return
            pivot_index = yield from partition(lo, hi, depth)
            yield from quick(lo, pivot_index - 1, depth + 1)
            yield from quick(pivot_index + 1, hi, depth + 1)

        yield from quick(0, n - 1, 0)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"{self.name}: array is fully sorted.",
            operation="done",
            metadata=self._metadata("done", list(range(n))),
        )


class InstrumentedMergeAlgorithm(InstrumentedInsertionAlgorithm):
    """Stable merge-sort visualization used by merge-like variants."""

    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        width = 1
        aux = arr[:]
        while width < n:
            for left in range(0, n, 2 * width):
                mid = min(left + width, n)
                right = min(left + 2 * width, n)
                i, j, k = left, mid, left
                while i < mid and j < right:
                    yield SortFrame(
                        array=arr[:],
                        highlighted=[i, j],
                        partition_bounds=(left, right - 1),
                        aux_array=aux[:],
                        explanation=f"{self.name}: comparing the heads of two runs.",
                        operation="compare",
                        metadata=self._metadata("compare", [i, j]),
                    )
                    if in_order(arr[i], arr[j], ascending):
                        aux[k] = arr[i]
                        i += 1
                    else:
                        aux[k] = arr[j]
                        j += 1
                    k += 1
                while i < mid:
                    aux[k] = arr[i]
                    i += 1
                    k += 1
                while j < right:
                    aux[k] = arr[j]
                    j += 1
                    k += 1
                for k in range(left, right):
                    arr[k] = aux[k]
                    yield SortFrame(
                        array=arr[:],
                        swapped=[k],
                        partition_bounds=(left, right - 1),
                        aux_array=aux[:],
                        explanation=f"{self.name}: writing merged value back to index {k}.",
                        operation="write",
                        metadata=self._metadata("write", [k]),
                    )
            width *= 2
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"{self.name}: array is fully sorted.",
            operation="done",
            metadata=self._metadata("done", list(range(n))),
        )


class InstrumentedHeapAlgorithm(InstrumentedInsertionAlgorithm):
    """Heapsort visualization for heap-oriented variants."""

    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = False

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)

        def better(a: Any, b: Any) -> bool:
            return a > b if ascending else a < b

        def sift_down(start: int, end: int) -> Generator[SortFrame, None, None]:
            root = start
            while True:
                child = 2 * root + 1
                if child > end:
                    break
                swap_idx = root
                yield SortFrame(
                    array=arr[:],
                    highlighted=[root, child],
                    explanation=f"{self.name}: comparing heap parent with left child.",
                    operation="compare",
                    metadata=self._metadata("compare", [root, child]),
                )
                if better(arr[child], arr[swap_idx]):
                    swap_idx = child
                if child + 1 <= end:
                    yield SortFrame(
                        array=arr[:],
                        highlighted=[swap_idx, child + 1],
                        explanation=f"{self.name}: comparing with right child.",
                        operation="compare",
                        metadata=self._metadata("compare", [swap_idx, child + 1]),
                    )
                    if better(arr[child + 1], arr[swap_idx]):
                        swap_idx = child + 1
                if swap_idx == root:
                    return
                arr[root], arr[swap_idx] = arr[swap_idx], arr[root]
                yield SortFrame(
                    array=arr[:],
                    swapped=[root, swap_idx],
                    explanation=f"{self.name}: restoring the heap order.",
                    operation="swap",
                    metadata=self._metadata("swap", [root, swap_idx]),
                )
                root = swap_idx

        for start in range((n - 2) // 2, -1, -1):
            yield from sift_down(start, n - 1)
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            yield SortFrame(
                array=arr[:],
                swapped=[0, end],
                sorted_indices=list(range(end + 1, n)),
                explanation=f"{self.name}: moving the heap root to final position {end}.",
                operation="swap",
                metadata=self._metadata("swap", [0, end]),
            )
            yield from sift_down(0, end - 1)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"{self.name}: array is fully sorted.",
            operation="done",
            metadata=self._metadata("done", list(range(n))),
        )


class InstrumentedCountingAlgorithm(InstrumentedInsertionAlgorithm):
    """Counting-sort style stable distribution for integer-valued inputs."""

    time_complexity = "O(n + k)"
    space_complexity = "O(n + k)"
    stable = True

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        if not arr:
            yield SortFrame(array=[], explanation=f"{self.name}: array is empty.", operation="done")
            return
        counts: dict[Any, int] = {}
        for i, value in enumerate(arr):
            counts[value] = counts.get(value, 0) + 1
            yield SortFrame(
                array=arr[:],
                highlighted=[i],
                explanation=f"{self.name}: counting value at index {i}.",
                operation="read",
                metadata=self._metadata("read", [i]),
            )
        output = sorted_copy(arr, ascending)
        for i, value in enumerate(output):
            arr[i] = value
            yield SortFrame(
                array=arr[:],
                swapped=[i],
                aux_array=output[:],
                explanation=f"{self.name}: writing bucketed value to index {i}.",
                operation="write",
                metadata=self._metadata("write", [i]),
            )
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation=f"{self.name}: array is fully sorted.",
            operation="done",
            metadata=self._metadata("done", list(range(n))),
        )


def make_algorithm_class(
    class_name: str,
    display_name: str,
    category: str,
    *,
    base: Type[SortAlgorithm] = InstrumentedInsertionAlgorithm,
    time_complexity: str | None = None,
    space_complexity: str | None = None,
    stable: bool | None = None,
    description: str = "",
    worst_case_input: str | None = None,
    metadata_defaults: dict[str, Any] | None = None,
) -> Type[SortAlgorithm]:
    attrs: dict[str, Any] = {
        "name": display_name,
        "category": category,
        "description": description or f"Instrumented visualization of {display_name}.",
        "metadata_defaults": metadata_defaults or {},
        "__module__": __name__,
    }
    if time_complexity is not None:
        attrs["time_complexity"] = time_complexity
    if space_complexity is not None:
        attrs["space_complexity"] = space_complexity
    if stable is not None:
        attrs["stable"] = stable
    if worst_case_input is not None:
        attrs["worst_case_input"] = worst_case_input
    return type(class_name, (base,), attrs)


class StalinSortAlgorithm(SortAlgorithm):
    name = "Stalin Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Purges elements that break ascending order until no purge is needed."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        while True:
            if not arr:
                break
            purged: list[int] = []
            kept = [arr[0]]
            last = arr[0]
            for idx, value in enumerate(arr[1:], start=1):
                yield SortFrame(
                    array=arr[:],
                    highlighted=[idx - 1, idx],
                    explanation="Stalin Sort: checking whether this value obeys the current order.",
                    operation="compare",
                )
                if in_order(last, value, ascending):
                    kept.append(value)
                    last = value
                else:
                    purged.append(idx)
            if not purged:
                break
            arr = kept
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))),
                explanation="Stalin Sort: purging values that broke the order.",
                operation="write",
                metadata={"purged": purged},
            )
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation="Stalin Sort: no more purges are required.",
            operation="done",
        )


class ThanosSortAlgorithm(SortAlgorithm):
    name = "Thanos Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(n log n) expected"
    space_complexity = "O(n)"
    stable = False
    description = "Randomly deletes half the array until what remains is sorted."
    worst_case_input = "random"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        rng = random.Random(0)
        while len(arr) > 1 and arr != sorted_copy(arr, ascending):
            survivors = set(rng.sample(range(len(arr)), max(1, len(arr) // 2)))
            deleted = [i for i in range(len(arr)) if i not in survivors]
            arr = [value for i, value in enumerate(arr) if i in survivors]
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))),
                explanation="Thanos Sort: deleting half of the remaining values.",
                operation="write",
                metadata={"snap": True, "deleted": deleted},
            )
        if arr != sorted_copy(arr, ascending):
            arr = sorted_copy(arr, ascending)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation="Thanos Sort: balance has been achieved.",
            operation="done",
        )


class BogoSortAlgorithm(SortAlgorithm):
    name = "Bogosort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(n!)"
    space_complexity = "O(1)"
    stable = False
    description = "Shuffles until sorted, capped for mercy."
    worst_case_input = "random"
    max_attempts = 100_000

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        rng = random.Random(0)
        attempts = 0
        while arr != sorted_copy(arr, ascending) and attempts < self.max_attempts:
            attempts += 1
            rng.shuffle(arr)
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))),
                explanation=f"{self.name}: shuffle attempt {attempts}.",
                operation="write",
                metadata={"attempts": attempts},
            )
        if arr != sorted_copy(arr, ascending):
            arr[:] = sorted_copy(arr, ascending)
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))),
                explanation=f"{self.name}: cap reached, snapping to sorted order.",
                operation="write",
                metadata={"attempts": attempts, "cap_reached": True},
            )
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation=f"{self.name}: array is sorted after {attempts} attempts.",
            operation="done",
            metadata={"attempts": attempts},
        )


class RandomSortAlgorithm(BogoSortAlgorithm):
    name = "Random Sort"
    description = "Another name for capped shuffle-and-check sorting."


class SleepSortAlgorithm(SortAlgorithm):
    name = "Sleep Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(n log n) simulated"
    space_complexity = "O(n)"
    stable = True
    description = "Simulates wake-up order with a priority queue; it never sleeps."
    worst_case_input = "random"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        heap: list[tuple[Any, int, Any]] = []
        for i, value in enumerate(arr):
            priority = value if ascending else -value
            heapq.heappush(heap, (priority, i, value))
            yield SortFrame(
                array=arr[:],
                highlighted=[i],
                explanation="Sleep Sort: scheduling a simulated wake-up event.",
                operation="read",
                metadata={"sleep_sort": True},
            )
        out: list[Any] = []
        while heap:
            _priority, _i, value = heapq.heappop(heap)
            out.append(value)
            arr[: len(out)] = out
            yield SortFrame(
                array=arr[:],
                swapped=[len(out) - 1],
                aux_array=out[:],
                explanation="Sleep Sort: writing the next simulated wake-up value.",
                operation="write",
                metadata={"sleep_sort": True},
            )
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation="Sleep Sort: all simulated timers have fired.",
            operation="done",
        )


class QuantumBogoSortAlgorithm(SortAlgorithm):
    name = "Quantum Bogosort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(1) in a convenient universe"
    space_complexity = "O(n)"
    stable = False
    description = "Flashes through universes, then observes the sorted one."
    worst_case_input = "random"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        for i in range(5):
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(n)),
                explanation=f"Quantum Bogosort: sampling multiverse branch {i + 1}.",
                operation="read",
                metadata={"multiverse": True},
            )
        arr[:] = sorted_copy(arr, ascending)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Quantum Bogosort: observed the sorted branch.",
            operation="done",
            metadata={"multiverse": True},
        )


class WaitingThenSnapSortAlgorithm(SortAlgorithm):
    name = "Waiting Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(wait)"
    space_complexity = "O(n)"
    stable = True
    description = "Waits for a while, then snaps to sorted order."
    worst_case_input = "random"
    waiting_frames = 200

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        for i in range(self.waiting_frames):
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))) if i % 10 == 0 else [],
                explanation=f"{self.name}: waiting for the universe to cooperate.",
                operation="read",
                metadata={"waiting": True, "tick": i + 1},
            )
        arr[:] = sorted_copy(arr, ascending)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation=f"{self.name}: the array is now sorted.",
            operation="done",
        )


class SlothSortAlgorithm(InstrumentedInsertionAlgorithm):
    name = "Sloth Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(n² + naps)"
    space_complexity = "O(1)"
    stable = True
    description = "Insertion sort that randomly skips generator steps."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        rng = random.Random(0)
        for frame in super().sort(arr, ascending):
            for _ in range(rng.randint(0, 50)):
                yield SortFrame(
                    array=frame.array[:],
                    highlighted=frame.highlighted[:],
                    explanation="Sloth Sort: skipping this moment.",
                    operation="read",
                    metadata={"skipped": True},
                )
            yield frame


class GondolaSortAlgorithm(SortAlgorithm):
    name = "Gondola Sort"
    category = "Specialized / Joke Sorts"
    time_complexity = "O(rounds)"
    space_complexity = "O(n)"
    stable = False
    description = "Shuffle, check, and restore if unsorted."
    worst_case_input = "random"
    max_rounds = 10_000

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        rng = random.Random(0)
        original = arr[:]
        rounds = 0
        while arr != sorted_copy(arr, ascending) and rounds < self.max_rounds:
            rounds += 1
            rng.shuffle(arr)
            yield SortFrame(
                array=arr[:],
                highlighted=list(range(len(arr))),
                explanation=f"Gondola Sort: shuffle round {rounds}.",
                operation="write",
                metadata={"rounds": rounds},
            )
            if arr != sorted_copy(arr, ascending):
                arr[:] = original[:]
                yield SortFrame(
                    array=arr[:],
                    explanation="Gondola Sort: restoring the original order after a failed round.",
                    operation="write",
                    metadata={"rounds": rounds, "restored": True},
                )
        if arr != sorted_copy(arr, ascending):
            arr[:] = sorted_copy(arr, ascending)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation=f"Gondola Sort: finished after {rounds} rounds.",
            operation="done",
            metadata={"rounds": rounds},
        )


def make_waiting_snap_class(class_name: str, display_name: str) -> Type[SortAlgorithm]:
    return type(
        class_name,
        (WaitingThenSnapSortAlgorithm,),
        {"name": display_name, "__module__": __name__},
    )


def registry_from(items: Iterable[tuple[str, Type[SortAlgorithm]]]) -> dict[str, Type[SortAlgorithm]]:
    return {key: cls for key, cls in items}


def keys_from(items: Iterable[tuple[str, Type[SortAlgorithm]]]) -> list[str]:
    return [key for key, _cls in items]


def ensure_sorted_done(
    arr: list[Any],
    ascending: bool,
    *,
    name: str,
    metadata: dict[str, Any] | None = None,
) -> SortFrame:
    arr[:] = sorted_copy(arr, ascending)
    return SortFrame(
        array=arr[:],
        sorted_indices=list(range(len(arr))),
        explanation=f"{name}: array is fully sorted.",
        operation="done",
        metadata=metadata or {},
    )
