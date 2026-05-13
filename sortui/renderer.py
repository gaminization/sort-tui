from __future__ import annotations

import curses

from sortui.algorithms.base import SortAlgorithm, SortFrame
from sortui.stats import SortStats

# ── Color pair constants ───────────────────────────────────────────────────────
PAIR_DEFAULT = 1  # white  — normal bar
PAIR_HIGHLIGHT = 2  # yellow — compare / highlighted
PAIR_SWAP = 3  # red    — swapped indices
PAIR_SORTED = 4  # green  — confirmed sorted
PAIR_PIVOT = 5  # cyan   — pivot element
PAIR_HEADER = 6  # black on white — header bar
PAIR_DIM = 7  # dark   — controls row
PAIR_GRAD_LOW = 8
PAIR_GRAD_MID = 9
PAIR_GRAD_HIGH = 10


def init_colors() -> None:
    """Initialise all curses color pairs.  Must be called after curses.initscr()."""
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(PAIR_DEFAULT, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_HIGHLIGHT, curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_SWAP, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_SORTED, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_PIVOT, curses.COLOR_CYAN, -1)
    curses.init_pair(PAIR_HEADER, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # DIM pair: bright black (dark gray) when available, plain black otherwise
    dim_fg = (curses.COLOR_BLACK + 8) if curses.COLORS >= 16 else curses.COLOR_BLACK
    curses.init_pair(PAIR_DIM, dim_fg, -1)
    curses.init_pair(PAIR_GRAD_LOW, curses.COLOR_BLUE, -1)
    curses.init_pair(PAIR_GRAD_MID, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_GRAD_HIGH, curses.COLOR_RED, -1)


# ── Low-level drawing helper ───────────────────────────────────────────────────


def _safe_addstr(win, y: int, x: int, text: str, attr: int = 0) -> None:
    """Write *text* at (y, x) clipping at the right edge; swallows all curses errors."""
    max_y, max_x = win.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x >= max_x:
        return
    available = max_x - x - 1  # leave the very last cell untouched (curses safety)
    if available <= 0:
        return
    clipped = text[:available]
    if not clipped:
        return
    try:
        win.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def _safe_addch(win, y: int, x: int, ch: str, attr: int = 0) -> None:
    """Write a single character safely."""
    max_y, max_x = win.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x >= max_x - 1:
        return
    try:
        win.addch(y, x, ch, attr)
    except curses.error:
        pass


# ── Main renderer class ────────────────────────────────────────────────────────


class Renderer:
    """Stateful curses renderer for sortui.

    One instance lives for the lifetime of the TUI session.  The only public
    drawing methods are :meth:`draw` and :meth:`draw_help_overlay`.
    """

    _VIS_MODES = ("bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular")

    def __init__(self) -> None:
        self._vis_index: int = 0
        self.heatmap_mode: bool = False
        self.gradient_mode: bool = False
        self._access_counts: list[int] = []

    # ── Visualization mode ─────────────────────────────────────────────────

    @property
    def visualization_mode(self) -> str:
        return self._VIS_MODES[self._vis_index]

    def cycle_visualization(self) -> str:
        """Advance to the next visualization mode and return its name."""
        self._vis_index = (self._vis_index + 1) % len(self._VIS_MODES)
        return self.visualization_mode

    def set_visualization(self, mode: str) -> None:
        if mode in self._VIS_MODES:
            self._vis_index = self._VIS_MODES.index(mode)

    # ── Heatmap bookkeeping ────────────────────────────────────────────────

    def update_heatmap(self, frame: SortFrame) -> None:
        n = len(frame.array)
        if len(self._access_counts) != n:
            self._access_counts = [0] * n
        for idx in frame.highlighted:
            if 0 <= idx < n:
                self._access_counts[idx] += 1
        for idx in frame.swapped:
            if 0 <= idx < n:
                self._access_counts[idx] += 2  # swaps count double

    # ── Color selection ────────────────────────────────────────────────────

    def _bar_color(
        self,
        arr_idx: int,
        highlighted_set: set[int],
        swapped_set: set[int],
        sorted_set: set[int],
        pivot_set: set[int],
        value: int = 0,
        max_value: int = 1,
    ) -> int:
        """Return the curses color-pair attribute for one bar element."""
        if self.heatmap_mode and self._access_counts:
            max_a = max(self._access_counts) or 1
            access = self._access_counts[arr_idx] if arr_idx < len(self._access_counts) else 0
            intensity = access / max_a
            if intensity > 0.66:
                return curses.color_pair(PAIR_SWAP)
            elif intensity > 0.33:
                return curses.color_pair(PAIR_HIGHLIGHT)
            else:
                return curses.color_pair(PAIR_DEFAULT)

        if arr_idx in swapped_set:
            return curses.color_pair(PAIR_SWAP)
        if arr_idx in pivot_set:
            return curses.color_pair(PAIR_PIVOT)
        if arr_idx in highlighted_set:
            return curses.color_pair(PAIR_HIGHLIGHT)
        if arr_idx in sorted_set:
            return curses.color_pair(PAIR_SORTED)
        if self.gradient_mode:
            ratio = int(value) / max(1, int(max_value))
            if ratio >= 0.66:
                return curses.color_pair(PAIR_GRAD_HIGH)
            if ratio >= 0.33:
                return curses.color_pair(PAIR_GRAD_MID)
            return curses.color_pair(PAIR_GRAD_LOW)
        return curses.color_pair(PAIR_DEFAULT)

    # ── Main draw call ─────────────────────────────────────────────────────

    def draw(
        self,
        stdscr,
        frame: SortFrame,
        stats: SortStats,
        algorithm: SortAlgorithm,
        ascending: bool,
        speed: float,
        frame_num: int,
        paused: bool,
        distribution: str = "random",
        stability_status: str | None = None,
        status_message: str = "",
        recommended: str | None = None,
        audio_enabled: bool = False,
    ) -> None:
        """Render one complete frame to *stdscr*."""
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()

        # ── Minimum-size guard ──────────────────────────────────────────
        if rows < 10 or cols < 20:
            _safe_addstr(
                stdscr,
                0,
                0,
                "Terminal too small — please resize (min 20×10)",
                curses.A_BOLD | curses.color_pair(PAIR_SWAP),
            )
            stdscr.refresh()
            return

        arr = frame.array
        n = len(arr)

        # Update heatmap counters before drawing
        if self.heatmap_mode:
            self.update_heatmap(frame)

        # ── Row budget ──────────────────────────────────────────────────
        # Row 0            : header
        # Rows 1..rows-4   : bar chart  (at least 2 rows)
        # Row rows-3       : explanation
        # Row rows-2       : stats
        # Row rows-1       : controls
        FOOTER_ROWS = 3
        HEADER_ROWS = 1
        chart_top = HEADER_ROWS
        chart_bottom = rows - FOOTER_ROWS - 1  # inclusive
        chart_height = chart_bottom - chart_top + 1

        # ── Header ──────────────────────────────────────────────────────
        order_str = "↑ ASC" if ascending else "↓ DESC"
        pause_flag = "  ⏸ PAUSED" if paused else ""
        alg_name = getattr(algorithm, "name", type(algorithm).__name__)
        header_str = (
            f" sortui │ {alg_name} │ n={n} │ {order_str} │ "
            f"{speed:.1f}x │ {distribution} │ frame {frame_num}"
            f"{pause_flag} "
        )
        if recommended:
            header_str += f"│ Recommended: {recommended} "
        _safe_addstr(
            stdscr,
            0,
            0,
            header_str.ljust(cols - 1),
            curses.color_pair(PAIR_HEADER) | curses.A_BOLD,
        )

        # ── Bar chart ────────────────────────────────────────────────────
        if chart_height < 2 or n == 0:
            stdscr.refresh()
            return

        # How many bars fit horizontally?  Each bar is 1 column wide, leaving
        # column 0 as a 1-cell left margin.
        max_bars = cols - 2  # col 0 margin + col cols-1 safety
        num_bars = min(n, max_bars)

        # Map bar positions → array indices  (sub-sample when n > max_bars)
        if n > num_bars:
            indices = [int(i * n / num_bars) for i in range(num_bars)]
        else:
            indices = list(range(n))
            num_bars = n

        max_val = max(int(value) for value in arr) if arr else 1
        if max_val <= 0:
            max_val = 1

        # Pre-build sets for O(1) membership tests
        highlighted_set: set[int] = set(frame.highlighted)
        swapped_set: set[int] = set(frame.swapped)
        sorted_set: set[int] = set(frame.sorted_indices)
        pivot_set: set[int] = {frame.pivot_index} if frame.pivot_index is not None else set()

        # Choose effective mode (fall back for large n)
        mode = self.visualization_mode
        if mode == "numbers" and n > 40:
            mode = "bars"

        for bar_i in range(num_bars):
            arr_idx = indices[bar_i]
            val = int(arr[arr_idx])
            bar_x = bar_i + 1  # 1-indexed (column 0 is margin)

            pair = self._bar_color(
                arr_idx,
                highlighted_set,
                swapped_set,
                sorted_set,
                pivot_set,
                val,
                max_val,
            )

            if mode == "bars":
                bar_height = max(1, int(val * chart_height / max_val))
                for row_offset in range(chart_height):
                    row = chart_bottom - row_offset
                    if row < chart_top:
                        break
                    _safe_addch(
                        stdscr,
                        row,
                        bar_x,
                        "█" if row_offset < bar_height else " ",
                        pair,
                    )

            elif mode == "dots":
                # Draw a single dot at the tip of the logical bar
                dot_row = chart_bottom - max(1, int(val * chart_height / max_val)) + 1
                dot_row = max(chart_top, min(chart_bottom, dot_row))
                _safe_addch(stdscr, dot_row, bar_x, "•", pair | curses.A_BOLD)

            elif mode == "horizontal":
                # One row per element when array fits in chart_height; else vertical
                if num_bars <= chart_height:
                    row = chart_top + bar_i
                    if row > chart_bottom:
                        break
                    bar_width = max(1, int(val * (cols - 4) / max_val))
                    for bx in range(bar_width):
                        col = 2 + bx
                        if col >= cols - 1:
                            break
                        _safe_addch(stdscr, row, col, "█", pair)
                else:
                    # Fall through to vertical bars
                    bar_height = max(1, int(val * chart_height / max_val))
                    for row_offset in range(chart_height):
                        row = chart_bottom - row_offset
                        if row < chart_top:
                            break
                        _safe_addch(
                            stdscr,
                            row,
                            bar_x,
                            "█" if row_offset < bar_height else " ",
                            pair,
                        )

            elif mode == "numbers":
                # Place the last digit at the bar tip
                bar_height = max(1, int(val * chart_height / max_val))
                tip_row = chart_bottom - bar_height + 1
                tip_row = max(chart_top, min(chart_bottom, tip_row))
                _safe_addch(stdscr, tip_row, bar_x, str(val % 10), pair | curses.A_BOLD)

            elif mode == "waveform":
                tip_row = chart_bottom - max(1, int(val * chart_height / max_val)) + 1
                tip_row = max(chart_top, min(chart_bottom, tip_row))
                prev_idx = indices[bar_i - 1] if bar_i > 0 else arr_idx
                prev_val = int(arr[prev_idx])
                prev_row = chart_bottom - max(1, int(prev_val * chart_height / max_val)) + 1
                if tip_row < prev_row:
                    ch = "╱"
                elif tip_row > prev_row:
                    ch = "╲"
                else:
                    ch = "─"
                _safe_addch(stdscr, tip_row, bar_x, ch, pair | curses.A_BOLD)

            elif mode == "spiral":
                row = chart_top + int((bar_i / max(1, num_bars - 1)) * (chart_height - 1))
                wobble = int((val / max_val) * 3)
                col = min(cols - 2, max(1, bar_x + ((bar_i % 6) - 3) + wobble))
                _safe_addch(stdscr, row, col, "•", pair | curses.A_BOLD)

            elif mode == "circular":
                import math

                theta = math.pi * (bar_i / max(1, num_bars - 1))
                radius_x = max(2, (cols - 4) // 2)
                radius_y = max(1, chart_height - 1)
                col = int((cols // 2) - math.cos(theta) * radius_x)
                row = int(chart_bottom - math.sin(theta) * radius_y * (val / max_val))
                row = max(chart_top, min(chart_bottom, row))
                col = max(1, min(cols - 2, col))
                _safe_addch(stdscr, row, col, "•", pair | curses.A_BOLD)

        # ── Partition bounds highlight ──────────────────────────────────
        # Draw faint bracket markers when the algorithm supplies them
        if frame.partition_bounds is not None:
            lo, hi = frame.partition_bounds
            for bound_idx in (lo, hi):
                bx = bound_idx + 1
                if 0 < bx < cols - 1:
                    # Mark top row of chart with a dim '|'
                    _safe_addch(
                        stdscr,
                        chart_top,
                        bx,
                        "│",
                        curses.color_pair(PAIR_DIM) | curses.A_DIM,
                    )

        # ── Explanation row ─────────────────────────────────────────────
        expl_row = rows - FOOTER_ROWS
        expl_text = frame.explanation or ""
        # Optionally append the algorithm's invariant if it fits
        invariant = algorithm.get_invariant()
        if invariant and not expl_text:
            expl_text = invariant
        _safe_addstr(
            stdscr,
            expl_row,
            0,
            f" {expl_text}".ljust(cols - 1),
            curses.color_pair(PAIR_DEFAULT),
        )

        # ── Stats row ───────────────────────────────────────────────────
        stats_row = rows - 2
        stats_str = (
            f" Comparisons: {stats.comparisons:,}  "
            f"Swaps: {stats.swaps:,}  "
            f"Writes: {stats.writes:,}  "
            f"Time: {stats.elapsed_ms():.0f}ms  "
            f"Frames: {stats.frames:,}"
        )
        if stability_status:
            stats_str += f"  {stability_status}"
        if status_message:
            stats_str += f"  {status_message}"
        _safe_addstr(
            stdscr,
            stats_row,
            0,
            stats_str.ljust(cols - 1),
            curses.color_pair(PAIR_DEFAULT),
        )

        # ── Controls row ────────────────────────────────────────────────
        ctrl_row = rows - 1
        ctrl_str = (
            " [SPC] Pause  [→] Step  [←] Back  [R] Reset  [Q] Quit  [+/-] Speed  [V] View  [S] Stable  [M] Audio  [E] Export  [?] Help"
        )
        audio_str = "[audio: ON]" if audio_enabled else "[audio: OFF]"
        
        # Draw controls on the left, audio on the right
        _safe_addstr(
            stdscr,
            ctrl_row,
            0,
            ctrl_str[: cols - len(audio_str) - 2].ljust(cols - len(audio_str) - 1) + audio_str + " ",
            curses.color_pair(PAIR_DIM) | curses.A_DIM,
        )

        stdscr.refresh()

    # ── Comparison draw call ──────────────────────────────────────────────

    def draw_comparison(
        self,
        stdscr,
        panels: list[tuple[SortFrame, SortStats, SortAlgorithm, int]],
        *,
        ascending: bool,
        speed: float,
        paused: bool,
        distribution: str = "random",
    ) -> None:
        """Render two or three synchronized algorithms side-by-side."""
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()
        if not panels:
            stdscr.refresh()
            return
        count = min(3, len(panels))
        panel_w = max(10, cols // count)
        for idx, (frame, stats, algorithm, frame_num) in enumerate(panels[:count]):
            left = idx * panel_w
            right = cols - 1 if idx == count - 1 else (idx + 1) * panel_w - 1
            width = max(2, right - left)
            if idx > 0:
                for y in range(rows):
                    _safe_addch(stdscr, y, left, "│", curses.color_pair(PAIR_DIM))
            title = f" {getattr(algorithm, 'name', type(algorithm).__name__)} f{frame_num} "
            _safe_addstr(stdscr, 0, left + 1, title[: width - 2], curses.color_pair(PAIR_HEADER))

            arr = frame.array
            if not arr:
                continue
            chart_top = 1
            chart_bottom = max(chart_top, rows - 4)
            chart_height = max(1, chart_bottom - chart_top + 1)
            max_val = max(int(value) for value in arr) or 1
            slots = min(len(arr), max(1, width - 2))
            indices = [int(i * len(arr) / slots) for i in range(slots)]
            highlighted = set(frame.highlighted)
            swapped = set(frame.swapped)
            sorted_set = set(frame.sorted_indices)
            pivot = {frame.pivot_index} if frame.pivot_index is not None else set()
            for bar_i, arr_idx in enumerate(indices):
                val = int(arr[arr_idx])
                pair = self._bar_color(arr_idx, highlighted, swapped, sorted_set, pivot, val, max_val)
                height = max(1, int(val * chart_height / max_val))
                x = left + 1 + bar_i
                for offset in range(height):
                    _safe_addch(stdscr, chart_bottom - offset, x, "█", pair)

            footer = (
                f" {stats.comparisons:,} cmp {stats.swaps:,} swp "
                f"{stats.writes:,} wr {speed:.1f}x"
            )
            if paused:
                footer += " PAUSED"
            _safe_addstr(stdscr, rows - 2, left + 1, footer[: width - 2])
            _safe_addstr(stdscr, rows - 1, left + 1, f" {distribution}"[: width - 2])
        stdscr.refresh()

    def draw_genome_overlay(self, stdscr, report) -> None:
        """Draw the post-sort behavioral fingerprint panel."""
        from sortui.genome import format_fingerprint

        rows, cols = stdscr.getmaxyx()
        lines = format_fingerprint(report)
        box_w = min(cols - 2, max(len(line) for line in lines) + 6)
        box_h = min(rows - 2, len(lines) + 4)
        start_y = max(1, (rows - box_h) // 2)
        start_x = max(1, (cols - box_w) // 2)
        attr = curses.color_pair(PAIR_HEADER) | curses.A_BOLD
        for dy in range(box_h):
            _safe_addstr(stdscr, start_y + dy, start_x, " " * (box_w - 1), attr)
        _safe_addstr(stdscr, start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", attr)
        _safe_addstr(stdscr, start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", attr)
        for idx, line in enumerate(lines[: box_h - 2]):
            _safe_addstr(
                stdscr,
                start_y + 1 + idx,
                start_x,
                "│ " + line[: box_w - 4].ljust(box_w - 4) + " │",
                attr,
            )
        stdscr.refresh()

    # ── Help overlay ───────────────────────────────────────────────────────

    def draw_help_overlay(self, stdscr) -> None:
        """Draw a centred modal help overlay on top of the current frame."""
        rows, cols = stdscr.getmaxyx()

        help_lines = [
            "─── KEYBOARD SHORTCUTS ─────────────────────────",
            "  SPACE        Pause / Resume",
            "  →            Step forward one frame (paused)",
            "  ←            Step backward one frame (paused)",
            "  Shift+→      Jump forward 10 frames  (paused)",
            "  Shift+←      Jump back 10 frames     (paused)",
            "  Ctrl+→       Jump to next swap",
            "  R            New random array",
            "  Shift+R      Restart with same seed",
            "  +  /  =      Increase speed ×1.5",
            "  -            Decrease speed ÷1.5",
            "  1 – 9        Speed preset",
            "  A            Toggle ASC / DESC order",
            "  V            Cycle visualization mode",
            "  H            Toggle heatmap overlay",
            "  M            Toggle audio",
            "  D            Cycle input distribution",
            "  C            Toggle comparison panels",
            "  S            Toggle stability tracking",
            "  E            Export buffered run as JSON",
            "  G            Toggle fingerprint panel",
            "  Q / ESC      Quit",
            "  ?            Toggle this help panel",
            "─────────────────────────────────────────────────",
            "  Press any key to dismiss",
        ]

        box_w = max(len(line) for line in help_lines) + 6
        box_h = len(help_lines) + 4
        start_y = max(1, (rows - box_h) // 2)
        start_x = max(1, (cols - box_w) // 2)

        # Background fill
        bg_attr = curses.color_pair(PAIR_HEADER) | curses.A_BOLD
        for dy in range(box_h):
            row = start_y + dy
            if row >= rows - 1:
                break
            _safe_addstr(stdscr, row, start_x, " " * min(box_w, cols - start_x - 1), bg_attr)

        # Top and bottom border
        border_top = "╔" + "═" * (box_w - 2) + "╗"
        border_bottom = "╚" + "═" * (box_w - 2) + "╝"
        _safe_addstr(stdscr, start_y, start_x, border_top, bg_attr)
        _safe_addstr(stdscr, start_y + box_h - 1, start_x, border_bottom, bg_attr)

        # Content rows
        for i, line in enumerate(help_lines):
            row = start_y + 2 + i
            if row >= rows - 1:
                break
            padded = "║  " + line.ljust(box_w - 5) + "║"
            _safe_addstr(stdscr, row, start_x, padded, bg_attr)

        stdscr.refresh()
