# Plugin Guide

`sort-tui` supports dropping in your own custom Python sorting algorithms dynamically. No need to fork or compile the engine!

## Plugin Directory

Place your custom `.py` plugin files in:

```text
~/.config/sortui/plugins/
```

> [!NOTE]
> Each `.py` file found in this directory is imported in isolation. Any class that successfully inherits from `SortAlgorithm` will be automatically registered under the **Community** category in the main menu. Invalid plugins are silently skipped without crashing the application.

## Creating a Plugin

Here is a complete, copy-pasteable example of a custom plugin that sorts an array using Python's built-in `sorted()` method, yielding a single "done" frame.

Save this file as `~/.config/sortui/plugins/my_sort.py`:

```python
from sortui.algorithms.base import SortAlgorithm, SortFrame

class MySort(SortAlgorithm):
    # Metadata required for the UI and Benchmarks
    name = "My Custom Sort"
    category = "Community"
    time_complexity = "O(n log n)"
    space_complexity = "O(n)"
    stable = True
    description = "A tiny example plugin utilizing Python's Timsort."

    def sort(self, arr, ascending=True):
        """
        The core generator method.
        'arr' is a mutable list copy provided by the engine.
        """
        # Perform the actual sort
        arr[:] = sorted(arr, reverse=not ascending)
        
        # Yield the final completion frame
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation="Array has been sorted completely.",
            operation="done",
        )
```

Now, run `sortui --list` and you will see `my_custom_sort` listed under the `Community` category! You can run it directly:

```bash
sortui --algorithm my_custom_sort
```
