# Architecture Decision Record: Time Travel Buffer Architecture

## Context
A key feature of the TUI is "Time Travel", allowing users to scrub backwards and forwards through an algorithm's execution history using left/right arrow keys.

## Decision
We utilize an **In-Memory Frame Buffer** (`list[SortFrame]`) that caches the metadata of each operation yielded by the generator up to the current point. When the user scrubs backwards, we simply render the cached historical `SortFrame`.

## Alternatives Considered
1. **Replay From Scratch**: Keep only the seed and input array. When scrubbing backwards to frame `N-1`, replay the generator from `0` to `N-1`. (Ruled out because some algorithms take O(n^2) or worse time, meaning backwards scrubbing would have massive latency spikes).
2. **Disk-Backed Buffer / SQLite**: Stream frames to a temporary file. (Ruled out for performance reasons; disk I/O would bottleneck fast-forwarding, and cleanup becomes unreliable).

## Why Chosen
Modern systems possess ample memory for standard terminal array sizes (typically `N < 500`). Storing full array clones and `SortFrame` metadata entirely in memory enables instantaneous `<O(1)` scrubbing latency in both directions. The `TimeTravelEngine` class orchestrates this buffer elegantly by lazily expanding the buffer as the user seeks forwards, and strictly caching everything for reverse seeks.
