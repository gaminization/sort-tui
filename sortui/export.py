from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sortui.algorithms.base import SortFrame


def default_export_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path.home() / f"sortui_run_{stamp}.json"


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))  # type: ignore[arg-type]
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    return value


def frame_to_dict(frame: SortFrame) -> dict[str, Any]:
    return _jsonable(frame)


def frame_from_dict(raw: dict[str, Any]) -> SortFrame:
    return SortFrame(**raw)


def export_run(engine, algorithm, stats, path: str | Path | None = None) -> Path:
    """Save the buffered run history and metadata as JSON."""
    out_path = Path(path) if path is not None else default_export_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = getattr(engine, "_history", [])
    payload = {
        "format": "sortui-run-v1",
        "algorithm": getattr(algorithm, "name", type(algorithm).__name__),
        "algorithm_key": getattr(algorithm, "key", None),
        "stats": {
            "comparisons": getattr(stats, "comparisons", 0),
            "swaps": getattr(stats, "swaps", 0),
            "writes": getattr(stats, "writes", 0),
            "frames": getattr(stats, "frames", len(frames)),
            "elapsed_ms": getattr(stats, "elapsed_ms", lambda: 0.0)(),
        },
        "frames": [frame_to_dict(frame) for frame in frames],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


def load_frames(path: str | Path) -> list[SortFrame]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        frames_raw = raw
    else:
        frames_raw = raw.get("frames", [])
    return [frame_from_dict(frame) for frame in frames_raw]
