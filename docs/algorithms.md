# Algorithms

`sortui.algorithms.ALGORITHMS` maps command keys to `SortAlgorithm` classes. `CATEGORIES` groups those keys for `sortui --list`.

Every algorithm follows the same contract:

- Input is a mutable list copy owned by the generator.
- Output is a sequence of `SortFrame` snapshots.
- `operation` is one of `compare`, `swap`, `write`, `read`, or `done`.
- `explanation` is filled on every frame.
- The final frame uses `done` and `sorted_indices=list(range(n))` for the current array.

The large Phase 2 catalog uses shared instrumented implementations for maintainability. Specialized entries add metadata such as `disk_op`, `threads`, `network`, `adaptive`, or joke-specific markers.

Joke algorithms are bounded. Bogosort/random sort cap shuffles, quantum bogosort flashes five multiverse frames, waiting algorithms yield 200 waiting frames, sleep sort uses a priority queue, and deletion-based algorithms operate on the current visible array.

