from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, List, Optional


@dataclass
class SortFrame:
    """A single snapshot of the array state at one step of a sorting algorithm."""

    array: List[int]
    highlighted: List[int] = field(default_factory=list)
    swapped: List[int] = field(default_factory=list)
    sorted_indices: List[int] = field(default_factory=list)
    pivot_index: Optional[int] = None
    partition_bounds: Optional[tuple] = None
    recursion_depth: int = 0
    explanation: str = ""
    operation: str = ""
    aux_array: Optional[List[int]] = None
    metadata: dict = field(default_factory=dict)


class SortAlgorithm(ABC):
    """Abstract base class for all sorting algorithm implementations.

    Subclasses must override ``sort`` and may override the helper methods.
    Class-level attributes describe the algorithm for display in the TUI.
    """

    name: str = ""
    category: str = ""
    time_complexity: str = ""
    space_complexity: str = ""
    stable: bool = False
    description: str = ""
    worst_case_input: str = "random"

    @abstractmethod
    def sort(self, arr: List[int], ascending: bool = True) -> Generator[SortFrame, None, None]:
        """Yield one :class:`SortFrame` per logical step of the algorithm.

        The generator must yield *at least* one frame and must eventually
        terminate.  ``arr`` is a mutable working copy — the generator owns it.

        Parameters
        ----------
        arr:
            The list of integers to sort (caller should pass a copy).
        ascending:
            When *True* sort from smallest to largest; when *False* reverse.

        Yields
        ------
        SortFrame
            Current state of the array plus metadata for this step.
        """
        ...

    def get_worst_case_array(self, size: int) -> List[int]:
        """Return an input array that triggers worst-case behaviour.

        The default implementation returns a sorted ascending list, which is
        the worst case for naïve algorithms such as insertion sort and bubble
        sort.  Override when a different arrangement is needed (e.g. reverse-
        sorted, or a specific permutation for quick sort).

        Parameters
        ----------
        size:
            Number of elements in the returned list.
        """
        return list(range(size))

    def get_invariant(self) -> str:
        """Return a human-readable description of the algorithm's loop invariant.

        Used by the TUI's explanation panel.  Override to provide a meaningful
        string; the default returns an empty string (no invariant displayed).
        """
        return ""
