from __future__ import annotations

import math
from typing import Any, Generator, List

from sortui.algorithms._helpers import (
    base_frame,
    bottom_up_merge_sort,
    done_frame,
    heap_sort_range,
    in_order,
    insertion_sort_range,
    is_sorted,
    merge_runs,
    out_of_order,
    sorted_values,
    value_of,
)
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.algorithms.common import keys_from, registry_from

CATEGORY = "Hybrid Sorts"


class TimSort(SortAlgorithm):
    name = "Timsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Python-style adaptive merge sort with natural runs and galloping metadata."
    worst_case_input = "random"

    @staticmethod
    def _calc_min_run(n: int) -> int:
        if n < 64:
            return n
        r = 0
        while n >= 64:
            r |= n & 1
            n >>= 1
        return n + r

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        min_run = self._calc_min_run(n)
        runs: list[tuple[int, int]] = []
        i = 0
        while i < n:
            start = i
            i += 1
            if i < n:
                descending = out_of_order(arr[i - 1], arr[i], ascending)
                while i < n:
                    yield base_frame(
                        arr,
                        highlighted=[i - 1, i],
                        explanation=f"{self.name}: detecting a natural run.",
                        operation="compare",
                        metadata={"min_run": min_run, "run_count": len(runs) + 1, "gallop": False},
                    )
                    continues = (
                        out_of_order(arr[i - 1], arr[i], ascending)
                        if descending
                        else in_order(arr[i - 1], arr[i], ascending)
                    )
                    if not continues:
                        break
                    i += 1
                if descending:
                    arr[start:i] = reversed(arr[start:i])
                    yield base_frame(
                        arr,
                        swapped=list(range(start, i)),
                        explanation=f"{self.name}: reversing a descending natural run.",
                        operation="write",
                        metadata={"min_run": min_run, "run_count": len(runs) + 1, "gallop": False},
                    )
            run_end = min(n, max(i, start + min_run))
            if run_end > i:
                yield from insertion_sort_range(
                    arr,
                    start,
                    run_end,
                    ascending,
                    self.name,
                    metadata={"min_run": min_run, "run_count": len(runs) + 1, "gallop": False},
                    explanation_prefix="extending a short natural run; ",
                )
                i = run_end
            runs.append((start, i))

            def merge_at(index: int) -> Generator[SortFrame, None, None]:
                left, mid = runs[index][0], runs[index][1]
                right = runs[index + 1][1]
                yield from self._merge(arr, left, mid, right, ascending, min_run, len(runs))
                runs[index : index + 2] = [(left, right)]

            while len(runs) >= 3:
                a = runs[-3][1] - runs[-3][0]
                b = runs[-2][1] - runs[-2][0]
                c = runs[-1][1] - runs[-1][0]
                if a > b + c and b > c:
                    break
                merge_index = len(runs) - 3 if a < c else len(runs) - 2
                yield from merge_at(merge_index)
            while len(runs) >= 2 and (runs[-2][1] - runs[-2][0]) <= (runs[-1][1] - runs[-1][0]):
                yield from merge_at(len(runs) - 2)

        while len(runs) > 1:
            left, mid = runs[-2][0], runs[-2][1]
            right = runs[-1][1]
            yield from self._merge(arr, left, mid, right, ascending, min_run, len(runs))
            runs[-2:] = [(left, right)]
        yield done_frame(arr, self.name, metadata={"min_run": min_run, "run_count": len(runs), "gallop": False})

    def _merge(
        self,
        arr: list[Any],
        left: int,
        mid: int,
        right: int,
        ascending: bool,
        min_run: int,
        run_count: int,
    ) -> Generator[SortFrame, None, None]:
        left_run = arr[left:mid]
        right_run = arr[mid:right]
        i = j = 0
        k = left
        left_wins = right_wins = 0
        aux = left_run[:] + right_run[:]
        while i < len(left_run) and j < len(right_run):
            gallop = left_wins >= 7 or right_wins >= 7
            yield base_frame(
                arr,
                highlighted=[left + i, mid + j],
                partition_bounds=(left, right - 1),
                aux_array=aux,
                explanation=f"{self.name}: merging run heads with galloping {'enabled' if gallop else 'watching'}.",
                operation="compare",
                metadata={"min_run": min_run, "run_count": run_count, "gallop": gallop},
            )
            if in_order(left_run[i], right_run[j], ascending):
                arr[k] = left_run[i]
                i += 1
                left_wins += 1
                right_wins = 0
            else:
                arr[k] = right_run[j]
                j += 1
                right_wins += 1
                left_wins = 0
            yield base_frame(
                arr,
                swapped=[k],
                partition_bounds=(left, right - 1),
                aux_array=aux,
                explanation=f"{self.name}: writing the next merged run value.",
                operation="write",
                metadata={"min_run": min_run, "run_count": run_count, "gallop": gallop},
            )
            k += 1
        while i < len(left_run):
            arr[k] = left_run[i]
            yield base_frame(
                arr,
                swapped=[k],
                partition_bounds=(left, right - 1),
                aux_array=aux,
                explanation=f"{self.name}: copying the remaining left run value.",
                operation="write",
                metadata={"min_run": min_run, "run_count": run_count, "gallop": False},
            )
            i += 1
            k += 1
        while j < len(right_run):
            arr[k] = right_run[j]
            yield base_frame(
                arr,
                swapped=[k],
                partition_bounds=(left, right - 1),
                aux_array=aux,
                explanation=f"{self.name}: copying the remaining right run value.",
                operation="write",
                metadata={"min_run": min_run, "run_count": run_count, "gallop": False},
            )
            j += 1
            k += 1


class IntroSort(SortAlgorithm):
    name = "Introsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Quicksort with median-of-3 pivots, insertion cutoff, and heapsort fallback."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        depth_limit = 2 * int(math.log2(n)) if n > 1 else 0
        if n >= 32 and (is_sorted(arr, ascending) or is_sorted(arr, not ascending)):
            yield base_frame(
                arr,
                highlighted=list(range(min(n, 8))),
                explanation=f"{self.name}: sorted-pattern scan hit the introspective heapsort fallback.",
                operation="read",
                metadata={"fallback": "heapsort"},
            )
            yield from heap_sort_range(arr, 0, n, ascending, self.name, metadata={"fallback": "heapsort"})
            yield done_frame(arr, self.name)
            return
        yield from self._intro(arr, 0, n, ascending, depth_limit, 0)
        yield done_frame(arr, self.name)

    def _intro(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth_left: int, depth: int
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1:
            return
        if hi - lo <= 16:
            yield from insertion_sort_range(
                arr,
                lo,
                hi,
                ascending,
                self.name,
                metadata={"small_partition": True},
                explanation_prefix="sorting a small partition; ",
            )
            return
        if depth_left <= 0:
            yield base_frame(
                arr,
                highlighted=list(range(lo, min(hi, lo + 8))),
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: depth limit reached; switching this partition to heapsort.",
                operation="read",
                metadata={"fallback": "heapsort"},
            )
            yield from heap_sort_range(arr, lo, hi, ascending, self.name, metadata={"fallback": "heapsort"})
            return
        mid = (lo + hi - 1) // 2
        candidates = [lo, mid, hi - 1]
        candidates.sort(key=lambda idx: value_of(arr[idx]), reverse=not ascending)
        pivot_index = candidates[1]
        arr[pivot_index], arr[hi - 1] = arr[hi - 1], arr[pivot_index]
        yield base_frame(
            arr,
            swapped=[pivot_index, hi - 1],
            pivot_index=hi - 1,
            partition_bounds=(lo, hi - 1),
            recursion_depth=depth,
            explanation=f"{self.name}: moving the median-of-3 pivot into Lomuto position.",
            operation="swap",
        )
        pivot = arr[hi - 1]
        i = lo
        for j in range(lo, hi - 1):
            yield base_frame(
                arr,
                highlighted=[j, hi - 1],
                pivot_index=hi - 1,
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing partition value with the pivot.",
                operation="compare",
            )
            if in_order(arr[j], pivot, ascending):
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        pivot_index=hi - 1,
                        partition_bounds=(lo, hi - 1),
                        recursion_depth=depth,
                        explanation=f"{self.name}: moving a value into the lower partition.",
                        operation="swap",
                    )
                i += 1
        arr[i], arr[hi - 1] = arr[hi - 1], arr[i]
        yield base_frame(
            arr,
            swapped=[i, hi - 1],
            pivot_index=i,
            partition_bounds=(lo, hi - 1),
            recursion_depth=depth,
            explanation=f"{self.name}: placing the median pivot.",
            operation="swap",
        )
        yield from self._intro(arr, lo, i, ascending, depth_left - 1, depth + 1)
        yield from self._intro(arr, i + 1, hi, ascending, depth_left - 1, depth + 1)


class DualPivotQuickSort(SortAlgorithm):
    name = "Dual-Pivot Quicksort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Java-style dual-pivot quicksort with three-way partitioning."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        yield from self._sort(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _sort(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        third = (hi - lo) // 3
        p1_index = lo + third
        p2_index = lo + 2 * third
        p, q = sorted_values([arr[p1_index], arr[p2_index]], ascending)
        yield base_frame(
            arr,
            highlighted=[p1_index, p2_index],
            pivot_index=p1_index,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: reading two pivot samples at one-third positions.",
            operation="read",
            metadata={"pivot2_index": p2_index},
        )
        less: list[Any] = []
        middle: list[Any] = []
        greater: list[Any] = []
        for i in range(lo, hi + 1):
            yield base_frame(
                arr,
                highlighted=[i, p1_index, p2_index],
                pivot_index=p1_index,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing index {i} with both pivots.",
                operation="compare",
                metadata={"pivot2_index": p2_index},
            )
            if out_of_order(p, arr[i], ascending):
                less.append(arr[i])
            elif out_of_order(arr[i], q, ascending):
                greater.append(arr[i])
            else:
                middle.append(arr[i])
        merged = less + middle + greater
        for offset, value in enumerate(merged):
            arr[lo + offset] = value
            yield base_frame(
                arr,
                swapped=[lo + offset],
                pivot_index=lo + len(less),
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: writing the three-way dual-pivot partition.",
                operation="write",
                metadata={"pivot2_index": lo + len(less) + len(middle) - 1},
            )
        total = hi - lo + 1
        spans = [
            (lo, lo + len(less) - 1),
            (lo + len(less), lo + len(less) + len(middle) - 1),
            (lo + len(less) + len(middle), hi),
        ]
        for start, end in spans:
            if end - start + 1 >= total:
                yield from insertion_sort_range(arr, start, end + 1, ascending, self.name)
            else:
                yield from self._sort(arr, start, end, ascending, depth + 1)


class FluxSort(SortAlgorithm):
    name = "Fluxsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "Adaptive stable quicksort with prescans and insertion fallback."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        for i in range(max(0, len(arr) - 1)):
            yield base_frame(
                arr,
                highlighted=[i, i + 1],
                explanation=f"{self.name}: adaptive prescan for sorted or reversed input.",
                operation="compare",
                metadata={"adaptive_check": True},
            )
        if is_sorted(arr, ascending):
            yield done_frame(arr, self.name, metadata={"adaptive_check": True})
            return
        if is_sorted(arr, not ascending):
            arr[:] = reversed(arr)
            yield base_frame(
                arr,
                swapped=list(range(len(arr))),
                explanation=f"{self.name}: reversing an already opposite-ordered input.",
                operation="write",
                metadata={"adaptive_check": True},
            )
            yield done_frame(arr, self.name, metadata={"adaptive_check": True})
            return
        yield from self._stable_quick(arr, 0, len(arr), ascending, 0)
        yield done_frame(arr, self.name)

    def _stable_quick(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if hi - lo <= 1:
            return
        inversions = sum(
            1 for i in range(lo, hi - 1) if out_of_order(arr[i], arr[i + 1], ascending)
        )
        if inversions < 8:
            yield from insertion_sort_range(
                arr,
                lo,
                hi,
                ascending,
                self.name,
                metadata={"nearly_sorted_partition": True},
                explanation_prefix="using insertion sort on a nearly sorted partition; ",
            )
            return
        mid = (lo + hi - 1) // 2
        samples = [arr[lo], arr[mid], arr[hi - 1]]
        pivot = sorted_values(samples, ascending)[1]
        less: list[Any] = []
        equal: list[Any] = []
        greater: list[Any] = []
        for i in range(lo, hi):
            yield base_frame(
                arr,
                highlighted=[i],
                pivot_index=mid,
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: stable branchless-style partition around a median pivot.",
                operation="compare",
            )
            if value_of(arr[i]) == value_of(pivot):
                equal.append(arr[i])
            elif strictly_before_value(arr[i], pivot, ascending):
                less.append(arr[i])
            else:
                greater.append(arr[i])
        merged = less + equal + greater
        for offset, value in enumerate(merged):
            arr[lo + offset] = value
            yield base_frame(
                arr,
                swapped=[lo + offset],
                partition_bounds=(lo, hi - 1),
                recursion_depth=depth,
                explanation=f"{self.name}: writing a stable partition value back.",
                operation="write",
            )
        yield from self._stable_quick(arr, lo, lo + len(less), ascending, depth + 1)
        yield from self._stable_quick(arr, lo + len(less) + len(equal), hi, ascending, depth + 1)


def strictly_before_value(left: Any, right: Any, ascending: bool) -> bool:
    return value_of(left) < value_of(right) if ascending else value_of(left) > value_of(right)


class Crumsort(SortAlgorithm):
    name = "Crumsort"
    category = CATEGORY
    time_complexity = "O(n log n)"
    space_complexity = "O(log n)"
    stable = False
    description = "Unstable adaptive quicksort with prescan and merge fallback."

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        sample_indices = list(range(min(16, len(arr)))) + list(range(max(0, len(arr) - 16), len(arr)))
        ordered = 0
        for i in sample_indices:
            if i + 1 < len(arr):
                yield base_frame(
                    arr,
                    highlighted=[i, i + 1],
                    explanation=f"{self.name}: prescanning edge values for existing order.",
                    operation="compare",
                    metadata={"prescan": True},
                )
                ordered += int(in_order(arr[i], arr[i + 1], ascending))
        ratio = ordered / max(1, len(sample_indices))
        if ratio > 0.9:
            yield from bottom_up_merge_sort(arr, ascending, self.name, metadata={"prescan": True})
        else:
            yield from self._quick(arr, 0, len(arr) - 1, ascending, 0)
        yield done_frame(arr, self.name)

    def _quick(
        self, arr: list[Any], lo: int, hi: int, ascending: bool, depth: int
    ) -> Generator[SortFrame, None, None]:
        if lo >= hi:
            return
        if hi - lo + 1 <= 16:
            yield from insertion_sort_range(arr, lo, hi + 1, ascending, self.name)
            return
        mid = (lo + hi) // 2
        pivots = [lo, mid, hi]
        pivots.sort(key=lambda idx: value_of(arr[idx]), reverse=not ascending)
        pivot_idx = pivots[1]
        arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
        yield base_frame(
            arr,
            swapped=[pivot_idx, hi],
            pivot_index=hi,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: moving the median-of-3 pivot into position.",
            operation="swap",
        )
        pivot = arr[hi]
        i = lo
        for j in range(lo, hi):
            yield base_frame(
                arr,
                highlighted=[j, hi],
                pivot_index=hi,
                partition_bounds=(lo, hi),
                recursion_depth=depth,
                explanation=f"{self.name}: comparing value with the pivot.",
                operation="compare",
            )
            if in_order(arr[j], pivot, ascending):
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    yield base_frame(
                        arr,
                        swapped=[i, j],
                        pivot_index=hi,
                        partition_bounds=(lo, hi),
                        recursion_depth=depth,
                        explanation=f"{self.name}: swapping into the lower partition.",
                        operation="swap",
                    )
                i += 1
        arr[i], arr[hi] = arr[hi], arr[i]
        yield base_frame(
            arr,
            swapped=[i, hi],
            pivot_index=i,
            partition_bounds=(lo, hi),
            recursion_depth=depth,
            explanation=f"{self.name}: placing the pivot.",
            operation="swap",
        )
        yield from self._quick(arr, lo, i - 1, ascending, depth + 1)
        yield from self._quick(arr, i + 1, hi, ascending, depth + 1)


_ITEMS = [
    ("timsort", TimSort),
    ("introsort", IntroSort),
    ("fluxsort", FluxSort),
    ("crumsort", Crumsort),
    ("dual_pivot_quicksort", DualPivotQuickSort),
]

CATEGORY_ALGORITHMS = registry_from(_ITEMS)
CATEGORY_KEYS = keys_from(_ITEMS)

__all__ = [cls.__name__ for _key, cls in _ITEMS] + ["CATEGORY_ALGORITHMS", "CATEGORY_KEYS"]
