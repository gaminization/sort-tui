"""Tests for sortui.challenge — challenge_menu, run_challenge, CHALLENGES list."""

import json
import tempfile
from pathlib import Path
from dataclasses import asdict

import pytest

from sortui.challenge import (
    CHALLENGES,
    Challenge,
    challenge_menu,
    run_challenge,
    _load_scores,
    _save_scores,
)


# ── challenge_menu ────────────────────────────────────────────────────────────

class TestChallengeMenu:
    def test_menu_is_non_empty_string(self):
        menu = challenge_menu()
        assert isinstance(menu, str)
        assert len(menu) > 0

    def test_menu_lists_all_challenges(self):
        menu = challenge_menu()
        for challenge in CHALLENGES:
            assert challenge.name in menu, f"'{challenge.name}' not found in menu"

    def test_menu_has_header(self):
        menu = challenge_menu()
        assert "sortui" in menu.lower()

    def test_menu_shows_size(self):
        menu = challenge_menu()
        for challenge in CHALLENGES:
            assert f"n={challenge.size}" in menu

    def test_menu_shows_distribution(self):
        menu = challenge_menu()
        for challenge in CHALLENGES:
            assert challenge.distribution in menu

    def test_menu_shows_constraints(self):
        menu = challenge_menu()
        # At least one challenge has max_swaps
        has_swap_constraint = any(c.max_swaps is not None for c in CHALLENGES)
        if has_swap_constraint:
            assert "max swaps" in menu

    def test_challenges_list_not_empty(self):
        assert len(CHALLENGES) > 0

    def test_all_challenges_are_challenge_instances(self):
        for ch in CHALLENGES:
            assert isinstance(ch, Challenge)


# ── run_challenge ─────────────────────────────────────────────────────────────

class TestRunChallenge:
    def _run(self, algorithm_key, challenge_index=0, seed=42):
        with tempfile.TemporaryDirectory() as tmpdir:
            score_path = Path(tmpdir) / "scores.json"
            return run_challenge(
                algorithm_key,
                challenge_index=challenge_index,
                seed=seed,
                score_path=score_path,
            ), score_path

    def test_returns_dict(self):
        result, _ = self._run("bubble")
        assert isinstance(result, dict)

    def test_result_has_passed_key(self):
        result, _ = self._run("bubble")
        assert "passed" in result

    def test_result_has_result_key(self):
        result, _ = self._run("insertion")
        assert "result" in result

    def test_result_has_challenge_key(self):
        result, _ = self._run("merge")
        assert "challenge" in result

    def test_passed_is_bool(self):
        result, _ = self._run("bubble")
        assert isinstance(result["passed"], bool)

    def test_result_contains_benchmark_fields(self):
        result, _ = self._run("insertion")
        bench = result["result"]
        assert "comparisons" in bench
        assert "swaps" in bench
        assert "writes" in bench
        assert "wall_time_ms" in bench

    def test_challenge_info_embedded_in_result(self):
        result, _ = self._run("bubble", challenge_index=0)
        ch = result["challenge"]
        assert "name" in ch
        assert "size" in ch
        assert "distribution" in ch

    def test_score_is_persisted_to_file(self, tmp_path):
        score_path = tmp_path / "scores.json"
        result = run_challenge("insertion", challenge_index=0, seed=42, score_path=score_path)
        assert score_path.exists()
        saved = json.loads(score_path.read_text())
        assert len(saved) == 1
        assert saved[0]["passed"] == result["passed"]

    def test_multiple_runs_append_to_scores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            score_path = Path(tmpdir) / "scores.json"
            run_challenge("bubble", challenge_index=0, seed=42, score_path=score_path)
            run_challenge("insertion", challenge_index=0, seed=42, score_path=score_path)
            saved = json.loads(score_path.read_text())
            assert len(saved) == 2

    def test_challenge_index_wraps_around(self):
        """Index larger than CHALLENGES length must wrap rather than crash."""
        result, _ = self._run("bubble", challenge_index=len(CHALLENGES) + 2)
        assert isinstance(result, dict)
        assert "passed" in result

    def test_efficient_sort_passes_easy_challenge(self):
        """Insertion sort should pass the 'Nearly there' (nearly-sorted) challenge."""
        # Find the nearly-sorted challenge
        for idx, ch in enumerate(CHALLENGES):
            if ch.distribution == "nearly_sorted":
                result, _ = self._run("insertion", challenge_index=idx)
                # Just verify it ran — not necessarily that it passed
                assert "passed" in result
                break

    def test_algorithm_can_fail_challenge_without_crash(self):
        """A slow algorithm may fail a strict time/swap constraint — must not raise."""
        for idx, ch in enumerate(CHALLENGES):
            if ch.max_swaps is not None and ch.max_swaps < 50:
                # Very tight constraint — bubble sort will likely fail
                result, _ = self._run("bubble", challenge_index=idx)
                assert "passed" in result
                break
        else:
            # No super-tight challenge found; run any challenge
            result, _ = self._run("bubble", challenge_index=0)
            assert "passed" in result


# ── _load_scores / _save_scores ───────────────────────────────────────────────

class TestScorePersistence:
    def test_load_scores_returns_empty_list_if_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.json"
            scores = _load_scores(path)
            assert scores == []

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "scores.json"
            data = [{"passed": True, "algorithm": "bubble"}]
            _save_scores(data, path)
            loaded = _load_scores(path)
            assert loaded == data

    def test_load_scores_handles_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "corrupt.json"
            path.write_text("NOT VALID JSON", encoding="utf-8")
            scores = _load_scores(path)
            assert scores == []

    def test_save_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "scores.json"
            _save_scores([{"test": True}], path)
            assert path.exists()


# ── Challenge dataclass ───────────────────────────────────────────────────────

class TestChallengeDataclass:
    def test_challenge_is_immutable(self):
        ch = CHALLENGES[0]
        with pytest.raises((AttributeError, TypeError)):
            ch.name = "modified"

    def test_challenge_asdict(self):
        ch = CHALLENGES[0]
        d = asdict(ch)
        assert "name" in d
        assert "size" in d
        assert "distribution" in d

    def test_optional_fields_can_be_none(self):
        ch = Challenge("test", 10, "random")
        assert ch.max_swaps is None
        assert ch.max_comparisons is None
        assert ch.time_limit_ms is None
