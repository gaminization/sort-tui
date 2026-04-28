from __future__ import annotations

from typing import Type

from sortui.algorithms.base import SortAlgorithm
from sortui.algorithms import adaptive
from sortui.algorithms import efficient
from sortui.algorithms import external
from sortui.algorithms import hybrid
from sortui.algorithms import hybrid_variants
from sortui.algorithms import network
from sortui.algorithms import non_comparison
from sortui.algorithms import numerical
from sortui.algorithms import other
from sortui.algorithms import parallel
from sortui.algorithms import specialized
from sortui.algorithms import string_specific
from sortui.algorithms.simple import (
    BubbleSort,
    CocktailShakerSort,
    CycleSort,
    ExchangeSort,
    GnomeSort,
    InsertionSort,
    OddEvenSort,
    SelectionSort,
    StrandSort,
)

# Map of algorithm key (lowercase, underscored) -> class
ALGORITHMS: dict[str, Type[SortAlgorithm]] = {
    "bubble": BubbleSort,
    "insertion": InsertionSort,
    "selection": SelectionSort,
    "cocktail_shaker": CocktailShakerSort,
    "gnome": GnomeSort,
    "odd_even": OddEvenSort,
    "exchange": ExchangeSort,
    "cycle": CycleSort,
    "strand": StrandSort,
}

_CATEGORY_MODULES = [
    efficient,
    hybrid,
    non_comparison,
    adaptive,
    external,
    parallel,
    string_specific,
    numerical,
    network,
    hybrid_variants,
    other,
    specialized,
]

for _module in _CATEGORY_MODULES:
    ALGORITHMS.update(_module.CATEGORY_ALGORITHMS)

# Map of category name -> list of algorithm keys
CATEGORIES: dict[str, list[str]] = {
    "Simple Sorts": [
        "bubble",
        "insertion",
        "selection",
        "cocktail_shaker",
        "gnome",
        "odd_even",
        "exchange",
        "cycle",
        "strand",
    ],
}

for _module in _CATEGORY_MODULES:
    CATEGORIES[_module.CATEGORY] = list(_module.CATEGORY_KEYS)

JOKE_ALGORITHMS = set(getattr(specialized, "JOKE_ALGORITHMS", set()))


def get_algorithm(name: str) -> Type[SortAlgorithm]:
    """Return algorithm class by key, case-insensitive. Raises KeyError if not found."""
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in ALGORITHMS:
        available = ", ".join(sorted(ALGORITHMS.keys()))
        raise KeyError(f"Unknown algorithm: {name!r}. Available: {available}")
    return ALGORITHMS[key]


def list_algorithms() -> str:
    """Return a formatted listing of all algorithms by category."""
    lines: list[str] = []
    for category, keys in CATEGORIES.items():
        lines.append(f"\n{category}:")
        for key in keys:
            cls = ALGORITHMS[key]
            stable_str = "stable" if cls.stable else "unstable"
            lines.append(f"  {key:<25} {cls.time_complexity:<12} {stable_str}")
    return "\n".join(lines)
