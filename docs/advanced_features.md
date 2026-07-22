# Advanced Features

`sort-tui` is more than just a toy visualizer; it provides deep analytical tools and rich features to explore sorting mechanics.

## 📊 Benchmarking

Run algorithms headlessly and extract pure analytical data.

```bash
# Compare standard algorithms directly in the terminal
sortui --benchmark bubble insertion quicksort --size 500 --seed 42

# Export benchmark results to a JSON file and plot them (if supported)
sortui --benchmark bubble quicksort --benchmark-export results.json --complexity-plot
```
*Benchmarks run each algorithm on identical generated inputs and report median operation metrics.*

## ⚖️ Stability Tracking

Stability ensures that identical values maintain their original relative order.

To track stability, use the `--stability` flag or press `S` in the TUI. Duplicate values will be tagged with tiny visual suffixes, and the terminal footer will explicitly report any duplicate-order violations found upon completion.

## 📼 Replay and Export

Found a particularly fascinating sort progression? You can export the in-memory buffered run directly to disk.

Press `E` during the TUI to export the run to `~/sortui_run_<timestamp>.json`.

You can then replay it later identically:
```bash
sortui --replay ~/sortui_run_20260101_120000.json
```

## 🆚 Comparison Mode

Watch algorithms race!

```bash
sortui --compare bubble insertion quicksort
```
The TUI splits into vertical panes and advances all algorithms exactly one frame per tick on the exact same starting array.

## 🧬 Algorithm Fingerprinting

Press `G` during execution to open the Algorithm Genome panel. This provides a deep dive into the algorithmic behavior:

- Swap density & Comparison rate
- Data Locality
- Recursion usage
- Write intensity
- Parallelism & Adaptiveness
- Cache friendliness 
- **Fingerprint Hash**: A unique short hash identifying the algorithm's exact computational path.

## 🎵 Audio Synthesis

Hear the shape of the data. 

Press `M` inside the TUI or start the application with `--audio`. The audio engine writes PCM data mapping array element values to musical pitch directly to `/dev/audio` (it will silently no-op if hardware audio is unavailable).
