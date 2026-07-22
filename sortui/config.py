from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[import]
else:
    # Minimal TOML parser fallback for Python 3.10 dev environments.
    # Python 3.10 does not ship tomllib, so keep this tiny fallback for the
    # subset of TOML used by sortui's config.
    import re as _re

    class _MinimalTomllib:  # noqa: N801
        """Best-effort TOML reader — handles the sortui config subset."""

        @staticmethod
        def load(fh) -> dict:
            return _MinimalTomllib.loads(fh.read().decode("utf-8"))

        @staticmethod
        def loads(text: str) -> dict:
            result: dict = {}
            current_section: list[str] = []

            def _set(keys: list[str], val: Any) -> None:
                d = result
                for k in keys[:-1]:
                    d = d.setdefault(k, {})
                d[keys[-1]] = val

            for raw_line in text.splitlines():
                line = raw_line.split("#")[0].strip()
                if not line:
                    continue
                # [section] or [section.sub]
                m = _re.match(r"^\[([^\]]+)\]$", line)
                if m:
                    current_section = [p.strip() for p in m.group(1).split(".")]
                    # ensure section exists
                    d = result
                    for p in current_section:
                        d = d.setdefault(p, {})
                    continue
                # key = value
                m = _re.match(r"^(\w+)\s*=\s*(.+)$", line)
                if m:
                    key, raw_val = m.group(1), m.group(2).strip()
                    # parse value
                    if raw_val.lower() == "true":
                        val: Any = True
                    elif raw_val.lower() == "false":
                        val = False
                    elif raw_val.lower() == "null":
                        val = None
                    elif raw_val.startswith('"') and raw_val.endswith('"'):
                        val = raw_val[1:-1]
                    elif raw_val.startswith("'") and raw_val.endswith("'"):
                        val = raw_val[1:-1]
                    else:
                        try:
                            val = int(raw_val)
                        except ValueError:
                            try:
                                val = float(raw_val)
                            except ValueError:
                                val = raw_val
                    _set(current_section + [key], val)
            return result

    tomllib = _MinimalTomllib()  # type: ignore[assignment]

# ── default config values ──────────────────────────────────────────────────────
DEFAULTS: dict[str, Any] = {
    "defaults": {
        "algorithm": "bubble",
        "speed": 1.0,
        "order": "asc",
        "distribution": "random",
        "seed": None,
        "visualization_mode": "bars",
    },
    "colors": {
        "bar": "white",
        "accent": "yellow",
        "swap": "red",
        "sorted": "green",
        "pivot": "cyan",
        "purge": "dark_gray",
    },
    "display": {
        "show_stats": True,
        "show_controls": True,
        "show_explanation": True,
        "show_invariant": True,
        "gradient_mode": False,
        "heatmap_mode": False,
    },
    "audio": {
        "enabled": False,
        "min_freq": 200,
        "max_freq": 1200,
    },
    "benchmark": {
        "default_iterations": 3,
        "default_size": 500,
    },
    "profiles": {
        "teaching": {
            "algorithm": "insertion",
            "speed": 0.3,
            "show_explanation": True,
        },
        "benchmarking": {
            "speed": 10.0,
            "show_explanation": False,
        },
        "demo": {
            "speed": 1.5,
            "gradient_mode": True,
        },
    },
}

DEFAULT_TOML = """\
[defaults]
algorithm = "bubble"
speed = 1.0
order = "asc"
distribution = "random"
# seed = 42
visualization_mode = "bars"

[colors]
bar = "white"
accent = "yellow"
swap = "red"
sorted = "green"
pivot = "cyan"
purge = "dark_gray"

[display]
show_stats = true
show_controls = true
show_explanation = true
show_invariant = true
gradient_mode = false
heatmap_mode = false

[audio]
enabled = false
min_freq = 200
max_freq = 1200

[benchmark]
default_iterations = 3
default_size = 500

[profiles.teaching]
algorithm = "insertion"
speed = 0.3
show_explanation = true

[profiles.benchmarking]
speed = 10.0
show_explanation = false

[profiles.demo]
speed = 1.5
gradient_mode = true
"""


class SortuiConfig:
    """Loaded and validated configuration."""

    def __init__(self, path: Path | None = None):
        self._path = path or Path.home() / ".config" / "sort-tui" / "config.toml"
        self._raw: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(DEFAULT_TOML)
        try:
            with open(self._path, "rb") as fh:
                self._raw = tomllib.load(fh)
        except Exception as exc:
            print(
                f"[sortui] Warning: could not parse config ({exc}), using defaults.",
                file=sys.stderr,
            )
            self._raw = {}

    def _validate_float(self, val: Any, lo: float, hi: float, default: float) -> float:
        try:
            v = float(val)
            if lo <= v <= hi:
                return v
        except (TypeError, ValueError):
            pass
        return default

    def _validate_int(self, val: Any, lo: int, hi: int, default: int) -> int:
        try:
            v = int(val)
            if lo <= v <= hi:
                return v
        except (TypeError, ValueError):
            pass
        return default

    def _validate_str(self, val: Any, choices: list[str], default: str) -> str:
        if isinstance(val, str) and val in choices:
            return val
        return default

    def _validate_bool(self, val: Any, default: bool) -> bool:
        if isinstance(val, bool):
            return val
        return default

    # ── public accessors ───────────────────────────────────────────────────────

    @property
    def algorithm(self) -> str:
        return self._raw.get("defaults", {}).get("algorithm", DEFAULTS["defaults"]["algorithm"])

    @property
    def speed(self) -> float:
        raw = self._raw.get("defaults", {}).get("speed", DEFAULTS["defaults"]["speed"])
        return self._validate_float(raw, 0.01, 100.0, DEFAULTS["defaults"]["speed"])

    @property
    def order(self) -> str:
        raw = self._raw.get("defaults", {}).get("order", "asc")
        return self._validate_str(raw, ["asc", "desc"], "asc")

    @property
    def distribution(self) -> str:
        raw = self._raw.get("defaults", {}).get("distribution", "random")
        return self._validate_str(
            raw,
            [
                "random",
                "sorted",
                "reverse",
                "nearly_sorted",
                "few_unique",
                "gaussian",
                "sawtooth",
                "pipe_organ",
                "shuffled_median",
                "worst_case",
                "custom",
            ],
            "random",
        )

    @property
    def seed(self) -> int | None:
        val = self._raw.get("defaults", {}).get("seed", None)
        if val is None:
            return None
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    @property
    def visualization_mode(self) -> str:
        raw = self._raw.get("defaults", {}).get("visualization_mode", "bars")
        return self._validate_str(
            raw,
            ["bars", "dots", "horizontal", "numbers", "waveform", "spiral", "circular"],
            "bars",
        )

    @property
    def show_stats(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("show_stats", True), True)

    @property
    def show_controls(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("show_controls", True), True)

    @property
    def show_explanation(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("show_explanation", True), True)

    @property
    def show_invariant(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("show_invariant", True), True)

    @property
    def gradient_mode(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("gradient_mode", False), False)

    @property
    def heatmap_mode(self) -> bool:
        return self._validate_bool(self._raw.get("display", {}).get("heatmap_mode", False), False)

    @property
    def audio_enabled(self) -> bool:
        return self._validate_bool(self._raw.get("audio", {}).get("enabled", False), False)

    @property
    def audio_min_freq(self) -> int:
        return self._validate_int(self._raw.get("audio", {}).get("min_freq", 200), 20, 20000, 200)

    @property
    def audio_max_freq(self) -> int:
        return self._validate_int(self._raw.get("audio", {}).get("max_freq", 1200), 20, 20000, 1200)

    @property
    def benchmark_iterations(self) -> int:
        return self._validate_int(
            self._raw.get("benchmark", {}).get("default_iterations", 3), 1, 100, 3
        )

    @property
    def benchmark_size(self) -> int:
        return self._validate_int(
            self._raw.get("benchmark", {}).get("default_size", 500), 2, 100_000, 500
        )

    @property
    def profiles(self) -> dict[str, Any]:
        return self._raw.get("profiles", DEFAULTS["profiles"])

    def apply_profile(self, profile_name: str) -> dict[str, Any]:
        """Return flat dict of overrides for the named profile."""
        profiles = self._raw.get("profiles", DEFAULTS["profiles"])
        profile = profiles.get(profile_name, {})
        return profile if isinstance(profile, dict) else {}

    def resolve_option(
        self,
        key: str,
        *,
        cli_value: Any = None,
        profile_name: str | None = None,
        section: str = "defaults",
        default: Any = None,
    ) -> Any:
        """Resolve one option with CLI > profile > config > defaults priority."""
        profile_value = None
        if profile_name:
            profile_value = self.apply_profile(profile_name).get(key)
        config_value = self._raw.get(section, {}).get(key)
        default_section = DEFAULTS.get(section, {})
        hardcoded = default_section.get(key, default) if isinstance(default_section, dict) else default
        for candidate in (cli_value, profile_value, config_value, hardcoded):
            if candidate is not None:
                return candidate
        return default

    def as_dict(self) -> dict[str, Any]:
        return dict(self._raw)
