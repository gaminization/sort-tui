import random

from sortui.algorithms import ALGORITHMS, JOKE_ALGORITHMS
from sortui.algorithms.base import SortFrame


def _last_frame(key, arr, ascending=True):
    frames = list(ALGORITHMS[key]().sort(arr[:], ascending=ascending))
    assert frames
    assert all(isinstance(frame, SortFrame) for frame in frames)
    return frames[-1]


def test_all_non_joke_algorithms_sort_ascending_and_descending():
    original = random.Random(42).sample(range(1, 1001), 50)
    for key in sorted(ALGORITHMS):
        if key in JOKE_ALGORITHMS:
            continue
        asc = _last_frame(key, original, True)
        assert asc.operation == "done", key
        assert asc.sorted_indices == list(range(len(original))), key
        assert asc.array == sorted(original), key

        desc = _last_frame(key, original, False)
        assert desc.operation == "done", key
        assert desc.sorted_indices == list(range(len(original))), key
        assert desc.array == sorted(original, reverse=True), key


def test_algorithm_frames_have_explanations_and_operations():
    for key in sorted(ALGORITHMS):
        if key in JOKE_ALGORITHMS:
            continue
        frames = list(ALGORITHMS[key]().sort([4, 1, 3, 2]))
        assert all(frame.explanation for frame in frames), key
        assert all(frame.operation in {"compare", "swap", "write", "read", "done"} for frame in frames), key


def test_timsort_detects_natural_runs():
    """TimSort should need fewer frames on nearly-sorted input than random."""
    from sortui.algorithms.hybrid import TimSort

    nearly = list(range(1, 51))
    nearly[10], nearly[11] = nearly[11], nearly[10]
    random_arr = random.Random(1).sample(range(1, 51), 50)
    nearly_frames = list(TimSort().sort(nearly))
    random_frames = list(TimSort().sort(random_arr))
    assert len(nearly_frames) < len(random_frames)


def test_shellsort_uses_gap_sequence():
    """ShellSort explanation must mention the gap value."""
    from sortui.algorithms.efficient import ShellSort

    frames = list(ShellSort().sort([5, 3, 8, 1, 4, 9, 2, 7, 6]))
    compare_frames = [f for f in frames if f.operation == "compare"]
    assert any("gap" in f.explanation.lower() for f in compare_frames)


def test_radix_lsd_uses_digit_metadata():
    from sortui.algorithms.non_comparison import RadixLSDSort

    frames = list(RadixLSDSort().sort([170, 45, 75, 90, 802, 24, 2, 66]))
    assert any(f.metadata.get("digit_position") is not None for f in frames)


def test_counting_sort_uses_aux_array():
    from sortui.algorithms.non_comparison import CountingSort

    frames = list(CountingSort().sort([3, 1, 4, 1, 5, 9, 2, 6]))
    assert any(f.aux_array is not None for f in frames)


def test_dual_pivot_quicksort_has_two_pivots():
    from sortui.algorithms.hybrid import DualPivotQuickSort

    frames = list(DualPivotQuickSort().sort([5, 3, 8, 1, 4, 9, 2, 7, 6]))
    assert any(f.metadata.get("pivot2_index") is not None for f in frames)


def test_introsort_switches_to_heapsort():
    from sortui.algorithms.hybrid import IntroSort

    arr = list(range(100))
    frames = list(IntroSort().sort(arr))
    assert any(f.metadata.get("fallback") == "heapsort" for f in frames)


def test_grailsort_has_buffer_phase():
    from sortui.algorithms.adaptive import GrailSort

    frames = list(GrailSort().sort(random.Random(42).sample(range(1, 51), 50)))
    phases = {f.metadata.get("phase") for f in frames if f.metadata}
    assert "collect" in phases or "merge" in phases


def test_external_merge_has_disk_metadata():
    from sortui.algorithms.external import ExternalMergeSort

    frames = list(ExternalMergeSort().sort(list(range(20, 0, -1))))
    assert any(f.metadata.get("disk_op") for f in frames)


def test_parallel_sorts_have_thread_metadata():
    from sortui.algorithms.parallel import ParallelMergeSort

    frames = list(ParallelMergeSort().sort([5, 3, 8, 1, 4, 9, 2, 7]))
    assert any(isinstance(f.metadata.get("threads"), list) for f in frames)


def test_bitonic_network_is_deterministic():
    from sortui.algorithms.network import BitonicMergeNetworkSort

    arr = [5, 3, 8, 1, 4, 9, 2, 7]
    a = list(BitonicMergeNetworkSort().sort(arr[:]))[-1].array
    b = list(BitonicMergeNetworkSort().sort(arr[:]))[-1].array
    assert a == b == sorted(arr)
