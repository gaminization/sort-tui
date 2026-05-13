# sortui

[![CI](https://github.com/yourusername/sortui/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/sortui/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/sortui)](https://pypi.org/project/sortui/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/sortui.svg)](https://badge.fury.io/py/sortui)

A high-performance, purely terminal-based educational visualizer for 110 sorting algorithms.

## Installation

```bash
pip install sortui
```

## Quick Start

```bash
# Visualize a standard Bubble Sort interactively
sortui --algorithm bubble

# Test TimSort on a nearly sorted array
sortui --algorithm timsort --distribution nearly_sorted --size 100

# Compare Quicksort, Merge Sort, and Heapsort side-by-side
sortui --compare quicksort merge heapsort

# Run headless benchmarking
sortui --benchmark bubble insertion quicksort --size 500
```

## Hotkeys

`sortui` is fully interactive during a visualization. 

| Key(s) | Action |
| --- | --- |
| `SPACE` | Pause / Resume |
| `→` / `←` | Step forward / backward one frame (paused) |
| `Shift+→` / `Shift+←` | Jump forward / backward 10 frames (paused) |
| `Ctrl+→` | Jump to next swap |
| `R` | Reload with a new random array |
| `Shift+R` | Restart current algorithm with the exact same starting array |
| `+` / `-` | Increase / Decrease simulation speed |
| `1` - `9` | Speed presets (1=slow, 9=fastest) |
| `A` | Toggle ascending / descending order target |
| `V` | Cycle visualization mode (Bars, Dots, etc.) |
| `H` | Toggle heatmap overlay (tracks array access frequency) |
| `M` | Toggle audio (pitch mapping based on array values) |
| `D` | Cycle input array distribution |
| `C` | Toggle side-by-side comparison mode |
| `S` | Toggle stability tracking |
| `E` | Export buffered run as a JSON replay |
| `G` | Toggle behavioral fingerprint panel (Algorithm Genome) |
| `?` | Toggle help panel |
| `Q` / `ESC` | Quit |

## Visualization Modes

Press `V` during playback to cycle through these render styles.

| Mode | Description |
| --- | --- |
| `bars` | Standard vertical bar chart (height proportional to value). |
| `dots` | Single dot plotted at the tip of where the bar would be. |
| `horizontal` | Horizontal bar chart flowing downwards. |
| `numbers` | Renders the last digit of the value at the tip of the bar. |
| `waveform` | Connects the tips of the bars to form a continuous line graph. |
| `spiral` | Plots elements as a density-mapped spiral point cloud. |
| `circular` | Renders the array in a circular clock-face orientation. |

## Input Distributions

Press `D` or pass `--distribution` to alter the array structure before sorting.

| Distribution | Description |
| --- | --- |
| `random` | Uniformly distributed random integers. |
| `sorted` | Already sorted in ascending order. |
| `reverse` | Already sorted in descending order. |
| `nearly_sorted` | Sorted array with 5% of elements randomly displaced. |
| `few_unique` | An array composed of only 5 unique distinct values. |
| `gaussian` | Normally distributed values clustered around the median. |
| `sawtooth` | Repeating ascending sequences of small periods. |
| `pipe_organ` | Ascending then descending values shaped like an arch. |
| `shuffled_median` | Median extracted values with 20% random shuffle. |
| `worst_case` | An algorithm-specific worst-case input topology. |
| `custom` | A user-defined CSV array passed via CLI `--custom`. |

## Algorithm Catalog

`sortui` bundles 110 unique sorting algorithms organized into academic categories.

| Category | Count |
| --- | --- |
| Simple Sorts | 9 |
| Efficient Sorts | 13 |
| Hybrid Sorts | 5 |
| Non-Comparison Sorts | 10 |
| Adaptive Sorts | 9 |
| External Sorts | 6 |
| Parallel Sorts | 10 |
| String-Specific Sorts | 4 |
| Numerical Sorts | 4 |
| Sorting Networks | 3 |
| Hybrid Variants | 7 |
| Other Sorts | 6 |
| Specialized / Joke Sorts | 24 |

## Benchmarks

Results of `sortui --benchmark <algorithms> --size 500 --seed 42`:

| Algorithm | Time(ms) | Comparisons | Swaps | Writes | Frames |
| --- | --- | --- | --- | --- | --- |
| counting | 9.001 | 0 | 0 | 500 | 1,501 |
| radix_msd | 25.467 | 0 | 0 | 1,498 | 2,997 |
| radix_lsd | 25.501 | 0 | 0 | 1,500 | 3,001 |
| quicksort | 93.055 | 4,575 | 2,019 | 0 | 6,925 |
| bucket | 97.112 | 3,231 | 0 | 3,787 | 7,997 |
| introsort | 105.486 | 4,430 | 1,480 | 1,579 | 7,901 |
| merge | 114.212 | 3,849 | 0 | 4,492 | 8,342 |
| dual_pivot_quicksort | 131.000 | 4,808 | 0 | 4,852 | 10,140 |
| comb | 141.879 | 9,370 | 1,848 | 0 | 11,219 |
| pdqsort | 143.260 | 6,624 | 3,200 | 197 | 10,065 |
| shellsort | 158.952 | 5,633 | 0 | 5,876 | 14,482 |
| heapsort | 167.553 | 7,462 | 4,070 | 0 | 11,533 |
| timsort | 272.860 | 10,077 | 0 | 10,095 | 20,665 |
| adaptive_merge | 642.940 | 21,502 | 0 | 25,401 | 46,905 |
| selection | 1382.751 | 124,750 | 500 | 0 | 125,251 |
| insertion | 1665.994 | 61,682 | 0 | 61,687 | 123,869 |
| cocktail_shaker | 2300.964 | 92,365 | 61,188 | 0 | 153,554 |
| bubble | 2656.198 | 124,659 | 61,188 | 0 | 185,848 |

## Tech Stack

| Technology | Reason Used |
| --- | --- |
| `curses` | Chosen for its Zero-Dependency footprint ensuring instant execution on any POSIX system without installing bloated 3rd party TUI libraries. |
| Python `generators` | Yielding `SortFrame` objects from algorithms natively preserves the function call stack and state, making visualization frame-by-frame O(1) latency. |
| `tomllib` | Standard library configuration parsing (no external `toml` or `yaml` dependencies). |
| `argparse` | Native CLI argument parsing allowing rich help texts and subcommands without needing `click` or `typer`. |

## Known Limitations

- **Time Travel RAM Usage**: Navigating backwards requires an in-memory buffer of previous `SortFrame` yields. For very slow `O(n^2)` algorithms on large arrays (`size > 1000`), RAM usage can grow.
- **Audio Cross-Platform Support**: Audio generation via ALSA/SoX is primarily built for Linux. Mac and Windows environments may silently bypass the audio system if standard drivers aren't found.
- **Terminal Sizing**: The UI requires a minimum dimension of `20x10`. Extremely small pane tiling will pause the visualization with a warning until resized.
- **Windows Support**: Native Windows `cmd` does not ship `curses` by default. Windows users must run via WSL or manually `pip install windows-curses`.
