from __future__ import annotations

import curses
import time
from pathlib import Path
from typing import Optional

from sortui.algorithms import get_algorithm
from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.audio import is_available, play_note
from sortui.export import default_export_path, export_run
from sortui.genome import analyze_frames
from sortui.input_generator import InputDistribution, generate_array
from sortui.recommendation import recommendation_text
from sortui.renderer import Renderer, init_colors
from sortui.stats import SortStats
from sortui.stability import StabilityTracker, tag_duplicates
from sortui.time_travel import TimeTravelEngine

_SPEED_PRESETS: dict[int, float] = {
    ord("1"): 0.1,
    ord("2"): 0.25,
    ord("3"): 0.5,
    ord("4"): 0.75,
    ord("5"): 1.0,
    ord("6"): 2.0,
    ord("7"): 5.0,
    ord("8"): 10.0,
    ord("9"): 15.0,
}

_DISTRIBUTIONS = [dist.value for dist in InputDistribution.cycleable()]


def _make_array(size: int, distribution: str, seed: Optional[int] = None) -> list[int]:
    return generate_array(size, distribution, seed=seed)


class Controller:
    """Top-level application controller.

    Owns the :class:`TimeTravelEngine`, drives the animation loop, handles all
    keyboard input, and delegates rendering to :class:`Renderer`.
    """

    def __init__(
        self,
        algorithm_key: str = "bubble",
        speed: float = 1.0,
        ascending: bool = True,
        size: Optional[int] = None,
        seed: Optional[int] = None,
        distribution: str = "random",
        visualization_mode: str = "bars",
        custom_array: Optional[list[int]] = None,
        stability_mode: bool = False,
        replay_path: str | Path | None = None,
        compare_keys: Optional[list[str]] = None,
        audio_enabled: bool = False,
        audio_min_freq: int = 200,
        audio_max_freq: int = 1200,
    ) -> None:
        self.algorithm_key = algorithm_key
        self.speed = speed
        self.ascending = ascending
        self._size = size  # None → auto-fit to terminal width
        self.seed = seed  # The user-configured seed (may be None)
        self.distribution = distribution
        self._dist_index = (
            _DISTRIBUTIONS.index(distribution) if distribution in _DISTRIBUTIONS else 0
        )
        self.custom_array = list(custom_array) if custom_array is not None else None
        self.stability_mode = stability_mode
        self.replay_path = Path(replay_path) if replay_path is not None else None
        self._audio_enabled = bool(audio_enabled) and is_available()
        self.audio_min_freq = audio_min_freq
        self.audio_max_freq = audio_max_freq
        self.compare_keys = [
            key.lower().replace(" ", "_").replace("-", "_") for key in (compare_keys or [])
        ][:3]
        self._comparison_mode = len(self.compare_keys) >= 2
        self.paused = False
        self._show_help = False
        self._show_genome = False

        self._renderer = Renderer()
        self._renderer.set_visualization(visualization_mode)

        self._engine: Optional[TimeTravelEngine] = None
        self._compare_engines: list[TimeTravelEngine] = []
        self._compare_stats: list[SortStats] = []
        self._compare_frame_nums: list[int] = []
        self._compare_current_frames: list[Optional[SortFrame]] = []
        self._compare_algorithms: list[SortAlgorithm] = []
        self._stats: SortStats = SortStats()
        self._frame_num: int = 0
        self._current_frame: Optional[SortFrame] = None
        self._initial_array: list[int] = []
        self._stability_tracker: Optional[StabilityTracker] = None
        self._status_message: str = ""
        self._recommended: str = ""
        self._last_audio_time: float = 0.0
        # Tracks the seed actually used by the most-recent engine so that
        # Shift+R ("same seed restart") can reproduce the exact same array.
        self._last_seed: Optional[int] = seed

    # ── private helpers ────────────────────────────────────────────────────────

    def _get_algorithm(self) -> SortAlgorithm:
        cls = get_algorithm(self.algorithm_key)
        return cls()

    def _get_size(self, cols: int) -> int:
        if self._size is not None:
            return max(2, self._size)
        # Auto-size: one bar per column, leaving a 1-column margin on each side
        return max(10, cols - 2)


    def _new_engine(self, cols: int, new_seed: bool = True) -> None:
        """Tear down the current engine and create a fresh one.

        Parameters
        ----------
        cols:
            Current terminal column count, used when ``self._size`` is None.
        new_seed:
            When *True* (default) adopt ``self.seed`` as the seed for the new
            array (i.e. "reset to configured seed or random").  When *False*
            reuse ``self._last_seed`` verbatim so that the exact same array is
            reproduced (used by Shift+R and resize).
        """
        if new_seed:
            self._last_seed = self.seed  # None → fresh random each time

        alg = self._get_algorithm()
        if self.replay_path is not None:
            self._engine = TimeTravelEngine.load_replay(str(self.replay_path))
            self._stats = SortStats()
            self._frame_num = 0
            self._current_frame = None
            self._initial_array = []
            self._stability_tracker = None
            self._recommended = ""
            self._renderer._access_counts = []
            return

        if self.custom_array is not None:
            arr = list(self.custom_array)
        else:
            size = self._get_size(cols)
            arr = generate_array(size, self.distribution, seed=self._last_seed, algorithm=alg)

        if self.stability_mode:
            arr = tag_duplicates(arr)  # type: ignore[assignment]
        self._recommended = recommendation_text(arr)

        if self._comparison_mode:
            keys = self.compare_keys or [self.algorithm_key, "insertion"]
            self._compare_algorithms = [get_algorithm(key)() for key in keys[:3]]
            self._compare_engines = [
                TimeTravelEngine(algorithm, list(arr), self.ascending)
                for algorithm in self._compare_algorithms
            ]
            self._compare_stats = [SortStats() for _ in self._compare_engines]
            self._compare_frame_nums = [0 for _ in self._compare_engines]
            self._compare_current_frames = [None for _ in self._compare_engines]
            self._engine = self._compare_engines[0]
            self._stats = self._compare_stats[0]
            self._frame_num = 0
            self._current_frame = None
            self._initial_array = list(arr)
            self._stability_tracker = (
                StabilityTracker(self._initial_array) if self.stability_mode else None
            )
            self._renderer._access_counts = []
            return

        self._compare_engines = []
        self._compare_stats = []
        self._compare_frame_nums = []
        self._compare_current_frames = []
        self._compare_algorithms = []
        self._engine = TimeTravelEngine(alg, arr, self.ascending)
        self._stats = SortStats()
        self._frame_num = 0
        self._current_frame = None
        self._initial_array = list(arr)
        self._stability_tracker = StabilityTracker(self._initial_array) if self.stability_mode else None
        # Reset heatmap counters for the new array size
        self._renderer._access_counts = []

    # ── main entry point ───────────────────────────────────────────────────────

    def run(self, stdscr) -> None:  # noqa: C901  (complexity is inherent here)
        """Run the TUI main loop.  Called by :func:`curses.wrapper`."""
        init_colors()
        curses.curs_set(0)
        stdscr.nodelay(True)  # non-blocking getch
        stdscr.keypad(True)  # interpret escape sequences (arrow keys, etc.)

        _rows, cols = stdscr.getmaxyx()
        self._new_engine(cols)

        alg = self._get_algorithm()
        last_tick = time.monotonic()

        while True:
            _rows, cols = stdscr.getmaxyx()

            # ── Keyboard / resize input ────────────────────────────────────
            key = stdscr.getch()  # returns -1 immediately if no key pressed

            # ── Terminal resize ────────────────────────────────────────────
            if key == curses.KEY_RESIZE:
                # Rebuild engine for new width; keep the same seed so the
                # array shape is consistent (element count may change though).
                _rows, cols = stdscr.getmaxyx()
                self._new_engine(cols, new_seed=False)
                alg = self._get_algorithm()
                continue

            # ── Quit ───────────────────────────────────────────────────────
            elif key in (ord("q"), ord("Q"), 27):  # 27 = ESC
                # curses.wrapper restores the terminal and calls endwin().
                return

            # ── Help overlay toggle ────────────────────────────────────────
            elif key == ord("?"):
                self._show_help = not self._show_help

            # ── Pause / resume ─────────────────────────────────────────────
            elif key == ord(" "):
                self.paused = not self.paused

            # ── Step forward (paused) ──────────────────────────────────────
            elif key == curses.KEY_RIGHT and self.paused:
                if self._comparison_mode and self._compare_engines:
                    for idx, engine in enumerate(self._compare_engines):
                        f = engine.advance()
                        if f is not None:
                            self._compare_stats[idx].update(f)
                            self._compare_current_frames[idx] = f
                            self._compare_frame_nums[idx] += 1
                            self._maybe_play_audio(f)
                elif self._engine:
                    f = self._engine.advance()
                    if f is not None:
                        self._stats.update(f)
                        self._current_frame = f
                        self._frame_num += 1
                        self._maybe_play_audio(f)

            # ── Step backward (paused) ─────────────────────────────────────
            elif key == curses.KEY_LEFT and self.paused:
                if self._comparison_mode and self._compare_engines:
                    for idx, engine in enumerate(self._compare_engines):
                        f = engine.rewind()
                        if f is not None:
                            self._compare_current_frames[idx] = f
                            self._compare_frame_nums[idx] = max(
                                0, self._compare_frame_nums[idx] - 1
                            )
                elif self._engine:
                    f = self._engine.rewind()
                    if f is not None:
                        self._current_frame = f
                        self._frame_num = max(0, self._frame_num - 1)

            # ── Jump forward 10 frames (Shift+Right, paused) ───────────────
            elif key == 566 and self.paused:
                if self._engine:
                    for _ in range(10):
                        f = self._engine.advance()
                        if f is not None:
                            self._stats.update(f)
                            self._current_frame = f
                            self._frame_num += 1
                            self._maybe_play_audio(f)
                        else:
                            break

            # ── Jump backward 10 frames (Shift+Left, paused) ──────────────
            elif key == 561 and self.paused:
                if self._engine:
                    for _ in range(10):
                        f = self._engine.rewind()
                        if f is not None:
                            self._current_frame = f
                            self._frame_num = max(0, self._frame_num - 1)
                        else:
                            break

            # ── Jump to next swap (Ctrl+Right) ─────────────────────────────
            elif key == 545:
                if self._engine:
                    f = self._engine.jump_to_next_swap()
                    if f is not None:
                        self._current_frame = f
                        self._frame_num = self._engine.position
                        self._maybe_play_audio(f)

            # ── Reset / restart ────────────────────────────────────────────
            elif key in (ord("r"), ord("R")):
                if key == ord("R"):
                    # Shift+R → exact same array (same seed)
                    self._new_engine(cols, new_seed=False)
                else:
                    # r → fresh random array (discard any stored seed)
                    self._last_seed = None
                    self._new_engine(cols, new_seed=True)
                alg = self._get_algorithm()
                self.paused = False

            # ── Speed up ──────────────────────────────────────────────────
            elif key in (ord("+"), ord("=")):
                self.speed = min(self.speed * 1.5, 100.0)

            # ── Slow down ─────────────────────────────────────────────────
            elif key == ord("-"):
                self.speed = max(self.speed / 1.5, 0.01)

            # ── Speed preset (1–9) ─────────────────────────────────────────
            elif key in _SPEED_PRESETS:
                self.speed = _SPEED_PRESETS[key]

            # ── Toggle ascending / descending ──────────────────────────────
            elif key in (ord("a"), ord("A")):
                self.ascending = not self.ascending
                self._new_engine(cols, new_seed=False)
                alg = self._get_algorithm()

            # ── Cycle distribution ─────────────────────────────────────────
            elif key in (ord("d"), ord("D")):
                self._dist_index = (self._dist_index + 1) % len(_DISTRIBUTIONS)
                self.distribution = _DISTRIBUTIONS[self._dist_index]
                self.custom_array = None
                self._new_engine(cols, new_seed=False)
                alg = self._get_algorithm()

            # ── Cycle visualization mode ───────────────────────────────────
            elif key in (ord("v"), ord("V")):
                self._renderer.cycle_visualization()

            # ── Toggle heatmap ─────────────────────────────────────────────
            elif key in (ord("h"), ord("H")):
                self._renderer.heatmap_mode = not self._renderer.heatmap_mode

            # ── Toggle audio ──────────────────────────────────────────────
            elif key in (ord("m"), ord("M")):
                self._audio_enabled = not self._audio_enabled
                self._status_message = f"Audio {'on' if self._audio_enabled else 'off'}"

            # ── Toggle side-by-side comparison ───────────────────────────
            elif key in (ord("c"), ord("C")) and self.replay_path is None:
                if self._comparison_mode:
                    self._comparison_mode = False
                    self.compare_keys = []
                else:
                    fallback = "insertion" if self.algorithm_key != "insertion" else "quicksort"
                    self.compare_keys = [self.algorithm_key, fallback]
                    self._comparison_mode = True
                self._new_engine(cols, new_seed=False)
                alg = self._get_algorithm()

            # ── Toggle stability tracking ────────────────────────────────
            elif key in (ord("s"), ord("S")):
                self.stability_mode = not self.stability_mode
                self._new_engine(cols, new_seed=False)
                alg = self._get_algorithm()

            # ── Export buffered run ──────────────────────────────────────
            elif key in (ord("e"), ord("E")):
                if self._engine:
                    path = export_run(self._engine, alg, self._stats, default_export_path())
                    self._status_message = f"Exported {path}"

            # ── Toggle behavioral fingerprint overlay ───────────────────
            elif key in (ord("g"), ord("G")):
                self._show_genome = not self._show_genome

            # ── Dismiss help overlay on any other key ──────────────────────
            if self._show_help and key not in (-1, ord("?")):
                self._show_help = False

            # ── Animation tick ─────────────────────────────────────────────
            now = time.monotonic()
            # delay between frames in seconds; clamp so we never spin too fast
            frame_delay = max(0.001, 0.1 / self.speed)

            if not self.paused and (now - last_tick) >= frame_delay:
                last_tick = now
                if self._comparison_mode and self._compare_engines:
                    for idx, engine in enumerate(self._compare_engines):
                        f = engine.advance()
                        if f is not None:
                            self._compare_stats[idx].update(f)
                            self._compare_current_frames[idx] = f
                            self._compare_frame_nums[idx] += 1
                            if self._audio_enabled and hasattr(f, 'operation'):
                                if f.operation in ('swap', 'compare', 'write'):
                                    if f.highlighted and f.array:
                                        idx = f.highlighted[0]
                                        if 0 <= idx < len(f.array):
                                            arr = f.array
                                            play_note(arr[idx], min(arr), max(arr))
                    if self._compare_current_frames:
                        self._current_frame = self._compare_current_frames[0]
                        self._stats = self._compare_stats[0]
                        self._frame_num = self._compare_frame_nums[0]
                elif self._engine:
                    f = self._engine.advance()
                    if f is not None:
                        self._stats.update(f)
                        self._current_frame = f
                        self._frame_num += 1
                        if self._audio_enabled and hasattr(f, 'operation'):
                            if f.operation in ('swap', 'compare', 'write'):
                                if f.highlighted and f.array:
                                    idx = f.highlighted[0]
                                    if 0 <= idx < len(f.array):
                                        arr = f.array
                                        play_note(arr[idx], min(arr), max(arr))
                    # When the engine is exhausted we keep showing the last
                    # frame; no automatic pause so the user can still interact.

            if self._comparison_mode and self._compare_engines:
                panels = []
                for idx, algorithm in enumerate(self._compare_algorithms):
                    frame = self._compare_current_frames[idx]
                    if frame is None:
                        frame = SortFrame(
                            array=self._initial_array[:],
                            explanation="Press SPACE to start or wait...",
                        )
                    panels.append(
                        (
                            frame,
                            self._compare_stats[idx],
                            algorithm,
                            self._compare_frame_nums[idx],
                        )
                    )
                self._renderer.draw_comparison(
                    stdscr,
                    panels,
                    ascending=self.ascending,
                    speed=self.speed,
                    paused=self.paused,
                    distribution=self.distribution,
                )
                if self._show_help:
                    self._renderer.draw_help_overlay(stdscr)
                if self._show_genome and self._compare_engines:
                    report = analyze_frames(
                        getattr(self._compare_engines[0], "_history", []),
                        self._compare_stats[0],
                    )
                    self._renderer.draw_genome_overlay(stdscr, report)
                time.sleep(0.001)
                continue

            # ── Determine what to draw ─────────────────────────────────────
            if self._current_frame is not None:
                frame_to_draw = self._current_frame
            else:
                # No frame produced yet — show the initial array as a preview
                # so the screen isn't blank while the first tick is pending.
                size = self._get_size(cols)
                preview = self._initial_array or _make_array(size, self.distribution, self._last_seed)
                frame_to_draw = SortFrame(
                    array=preview[:],
                    explanation="Press SPACE to start or wait...",
                )

            stability_status = None
            if self._stability_tracker is not None:
                stability_status = self._stability_tracker.report(frame_to_draw).footer_text()

            # ── Render ─────────────────────────────────────────────────────
            self._renderer.draw(
                stdscr,
                frame_to_draw,
                self._stats,
                alg,
                self.ascending,
                self.speed,
                self._frame_num,
                self.paused,
                self.distribution,
                stability_status=stability_status,
                status_message=self._status_message,
                recommended=self._recommended,
                audio_enabled=self._audio_enabled,
            )
            if self._show_help:
                self._renderer.draw_help_overlay(stdscr)
            if self._show_genome and self._engine:
                report = analyze_frames(getattr(self._engine, "_history", []), self._stats)
                self._renderer.draw_genome_overlay(stdscr, report)

            # Yield the CPU briefly; without this the loop burns 100 % of a core.
            time.sleep(0.001)
