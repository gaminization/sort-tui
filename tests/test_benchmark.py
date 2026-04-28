import json

from sortui.benchmark import complexity_plot, run_benchmark


def test_benchmark_runs_and_exports_json(tmp_path):
    export_path = tmp_path / "bench.json"
    results = run_benchmark(
        ["bubble", "insertion", "quicksort"],
        size=25,
        seed=42,
        iterations=1,
        export_path=export_path,
    )
    assert len(results) == 3
    raw = json.loads(export_path.read_text())
    assert len(raw) == 3
    assert {"algorithm", "wall_time_ms", "comparisons", "swaps", "writes"} <= set(raw[0])


def test_same_seed_produces_same_deterministic_metrics():
    a = run_benchmark(["bubble", "insertion"], size=20, seed=42, iterations=1)
    b = run_benchmark(["bubble", "insertion"], size=20, seed=42, iterations=1)
    assert [(r.algorithm, r.wall_time_ms, r.comparisons, r.swaps, r.writes) for r in a] == [
        (r.algorithm, r.wall_time_ms, r.comparisons, r.swaps, r.writes) for r in b
    ]


def test_complexity_plot_returns_braille_curve():
    plot = complexity_plot("insertion", max_size=16, points=4)
    assert "curve:" in plot

