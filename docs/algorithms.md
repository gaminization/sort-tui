# Algorithms Architecture

The core of `sort-tui` is its massively extensible algorithm catalog. 

`sortui.algorithms.ALGORITHMS` maps command keys to `SortAlgorithm` classes. `CATEGORIES` groups those keys for the `sortui --list` menu.

## The `SortAlgorithm` Contract

Every algorithm implemented in `sort-tui` follows a strict contract. This ensures seamless integration with the TUI, time-travel, audio, and headless benchmarking modes.

1. **Input Isolation:** The input array provided to `sort()` is a mutable copy owned strictly by the generator.
2. **Generator Pattern:** The sorting algorithm must `yield` a sequence of `SortFrame` snapshots.
3. **Operations:** `operation` inside the `SortFrame` must be one of:
   - `compare`: When two elements are evaluated against each other.
   - `swap`: When two elements exchange positions.
   - `write`: When a value is explicitly overwritten (e.g., in Merge Sort).
   - `read`: When an element is read for logic (not often yielded unless significant).
   - `done`: The terminal frame marking completion.
4. **Explanations:** The `explanation` string must be filled out for every frame to provide educational context.
5. **Completion:** The final frame must use `done` and assert `sorted_indices=list(range(n))` indicating the full array is sorted.

## Shared Instrumentation

The massive catalog (149 algorithms) utilizes shared instrumented implementations for maintainability. Specialized entries add metadata class attributes such as:

- `disk_op=True` (External Sorts)
- `threads=True` (Parallel Sorts)
- `adaptive=True` (Adaptive Sorts)

## Joke Algorithms & Boundaries

To prevent infinite loops or memory crashes, joke algorithms are strictly bounded:

- **Bogosort / Random Sort:** Execution is capped to a fixed maximum number of shuffles.
- **Quantum Bogosort:** Yields exactly five "multiverse branch" frames before collapsing.
- **Waiting Algorithms:** Yield ~200 waiting frames.
- **Sleep Sort:** Evaluates immediately via a priority queue rather than actual thread blocking to maintain O(1) latency in the TUI.
- **Deletion Sorts:** Operate solely on the remaining visible array elements.
