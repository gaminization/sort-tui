"""Edge case tests: empty, single, all-equal, pre-sorted, reverse-sorted arrays."""

import pytest

from sortui.algorithms import ALGORITHMS, JOKE_ALGORITHMS
from sortui.algorithms.base import SortFrame
from sortui.algorithms import get_algorithm
from sortui.stability import StabilityTracker, tag_duplicates, stability_violations
from sortui.time_travel import TimeTravelEngine


# ── helpers ──────────────────────────────────────────────────────────────────

def _non_joke_keys():
    return [key for key in sorted(ALGORITHMS) if key not in JOKE_ALGORITHMS]


def _run(key, arr, ascending=True):
    frames = list(ALGORITHMS[key]().sort(arr[:], ascending=ascending))
    return frames


def _last(key, arr, ascending=True):
    frames = _run(key, arr, ascending)
    assert frames, f"{key}: expected at least one frame"
    return frames[-1]


# ── empty array ───────────────────────────────────────────────────────────────

class TestEmptyArray:
    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_empty_does_not_crash(self, key):
        frames = _run(key, [])
        # Must produce at least one frame (the "done" frame) and not raise
        assert isinstance(frames, list)
        assert all(isinstance(f, SortFrame) for f in frames)

    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_empty_result_is_empty(self, key):
        last = _last(key, [])
        assert last.array == [], f"{key}: empty input must yield empty array"


# ── single element ────────────────────────────────────────────────────────────

class TestSingleElement:
    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_single_element_ascending(self, key):
        last = _last(key, [42])
        assert last.array == [42], key

    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_single_element_descending(self, key):
        last = _last(key, [7], ascending=False)
        assert last.array == [7], key


# ── all-equal elements ────────────────────────────────────────────────────────

class TestAllEqual:
    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_all_equal_ascending(self, key):
        arr = [5, 5, 5, 5, 5]
        last = _last(key, arr)
        assert last.array == [5, 5, 5, 5, 5], key

    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_all_equal_descending(self, key):
        arr = [3, 3, 3]
        last = _last(key, arr, ascending=False)
        assert last.array == [3, 3, 3], key


# ── pre-sorted ────────────────────────────────────────────────────────────────

class TestPreSorted:
    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_pre_sorted_ascending(self, key):
        arr = list(range(1, 11))
        last = _last(key, arr)
        assert last.array == list(range(1, 11)), key

    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_pre_sorted_descending(self, key):
        arr = list(range(1, 11))
        last = _last(key, arr, ascending=False)
        assert last.array == list(range(10, 0, -1)), key


# ── reverse-sorted ────────────────────────────────────────────────────────────

class TestReverseSorted:
    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_reverse_sorted_ascending(self, key):
        arr = list(range(10, 0, -1))
        last = _last(key, arr)
        assert last.array == list(range(1, 11)), key

    @pytest.mark.parametrize("key", _non_joke_keys())
    def test_reverse_sorted_descending(self, key):
        arr = list(range(10, 0, -1))
        last = _last(key, arr, ascending=False)
        assert last.array == list(range(10, 0, -1)), key


# ── TimeTravelEngine edge cases ───────────────────────────────────────────────

class TestTimeTravelEdgeCases:
    def test_seek_beyond_end_returns_none(self):
        engine = TimeTravelEngine(get_algorithm("bubble")(), [3, 1, 2])
        # Exhaust the algorithm first
        while engine.advance() is not None:
            pass
        # Seeking well past the end should return None
        result = engine.seek(999_999)
        assert result is None

    def test_seek_to_last_valid_index(self):
        engine = TimeTravelEngine(get_algorithm("insertion")(), [2, 1])
        # Exhaust first
        while engine.advance() is not None:
            pass
        total = engine.buffered
        # Seek to the very last recorded frame
        frame = engine.seek(total - 1)
        assert frame is not None
        assert frame.operation == "done"

    def test_rewind_at_start_returns_none(self):
        engine = TimeTravelEngine(get_algorithm("bubble")(), [1, 2, 3])
        engine.advance()  # move to first frame
        engine.rewind()  # back to pos 0
        result = engine.rewind()  # already at start
        assert result is None

    def test_current_before_any_advance_is_none(self):
        engine = TimeTravelEngine(get_algorithm("bubble")(), [2, 1])
        assert engine.current() is None

    def test_jump_to_next_swap_finds_swap(self):
        engine = TimeTravelEngine(get_algorithm("bubble")(), [3, 1, 2])
        frame = engine.jump_to_next_swap()
        # bubble sort on [3,1,2] must perform at least one swap
        assert frame is not None
        assert frame.operation == "swap"

    def test_jump_to_next_swap_returns_none_when_done(self):
        engine = TimeTravelEngine(get_algorithm("insertion")(), [1, 2, 3])
        # Already sorted — insertion sort makes no swaps (only writes/compares)
        # Jump until exhausted
        result = None
        for _ in range(1000):
            f = engine.advance()
            if f is None:
                break
        # Now jump_to_next_swap should return None
        result = engine.jump_to_next_swap()
        assert result is None

    def test_is_done_flag(self):
        engine = TimeTravelEngine(get_algorithm("bubble")(), [2, 1])
        assert not engine.is_done
        while engine.advance() is not None:
            pass
        assert engine.is_done


# ── StabilityTracker with no duplicates ──────────────────────────────────────

class TestStabilityTrackerNoDuplicates:
    def test_no_duplicates_zero_violations(self):
        arr = [3, 1, 4, 1, 5]  # has duplicates — let's use unique values
        unique = [3, 1, 4, 2, 5]
        tracker = StabilityTracker(unique)
        # Run any stable sort
        from sortui.algorithms.efficient import MergeSort
        frames = list(MergeSort().sort(unique[:]))
        report = tracker.report(frames[-1])
        assert report.violations == 0
        assert report.stable

    def test_stability_report_none_frame(self):
        tracker = StabilityTracker([1, 2, 3])
        report = tracker.report(None)
        assert report.stable
        assert report.violations == 0

    def test_stability_violations_zero_for_unique(self):
        original = [5, 3, 1, 4, 2]
        sorted_arr = sorted(original)
        violations = stability_violations(original, sorted_arr)
        assert violations == 0

    def test_footer_text_stable(self):
        tracker = StabilityTracker([1, 2, 3])
        report = tracker.report(None)
        text = report.footer_text()
        assert "YES" in text
        assert "0 violations" in text

    def test_footer_text_unstable(self):
        # Force a violation by using tagged values in wrong order
        original = tag_duplicates([5, 5])
        # Reverse the tagged values to create a violation
        reversed_arr = list(reversed(original))
        violations = stability_violations(original, reversed_arr)
        assert violations == 1


# ── Invalid index detection (highlighted/swapped out of bounds) ───────────────

class TestInvalidIndexDetection:
    def test_frames_do_not_have_out_of_bounds_indices(self):
        """All highlighted/swapped indices must be valid array indices."""
        for key in _non_joke_keys():
            arr = [4, 2, 7, 1, 9, 3]
            frames = _run(key, arr)
            n = len(arr)
            for frame in frames:
                for idx in frame.highlighted:
                    assert 0 <= idx < n, f"{key}: highlighted index {idx} out of bounds [0,{n})"
                for idx in frame.swapped:
                    assert 0 <= idx < n, f"{key}: swapped index {idx} out of bounds [0,{n})"
