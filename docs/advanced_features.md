# Advanced Features

## Benchmark

```bash
sortui --benchmark bubble insertion quicksort --size 500 --seed 42
sortui --benchmark bubble quicksort --benchmark-export results.json --complexity-plot
```

Benchmarks run each algorithm on identical generated input and report median operation metrics.

## Stability

Use `--stability` or press `S`. Duplicate values are tagged with suffixes, and the footer reports duplicate-order violations.

## Replay and Export

Press `E` to export a buffered run to `~/sortui_run_<timestamp>.json`.

```bash
sortui --replay ~/sortui_run_20260101_120000.json
```

## Comparison

```bash
sortui --compare bubble insertion quicksort
```

The TUI advances all panels one frame per tick on the same initial array.

## Fingerprint

Press `G` to show swap density, comparison rate, locality, recursion use, write intensity, parallelism, adaptiveness, cache friendliness, and a short fingerprint hash.

## Audio

Press `M` or pass `--audio`. Audio writes PCM to `/dev/audio` and silently no-ops when unavailable.

