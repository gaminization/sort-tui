"""Targeted tests for genome.py and common.py to push coverage to 85%."""

import pytest

from sortui.algorithms.base import SortFrame
from sortui.algorithms import get_algorithm
from sortui.algorithms.common import in_order, out_of_order, sorted_copy
from sortui.genome import (
    analyze_frames,
    bar,
    format_fingerprint,
    GenomeReport,
    METRIC_NAMES,
    _clamp,
)
from sortui.stats import SortStats


# ── genome.py ─────────────────────────────────────────────────────────────────

class TestGenome:
    def _run_frames(self, key, arr):
        frames = list(get_algorithm(key)().sort(arr[:]))
        stats = SortStats()
        for f in frames:
            stats.update(f)
        return frames, stats

    def test_analyze_frames_returns_genome_report(self):
        frames, stats = self._run_frames("bubble", [3, 1, 2])
        report = analyze_frames(frames, stats)
        assert isinstance(report, GenomeReport)
        assert isinstance(report.metrics, dict)
        assert isinstance(report.fingerprint_hash, str)
        assert len(report.fingerprint_hash) == 12

    def test_all_metric_names_present(self):
        frames, stats = self._run_frames("insertion", [4, 2, 3, 1])
        report = analyze_frames(frames, stats)
        for key in METRIC_NAMES:
            assert key in report.metrics

    def test_metrics_all_in_0_1(self):
        frames, stats = self._run_frames("merge", [5, 3, 1, 4, 2])
        report = analyze_frames(frames, stats)
        for key, value in report.metrics.items():
            assert 0.0 <= value <= 1.0, f"{key}: {value} out of [0,1]"

    def test_analyze_frames_with_no_stats(self):
        frames = list(get_algorithm("bubble")().sort([2, 1]))
        report = analyze_frames(frames)  # stats=None defaults to empty SortStats
        assert report is not None

    def test_analyze_frames_empty_list(self):
        report = analyze_frames([])
        assert isinstance(report, GenomeReport)
        # frame_count defaults to max(1, 0) = 1, so no division by zero

    def test_analyze_frames_detects_parallel_metadata(self):
        frames = [
            SortFrame(array=[2, 1], operation="compare", metadata={"threads": ["w1", "w2"]}),
            SortFrame(array=[1, 2], operation="done"),
        ]
        report = analyze_frames(frames)
        assert report.metrics["parallelism"] > 0.0

    def test_analyze_frames_detects_adaptive_metadata(self):
        frames = [
            SortFrame(array=[2, 1], operation="compare", metadata={"adaptive": True}),
            SortFrame(array=[1, 2], operation="done"),
        ]
        report = analyze_frames(frames)
        assert report.metrics["adaptiveness"] > 0.0

    def test_analyze_frames_with_recursion_depth(self):
        frames = [
            SortFrame(array=[2, 1], operation="compare", recursion_depth=5),
            SortFrame(array=[1, 2], operation="done"),
        ]
        report = analyze_frames(frames)
        assert report.metrics["recursion_use"] > 0.0

    def test_bar_helper_full(self):
        result = bar(1.0)
        assert "░" not in result or result.count("█") == 8

    def test_bar_helper_empty(self):
        result = bar(0.0)
        assert "█" not in result

    def test_bar_helper_half(self):
        result = bar(0.5, width=8)
        assert len(result) == 8

    def test_clamp_clamps_above_one(self):
        assert _clamp(2.0) == 1.0

    def test_clamp_clamps_below_zero(self):
        assert _clamp(-0.5) == 0.0

    def test_clamp_passthrough(self):
        assert _clamp(0.7) == pytest.approx(0.7)

    def test_format_fingerprint_returns_list_of_strings(self):
        report = GenomeReport(
            metrics={key: 0.5 for key in METRIC_NAMES},
            fingerprint_hash="abc123456789",
        )
        lines = format_fingerprint(report)
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)

    def test_format_fingerprint_includes_hash(self):
        report = GenomeReport(
            metrics={key: 0.5 for key in METRIC_NAMES},
            fingerprint_hash="abc123456789",
        )
        lines = format_fingerprint(report)
        assert any("abc123456789" in line for line in lines)

    def test_format_fingerprint_includes_all_metrics(self):
        report = GenomeReport(
            metrics={key: 0.5 for key in METRIC_NAMES},
            fingerprint_hash="000000000000",
        )
        lines = format_fingerprint(report)
        text = " ".join(lines)
        for key in METRIC_NAMES:
            label = key.replace("_", " ").title()
            assert label in text or key in text.lower()

    def test_analyze_frames_access_distance_computed(self):
        """Frames with highlighted + swapped multiple indices should compute access distances."""
        frames = [
            SortFrame(array=[3, 1, 2], highlighted=[0, 2], swapped=[1], operation="swap"),
            SortFrame(array=[1, 2, 3], operation="done"),
        ]
        report = analyze_frames(frames)
        # memory_locality should be < 1 because we had non-adjacent accesses
        assert 0.0 < report.metrics["memory_locality"] <= 1.0

    def test_fingerprint_is_deterministic(self):
        frames, stats = self._run_frames("insertion", [4, 3, 2, 1])
        r1 = analyze_frames(frames, stats)
        r2 = analyze_frames(frames, stats)
        assert r1.fingerprint_hash == r2.fingerprint_hash


# ── common.py helpers ─────────────────────────────────────────────────────────

class TestCommonHelpers:
    def test_in_order_ascending(self):
        assert in_order(1, 2, ascending=True)
        assert in_order(2, 2, ascending=True)
        assert not in_order(3, 2, ascending=True)

    def test_in_order_descending(self):
        assert in_order(3, 2, ascending=False)
        assert in_order(2, 2, ascending=False)
        assert not in_order(1, 2, ascending=False)

    def test_out_of_order_ascending(self):
        assert out_of_order(3, 2, ascending=True)
        assert not out_of_order(1, 2, ascending=True)
        assert not out_of_order(2, 2, ascending=True)

    def test_out_of_order_descending(self):
        assert out_of_order(1, 2, ascending=False)
        assert not out_of_order(3, 2, ascending=False)

    def test_sorted_copy_ascending(self):
        arr = [3, 1, 4, 1, 5]
        result = sorted_copy(arr, ascending=True)
        assert result == sorted(arr)
        # Original unchanged
        assert arr == [3, 1, 4, 1, 5]

    def test_sorted_copy_descending(self):
        arr = [3, 1, 4, 1, 5]
        result = sorted_copy(arr, ascending=False)
        assert result == sorted(arr, reverse=True)
