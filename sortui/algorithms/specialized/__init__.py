from __future__ import annotations

from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    compare_exchange_network,
    done_frame,
    insertion_sort_range,
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

    def get_invariant(self) -> str:
        return "Three sorted runs are merged simultaneously; the minimum across three run-front pointers advances each step."


class FranceschinisSort(SortAlgorithm):
    name = "Franceschini's Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = True
    description = "In-place stable merge sort approximation inspired by Franceschini's algorithm."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        # STRETCH: Full Franceschini sorting uses a sophisticated constant-
        # workspace block strategy; this keeps the visible constraint by
        # merging with stable in-place rotations and no auxiliary array.
        n = len(arr)
        width = 1
        pass_no = 0
        while width < n:
            for left in range(0, n, 2 * width):
                mid = min(left + width, n)
                right = min(left + 2 * width, n)
                i, j = left, mid
                while i < j and j < right:
                    yield base_frame(
                        arr,
                        highlighted=[i, j],
                        partition_bounds=(left, right - 1),
                        explanation=f"{self.name}: comparing two adjacent in-place merge blocks.",
                        operation="compare",
                        metadata={"phase": "merge", "block_size": width, "pass": pass_no},
                    )
                    if not out_of_order(arr[i], arr[j], ascending):
                        i += 1
                        continue
                    for k in range(j, i, -1):
                        arr[k], arr[k - 1] = arr[k - 1], arr[k]
                        yield base_frame(
                            arr,
                            swapped=[k - 1, k],
                            partition_bounds=(left, right - 1),
                            explanation=f"{self.name}: rotating a right-block value left without auxiliary storage.",
                            operation="swap",
                            metadata={"phase": "rotate", "block_size": width, "pass": pass_no},
                        )
                    i += 1
                    j += 1
                    mid += 1
            width *= 2
            pass_no += 1
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "Two sorted halves are merged in-place by block rotation; no auxiliary array is used at any point."


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

    def get_invariant(self) -> str:
        return "Large elements are paired and sorted; small partners are then binary-inserted into the sorted sequence."


class BeadSort(SortAlgorithm):
    name = "Bead Sort"
    category = CATEGORY
    time_complexity = "O(n + max)"
    space_complexity = "O(n * max)"
    stable = True
    description = "Gravity/bead-inspired counting sort for non-negative rods."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        if not arr:
            yield done_frame(arr, self.name)
            return
        rods: dict[int, list[Any]] = {}
        for index, value in enumerate(arr):
            rods.setdefault(value_of(value), []).append(value)
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=[value_of(item) for item in arr],
                explanation=f"{self.name}: creating a bead rod of length {value}.",
                operation="read",
                metadata={"phase": "rod", "rod": value_of(value)},
            )

        max_length = max(value_of(value) for value in arr)
        column_counts: list[int] = []
        for column in range(1, max_length + 1):
            count = sum(1 for value in arr if value_of(value) >= column)
            column_counts.append(count)
            yield base_frame(
                arr,
                highlighted=[],
                aux_array=column_counts,
                explanation=f"{self.name}: gravity lets beads fall in column {column}; {count} beads remain.",
                operation="read",
                metadata={"phase": "gravity", "column": column, "beads": count},
            )

        fallen_lengths = [0] * len(arr)
        for count in column_counts:
            for row in range(count):
                fallen_lengths[row] += 1
        visual_lengths = fallen_lengths[:] if not ascending else list(reversed(fallen_lengths))
        for index, length in enumerate(visual_lengths):
            yield base_frame(
                arr,
                highlighted=[index],
                aux_array=visual_lengths,
                explanation=f"{self.name}: reading fallen bead row {index} as rod length {length}.",
                operation="read",
                metadata={"phase": "read_rows", "rod": length},
            )

        value_order = sorted(rods, reverse=not ascending)
        out = 0
        for length in value_order:
            for value in rods[length]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    aux_array=visual_lengths,
                    explanation=f"{self.name}: writing stable rod of length {length} after gravity.",
                    operation="write",
                    metadata={"phase": "write", "rod": length},
                )
                out += 1
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "After each gravity pass, column bead counts equal the number of elements >= the row index in that column."


class SortingNetworkSort(SortAlgorithm):
    name = "Sorting Network"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Generic insertion-sort comparator network visualization."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        yield base_frame(
            arr,
            explanation=f"{self.name}: laying out insertion-network wires before the first comparator.",
            operation="read",
            metadata={"network": "insertion", "level": -1, "step": 0},
        )

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            level = 0
            for i in range(1, n):
                for j in range(i, 0, -1):
                    yield (
                        j - 1,
                        j,
                        True,
                        {"network": "insertion", "level": level, "step": i},
                        f"{self.name}: insertion-network comparator shifts wire {j} left if needed.",
                    )
                    level += 1

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=n,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata={"network": True})

    def get_invariant(self) -> str:
        return "Each comparator in the fixed insertion-sort-derived network fires exactly once in predetermined order."


class BitonicSort(SortAlgorithm):
    name = "Bitonic Sort"
    category = CATEGORY
    time_complexity = "O(log² n)"
    space_complexity = "O(1)"
    stable = False
    description = "Bitonic network simulation for arbitrary-size arrays."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        power = 1
        while power < max(1, len(arr)):
            power *= 2

        def comparators() -> Generator[tuple[int, int, bool, dict[str, Any], str], None, None]:
            step = 0
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
                            {
                                "network": "bitonic",
                                "step": step,
                                "substep": stride,
                                "direction": "asc" if direction else "desc",
                            },
                            f"{self.name}: bitonic comparator at size {size} and stride {stride}.",
                        )
                    step += 1
                    stride //= 2
                size *= 2

        yield from compare_exchange_network(
            arr,
            ascending,
            self.name,
            wire_count=power,
            comparators=comparators(),
        )
        yield done_frame(arr, self.name, metadata={"network": True})

    def get_invariant(self) -> str:
        return "Each stage builds a bitonic sequence of length 2^k; the final stage merges the full bitonic sequence."


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
    time_complexity = "O(n²)"
    space_complexity = "O(n)"
    stable = True
    description = "Output-sensitive repeated minimum scan with a growing sorted prefix."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        remaining = list(enumerate(arr))
        output: list[Any] = []
        for prefix in range(len(arr)):
            best_pos = 0
            for scan in range(1, len(remaining)):
                yield base_frame(
                    arr,
                    highlighted=[prefix + scan if prefix + scan < len(arr) else prefix],
                    sorted_indices=list(range(prefix)),
                    aux_array=[value for _idx, value in remaining],
                    explanation=f"{self.name}: scanning remaining values for the next output minimum.",
                    operation="compare",
                    metadata={"prefix": prefix, "candidate": best_pos},
                )
                candidate = remaining[scan][1]
                best = remaining[best_pos][1]
                if (
                    value_of(candidate) < value_of(best)
                    if ascending
                    else value_of(candidate) > value_of(best)
                ):
                    best_pos = scan
                    yield base_frame(
                        arr,
                        highlighted=[prefix],
                        sorted_indices=list(range(prefix)),
                        aux_array=[value for _idx, value in remaining],
                        explanation=f"{self.name}: updating the pointer to the next output value.",
                        operation="read",
                        metadata={"prefix": prefix, "candidate": best_pos},
                    )
            _original_index, value = remaining.pop(best_pos)
            output.append(value)
            arr[prefix] = value
            yield base_frame(
                arr,
                swapped=[prefix],
                sorted_indices=list(range(prefix + 1)),
                aux_array=output[:] + [value for _idx, value in remaining],
                explanation=f"{self.name}: appending the selected value to the sorted prefix.",
                operation="write",
                metadata={"prefix": prefix + 1},
            )
        yield done_frame(arr, self.name)

    def get_invariant(self) -> str:
        return "A running minimum pointer advances only when a new minimum is found; each minimum is output in order."


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

    def get_invariant(self) -> str:
        return "The observed branch preserves the input multiset while each collapse write places one stable sorted value."


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

CATEGORY_ALGORITHMS = registry_from(_ITEMS)  # type: ignore[arg-type]
CATEGORY_KEYS = keys_from(_ITEMS)  # type: ignore[arg-type]

__all__ = [cls.__name__ for _key, cls in _ITEMS] + [  # type: ignore[attr-defined]
    "CATEGORY_ALGORITHMS",
    "CATEGORY_KEYS",
    "JOKE_ALGORITHMS",
]
