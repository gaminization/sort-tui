from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from sortui.benchmark import run_benchmark

SCORE_PATH = Path.home() / ".config" / "sort-tui" / "scores.json"


@dataclass(frozen=True)
class Challenge:
    name: str
    size: int
    distribution: str
    max_swaps: int | None = None
    max_comparisons: int | None = None
    time_limit_ms: float | None = None


CHALLENGES = [
    Challenge("Tiny scramble", 20, "random", max_swaps=250),
    Challenge("Nearly there", 80, "nearly_sorted", max_comparisons=700),
    Challenge("Few unique", 120, "few_unique", max_comparisons=1200),
    Challenge("Reverse climb", 60, "reverse", max_swaps=1900),
    Challenge("Gaussian buckets", 120, "gaussian", time_limit_ms=350),
    Challenge("Sawtooth sweep", 100, "sawtooth", max_comparisons=2000),
    Challenge("Pipe organ", 90, "pipe_organ", max_swaps=2500),
    Challenge("Median shuffle", 110, "shuffled_median", max_comparisons=3000),
    Challenge("Large demo", 250, "random", time_limit_ms=900),
    Challenge("Worst case escape", 120, "worst_case", max_comparisons=5000),
]


def _load_scores(path: Path = SCORE_PATH) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_scores(scores: list[dict], path: Path = SCORE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scores, indent=2), encoding="utf-8")


def run_challenge(
    algorithm_key: str,
    *,
    challenge_index: int = 0,
    seed: int | None = 42,
    score_path: Path = SCORE_PATH,
) -> dict:
    challenge = CHALLENGES[challenge_index % len(CHALLENGES)]
    result = run_benchmark(
        [algorithm_key],
        size=challenge.size,
        seed=seed,
        iterations=1,
        distribution=challenge.distribution,
    )[0]
    passed = True
    if challenge.max_swaps is not None and result.swaps > challenge.max_swaps:
        passed = False
    if challenge.max_comparisons is not None and result.comparisons > challenge.max_comparisons:
        passed = False
    if challenge.time_limit_ms is not None and result.wall_time_ms > challenge.time_limit_ms:
        passed = False
    score = {
        "challenge": asdict(challenge),
        "algorithm": algorithm_key,
        "passed": passed,
        "result": asdict(result),
    }
    scores = _load_scores(score_path)
    scores.append(score)
    _save_scores(scores, score_path)
    return score


def challenge_menu() -> str:
    lines = ["sort-tui challenges"]
    for idx, challenge in enumerate(CHALLENGES, start=1):
        constraints = []
        if challenge.max_swaps is not None:
            constraints.append(f"max swaps {challenge.max_swaps}")
        if challenge.max_comparisons is not None:
            constraints.append(f"max comparisons {challenge.max_comparisons}")
        if challenge.time_limit_ms is not None:
            constraints.append(f"time {challenge.time_limit_ms:g}ms")
        lines.append(
            f"{idx:>2}. {challenge.name:<18} n={challenge.size:<4} "
            f"{challenge.distribution:<15} {', '.join(constraints)}"
        )
    return "\n".join(lines)

