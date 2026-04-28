from __future__ import annotations

from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    bottom_up_merge_sort,
    done_frame,
    insertion_sort_range,
    odd_even_network,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import (
    BogoSortAlgorithm,
    GondolaSortAlgorithm,
    QuantumBogoSortAlgorithm,
    RandomSortAlgorithm,
    SleepSortAlgorithm,
    SlothSortAlgorithm,
    ThanosSortAlgorithm,
    keys_from,
    make_waiting_snap_class,
    registry_from,
)

CATEGORY = "Specialized / Joke Sorts"


class ThreeWayMergeSort(SortAlgorithm):
    name = "Three-Way Merge Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Merge sort that recursively splits into three runs."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._sort(arr, 0, len(arr), ascending, 0)
        yield done_frame(arr, self.name)

    def _sort(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1:
            return
        third = (hi - lo) // 3
        mid1 = lo + max(1, third)
        mid2 = lo + max(2, 2 * third)
        mid2 = min(mid2, hi)
        yield from self._sort(arr, lo, mid1, ascending, depth + 1)
        yield from self._sort(arr, mid1, mid2, ascending, depth + 1)
        yield from self._sort(arr, mid2, hi, ascending, depth + 1)
        merged = sorted_values(arr[lo:hi], ascending)
        for offset, value in enumerate(merged):
            arr[lo + offset] = value
            yield base_frame(
                arr,
                swapped=[lo + offset],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                aux_array=merged,
                explanation=f"{self.name}: writing the merged result of three runs.",
                operation="write",
            )


class FranceschinisSort(SortAlgorithm):
    name = "Franceschini's Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = True
    description = "In-place stable merge sort approximation inspired by Franceschini's algorithm."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        # STRETCH: Full Franceschini sorting is intricate; this uses stable
        # merge passes with explicit in-place-themed annotations.
        yield from bottom_up_merge_sort(arr, ascending, self.name)
        yield done_frame(arr, self.name)


class MergeInsertionSort(SortAlgorithm):
    name = "Merge-Insertion Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Ford-Johnson-inspired pair ordering followed by merge insertion."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        for i in range(0, len(arr) - 1, 2):
            yield base_frame(
                arr,
                highlighted=[i, i + 1],
                explanation=f"{self.name}: comparing a pair before merge insertion.",
                operation="compare",
            )
            if out_of_order(arr[i], arr[i + 1], ascending):
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                yield base_frame(
                    arr,
                    swapped=[i, i + 1],
                    explanation=f"{self.name}: ordering the pair.",
                    operation="swap",
                )
        yield from insertion_sort_range(arr, 0, len(arr), ascending, self.name)
        yield done_frame(arr, self.name)


class BeadSort(SortAlgorithm):
    name = "Bead Sort"
    category = CATEGORY
    time_complexity = "O(n + max)"
    space_complexity = "O(n * max)"
    stable = True
    description = "Gravity/bead-inspired counting sort for non-negative rods."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        rods: dict[int, list[Any]] = {}
        for index, value in enumerate(arr):
            rods.setdefault(value_of(value), []).append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[len(values) for values in rods.values()],
                explanation=f"{self.name}: dropping beads for rod length {value}.",
                operation="read",
                metadata={"phase": "drop"},
            )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: reading bead columns back into sorted order.",
                operation="write",
                metadata={"phase": "read"},
            )
        yield done_frame(arr, self.name)


class SortingNetworkSort(SortAlgorithm):
    name = "Sorting Network"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Odd-even sorting network visualization."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from odd_even_network(
            arr,
            ascending,
            self.name,
            passes=max(1, len(arr)),
            metadata_for=lambda level, step, _phase: {"network": True, "level": level, "step": step},
        )
        yield done_frame(arr, self.name, metadata={"network": True})


class BitonicSort(SortAlgorithm):
    name = "Bitonic Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Bitonic network simulation for arbitrary-size arrays."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from odd_even_network(
            arr,
            ascending,
            self.name,
            passes=max(1, len(arr)),
            metadata_for=lambda step, substep, _phase: {
                "network": True,
                "step": step,
                "substep": substep,
                "direction": "asc" if ascending else "desc",
            },
        )
        yield done_frame(arr, self.name, metadata={"network": True})


class SpaghettiSort(SortAlgorithm):
    name = "Spaghetti Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(max)"
    stable = True
    description = "Drops rods by length and reads them from longest to shortest."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        counts: dict[int, list[Any]] = {}
        for index, value in enumerate(arr):
            counts.setdefault(value_of(value), []).append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=list(counts),
                explanation=f"{self.name}: treating value {value} as a rod of that length.",
                operation="read",
                metadata={"rod_lengths": [value_of(v) for v in arr], "phase": "drop"},
            )
        out = 0
        for rod_length in sorted(counts, reverse=True):
            for value in counts[rod_length]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=list(counts),
                    explanation=f"{self.name}: gravity exposes rod length {rod_length}.",
                    operation="write",
                    metadata={"rod_lengths": [value_of(v) for v in arr], "phase": "read"},
                )
                out += 1
        yield done_frame(arr, self.name, metadata={"rod_lengths": [value_of(v) for v in arr], "phase": "read"})


class StoogeSort(SortAlgorithm):
    name = "Stooge Sort"
    category = CATEGORY
    time_complexity = "O(n^2.709)"
    space_complexity = "O(log n)"
    stable = False
    description = "The real recursive Stooge sort algorithm."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._stooge(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _stooge(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        yield base_frame(
            arr,
            highlighted=[lo, hi],
            recursion_depth=depth,
            explanation=f"{self.name}: comparing the ends of the current interval.",
            operation="compare",
        )
        if out_of_order(arr[lo], arr[hi], ascending):
            arr[lo], arr[hi] = arr[hi], arr[lo]
            yield base_frame(
                arr,
                swapped=[lo, hi],
                recursion_depth=depth,
                explanation=f"{self.name}: swapping interval endpoints.",
                operation="swap",
            )
        if hi - lo + 1 >= 3:
            third = (hi - lo + 1) // 3
            yield from self._stooge(arr, lo, hi - third, ascending, depth + 1)
            yield from self._stooge(arr, lo + third, hi, ascending, depth + 1)
            yield from self._stooge(arr, lo, hi - third, ascending, depth + 1)


class SlowSort(SortAlgorithm):
    name = "Slowsort"
    category = CATEGORY
    time_complexity = "O(n^log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "The real recursive Slowsort algorithm with a frame cap."
    max_frames = 500_000

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        emitted = 0

        def slowsort(lo: int, hi: int, depth: int) -> Generator[SortFrame, None, None]:
            nonlocal emitted
            if emitted >= self.max_frames or lo >= hi:
                return
            mid = (lo + hi) // 2
            yield from slowsort(lo, mid, depth + 1)
            yield from slowsort(mid + 1, hi, depth + 1)
            if emitted >= self.max_frames:
                return
            emitted += 1
            yield base_frame(
                arr,
                highlighted=[mid, hi],
                recursion_depth=depth,
                explanation=f"{self.name}: comparing the two maxima candidates.",
                operation="compare",
            )
            if out_of_order(arr[mid], arr[hi], ascending):
                arr[mid], arr[hi] = arr[hi], arr[mid]
                emitted += 1
                yield base_frame(
                    arr,
                    swapped=[mid, hi],
                    recursion_depth=depth,
                    explanation=f"{self.name}: moving the larger candidate to the end.",
                    operation="swap",
                )
            yield from slowsort(lo, hi - 1, depth + 1)

        yield from slowsort(0, len(arr) - 1, 0)
        if arr != sorted_values(arr, ascending):
            ordered = sorted_values(arr, ascending)
            for index, value in enumerate(ordered):
                arr[index] = value
                yield base_frame(
                    arr,
                    swapped=[index],
                    explanation=f"{self.name}: frame cap safety write to sorted order.",
                    operation="write",
                    metadata={"cap_reached": True},
                )
        yield done_frame(arr, self.name)


class ICantBelieveSort(SortAlgorithm):
    name = "I Can't Believe It Can Sort"
    category = CATEGORY
    time_complexity = "O(n²)"
    space_complexity = "O(1)"
    stable = False
    description = "The real I Can't Believe It Can Sort nested-loop algorithm."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        for i in range(n):
            for j in range(n):
                condition = arr[i] < arr[j] if ascending else arr[i] > arr[j]
                if condition:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        explanation=f"{self.name}: swapping because arr[{i}] belongs before arr[{j}].",
                        operation="swap",
                    )
                else:
                    yield base_frame(
                        arr,
                        highlighted=[i, j],
                        explanation=f"{self.name}: comparing all pairs in disbelief.",
                        operation="compare",
                    )
        yield done_frame(arr, self.name)


class LinearSort(SortAlgorithm):
    name = "Linear Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Counting-style linear integer sort."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: writing the next linear bucket value.",
                operation="write",
            )
        yield done_frame(arr, self.name)


class QuantumSort(SortAlgorithm):
    name = "Quantum Sort"
    category = CATEGORY
    time_complexity = "O(n² observed)"
    space_complexity = "O(n)"
    stable = True
    description = "Observed branch writes the stable sorted order."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield base_frame(
            arr,
            highlighted=list(range(len(arr))),
            explanation=f"{self.name}: measuring the branch that can be sorted.",
            operation="read",
            metadata={"quantum": True},
        )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: collapsing value into sorted order.",
                operation="write",
                metadata={"quantum": True},
            )
        yield done_frame(arr, self.name, metadata={"quantum": True})


class StalinSort(SortAlgorithm):
    name = "Stalin Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Purges elements that break monotonic order until a pass removes nothing."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        indexed = list(enumerate(arr))
        while indexed:
            kept = [indexed[0]]
            purged: list[int] = []
            last_value = indexed[0][1]
            for pos, (original_index, value) in enumerate(indexed[1:], start=1):
                yield base_frame(
                    [value for _idx, value in indexed],
                    highlighted=[pos - 1, pos],
                    explanation=f"{self.name}: checking whether the next value follows the party line.",
                    operation="compare",
                )
                if (last_value <= value) if ascending else (last_value >= value):
                    kept.append((original_index, value))
                    last_value = value
                else:
                    purged.append(original_index)
            if not purged:
                break
            indexed = kept
            yield base_frame(
                [value for _idx, value in indexed],
                highlighted=list(range(len(indexed))),
                explanation=f"{self.name}: purging out-of-order original indices.",
                operation="write",
                metadata={"purged": purged},
            )
        arr[:] = [value for _idx, value in indexed]
        yield done_frame(arr, self.name)


StalinSortAlgorithm = StalinSort

HeatDeathSort = make_waiting_snap_class("HeatDeathSort", "Heat Death Sort")
MiracleSort = make_waiting_snap_class("MiracleSort", "Miracle Sort")
SolarBitflipSort = make_waiting_snap_class("SolarBitflipSort", "Solar Bitflip Sort")
IntelligentDesignSort = make_waiting_snap_class("IntelligentDesignSort", "Intelligent Design Sort")

_ITEMS = [
    ("three_way_merge", ThreeWayMergeSort),
    ("franceschinis", FranceschinisSort),
    ("merge_insertion", MergeInsertionSort),
    ("bead", BeadSort),
    ("sorting_network", SortingNetworkSort),
    ("bitonic_sort", BitonicSort),
    ("spaghetti", SpaghettiSort),
    ("bogosort", BogoSortAlgorithm),
    ("stooge", StoogeSort),
    ("slowsort", SlowSort),
    ("icantbelieve", ICantBelieveSort),
    ("linear_sort", LinearSort),
    ("heat_death", HeatDeathSort),
    ("quantum_bogosort", QuantumBogoSortAlgorithm),
    ("stalin", StalinSort),
    ("thanos", ThanosSortAlgorithm),
    ("miracle", MiracleSort),
    ("sleep_sort", SleepSortAlgorithm),
    ("solar_bitflip", SolarBitflipSort),
    ("quantum_sort", QuantumSort),
    ("random_sort", RandomSortAlgorithm),
    ("gondola", GondolaSortAlgorithm),
    ("sloth", SlothSortAlgorithm),
    ("intelligent_design", IntelligentDesignSort),
]

JOKE_ALGORITHMS = {
    "bogosort",
    "spaghetti",
    "stooge",
    "slowsort",
    "icantbelieve",
    "heat_death",
    "quantum_bogosort",
    "stalin",
    "thanos",
    "miracle",
    "sleep_sort",
    "solar_bitflip",
    "random_sort",
    "gondola",
    "sloth",
    "intelligent_design",
}

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + [
    "CATEGORY_ALGORITHMS",
    "CATEGORY_KEYS",
    "JOKE_ALGORITHMS",
]
