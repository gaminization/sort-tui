# Plugin Guide

Place plugin files in:

```text
~/.config/sortui/plugins/
```

Each `.py` file is imported in isolation. Any valid `SortAlgorithm` subclass is registered under the `Community` category.

```python
from sortui.algorithms.base import SortAlgorithm, SortFrame


class MySort(SortAlgorithm):
    name = "My Sort"
    category = "Community"
    time_complexity = "O(n log n)"
    space_complexity = "O(1)"
    stable = True
    description = "A tiny example plugin."

    def sort(self, arr, ascending=True):
        arr[:] = sorted(arr, reverse=not ascending)
        yield SortFrame(
            array=arr[:],
            sorted_indices=list(range(len(arr))),
            explanation="Array is sorted.",
            operation="done",
        )
```

Invalid plugins are skipped without crashing the app.

