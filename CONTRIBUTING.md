# Contributing

Thanks for helping with `sortui`.

## Local Setup

```bash
pip install -e ".[dev]"
pytest
```

## Algorithm Rules

- Algorithms must subclass `SortAlgorithm`.
- `sort()` must be a generator yielding `SortFrame` objects.
- Yield a frame for comparisons, swaps, writes, and meaningful reads.
- Every frame should include `operation` and plain-English `explanation`.
- The final frame must use `operation="done"` and mark all current indices sorted.
- Runtime code must remain stdlib-only.

## Style

Prefer small, readable implementations over highly optimized code. If a future feature is intentionally incomplete, mark it with `# STRETCH: <description>` and keep the runnable path working.

