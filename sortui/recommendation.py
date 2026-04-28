from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class ArrayCharacteristics:
    size: int
    inversion_count: int
    unique_ratio: float
    is_gaussian: bool
    sorted_run_ratio: float


def _inversions(values: Sequence[int]) -> int:
    n = len(values)
    if n > 2000:
        step = max(1, n // 1000)
        sampled = values[::step]
        return _inversions(sampled) * step
    count = 0
    for i in range(n):
        left = int(values[i])
        for j in range(i + 1, n):
            if left > int(values[j]):
                count += 1
    return count


def _sorted_run_ratio(values: Sequence[int]) -> float:
    if not values:
        return 1.0
    runs = 1
    for i in range(1, len(values)):
        if int(values[i - 1]) > int(values[i]):
            runs += 1
    return 1.0 - ((runs - 1) / max(1, len(values) - 1))


def _looks_gaussian(values: Sequence[int]) -> bool:
    if len(values) < 8:
        return False
    nums = [int(value) for value in values]
    mean = sum(nums) / len(nums)
    variance = sum((value - mean) ** 2 for value in nums) / len(nums)
    if variance == 0:
        return False
    stdev = math.sqrt(variance)
    within_one = sum(1 for value in nums if abs(value - mean) <= stdev) / len(nums)
    return 0.55 <= within_one <= 0.8


def analyze_array(values: Sequence[int]) -> ArrayCharacteristics:
    size = len(values)
    unique_ratio = len({int(value) for value in values}) / max(1, size)
    return ArrayCharacteristics(
        size=size,
        inversion_count=_inversions(values),
        unique_ratio=unique_ratio,
        is_gaussian=_looks_gaussian(values),
        sorted_run_ratio=_sorted_run_ratio(values),
    )


def recommend(characteristics: ArrayCharacteristics) -> list[str]:
    if characteristics.size <= 32:
        return ["insertion", "binary_insertion", "gnome"]
    max_inversions = max(1, characteristics.size * (characteristics.size - 1) // 2)
    inversion_ratio = characteristics.inversion_count / max_inversions
    if characteristics.sorted_run_ratio >= 0.9 or inversion_ratio <= 0.05:
        return ["insertion", "timsort", "adaptive_merge"]
    if characteristics.unique_ratio <= 0.15:
        return ["counting", "radix_lsd", "bucket"]
    if characteristics.is_gaussian:
        return ["bucket", "spreadsort", "merge"]
    if characteristics.size >= 1000:
        return ["quicksort", "merge", "heapsort"]
    return ["quicksort", "merge", "timsort"]


def recommendation_reason(characteristics: ArrayCharacteristics) -> str:
    max_inversions = max(1, characteristics.size * (characteristics.size - 1) // 2)
    inversion_ratio = characteristics.inversion_count / max_inversions
    if characteristics.size <= 32:
        return "small input"
    if characteristics.sorted_run_ratio >= 0.9 or inversion_ratio <= 0.05:
        return "nearly sorted detected"
    if characteristics.unique_ratio <= 0.15:
        return "few unique values detected"
    if characteristics.is_gaussian:
        return "gaussian distribution detected"
    if characteristics.size >= 1000:
        return "large input"
    return "balanced general input"


def recommendation_text(values: Sequence[int]) -> str:
    characteristics = analyze_array(values)
    first = recommend(characteristics)[0]
    label = first.replace("_", " ").title()
    return f"{label} ({recommendation_reason(characteristics)})"

