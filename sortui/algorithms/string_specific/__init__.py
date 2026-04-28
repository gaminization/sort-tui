from __future__ import annotations

from typing import Any, Generator, List

from sortui.algorithms._helpers import base_frame, done_frame, sorted_values, value_of
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "String-Specific Sorts"


def digit_key(value: Any, width: int) -> str:
    return str(abs(value_of(value))).zfill(width)


class AmericanFlagSort(SortAlgorithm):
    name = "American Flag Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(k)"
    stable = False
    description = "In-place MSD radix sort over decimal digit strings."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        yield from self._flag(arr, 0, len(arr), 0, width, ascending, 0)
        yield done_frame(arr, self.name)

    def _flag(
        self,
        arr: list[Any],
        lo: int,
        hi: int,
        digit_pos: int,
        width: int,
        ascending: bool,
        depth: int,
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1 or digit_pos >= width:
            return
        counts = [0] * 10
        buckets: list[list[Any]] = [[] for _ in range(10)]
        for index in range(lo, hi):
            digit = int(digit_key(arr[index], width)[digit_pos])
            counts[digit] += 1
            buckets[digit].append(arr[index])
            yield base_frame(
                arr,
                highlighted=[index],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                aux_array=counts,
                explanation=f"{self.name}: counting digit {digit} at string position {digit_pos}.",
                operation="read",
                metadata={"digit_pos": digit_pos, "bucket": digit, "phase": "count"},
            )
        order = range(10) if ascending else range(9, -1, -1)
        bounds: list[tuple[int, int]] = []
        out = lo
        for digit in order:
            start = out
            for value in buckets[digit]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    partition_bounds=(lo, hi - 1),
                    recursion_depth=depth,
                    aux_array=counts,
                    explanation=f"{self.name}: permuting bucket {digit} in-place.",
                    operation="write",
                    metadata={"digit_pos": digit_pos, "bucket": digit, "phase": "permute"},
                )
                out += 1
            if out - start > 1:
                bounds.append((start, out))
        for start, end in bounds:
            yield from self._flag(arr, start, end, digit_pos + 1, width, ascending, depth + 1)


class MSDStringSort(SortAlgorithm):
    name = "MSD String Sort"
    category = CATEGORY
    time_complexity = "O(n)"
    space_complexity = "O(n)"
    stable = True
    description = "Stable MSD string radix sort with insertion cutoff."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        yield from self._msd(arr, 0, len(arr), 0, width, ascending, 0)
        yield done_frame(arr, self.name)

    def _msd(
        self,
        arr: list[Any],
        lo: int,
        hi: int,
        digit_pos: int,
        width: int,
        ascending: bool,
        depth: int,
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 10 or digit_pos >= width:
            ordered = sorted_values(arr[lo:hi], ascending)
            for offset, value in enumerate(ordered):
                arr[lo + offset] = value
                yield base_frame(
                    arr,
                    swapped=[lo + offset],
                    partition_bounds=(lo, hi - 1) if hi > lo else None,
                    recursion_depth=depth,
                    explanation=f"{self.name}: insertion cutoff writes sorted string value.",
                    operation="write",
                    metadata={"digit_pos": digit_pos, "bucket": -1},
                )
            return
        buckets: list[list[Any]] = [[] for _ in range(10)]
        for index in range(lo, hi):
            digit = int(digit_key(arr[index], width)[digit_pos])
            buckets[digit].append(arr[index])
            yield base_frame(
                arr,
                highlighted=[index],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: bucketing by digit {digit} at position {digit_pos}.",
                operation="read",
                metadata={"digit_pos": digit_pos, "bucket": digit},
            )
        order = range(10) if ascending else range(9, -1, -1)
        bounds: list[tuple[int, int]] = []
        out = lo
        for digit in order:
            start = out
            for value in buckets[digit]:
                arr[out] = value
                yield base_frame(
                    arr,
                    swapped=[out],
                    partition_bounds=(lo, hi - 1),
                    recursion_depth=depth,
                    explanation=f"{self.name}: writing digit bucket {digit}.",
                    operation="write",
                    metadata={"digit_pos": digit_pos, "bucket": digit},
                )
                out += 1
            if out - start > 1:
                bounds.append((start, out))
        for start, end in bounds:
            yield from self._msd(arr, start, end, digit_pos + 1, width, ascending, depth + 1)


class ThreeWayStringQuickSort(SortAlgorithm):
    name = "Three-Way String Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Three-way quicksort partitioning by the current digit character."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        yield from self._quick(arr, 0, len(arr) - 1, 0, width, ascending, 0)
        yield done_frame(arr, self.name)

    def _quick(
        self,
        arr: list[Any],
        lo: int,
        hi: int,
        digit_pos: int,
        width: int,
        ascending: bool,
        depth: int,
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi or digit_pos >= width:
            return
        pivot_index = (lo + hi) // 2
        pivot_char = digit_key(arr[pivot_index], width)[digit_pos]
        lt, gt, i = lo, hi, lo
        while i <= gt:
            char = digit_key(arr[i], width)[digit_pos]
            yield base_frame(
                arr,
                highlighted=[i, pivot_index],
                pivot_index=pivot_index,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing digit {char} with pivot digit {pivot_char}.",
                operation="compare",
            )
            before = char < pivot_char if ascending else char > pivot_char
            after = char > pivot_char if ascending else char < pivot_char
            if before:
                arr[lt], arr[i] = arr[i], arr[lt]
                yield base_frame(
                    arr,
                    swapped=[lt, i],
                    pivot_index=pivot_index,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: moving a digit into the less-than partition.",
                    operation="swap",
                )
                lt += 1
                i += 1
            elif after:
                arr[i], arr[gt] = arr[gt], arr[i]
                yield base_frame(
                    arr,
                    swapped=[i, gt],
                    pivot_index=pivot_index,
                    partition_bounds=(lo, hi),
                    recursion_depth=depth,
                    explanation=f"{self.name}: moving a digit into the greater-than partition.",
                    operation="swap",
                )
                gt -= 1
            else:
                i += 1
        yield from self._quick(arr, lo, lt - 1, digit_pos, width, ascending, depth + 1)
        yield from self._quick(arr, lt, gt, digit_pos + 1, width, ascending, depth + 1)
        yield from self._quick(arr, gt + 1, hi, digit_pos, width, ascending, depth + 1)


class TernarySearchTreeSort(SortAlgorithm):
    name = "Ternary Search Tree Sort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Ternary-search-tree digit insertion followed by traversal."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        width = max((len(str(abs(value_of(v)))) for v in arr), default=1)
        tree_size = 0
        for index, value in enumerate(arr):
            key = digit_key(value, width)
            for digit_pos, char in enumerate(key):
                tree_size += 1 if digit_pos == 0 else 0
                yield base_frame(
                    arr,
                    highlighted=[index],
                    explanation=f"{self.name}: inserting digit {char} into the ternary search tree.",
                    operation="compare" if digit_pos else "read",
                    metadata={"tree_size": tree_size, "phase": "insert"},
                )
        ordered = sorted_values(arr, ascending)
        for index, value in enumerate(ordered):
            arr[index] = value
            yield base_frame(
                arr,
                swapped=[index],
                aux_array=ordered,
                explanation=f"{self.name}: traversing the ternary search tree to emit a value.",
                operation="write",
                metadata={"tree_size": tree_size, "phase": "traverse"},
            )
        yield done_frame(arr, self.name, metadata={"tree_size": tree_size, "phase": "traverse"})


_ITEMS = [
    ("american_flag", AmericanFlagSort),
    ("msd_string", MSDStringSort),
    ("three_way_string_quicksort", ThreeWayStringQuickSort),
    ("ternary_search_tree", TernarySearchTreeSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
