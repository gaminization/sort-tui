# Contributing to sort-tui

First off, thank you for considering contributing to `sort-tui`! It's people like you that make open-source educational tools great. 

The following is a set of guidelines for contributing to `sort-tui`. These are mostly guidelines, not hard rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Algorithm Implementation Rules](#algorithm-implementation-rules)
3. [Code Style Guide](#code-style-guide)
4. [Submitting a Pull Request](#submitting-a-pull-request)

---

## Local Development Setup

To set up a local development environment:

```bash
# 1. Clone the repository
git clone https://github.com/gaminization/sort-tui.git
cd sort-tui

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install in editable mode with development dependencies
pip install -e ".[dev]"

# 4. Run the test suite to ensure everything works
pytest
```

## Algorithm Implementation Rules

When contributing a new sorting algorithm to the catalog, it must adhere to the `SortAlgorithm` contract:

- **Subclassing:** All algorithms must subclass `sortui.algorithms.base.SortAlgorithm`.
- **Generator Pattern:** The `sort(self, arr, ascending=True)` method must be a generator that `yield`s `SortFrame` objects.
- **Operations:** Yield a `SortFrame` for every meaningful algorithmic step: `compare`, `swap`, `write`, or `read`.
- **Explanation:** Provide a concise, plain-English `explanation` in every frame (e.g., `"Comparing index 4 and 5"`).
- **Completion:** The final frame must set `operation="done"` and pass the entire array length to `sorted_indices` (e.g., `list(range(len(arr)))`).
- **Dependencies:** The algorithmic logic must only use Python Standard Library modules.

> [!WARNING]  
> Please ensure your algorithm handles both ascending and descending logic properly if applicable, or document if it's strictly unidirectional.

## Code Style Guide

- **Clarity over cleverness:** Prefer small, readable implementations over highly golfed or obscure optimizations. This is an educational tool first.
- **Stretch Goals:** If a feature or algorithm is intentionally left incomplete, mark it clearly with `# STRETCH: <description>` while ensuring the runnable path still executes without crashing.
- **Linting:** We enforce formatting with `ruff`. Run `make lint` prior to committing.

## Submitting a Pull Request

1. Fork the repository and create your branch from `main`.
2. Write clear, documented code.
3. Add unit tests for your algorithm or feature. Ensure `pytest` passes cleanly.
4. Update the `README.md` or `docs/` if you add a major feature.
5. Open a Pull Request with a detailed description of what you added and a GIF (if it's a visual feature).
