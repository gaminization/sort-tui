# Architecture Decision Record: Generator-Based Algorithm Execution

## Context
Sorting algorithm visualizations require pausing and extracting the state of the array at each operation (compare, swap, write, read). We need a mechanism to orchestrate this step-by-step execution.

## Decision
We chose **Python Generators (`yield`)** as the core contract for all sorting algorithms. Every sorting algorithm implements a `sort(self, arr) -> Generator[SortFrame, None, None]` method.

## Alternatives Considered
1. **Callbacks**: Passing an `on_step()` function into the sort. (Too much boilerplate for authors; hard to track call stacks).
2. **Snapshot Arrays**: Storing full array copies iteratively. (O(n) memory overhead per frame, disastrous for larger arrays or long-running algorithms).
3. **Async / Await**: Using `asyncio` to yield control back to an event loop. (Adds unnecessary complexity for synchronous sorting logic and requires `async` boilerplate for educational algorithms).

## Why Chosen
Generators provide an elegant, native Python approach to cooperative multitasking. Algorithm authors simply `yield base_frame(...)` exactly where they want to expose a visual step, preserving their local function state and call stack implicitly. This drastically lowers the barrier to entry for contributing new algorithms while giving the controller exact frame-by-frame pacing control.
