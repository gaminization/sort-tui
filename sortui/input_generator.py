from __future__ import annotations

import random
from enum import Enum
from typing import Sequence

from sortui.algorithms.base import SortAlgorithm


class InputDistribution(str, Enum):
    RANDOM = "random"
    SORTED = "sorted"
    REVERSE = "reverse"
    NEARLY_SORTED = "nearly_sorted"
    FEW_UNIQUE = "few_unique"
    GAUSSIAN = "gaussian"
    SAWTOOTH = "sawtooth"
    PIPE_ORGAN = "pipe_organ"
    SHUFFLED_MEDIAN = "shuffled_median"
    WORST_CASE = "worst_case"
    CUSTOM = "custom"

    @classmethod
    def choices(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def cycleable(cls) -> list["InputDistribution"]:
        return [
            cls.RANDOM,
            cls.SORTED,
            cls.REVERSE,
            cls.NEARLY_SORTED,
            cls.FEW_UNIQUE,
            cls.GAUSSIAN,
            cls.SAWTOOTH,
            cls.PIPE_ORGAN,
            cls.SHUFFLED_MEDIAN,
            cls.WORST_CASE,
        ]

    @classmethod
    def parse(cls, value: str | "InputDistribution" | None) -> "InputDistribution":
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.RANDOM
        normalized = str(value).lower().replace("-", "_").replace(" ", "_")
        for item in cls:
            if item.value == normalized:
                return item
        return cls.RANDOM


def _nearly_sorted(size: int, rng: random.Random) -> list[int]:
    arr = list(range(1, size + 1))
    displaced = max(1, round(size * 0.05))
    for _ in range(displaced):
        i, j = rng.randrange(size), rng.randrange(size)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def _gaussian(size: int, rng: random.Random) -> list[int]:
    midpoint = (size + 1) / 2
    sigma = max(1.0, size / 6)
    return [
        max(1, min(size, int(rng.gauss(midpoint, sigma))))
        for _ in range(size)
    ]


def _sawtooth(size: int) -> list[int]:
    period = max(2, min(12, size // 4 or 2))
    return [(i % period) + 1 for i in range(size)]


def _pipe_organ(size: int) -> list[int]:
    left = list(range(1, (size + 1) // 2 + 1))
    right = list(range(size // 2, 0, -1))
    return (left + right)[:size]


def _shuffled_median(size: int) -> list[int]:
    values = list(range(1, size + 1))
    result: list[int] = []
    lo, hi = 0, size - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        result.append(values[mid])
        values.pop(mid)
        hi -= 1
    return result[:size]


def parse_custom_input(raw: str | Sequence[int] | None) -> list[int] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        values = [part.strip() for part in raw.split(",") if part.strip()]
        return [int(value) for value in values]
    return [int(value) for value in raw]


def generate_array(
    size: int,
    distribution: str | InputDistribution = InputDistribution.RANDOM,
    *,
    seed: int | None = None,
    algorithm: SortAlgorithm | None = None,
    custom: str | Sequence[int] | None = None,
) -> list[int]:
    """Return an integer array for the chosen distribution."""
    custom_values = parse_custom_input(custom)
    if custom_values is not None:
        return custom_values

    size = max(0, int(size))
    if size == 0:
        return []
    dist = InputDistribution.parse(distribution)
    rng = random.Random(seed)

    if dist == InputDistribution.SORTED:
        return list(range(1, size + 1))
    if dist == InputDistribution.REVERSE:
        return list(range(size, 0, -1))
    if dist == InputDistribution.NEARLY_SORTED:
        return _nearly_sorted(size, rng)
    if dist == InputDistribution.FEW_UNIQUE:
        choices = [max(1, round(1 + i * (size - 1) / 4)) for i in range(5)]
        return [rng.choice(choices) for _ in range(size)]
    if dist == InputDistribution.GAUSSIAN:
        return _gaussian(size, rng)
    if dist == InputDistribution.SAWTOOTH:
        return _sawtooth(size)
    if dist == InputDistribution.PIPE_ORGAN:
        return _pipe_organ(size)
    if dist == InputDistribution.SHUFFLED_MEDIAN:
        arr = _shuffled_median(size)
        for _ in range(max(1, size // 5)):
            i, j = rng.randrange(size), rng.randrange(size)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    if dist == InputDistribution.WORST_CASE and algorithm is not None:
        return list(algorithm.get_worst_case_array(size))

    arr = list(range(1, size + 1))
    rng.shuffle(arr)
    return arr


def distribution_label(value: str | InputDistribution) -> str:
    dist = InputDistribution.parse(value)
    return dist.value.replace("_", " ").title()
