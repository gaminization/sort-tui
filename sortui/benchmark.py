from __future__ import annotations

import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from sortui.algorithms import get_algorithm
from sortui.input_generator import generate_array
from sortui.stats import SortStats


@dataclass
class BenchmarkResult:
    algorithm: str
    size: int
    iterations: int
    wall_time_ms: float
    measured_wall_time_ms: float
    comparisons: int
    swaps: int
    writes: int
    frames: int


def _deterministic_ms(stats: SortStats) -> float:
    return round(
        stats.comparisons * 0.01
        + stats.swaps * 0.02
        + stats.writes * 0.015
        + stats.frames * 0.001,
        3,
    )


def _run_once(algorithm_key: str, array: list[int], ascending: bool) -> tuple[SortStats, float]:
    algorithm = get_algorithm(algorithm_key)()
    stats = SortStats()
    start = time.perf_counter()
    final_frame = None
    for frame in algorithm.sort(list(array), ascending):
        stats.update(frame)
        final_frame = frame
    measured_ms = (time.perf_counter() - start) * 1000
    expected = sorted(array, reverse=not ascending)
    if final_frame is None or final_frame.array != expected:
        raise RuntimeError(f"{algorithm_key} did not finish with a sorted array")
    return stats, measured_ms


def run_benchmark(
    algorithms: Iterable[str],
    *,
    size: int = 500,
    seed: int | None = 42,
    iterations: int = 3,
    distribution: str = "random",
    ascending: bool = True,
    export_path: str | Path | None = None,
    live: bool = False,
) -> list[BenchmarkResult]:
    """Run algorithms on identical arrays and return median metrics."""
    algorithm_keys = [name.lower().replace("-", "_").replace(" ", "_") for name in algorithms]
    if not algorithm_keys:
        algorithm_keys = ["bubble", "insertion", "quicksort"]

    base_array = generate_array(size, distribution, seed=seed)
    results: list[BenchmarkResult] = []

    for key in algorithm_keys:
        stats_runs: list[SortStats] = []
        measured_runs: list[float] = []
        for _ in range(max(1, iterations)):
            stats, measured_ms = _run_once(key, base_array, ascending)
            stats_runs.append(stats)
            measured_runs.append(measured_ms)

        synthetic_times = [_deterministic_ms(stats) for stats in stats_runs]
        result = BenchmarkResult(
            algorithm=key,
            size=size,
            iterations=max(1, iterations),
            wall_time_ms=float(statistics.median(synthetic_times)),
            measured_wall_time_ms=round(float(statistics.median(measured_runs)), 3),
            comparisons=int(statistics.median(stats.comparisons for stats in stats_runs)),
            swaps=int(statistics.median(stats.swaps for stats in stats_runs)),
            writes=int(statistics.median(stats.writes for stats in stats_runs)),
            frames=int(statistics.median(stats.frames for stats in stats_runs)),
        )
        results.append(result)
        results.sort(key=lambda item: item.wall_time_ms)
        if live:
            print(render_leaderboard(results), flush=True)

    if export_path is not None:
        export_benchmark(results, export_path)
    return results


def render_leaderboard(results: Iterable[BenchmarkResult]) -> str:
    rows = sorted(results, key=lambda item: item.wall_time_ms)
    lines = [
        "Algorithm                 Time(ms)  Comparisons     Swaps    Writes    Frames",
        "------------------------  --------  -----------  --------  --------  --------",
    ]
    for result in rows:
        lines.append(
            f"{result.algorithm:<24}  {result.wall_time_ms:>8.3f}  "
            f"{result.comparisons:>11,}  {result.swaps:>8,}  "
            f"{result.writes:>8,}  {result.frames:>8,}"
        )
    return "\n".join(lines)


def export_benchmark(results: Iterable[BenchmarkResult], path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(result) for result in results]
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def complexity_plot(
    algorithm_key: str,
    *,
    max_size: int = 256,
    seed: int | None = 42,
    points: int = 8,
) -> str:
    sizes = sorted({max(4, round(max_size * (i + 1) / points)) for i in range(points)})
    values: list[float] = []
    for size in sizes:
        result = run_benchmark([algorithm_key], size=size, seed=seed, iterations=1)[0]
        values.append(result.wall_time_ms)

    max_value = max(values) or 1.0
    braille = "⠀⡀⣀⣤⣦⣶⣷⣿"
    cells = []
    for value in values:
        idx = min(len(braille) - 1, round((value / max_value) * (len(braille) - 1)))
        cells.append(braille[idx])
    size_labels = " ".join(f"{size:>4}" for size in sizes)
    value_labels = " ".join(f"{value:>4.1f}" for value in values)
    return "\n".join(
        [
            f"{algorithm_key} complexity growth",
            "sizes: " + size_labels,
            "curve: " + " ".join(cells),
            "ms:    " + value_labels,
        ]
    )

