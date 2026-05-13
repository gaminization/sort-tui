# Architecture Decision Record: Zero External Dependencies

## Context
A CLI tool requires a reliable deployment footprint. Users installing educational or experimental visualization software are often discouraged if it pollutes their Python environment with heavy dependencies or compilation steps.

## Decision
We enforce a strict **Standard Library Only** policy for runtime execution. No external packages are required to install or run the application.

## Alternatives Considered
1. **`urwid` / `blessed` / `textual`**: Rich TUI frameworks that make terminal UI much easier. (Ruled out because they add external footprint, even though `textual` is excellent, `curses` is built-in).
2. **`numpy`**: Fast array manipulation. (Ruled out because our arrays are small and the bottleneck is terminal rendering, not raw CPU math).
3. **`colorama`**: Cross-platform coloring. (Ruled out; we handle standard ANSI escape sequences or rely on native `curses` color pairs).

## Why Chosen
By restricting the stack to `curses`, `json`, `math`, `heapq`, and other stdlib modules, `sortui` guarantees instant out-of-the-box functionality on any modern POSIX Python 3.10+ installation. It maximizes portability and makes the application ideal as a standalone script or lightweight package. Development dependencies (like `pytest` or `mypy`) are strictly optional and isolated.
