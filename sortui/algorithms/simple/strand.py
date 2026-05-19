from __future__ import annotations

from typing import Generator, List

from sortui.algorithms.base import SortAlgorithm, SortFrame



def _base_frame(arr, **kwargs):
    kwargs.setdefault('explanation', 'Sorting step')
    kwargs.setdefault('operation', 'compare')
    return base_frame(arr, **kwargs)

class StrandSort(SortAlgorithm):
    name = "Strand Sort"
    category = "Simple Sorts"
    time_complexity = "O(n²)"
    space_complexity = "O(n)"
    stable = True
    description = "Extracts increasing sub-sequences (strands) and merges them into the result."
    worst_case_input = "reverse"

    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        n = len(arr)
        result: List[int] = []
        remaining = arr[:]

        def should_append(last: int, candidate: int) -> bool:
            return candidate >= last if ascending else candidate <= last

        pass_num = 0
        while remaining:
            pass_num += 1
            strand = [remaining[0]]
            new_remaining: List[int] = []
            for i in range(1, len(remaining)):
                yield SortFrame(
                    array=remaining[:] + [0] * (n - len(remaining)),
                    highlighted=[i],
                    aux_array=strand[:],
                    explanation=f"Pass {pass_num}: checking if {remaining[i]} extends strand (last={strand[-1]}).",
                    operation="compare",
                )
                if should_append(strand[-1], remaining[i]):
                    strand.append(remaining[i])
                    yield SortFrame(
                        array=remaining[:] + [0] * (n - len(remaining)),
                        swapped=[i],
                        aux_array=strand[:],
                        explanation=f"Pass {pass_num}: {remaining[i]} extends the strand.",
                        operation="write",
                    )
                else:
                    new_remaining.append(remaining[i])

            # merge strand into result
            merged: List[int] = []
            i, j = 0, 0
            while i < len(result) and j < len(strand):
                yield SortFrame(
                    array=result[:] + [0] * (n - len(result)),
                    highlighted=[i],
                    aux_array=strand[:],
                    explanation=f"Merging: comparing result[{i}]={result[i]} with strand[{j}]={strand[j]}.",
                    operation="compare",
                )
                if (result[i] <= strand[j]) if ascending else (result[i] >= strand[j]):
                    merged.append(result[i])
                    i += 1
                else:
                    merged.append(strand[j])
                    j += 1
                yield SortFrame(
                    array=merged[:] + [0] * (n - len(merged)),
                    swapped=[len(merged) - 1],
                    aux_array=strand[:],
                    explanation=f"Merging: writing the next strand-merged value at output index {len(merged) - 1}.",
                    operation="write",
                )
            while i < len(result):
                merged.append(result[i])
                i += 1
                yield SortFrame(
                    array=merged[:] + [0] * (n - len(merged)),
                    swapped=[len(merged) - 1],
                    aux_array=strand[:],
                    explanation=f"Merging: copying a remaining result value to output index {len(merged) - 1}.",
                    operation="write",
                )
            while j < len(strand):
                merged.append(strand[j])
                j += 1
                yield SortFrame(
                    array=merged[:] + [0] * (n - len(merged)),
                    swapped=[len(merged) - 1],
                    aux_array=strand[:],
                    explanation=f"Merging: copying a remaining strand value to output index {len(merged) - 1}.",
                    operation="write",
                )
            result = merged
            remaining = new_remaining

        arr[:] = result
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(n)),
            explanation="Array is fully sorted.",
            operation="done",
        )

    def get_invariant(self) -> str:
        return "result is always a sorted list of all elements extracted so far."
