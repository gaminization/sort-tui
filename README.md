<div align="center">

# 📊 sort-tui

**A high-performance, purely terminal-based educational visualizer for 149 sorting algorithms.**

[![PyPI Version](https://img.shields.io/pypi/v/sort-tui.svg?style=for-the-badge&logo=pypi)](https://pypi.org/project/sort-tui/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/github/actions/workflow/status/gaminization/sort-tui/ci.yml?branch=main&style=for-the-badge&logo=github)](https://github.com/gaminization/sort-tui/actions)

![sort-tui Demo](docs/assets/demo.gif)

</div>

<br/>

> [!NOTE]
> `sort-tui` is built entirely on standard libraries (`curses`), meaning **zero dependencies** and instant execution on any POSIX system. 

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 📚 **Massive Catalog** | Over **149** unique sorting algorithms, from QuickSort to Bogosort. |
| 🚀 **High Performance** | O(1) latency frame-by-frame rendering using Python generators. |
| 🎵 **Audio Mapping** | Hear the arrays sort with dynamic PCM audio pitch mapping. |
| 🆚 **Comparison Mode** | Run multiple algorithms side-by-side in split panes. |
| 📊 **Benchmarking** | Headless execution mode for gathering raw computational metrics. |
| 🎨 **Rich Visuals** | 7 different rendering modes (Bars, Dots, Spiral, Circular, etc.). |
| 🧩 **Extensible** | Drop-in community plugin support for custom algorithms. |

---

## 📦 Installation

Install `sort-tui` directly from PyPI. A Python `3.10+` environment is required.

```bash
pip install sort-tui
```

> [!TIP]
> For Windows users, `curses` is not natively supported by `cmd`. We recommend running `sort-tui` inside **WSL**, or manually installing `windows-curses` (`pip install windows-curses`).

## 🚀 Quick Start

Launch an interactive visualization immediately:

```bash
# Visualize a standard Bubble Sort
sort-tui --algorithm bubble

# Test TimSort on a nearly sorted array of 100 elements
sort-tui --algorithm timsort --distribution nearly_sorted --size 100

# Compare Quicksort, Merge Sort, and Heapsort side-by-side
sort-tui --compare quicksort merge heapsort

# Run a headless benchmark suite
sort-tui --benchmark bubble insertion quicksort --size 500
```

## ⌨️ Interactive Hotkeys

`sort-tui` is fully interactive during playback. 

| Key(s) | Action | Key(s) | Action |
| :--- | :--- | :--- | :--- |
| `SPACE` | Pause / Resume | `A` | Toggle Ascending / Descending |
| `→` / `←` | Step forward / backward 1 frame | `V` | Cycle Visualization Mode |
| `Shift+→`/`←`| Jump forward / backward 10 frames| `H` | Toggle Heatmap Overlay |
| `Ctrl+→` | Jump to next swap | `M` | Toggle Audio |
| `R` | Reload with new random array | `D` | Cycle Input Distribution |
| `Shift+R` | Restart exact same array | `C` | Toggle Comparison Mode |
| `+` / `-` | Adjust simulation speed | `S` | Toggle Stability Tracking |
| `1` - `9` | Speed presets (1=slow, 9=fastest) | `E` | Export replay as JSON |
| `G` | Toggle Algorithm Genome panel | `?` | Toggle Help Panel |
| `Q` / `ESC` | Quit application | | |

## 📚 Documentation

Dive deeper into the inner workings, advanced configuration, and data science metrics of `sort-tui`:

- [Algorithm Contract & Architecture](docs/algorithms.md)
- [Performance Benchmarks](docs/benchmarks.md)
- [Advanced Features (Replay, Audio, Fingerprinting)](docs/advanced_features.md)
- [Configuration & Profiles](docs/configuration.md)
- [Plugin Guide (Write your own sorts!)](docs/plugin_guide.md)

## 🏗 Tech Stack

| Technology | Rationale |
| :--- | :--- |
| **`curses`** | Chosen for its zero-dependency footprint. Ensures instant execution without bloated TUI libraries. |
| **Python Generators** | Yielding `SortFrame` objects natively preserves the function call stack and local state for O(1) rewinding. |
| **`tomllib`** | Standard library configuration parsing (no external `toml` or `yaml` packages required). |
| **`argparse`** | Native CLI argument parsing allowing rich help texts and subcommands. |

## 🤝 Contributing & Community

We welcome contributions of all sizes! Whether it's adding a new esoteric sorting algorithm, fixing a bug, or improving the visuals.

- Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.
- Check out the [Roadmap](ROADMAP.md) to see where the project is heading.
- Review our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
