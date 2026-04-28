# sortui

`sortui` is a stdlib-only Python terminal TUI for visualizing sorting algorithms as animated bar charts.

## Install

```bash
pip install -e .
sortui
```

Python 3.10+ is supported. Runtime dependencies are intentionally zero.

## Common Commands

```bash
sortui --list
sortui --algorithm quicksort --size 80 --seed 42
sortui --distribution nearly_sorted --stability
sortui --compare bubble insertion quicksort
sortui --benchmark bubble insertion quicksort --size 500 --seed 42
sortui --benchmark bubble insertion --benchmark-export bench.json
sortui --replay ~/sortui_run_20260101_120000.json
```

## Keyboard

`SPACE` pauses, arrow keys step while paused, `R` resets, `A` toggles order, `D` cycles distributions, `V` cycles visual modes, `C` toggles comparison panels, `S` toggles stability tracking, `G` opens the fingerprint panel, `M` toggles audio, `E` exports the run, and `Q` quits.

## Feature Map

- 100+ algorithms across simple, efficient, hybrid, non-comparison, adaptive, external, parallel, string-specific, numerical, network, variant, other, and specialized categories.
- Every algorithm yields `SortFrame` objects and ends with a `done` frame.
- Input distributions include random, sorted, reverse, nearly sorted, few unique, gaussian, sawtooth, pipe organ, shuffled median, worst case, and custom arrays.
- Visual modes include bars, dots, horizontal bars, numbers, waveform, spiral, and circular projection.
- Benchmark, replay/export, stability checking, plugins, recommendations, challenges, and optional `/dev/audio` swap tones are included.

See `docs/` for algorithm notes, plugin authoring, configuration, and advanced features.

