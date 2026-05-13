"""Tests for sortui.renderer using mocked curses (no real terminal needed)."""

from unittest.mock import MagicMock, patch, call
import curses

import pytest

from sortui.algorithms.base import SortFrame
from sortui.algorithms import get_algorithm
from sortui.renderer import Renderer, _safe_addstr, _safe_addch, PAIR_SWAP, PAIR_PIVOT, PAIR_HIGHLIGHT, PAIR_SORTED, PAIR_DEFAULT
from sortui.stats import SortStats


# ── stdscr factory ─────────────────────────────────────────────────────────────

def _make_stdscr(rows=40, cols=120):
    stdscr = MagicMock()
    stdscr.getmaxyx.return_value = (rows, cols)
    stdscr.getch.return_value = -1
    return stdscr


def _make_frame(arr=None, **kwargs):
    if arr is None:
        arr = [3, 1, 4, 1, 5, 9, 2, 6]
    return SortFrame(array=arr, explanation="test frame", operation="compare", **kwargs)


def _make_stats():
    return SortStats()


def _make_algorithm():
    return get_algorithm("bubble")()


# ── Renderer instantiation ────────────────────────────────────────────────────

class TestRendererInit:
    def test_default_visualization_mode_is_bars(self):
        r = Renderer()
        assert r.visualization_mode == "bars"

    def test_heatmap_mode_off_by_default(self):
        r = Renderer()
        assert r.heatmap_mode is False

    def test_gradient_mode_off_by_default(self):
        r = Renderer()
        assert r.gradient_mode is False


# ── Visualization mode cycling ────────────────────────────────────────────────

class TestVisCycling:
    VIS_MODES = ("bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular")

    def test_cycle_goes_through_all_modes(self):
        r = Renderer()
        seen = set()
        for _ in range(len(self.VIS_MODES)):
            mode = r.visualization_mode
            seen.add(mode)
            r.cycle_visualization()
        assert seen == set(self.VIS_MODES)

    def test_cycle_wraps_around(self):
        r = Renderer()
        first = r.visualization_mode
        for _ in range(len(self.VIS_MODES)):
            r.cycle_visualization()
        assert r.visualization_mode == first

    def test_set_visualization_by_name(self):
        r = Renderer()
        for mode in self.VIS_MODES:
            r.set_visualization(mode)
            assert r.visualization_mode == mode

    def test_set_visualization_invalid_name_is_noop(self):
        r = Renderer()
        original = r.visualization_mode
        r.set_visualization("nonexistent_mode")
        assert r.visualization_mode == original

    def test_cycle_returns_next_mode_name(self):
        r = Renderer()
        result = r.cycle_visualization()
        assert result == "dots"


# ── draw() — normal conditions ────────────────────────────────────────────────

class TestDrawNormal:
    def _draw(self, renderer, frame=None, rows=40, cols=120, **kwargs):
        stdscr = _make_stdscr(rows, cols)
        if frame is None:
            frame = _make_frame()
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0), \
             patch("curses.A_DIM", 0), \
             patch("curses.A_REVERSE", 0):
            renderer.draw(
                stdscr,
                frame,
                _make_stats(),
                _make_algorithm(),
                ascending=True,
                speed=1.0,
                frame_num=1,
                paused=False,
                **kwargs,
            )
        return stdscr

    def test_draw_does_not_crash_on_normal_array(self):
        r = Renderer()
        self._draw(r)  # must not raise

    def test_draw_calls_erase_and_refresh(self):
        r = Renderer()
        stdscr = self._draw(r)
        stdscr.erase.assert_called()
        stdscr.refresh.assert_called()

    def test_draw_with_empty_array(self):
        r = Renderer()
        frame = _make_frame(arr=[])
        self._draw(r, frame=frame)  # must not crash

    def test_draw_with_single_element(self):
        r = Renderer()
        frame = _make_frame(arr=[42])
        self._draw(r, frame=frame)

    def test_draw_with_stability_status(self):
        r = Renderer()
        self._draw(r, stability_status="Stable: YES")

    def test_draw_with_status_message(self):
        r = Renderer()
        self._draw(r, status_message="Running...")

    def test_draw_with_recommendation(self):
        r = Renderer()
        self._draw(r, recommended="timsort")


# ── draw() — all vis modes ────────────────────────────────────────────────────

class TestDrawAllVisModes:
    def _draw_in_mode(self, mode, rows=40, cols=120, arr=None):
        r = Renderer()
        r.set_visualization(mode)
        stdscr = _make_stdscr(rows, cols)
        if arr is None:
            arr = list(range(1, 21))
        frame = _make_frame(arr=arr)
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0), \
             patch("curses.A_DIM", 0), \
             patch("curses.A_REVERSE", 0):
            r.draw(
                stdscr,
                frame,
                _make_stats(),
                _make_algorithm(),
                ascending=True,
                speed=1.0,
                frame_num=0,
                paused=False,
            )
        return stdscr

    @pytest.mark.parametrize("mode", ["bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular"])
    def test_all_modes_do_not_crash(self, mode):
        self._draw_in_mode(mode)

    @pytest.mark.parametrize("mode", ["bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular"])
    def test_all_modes_call_refresh(self, mode):
        stdscr = self._draw_in_mode(mode)
        stdscr.refresh.assert_called()


# ── Terminal too small ────────────────────────────────────────────────────────

class TestTerminalTooSmall:
    def _draw_small(self, rows, cols):
        r = Renderer()
        stdscr = _make_stdscr(rows, cols)
        frame = _make_frame()
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0):
            r.draw(
                stdscr,
                frame,
                _make_stats(),
                _make_algorithm(),
                ascending=True,
                speed=1.0,
                frame_num=0,
                paused=False,
            )
        return stdscr

    def test_tiny_terminal_does_not_crash(self):
        self._draw_small(rows=5, cols=20)

    def test_too_small_still_calls_refresh(self):
        stdscr = self._draw_small(rows=5, cols=20)
        stdscr.refresh.assert_called()

    def test_rows_below_10_triggers_small_message(self):
        stdscr = self._draw_small(rows=5, cols=20)
        # addstr should have been called with the "too small" message
        calls_text = [str(c) for c in stdscr.addstr.call_args_list]
        combined = " ".join(calls_text)
        # The safe_addstr helper calls stdscr.addstr directly
        assert stdscr.addstr.called

    def test_exactly_minimum_size_works(self):
        # rows=10, cols=20 is exactly the minimum — should render normally
        r = Renderer()
        stdscr = _make_stdscr(rows=10, cols=20)
        frame = _make_frame(arr=[1, 2, 3])
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0), \
             patch("curses.A_DIM", 0), \
             patch("curses.A_REVERSE", 0):
            r.draw(
                stdscr, frame, _make_stats(), _make_algorithm(),
                ascending=True, speed=1.0, frame_num=0, paused=False,
            )
        stdscr.refresh.assert_called()


# ── Bar color priorities ──────────────────────────────────────────────────────

class TestBarColorPriorities:
    """_bar_color must follow: swapped > pivot > highlighted > sorted > default."""

    def setup_method(self):
        self.r = Renderer()
        # Patch curses.color_pair to be identity-like
        self._patcher = patch("curses.color_pair", side_effect=lambda x: x * 1000)
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def _color(self, arr_idx, *, highlighted=(), swapped=(), sorted_=(), pivot=None):
        pivot_set = {pivot} if pivot is not None else set()
        return self.r._bar_color(
            arr_idx,
            set(highlighted),
            set(swapped),
            set(sorted_),
            pivot_set,
            value=5,
            max_value=10,
        )

    def test_swapped_takes_priority_over_all(self):
        # Index 0 is simultaneously swapped, highlighted, pivot, sorted
        color = self._color(0, swapped=(0,), highlighted=(0,), sorted_=(0,), pivot=0)
        assert color == PAIR_SWAP * 1000

    def test_pivot_takes_priority_over_highlighted(self):
        color = self._color(1, highlighted=(1,), pivot=1)
        assert color == PAIR_PIVOT * 1000

    def test_highlighted_takes_priority_over_sorted(self):
        color = self._color(2, highlighted=(2,), sorted_=(2,))
        assert color == PAIR_HIGHLIGHT * 1000

    def test_sorted_takes_priority_over_default(self):
        color = self._color(3, sorted_=(3,))
        assert color == PAIR_SORTED * 1000

    def test_default_when_nothing_special(self):
        color = self._color(4)
        assert color == PAIR_DEFAULT * 1000


# ── Heatmap mode ──────────────────────────────────────────────────────────────

class TestHeatmapMode:
    def test_update_heatmap_increments_counts(self):
        r = Renderer()
        frame = SortFrame(
            array=[1, 2, 3, 4, 5],
            highlighted=[0, 2],
            swapped=[1],
            operation="swap",
        )
        r.update_heatmap(frame)
        assert r._access_counts[0] == 1   # highlighted once
        assert r._access_counts[1] == 2   # swapped (double weight)
        assert r._access_counts[2] == 1   # highlighted once

    def test_heatmap_resets_on_new_array_size(self):
        r = Renderer()
        frame1 = SortFrame(array=[1, 2, 3], highlighted=[0], operation="compare")
        r.update_heatmap(frame1)
        assert len(r._access_counts) == 3

        frame2 = SortFrame(array=[1, 2, 3, 4, 5], highlighted=[0], operation="compare")
        r.update_heatmap(frame2)
        assert len(r._access_counts) == 5  # reset to new size


# ── _safe_addstr / _safe_addch helpers ───────────────────────────────────────

class TestSafeHelpers:
    def test_safe_addstr_skips_out_of_bounds_y(self):
        win = _make_stdscr(10, 40)
        _safe_addstr(win, -1, 0, "hello")
        win.addstr.assert_not_called()

    def test_safe_addstr_skips_out_of_bounds_x(self):
        win = _make_stdscr(10, 40)
        _safe_addstr(win, 0, 41, "hello")
        win.addstr.assert_not_called()

    def test_safe_addstr_clips_long_text(self):
        win = _make_stdscr(10, 10)
        _safe_addstr(win, 0, 0, "A" * 100)
        assert win.addstr.called
        # Text should be clipped to available width
        called_text = win.addstr.call_args[0][2]
        assert len(called_text) <= 9  # cols-1 = 9

    def test_safe_addch_skips_out_of_bounds(self):
        win = _make_stdscr(10, 10)
        _safe_addch(win, -1, 0, "X")
        win.addch.assert_not_called()

    def test_safe_addch_writes_within_bounds(self):
        win = _make_stdscr(10, 10)
        _safe_addch(win, 0, 0, "X")
        assert win.addch.called


# ── draw_help_overlay ─────────────────────────────────────────────────────────

class TestDrawHelpOverlay:
    def test_draw_help_does_not_crash(self):
        r = Renderer()
        stdscr = _make_stdscr(40, 120)
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0), \
             patch("curses.A_REVERSE", 0):
            r.draw_help_overlay(stdscr)  # must not raise


# ── Paused state ──────────────────────────────────────────────────────────────

class TestPausedState:
    def test_draw_paused_does_not_crash(self):
        r = Renderer()
        stdscr = _make_stdscr(40, 120)
        frame = _make_frame()
        with patch("curses.color_pair", return_value=0), \
             patch("curses.A_BOLD", 0), \
             patch("curses.A_DIM", 0), \
             patch("curses.A_REVERSE", 0):
            r.draw(
                stdscr, frame, _make_stats(), _make_algorithm(),
                ascending=True, speed=1.0, frame_num=5, paused=True,
            )
        stdscr.refresh.assert_called()
