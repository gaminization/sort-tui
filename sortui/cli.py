from __future__ import annotations

import argparse
import curses
import sys
from typing import Optional

from sortui import __version__
from sortui.input_generator import InputDistribution

MIN_SIZE = 2
MAX_VISUAL_SIZE = 5000
MAX_SPEED = 100.0
MAX_BENCHMARK_SIZE = 100_000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sort-tui",
        description="Terminal visualiser for sorting algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sort-tui                                     # launch with defaults
  sort-tui -a insertion -s 2.0                 # insertion sort at 2x speed
  sort-tui -a bubble -n 60                     # bubble sort with 60 elements
  sort-tui --list                              # list all algorithms
  sort-tui --order desc                        # sort descending
  sort-tui --distribution nearly_sorted -n 80  # nearly-sorted input, 80 elements
  sort-tui --seed 42 -a selection              # reproducible run
  sort-tui --input "5,3,1,4,2"                # visualise a custom array
  sort-tui --profile teaching                  # load teaching profile from config
        """,
    )

    parser.add_argument(
        "-a",
        "--algorithm",
        default=None,
        metavar="NAME",
        help="Algorithm to visualise (default: from config or 'bubble')",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Animation speed multiplier, e.g. 0.5 for half speed, 2.0 for double (default: 1.0)",
    )
    parser.add_argument(
        "-o",
        "--order",
        choices=["asc", "desc"],
        default=None,
        help="Sort order: 'asc' (ascending) or 'desc' (descending) (default: asc)",
    )
    parser.add_argument(
        "-n",
        "--size",
        type=int,
        default=None,
        metavar="INT",
        help="Number of elements to sort (default: terminal width - 2)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="INT",
        help="Random seed for reproducible array generation",
    )
    parser.add_argument(
        "--distribution",
        default=None,
        metavar="NAME",
        choices=InputDistribution.choices(),
        help=(
            "Input distribution shape (default: random). "
            "Choices: random, sorted, reverse, nearly_sorted, few_unique, "
            "gaussian, sawtooth, pipe_organ, shuffled_median, worst_case, custom"
        ),
    )
    parser.add_argument(
        "--input",
        default=None,
        metavar='"v1,v2,..."',
        help=(
            "Comma-separated list of integers to use as the initial array. "
            "Overrides --size and --distribution."
        ),
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Path to a TOML config file (default: ~/.config/sortui/config.toml)",
    )
    parser.add_argument(
        "--profile",
        default=None,
        metavar="NAME",
        help="Named profile to load from config (e.g. teaching, benchmarking, demo)",
    )
    parser.add_argument(
        "--mode",
        default=None,
        choices=["bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular"],
        help="Visualization mode (default: bars)",
    )
    parser.add_argument(
        "--gradient",
        action="store_true",
        default=False,
        help="Enable gradient color mode (bars are shaded by value height)",
    )
    parser.add_argument(
        "--heatmap",
        action="store_true",
        default=False,
        help="Enable heatmap mode (bars are shaded by access frequency)",
    )
    parser.add_argument(
        "--stability",
        action="store_true",
        default=False,
        help="Track duplicate stability with letter-tagged values",
    )
    parser.add_argument(
        "--audio",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable swap tones",
    )
    parser.add_argument(
        "--benchmark",
        nargs="*",
        metavar="ALGO",
        help="Run benchmark mode for one or more algorithms and exit",
    )
    parser.add_argument(
        "--benchmark-size",
        type=int,
        default=None,
        metavar="INT",
        help="Number of elements for benchmark and complexity-plot modes",
    )
    parser.add_argument(
        "--benchmark-export",
        default=None,
        metavar="PATH",
        help="Save benchmark results as JSON",
    )
    parser.add_argument(
        "--complexity-plot",
        action="store_true",
        default=False,
        help="Render an ASCII/braille growth curve after benchmark results",
    )
    parser.add_argument(
        "--worst-case",
        action="store_true",
        default=False,
        help="Use the selected algorithm's worst-case input distribution",
    )
    parser.add_argument(
        "--export",
        nargs="?",
        const="",
        default=None,
        metavar="PATH",
        help="Run once, export frames to JSON, and exit (default: ~/sort-tui_run_<timestamp>.json)",
    )
    parser.add_argument(
        "--replay",
        default=None,
        metavar="PATH",
        help="Replay a previously exported sortui JSON run",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        metavar="ALGO",
        help="Compare 2-3 algorithms side-by-side on the same input",
    )
    parser.add_argument(
        "--challenge",
        action="store_true",
        default=False,
        help="Run a challenge mode attempt and exit",
    )
    parser.add_argument(
        "--recommend",
        action="store_true",
        default=False,
        help="Print a recommendation for the selected/generated input and exit",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_algorithms",
        help="List all available algorithms by category and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"sort-tui {__version__}",
    )

    return parser


def _resolve(cli_val, profile_val, config_val, default):
    """Return the highest-priority non-None value: CLI > profile > config > default."""
    for candidate in (cli_val, profile_val, config_val, default):
        if candidate is not None:
            return candidate
    return default


def _normalize_key(value: str) -> str:
    return value.lower().replace(" ", "_").replace("-", "_")


def _validate_size(parser: argparse.ArgumentParser, value, flag: str, *, maximum: int) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parser.error(f"{flag} must be an integer.")
    if parsed < MIN_SIZE:
        parser.error(f"{flag} must be at least {MIN_SIZE}.")
    if parsed > maximum:
        parser.error(f"{flag} must be at most {maximum}.")
    return parsed


def _parse_custom_input(parser: argparse.ArgumentParser, raw: str | None) -> list[int] | None:
    if raw is None:
        return None
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError:
        parser.error("--input must be a comma-separated list of integers.")
    if len(values) < MIN_SIZE:
        parser.error(f"--input must contain at least {MIN_SIZE} values.")
    return values


def main() -> None:
    from pathlib import Path

    from sortui.algorithms import ALGORITHMS, list_algorithms
    from sortui.benchmark import complexity_plot, render_leaderboard, run_benchmark
    from sortui.challenge import challenge_menu, run_challenge
    from sortui.config import SortuiConfig
    from sortui.controller import Controller
    from sortui.export import default_export_path, export_run
    from sortui.input_generator import generate_array
    from sortui.plugin_loader import register_plugins
    from sortui.recommendation import recommendation_text
    from sortui.stability import tag_duplicates
    from sortui.stats import SortStats
    from sortui.time_travel import TimeTravelEngine
    from sortui.audio import is_available

    parser = build_parser()
    args = parser.parse_args()

    register_plugins()

    # ── --list ─────────────────────────────────────────────────────────────
    if args.list_algorithms:
        print(list_algorithms())
        sys.exit(0)

    # ── Load config ────────────────────────────────────────────────────────
    config_path: Optional[Path] = Path(args.config) if args.config else None
    try:
        cfg = SortuiConfig(config_path)
    except Exception as exc:
        print(f"Warning: could not load config: {exc}", file=sys.stderr)
        # Construct a bare config that will use all defaults
        cfg = SortuiConfig.__new__(SortuiConfig)
        cfg._raw = {}
        cfg._path = Path.home() / ".config" / "sort-tui" / "config.toml"

    # ── Apply profile (CLI > profile > config > hard-coded default) ────────
    profile_overrides: dict = {}
    if args.profile:
        profile_overrides = cfg.apply_profile(args.profile)
        if not profile_overrides:
            print(
                f"Warning: profile {args.profile!r} not found in config.",
                file=sys.stderr,
            )

    # ── Resolve each option ────────────────────────────────────────────────
    algorithm_key: str = _resolve(
        args.algorithm,
        profile_overrides.get("algorithm"),
        cfg.algorithm,
        "bubble",
    )

    # Normalise key (spaces/hyphens → underscores, lower-case)
    algorithm_key = _normalize_key(algorithm_key)

    raw_speed = _resolve(
        args.speed,
        profile_overrides.get("speed"),
        cfg.speed,
        1.0,
    )
    try:
        speed = float(raw_speed)
        if speed <= 0:
            raise ValueError("speed must be positive")
        if speed > MAX_SPEED:
            raise ValueError(f"speed must be <= {MAX_SPEED:g}")
    except (TypeError, ValueError) as exc:
        parser.error(f"invalid --speed value {raw_speed!r}: {exc}")

    order: str = _resolve(
        args.order,
        profile_overrides.get("order"),
        cfg.order,
        "asc",
    )
    if str(order).lower() not in {"asc", "desc"}:
        parser.error("--order must be one of: asc, desc.")
    ascending: bool = order.lower() == "asc"

    # --size: int or None (None → auto-detect from terminal width at runtime)
    size: Optional[int] = _validate_size(
        parser,
        _resolve(args.size, profile_overrides.get("size"), None, None),
        "--size",
        maximum=MAX_VISUAL_SIZE,
    )

    benchmark_size = _validate_size(
        parser,
        args.benchmark_size if args.benchmark_size is not None else None,
        "--benchmark-size",
        maximum=MAX_BENCHMARK_SIZE,
    )

    seed: Optional[int] = args.seed if args.seed is not None else cfg.seed

    distribution: str = _resolve(
        args.distribution,
        profile_overrides.get("distribution"),
        cfg.distribution,
        "random",
    )
    if args.worst_case:
        distribution = InputDistribution.WORST_CASE.value
    distribution = str(distribution).lower().replace("-", "_").replace(" ", "_")
    if distribution not in InputDistribution.choices():
        parser.error(
            f"--distribution must be one of: {', '.join(InputDistribution.choices())}."
        )

    vis_mode: str = _resolve(
        args.mode,
        profile_overrides.get("visualization_mode"),
        cfg.visualization_mode,
        "bars",
    )
    valid_modes = {"bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular"}
    if vis_mode not in valid_modes:
        parser.error(f"--mode must be one of: {', '.join(sorted(valid_modes))}.")
    audio_enabled: bool = bool(
        _resolve(
            args.audio,
            profile_overrides.get("audio_enabled", profile_overrides.get("audio")),
            cfg.audio_enabled,
            False,
        )
    )
    audio_min_freq = int(
        _resolve(None, profile_overrides.get("audio_min_freq"), cfg.audio_min_freq, 200)
    )
    audio_max_freq = int(
        _resolve(None, profile_overrides.get("audio_max_freq"), cfg.audio_max_freq, 1200)
    )

    if audio_enabled:
        if not is_available():
            print(
                "[sortui] Audio unavailable: no working ALSA/OSS device found.",
                file=sys.stderr,
            )
            audio_enabled = False

    # ── Validate algorithm ─────────────────────────────────────────────────
    if algorithm_key not in ALGORITHMS:
        available = ", ".join(sorted(ALGORITHMS.keys()))
        print(
            f"Error: unknown algorithm {algorithm_key!r}.\n"
            f"Available: {available}\n"
            f"Run `sort-tui --list` for a full listing.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Parse --input (custom array) ───────────────────────────────────────
    custom_array = _parse_custom_input(parser, args.input)
    if custom_array is not None:
        # Override size; distribution is irrelevant for a custom array
        size = len(custom_array)

    def build_array() -> list[int]:
        algorithm = ALGORITHMS[algorithm_key]()
        requested_size = size if size is not None else MIN_SIZE * 25
        if custom_array is not None:
            return list(custom_array)
        return generate_array(requested_size, distribution, seed=seed, algorithm=algorithm)

    # ── Recommendation mode ────────────────────────────────────────────────
    if args.recommend:
        print(recommendation_text(build_array()))
        sys.exit(0)

    # ── Export mode ────────────────────────────────────────────────────────
    if args.export is not None:
        algorithm = ALGORITHMS[algorithm_key]()
        setattr(algorithm, "key", algorithm_key)
        array = build_array()
        if args.stability:
            array = tag_duplicates(array)  # type: ignore[assignment]
        engine = TimeTravelEngine(algorithm, array, ascending)
        stats = SortStats()
        while True:
            frame = engine.advance()
            if frame is None:
                break
            stats.update(frame)
        export_path = default_export_path() if args.export == "" else Path(args.export)
        path = export_run(engine, algorithm, stats, export_path)
        print(f"Exported {path}")
        sys.exit(0)

    # ── Benchmark mode ────────────────────────────────────────────────────
    if args.benchmark is not None:
        benchmark_algorithms = [_normalize_key(key) for key in (args.benchmark or [algorithm_key])]
        unknown = [key for key in benchmark_algorithms if key not in ALGORITHMS]
        if unknown:
            print(
                f"Error: unknown benchmark algorithm(s): {', '.join(unknown)}.",
                file=sys.stderr,
            )
            sys.exit(1)
        resolved_benchmark_size = benchmark_size or size or cfg.benchmark_size
        try:
            results = run_benchmark(
                benchmark_algorithms,
                size=resolved_benchmark_size,
                seed=seed,
                iterations=cfg.benchmark_iterations,
                distribution=distribution,
                ascending=ascending,
                export_path=args.benchmark_export,
                live=True,
            )
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        print(render_leaderboard(results))
        if args.complexity_plot:
            print()
            print(complexity_plot(benchmark_algorithms[0], max_size=resolved_benchmark_size, seed=seed))
        sys.exit(0)

    if args.complexity_plot:
        resolved_benchmark_size = benchmark_size or size or cfg.benchmark_size
        print(complexity_plot(algorithm_key, max_size=resolved_benchmark_size, seed=seed))
        sys.exit(0)

    if args.compare:
        compare_keys = [_normalize_key(key) for key in args.compare]
        if not (2 <= len(compare_keys) <= 3):
            print("Error: --compare expects 2 or 3 algorithms.", file=sys.stderr)
            sys.exit(1)
        unknown = [key for key in compare_keys if key not in ALGORITHMS]
        if unknown:
            print(
                f"Error: unknown compare algorithm(s): {', '.join(unknown)}.",
                file=sys.stderr,
            )
            sys.exit(1)
        args.compare = compare_keys

    if args.challenge:
        print(challenge_menu())
        score = run_challenge(algorithm_key, seed=seed)
        status = "PASSED" if score["passed"] else "FAILED"
        result = score["result"]
        print(
            f"\n{status}: {algorithm_key} on {score['challenge']['name']} - "
            f"{result['wall_time_ms']:.3f}ms, {result['comparisons']} comparisons, "
            f"{result['swaps']} swaps"
        )
        sys.exit(0)

    # ── Build controller ───────────────────────────────────────────────────
    controller = Controller(
        algorithm_key=algorithm_key,
        speed=speed,
        ascending=ascending,
        size=size,
        seed=seed,
        distribution=distribution,
        visualization_mode=vis_mode,
        custom_array=custom_array,
        stability_mode=args.stability,
        replay_path=args.replay,
        compare_keys=args.compare,
        audio_enabled=audio_enabled,
        audio_min_freq=audio_min_freq,
        audio_max_freq=audio_max_freq,
    )

    # Apply flags that don't have controller constructor params
    if args.heatmap or profile_overrides.get("heatmap_mode") or cfg.heatmap_mode:
        controller._renderer.heatmap_mode = True
    if args.gradient or profile_overrides.get("gradient_mode") or cfg.gradient_mode:
        controller._renderer.gradient_mode = True

    # ── Launch TUI ─────────────────────────────────────────────────────────
    try:
        curses.wrapper(controller.run)
    except KeyboardInterrupt:
        try:
            curses.endwin()
        except curses.error:
            pass
        sys.exit(0)  # clean Ctrl-C exit — no traceback
    except Exception as exc:
        # Surface unexpected crashes outside the curses context so the
        # terminal is restored before printing the error.
        print(f"sortui crashed: {exc}", file=sys.stderr)
        raise
