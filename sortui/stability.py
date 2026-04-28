from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

from sortui.algorithms.base import SortFrame


class TaggedValue(int):
    """An int that carries a stable identity tag for duplicate tracking."""

    def __new__(cls, value: int, tag: str = "", original_index: int = 0):
        obj = int.__new__(cls, value)
        obj.value = int(value)
        obj.tag = tag
        obj.original_index = original_index
        return obj

    @property
    def label(self) -> str:
        return f"{self.value}{self.tag}"

    def __repr__(self) -> str:
        return self.label

    def __str__(self) -> str:
        return self.label


def _suffix(index: int) -> str:
    letters = []
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters.append(chr(ord("a") + rem))
    return "".join(reversed(letters))


def tag_duplicates(values: Sequence[int]) -> list[TaggedValue]:
    counts: dict[int, int] = defaultdict(int)
    totals: dict[int, int] = defaultdict(int)
    for value in values:
        totals[int(value)] += 1

    tagged: list[TaggedValue] = []
    for idx, value in enumerate(values):
        base = int(value)
        tag = ""
        if totals[base] > 1:
            tag = _suffix(counts[base])
            counts[base] += 1
        tagged.append(TaggedValue(base, tag, idx))
    return tagged


def stability_violations(original: Sequence[int], current: Sequence[int]) -> int:
    """Count duplicate-order violations using TaggedValue identities when present."""
    expected: dict[int, list[int]] = defaultdict(list)
    observed: dict[int, list[int]] = defaultdict(list)

    for idx, value in enumerate(original):
        base = int(value)
        original_index = getattr(value, "original_index", idx)
        expected[base].append(original_index)

    for idx, value in enumerate(current):
        base = int(value)
        original_index = getattr(value, "original_index", idx)
        observed[base].append(original_index)

    violations = 0
    for base, expected_order in expected.items():
        observed_order = observed.get(base, [])
        if len(expected_order) <= 1 or len(observed_order) <= 1:
            continue
        inversions = 0
        position = {original_index: i for i, original_index in enumerate(expected_order)}
        ranks = [position.get(original_index, -1) for original_index in observed_order]
        for i in range(len(ranks)):
            for j in range(i + 1, len(ranks)):
                if ranks[i] > ranks[j]:
                    inversions += 1
        violations += inversions
    return violations


@dataclass
class StabilityReport:
    stable: bool
    violations: int

    def footer_text(self) -> str:
        answer = "YES" if self.stable else "NO"
        return f"Stable: {answer} - {self.violations} violations"


class StabilityTracker:
    def __init__(self, original: Sequence[int]):
        self.original = list(original)

    def report(self, frame: SortFrame | None) -> StabilityReport:
        if frame is None:
            return StabilityReport(True, 0)
        violations = stability_violations(self.original, frame.array)
        return StabilityReport(violations == 0, violations)


def format_tagged(values: Iterable[int]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"

