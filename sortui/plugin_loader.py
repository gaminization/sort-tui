from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Type

from sortui.algorithms.base import SortAlgorithm

PLUGIN_DIR = Path.home() / ".config" / "sortui" / "plugins"
COMMUNITY_CATEGORY = "Community"


def _key_from_name(name: str) -> str:
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    return "".join(ch for ch in key if ch.isalnum() or ch == "_")


def _load_module(path: Path) -> ModuleType | None:
    module_name = f"sortui_plugin_{path.stem}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def validate_plugin_class(cls: Type[SortAlgorithm]) -> bool:
    if not inspect.isclass(cls) or not issubclass(cls, SortAlgorithm) or cls is SortAlgorithm:
        return False
    required = ["name", "category", "time_complexity", "space_complexity", "description"]
    for attr in required:
        value = getattr(cls, attr, None)
        if not isinstance(value, str) or not value.strip():
            return False
    return callable(getattr(cls, "sort", None))


def discover_plugins(plugin_dir: str | Path | None = None) -> dict[str, Type[SortAlgorithm]]:
    root = Path(plugin_dir) if plugin_dir is not None else PLUGIN_DIR
    discovered: dict[str, Type[SortAlgorithm]] = {}
    if not root.exists():
        return discovered
    for path in sorted(root.glob("*.py")):
        module = _load_module(path)
        if module is None:
            continue
        for _name, cls in inspect.getmembers(module, inspect.isclass):
            if not validate_plugin_class(cls):
                continue
            key = _key_from_name(getattr(cls, "name"))
            if key:
                cls.category = COMMUNITY_CATEGORY
                discovered[key] = cls
    return discovered


def register_plugins(plugin_dir: str | Path | None = None) -> dict[str, Type[SortAlgorithm]]:
    plugins = discover_plugins(plugin_dir)
    if not plugins:
        return {}
    from sortui.algorithms import ALGORITHMS, CATEGORIES

    ALGORITHMS.update(plugins)
    community = CATEGORIES.setdefault(COMMUNITY_CATEGORY, [])
    for key in sorted(plugins):
        if key not in community:
            community.append(key)
    return plugins

