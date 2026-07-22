# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-07-22

### Added
- **PyPI Release Automation**: Added automated PyPI deployments using Trusted Publishers via GitHub Actions.
- **PyPI Badges**: Integrated PyPI version badges into the README.

### Fixed
- Fixed an infinite loop in `SwapSort` when handling arrays with duplicate elements.
- Fixed `ci.yml` validation logic for the exhaustive Algorithm Correctness Sweep.
- Updated documentation links and `pip install` commands to use the correct `sort-tui` package name.

## [0.1.0] - 2026-07-22

### Added
- **Full Phase 2 Algorithm Catalog**: Implemented 149 diverse sorting algorithms utilizing `SortFrame`-based generators.
- **Input Distributions**: 11 unique array topologies (e.g., `random`, `nearly_sorted`, `pipe_organ`).
- **Benchmarking Mode**: Headless execution mode for profiling raw computational complexity (comparisons, swaps, writes, frames).
- **Stability Tracking**: Optional tracking to monitor algorithm stability on duplicate elements.
- **Export & Replay**: Ability to buffer and export simulation runs as JSON replays.
- **Visual Modes**: 7 rendering styles including Bars, Dots, Horizontal, Waveform, Spiral, Circular.
- **Comparison Panels**: Split-screen execution for side-by-side algorithm racing.
- **Plugin Loading**: Dynamic loading of community-created algorithms from `~/.config/sortui/plugins/`.
- **Audio Module**: Pitch-mapped audio generation directly through ALSA/SoX.
- **Comprehensive Testing**: Automated test suite guaranteeing 85%+ coverage.
- **Documentation**: Comprehensive manuals covering internals, benchmarking, and plugins.

### Changed
- Refactored engine to maintain **zero external runtime dependencies** (pure Python standard library).

### Fixed
- Fixed memory leakage in time-travel buffers for large dataset `O(n^2)` algorithms.

[0.1.3]: https://github.com/gaminization/sort-tui/releases/tag/v0.1.3
[0.1.0]: https://github.com/gaminization/sort-tui/releases/tag/v0.1.0
