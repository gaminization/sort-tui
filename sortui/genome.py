from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from sortui.algorithms.base import SortFrame
from sortui.stats import SortStats

METRIC_NAMES = [
    "swap_density",
    "comparison_rate",
    "memory_locality",
    "recursion_use",
    "write_intensity",
    "parallelism",
    "adaptiveness",
    "cache_friendliness",
]


@dataclass
class GenomeReport:
    metrics: dict[str, float]
    fingerprint_hash: str


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def analyze_frames(frames: Iterable[SortFrame], stats: SortStats | None = None) -> GenomeReport:
    frame_list = list(frames)
    frame_count = max(1, len(frame_list))
    stats = stats or SortStats()

    access_distances: list[int] = []
    recursion_depth = 0
    parallel_frames = 0
    adaptive_frames = 0
    touched_indices = 0

    for frame in frame_list:
        indices = list(frame.highlighted) + list(frame.swapped)
        touched_indices += len(set(indices))
        if len(indices) >= 2:
            access_distances.extend(abs(indices[i] - indices[i - 1]) for i in range(1, len(indices)))
        recursion_depth = max(recursion_depth, frame.recursion_depth)
        if frame.metadata.get("threads"):
            parallel_frames += 1
        if frame.metadata.get("adaptive"):
            adaptive_frames += 1

    avg_distance = sum(access_distances) / len(access_distances) if access_distances else 0.0
    avg_touched = touched_indices / frame_count
    metrics = {
        "swap_density": _clamp(stats.swaps / frame_count),
        "comparison_rate": _clamp(stats.comparisons / frame_count),
        "memory_locality": _clamp(1.0 / (1.0 + avg_distance / 10.0)),
        "recursion_use": _clamp(recursion_depth / 10.0),
        "write_intensity": _clamp(stats.writes / frame_count),
        "parallelism": _clamp(parallel_frames / frame_count),
        "adaptiveness": _clamp(adaptive_frames / frame_count),
        "cache_friendliness": _clamp(1.0 / (1.0 + avg_touched / 6.0)),
    }
    digest_source = "|".join(f"{key}:{metrics[key]:.3f}" for key in METRIC_NAMES)
    fingerprint_hash = hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    return GenomeReport(metrics, fingerprint_hash)


def bar(value: float, width: int = 8) -> str:
    filled = round(_clamp(value) * width)
    return "█" * filled + "░" * (width - filled)


def format_fingerprint(report: GenomeReport) -> list[str]:
    lines = ["Behavioral Fingerprint"]
    for key in METRIC_NAMES:
        label = key.replace("_", " ").title()
        value = report.metrics.get(key, 0.0)
        lines.append(f"{label:<20} {bar(value)} {value * 100:5.1f}%")
    lines.append(f"Hash: {report.fingerprint_hash}")
    return lines

