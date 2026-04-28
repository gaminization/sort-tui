from sortui.plugin_loader import discover_plugins


def test_valid_plugin_discovered(tmp_path):
    plugin = tmp_path / "demo_plugin.py"
    plugin.write_text(
        """
from sortui.algorithms.base import SortAlgorithm, SortFrame

class DemoPluginSort(SortAlgorithm):
    name = "Demo Plugin"
    category = "Community"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    stable = True
    description = "Test plugin."

    def sort(self, arr, ascending=True):
        arr[:] = sorted(arr, reverse=not ascending)
        yield SortFrame(array=arr[:], sorted_indices=list(range(len(arr))), explanation="done", operation="done")
""",
        encoding="utf-8",
    )
    plugins = discover_plugins(tmp_path)
    assert "demo_plugin" in plugins


def test_invalid_plugin_rejected_without_crash(tmp_path):
    plugin = tmp_path / "bad_plugin.py"
    plugin.write_text(
        """
from sortui.algorithms.base import SortAlgorithm, SortFrame

class BadPluginSort(SortAlgorithm):
    category = "Community"
    time_complexity = "O(n)"
    space_complexity = "O(1)"
    description = "Missing name."

    def sort(self, arr, ascending=True):
        yield SortFrame(array=arr[:], explanation="done", operation="done")
""",
        encoding="utf-8",
    )
    assert discover_plugins(tmp_path) == {}

