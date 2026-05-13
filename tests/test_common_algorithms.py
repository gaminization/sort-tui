"""Tests for common.py instrumented algorithm classes and make_algorithm_class factory."""

import pytest

from sortui.algorithms.base import SortFrame
from sortui.algorithms.common import (
    InstrumentedInsertionAlgorithm,
    InstrumentedMergeAlgorithm,
    InstrumentedHeapAlgorithm,
    InstrumentedCountingAlgorithm,
    InstrumentedQuickAlgorithm,
    make_algorithm_class,
    ensure_sorted_done,
    registry_from,
    keys_from,
)


# ── InstrumentedInsertionAlgorithm ────────────────────────────────────────────

class TestInstrumentedInsertionAlgorithm:
    def _cls(self):
        cls = make_algorithm_class("TestIns", "Test Insertion", "test")
        return cls

    def test_sort_produces_frames(self):
        cls = self._cls()
        frames = list(cls().sort([3, 1, 2]))
        assert len(frames) > 0
        assert all(isinstance(f, SortFrame) for f in frames)

    def test_sort_final_frame_is_done(self):
        cls = self._cls()
        frames = list(cls().sort([3, 1, 2]))
        assert frames[-1].operation == "done"

    def test_sort_result_is_sorted(self):
        cls = self._cls()
        frames = list(cls().sort([5, 3, 1, 4, 2]))
        assert frames[-1].array == [1, 2, 3, 4, 5]

    def test_sort_descending(self):
        cls = self._cls()
        frames = list(cls().sort([1, 3, 2], ascending=False))
        assert frames[-1].array == [3, 2, 1]

    def test_sort_single_element(self):
        cls = self._cls()
        frames = list(cls().sort([42]))
        assert frames[-1].array == [42]

    def test_sort_empty(self):
        cls = self._cls()
        frames = list(cls().sort([]))
        assert frames[-1].operation == "done"
        assert frames[-1].array == []

    def test_get_worst_case_array(self):
        cls = self._cls()
        worst = cls().get_worst_case_array(5)
        assert worst == list(range(5, 0, -1))

    def test_get_invariant_non_empty(self):
        cls = self._cls()
        invariant = cls().get_invariant()
        assert isinstance(invariant, str)
        assert len(invariant) > 0

    def test_metadata_with_external_flag(self):
        """external=True in metadata_defaults should set disk_op."""
        cls = make_algorithm_class(
            "ExtTest", "External Test", "external",
            metadata_defaults={"external": True},
        )
        frames = list(cls().sort([2, 1]))
        write_frames = [f for f in frames if f.operation in ("write", "done")]
        assert any(f.metadata.get("disk_op") == "write" for f in write_frames)

    def test_metadata_with_threads_int(self):
        """threads as int in metadata_defaults should be expanded to list."""
        cls = make_algorithm_class(
            "ThreadTest", "Thread Test", "parallel",
            metadata_defaults={"threads": 2},
        )
        frames = list(cls().sort([3, 1, 2]))
        # At least one frame should have threads as a list
        threaded = [f for f in frames if isinstance(f.metadata.get("threads"), list)]
        assert len(threaded) > 0


# ── InstrumentedMergeAlgorithm ────────────────────────────────────────────────

class TestInstrumentedMergeAlgorithm:
    def test_sort_produces_frames(self):
        cls = make_algorithm_class(
            "TestMerge", "Test Merge", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([5, 3, 1, 4, 2]))
        assert len(frames) > 0

    def test_sort_result_sorted(self):
        cls = make_algorithm_class(
            "TestMerge2", "Test Merge 2", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([5, 3, 1, 4, 2]))
        assert frames[-1].array == [1, 2, 3, 4, 5]

    def test_sort_empty(self):
        cls = make_algorithm_class(
            "TestMergeEmpty", "Test Merge Empty", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([]))
        assert frames[-1].operation == "done"

    def test_sort_single_element(self):
        cls = make_algorithm_class(
            "TestMergeSingle", "Test Merge Single", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([7]))
        assert frames[-1].array == [7]

    def test_sort_descending(self):
        cls = make_algorithm_class(
            "TestMergeDesc", "Test Merge Desc", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([1, 3, 2], ascending=False))
        assert frames[-1].array == [3, 2, 1]

    def test_frames_have_aux_array(self):
        cls = make_algorithm_class(
            "TestMergeAux", "Test Merge Aux", "test",
            base=InstrumentedMergeAlgorithm,
        )
        frames = list(cls().sort([4, 2, 3, 1]))
        compare_frames = [f for f in frames if f.operation == "compare"]
        assert any(f.aux_array is not None for f in compare_frames)


# ── InstrumentedHeapAlgorithm ─────────────────────────────────────────────────

class TestInstrumentedHeapAlgorithm:
    def test_sort_produces_correct_result(self):
        cls = make_algorithm_class(
            "TestHeap", "Test Heap", "test",
            base=InstrumentedHeapAlgorithm,
        )
        frames = list(cls().sort([5, 3, 1, 4, 2]))
        assert frames[-1].array == [1, 2, 3, 4, 5]

    def test_sort_descending(self):
        cls = make_algorithm_class(
            "TestHeapDesc", "Test Heap Desc", "test",
            base=InstrumentedHeapAlgorithm,
        )
        frames = list(cls().sort([1, 3, 2], ascending=False))
        assert frames[-1].array == [3, 2, 1]

    def test_sort_empty(self):
        cls = make_algorithm_class(
            "TestHeapEmpty", "Test Heap Empty", "test",
            base=InstrumentedHeapAlgorithm,
        )
        frames = list(cls().sort([]))
        assert frames[-1].operation == "done"


# ── InstrumentedQuickAlgorithm ────────────────────────────────────────────────

class TestInstrumentedQuickAlgorithm:
    def test_sort_produces_correct_result(self):
        cls = make_algorithm_class(
            "TestQuick", "Test Quick", "test",
            base=InstrumentedQuickAlgorithm,
        )
        frames = list(cls().sort([5, 3, 1, 4, 2]))
        assert frames[-1].array == [1, 2, 3, 4, 5]

    def test_sort_empty(self):
        cls = make_algorithm_class(
            "TestQuickEmpty", "Test Quick Empty", "test",
            base=InstrumentedQuickAlgorithm,
        )
        frames = list(cls().sort([]))
        assert frames[-1].operation == "done"


# ── InstrumentedCountingAlgorithm ─────────────────────────────────────────────

class TestInstrumentedCountingAlgorithm:
    def test_sort_produces_correct_result(self):
        cls = make_algorithm_class(
            "TestCounting", "Test Counting", "test",
            base=InstrumentedCountingAlgorithm,
        )
        frames = list(cls().sort([3, 1, 4, 1, 5, 9, 2, 6]))
        assert frames[-1].array == sorted([3, 1, 4, 1, 5, 9, 2, 6])

    def test_sort_empty(self):
        cls = make_algorithm_class(
            "TestCountingEmpty", "Test Counting Empty", "test",
            base=InstrumentedCountingAlgorithm,
        )
        frames = list(cls().sort([]))
        assert frames[-1].operation == "done"


# ── make_algorithm_class factory ──────────────────────────────────────────────

class TestMakeAlgorithmClass:
    def test_creates_class_with_name(self):
        cls = make_algorithm_class("MyAlgo", "My Algorithm", "test")
        assert cls.name == "My Algorithm"
        assert cls.category == "test"

    def test_creates_class_with_time_complexity(self):
        cls = make_algorithm_class("MyAlgo2", "My Algorithm 2", "test", time_complexity="O(n)")
        assert cls.time_complexity == "O(n)"

    def test_creates_class_with_space_complexity(self):
        cls = make_algorithm_class("MyAlgo3", "My Algorithm 3", "test", space_complexity="O(1)")
        assert cls.space_complexity == "O(1)"

    def test_creates_class_with_stable(self):
        cls = make_algorithm_class("MyAlgo4", "My Algorithm 4", "test", stable=True)
        assert cls.stable is True

    def test_creates_class_with_description(self):
        cls = make_algorithm_class("MyAlgo5", "My Algorithm 5", "test", description="A custom algorithm.")
        assert cls.description == "A custom algorithm."

    def test_creates_class_with_worst_case(self):
        cls = make_algorithm_class("MyAlgo6", "My Algorithm 6", "test", worst_case_input="reverse")
        assert cls.worst_case_input == "reverse"

    def test_created_class_is_instantiable(self):
        cls = make_algorithm_class("MyAlgo7", "My Algorithm 7", "test")
        obj = cls()
        assert obj is not None

    def test_default_description_includes_name(self):
        cls = make_algorithm_class("MyAlgo8", "My Awesome Sort", "test")
        assert "My Awesome Sort" in cls.description


# ── ensure_sorted_done ────────────────────────────────────────────────────────

class TestEnsureSortedDone:
    def test_ensure_sorted_done_appends_done_frame(self):
        arr = [3, 1, 2]
        frame = ensure_sorted_done(arr, ascending=True, name="TestSort")
        assert frame.operation == "done"

    def test_ensure_sorted_done_sorted_indices_cover_all(self):
        arr = [3, 1, 2, 5, 4]
        frame = ensure_sorted_done(arr, ascending=True, name="TestSort")
        assert frame.sorted_indices == list(range(len(arr)))

    def test_ensure_sorted_done_sorts_array_in_place(self):
        arr = [3, 1, 2]
        frame = ensure_sorted_done(arr, ascending=True, name="TestSort")
        assert frame.array == [1, 2, 3]

    def test_ensure_sorted_done_descending(self):
        arr = [1, 3, 2]
        frame = ensure_sorted_done(arr, ascending=False, name="TestSort")
        assert frame.array == [3, 2, 1]

    def test_ensure_sorted_done_with_metadata(self):
        arr = [2, 1]
        frame = ensure_sorted_done(arr, ascending=True, name="TestSort", metadata={"key": "val"})
        assert frame.metadata == {"key": "val"}



# ── registry_from / keys_from ─────────────────────────────────────────────────

class TestRegistryHelpers:
    def _sample_items(self):
        cls1 = make_algorithm_class("A", "Algorithm A", "test")
        cls2 = make_algorithm_class("B", "Algorithm B", "test")
        return [("algo_a", cls1), ("algo_b", cls2)]

    def test_registry_from_returns_dict(self):
        items = self._sample_items()
        reg = registry_from(items)
        assert isinstance(reg, dict)
        assert "algo_a" in reg
        assert "algo_b" in reg

    def test_keys_from_returns_list(self):
        items = self._sample_items()
        keys = keys_from(items)
        assert isinstance(keys, list)
        assert "algo_a" in keys
        assert "algo_b" in keys
