"""Tests for sortui.input_generator — all distributions, size=0, determinism."""

import pytest
import statistics

from sortui.input_generator import (
    InputDistribution,
    generate_array,
    distribution_label,
    parse_custom_input,
)


# ── n=0 ───────────────────────────────────────────────────────────────────────

def test_n0_returns_empty():
    for dist in InputDistribution.cycleable():
        result = generate_array(0, dist, seed=1)
        assert result == [], f"n=0 for {dist} must return []"


# ── All distributions return correct size ────────────────────────────────────

@pytest.mark.parametrize("dist", InputDistribution.cycleable())
def test_correct_size(dist):
    result = generate_array(30, dist, seed=42)
    assert len(result) == 30, f"{dist}: expected 30 elements"


@pytest.mark.parametrize("size", [1, 5, 50, 100])
def test_various_sizes_random(size):
    result = generate_array(size, InputDistribution.RANDOM, seed=7)
    assert len(result) == size


# ── Seeded random is deterministic ───────────────────────────────────────────

@pytest.mark.parametrize("dist", [
    InputDistribution.RANDOM,
    InputDistribution.NEARLY_SORTED,
    InputDistribution.FEW_UNIQUE,
    InputDistribution.GAUSSIAN,
    InputDistribution.SHUFFLED_MEDIAN,
])
def test_seeded_is_deterministic(dist):
    a = generate_array(40, dist, seed=123)
    b = generate_array(40, dist, seed=123)
    assert a == b, f"{dist}: seeded outputs must be identical"


def test_different_seeds_give_different_random():
    a = generate_array(50, InputDistribution.RANDOM, seed=1)
    b = generate_array(50, InputDistribution.RANDOM, seed=2)
    assert a != b


# ── SORTED distribution ───────────────────────────────────────────────────────

def test_sorted_is_ascending():
    result = generate_array(20, InputDistribution.SORTED)
    assert result == sorted(result)
    assert result == list(range(1, 21))


def test_sorted_elements_are_unique():
    result = generate_array(10, InputDistribution.SORTED)
    assert len(set(result)) == len(result)


# ── REVERSE distribution ──────────────────────────────────────────────────────

def test_reverse_is_descending():
    result = generate_array(15, InputDistribution.REVERSE)
    assert result == sorted(result, reverse=True)
    assert result == list(range(15, 0, -1))


# ── NEARLY_SORTED distribution ────────────────────────────────────────────────

def test_nearly_sorted_is_mostly_ordered():
    """A nearly-sorted array should have few inversions compared to random."""
    n = 100
    nearly = generate_array(n, InputDistribution.NEARLY_SORTED, seed=99)
    assert len(nearly) == n
    # Count inversions — should be much less than n*(n-1)/2
    inversions = sum(
        1
        for i in range(n)
        for j in range(i + 1, n)
        if nearly[i] > nearly[j]
    )
    max_inversions = n * (n - 1) // 2
    assert inversions < max_inversions * 0.15, "nearly_sorted should be mostly ordered"


def test_nearly_sorted_contains_expected_range():
    result = generate_array(20, InputDistribution.NEARLY_SORTED, seed=1)
    assert min(result) >= 1
    assert max(result) <= 20


# ── FEW_UNIQUE distribution ───────────────────────────────────────────────────

def test_few_unique_has_few_distinct_values():
    result = generate_array(80, InputDistribution.FEW_UNIQUE, seed=5)
    distinct = len(set(result))
    assert distinct <= 10, f"few_unique should have few distinct values, got {distinct}"


def test_few_unique_values_in_range():
    result = generate_array(40, InputDistribution.FEW_UNIQUE, seed=3)
    assert all(v >= 1 for v in result)


# ── GAUSSIAN distribution ─────────────────────────────────────────────────────

def test_gaussian_has_central_tendency():
    """Most values should be near the middle of the range."""
    n = 200
    result = generate_array(n, InputDistribution.GAUSSIAN, seed=7)
    assert len(result) == n
    mid = (n + 1) / 2
    near_mid = sum(1 for v in result if abs(v - mid) <= n / 4)
    assert near_mid > n * 0.4, "gaussian should cluster near the centre"


def test_gaussian_values_clamped_in_range():
    n = 50
    result = generate_array(n, InputDistribution.GAUSSIAN, seed=11)
    assert all(1 <= v <= n for v in result)


def test_gaussian_has_variance():
    result = generate_array(100, InputDistribution.GAUSSIAN, seed=42)
    # Should not be all the same value
    assert len(set(result)) > 1


# ── SAWTOOTH distribution ─────────────────────────────────────────────────────

def test_sawtooth_repeating_pattern():
    result = generate_array(20, InputDistribution.SAWTOOTH)
    # First element should repeat somewhere (it's periodic)
    assert result[0] in result[1:]


# ── PIPE_ORGAN distribution ───────────────────────────────────────────────────

def test_pipe_organ_peak_in_middle():
    n = 10
    result = generate_array(n, InputDistribution.PIPE_ORGAN)
    assert len(result) == n
    mid = n // 2
    # Values should increase then decrease
    assert result[0] < result[mid - 1]


# ── SHUFFLED_MEDIAN distribution ──────────────────────────────────────────────

def test_shuffled_median_correct_size():
    result = generate_array(25, InputDistribution.SHUFFLED_MEDIAN, seed=1)
    assert len(result) == 25


# ── parse_custom_input ────────────────────────────────────────────────────────

def test_parse_custom_input_from_string():
    result = parse_custom_input("3, 1, 4, 1, 5")
    assert result == [3, 1, 4, 1, 5]


def test_parse_custom_input_from_list():
    result = parse_custom_input([7, 2, 9])
    assert result == [7, 2, 9]


def test_parse_custom_input_none():
    assert parse_custom_input(None) is None


def test_generate_array_custom_overrides_distribution():
    result = generate_array(100, InputDistribution.RANDOM, custom="9, 8, 7")
    assert result == [9, 8, 7]


# ── InputDistribution helpers ─────────────────────────────────────────────────

def test_choices_returns_all_variants():
    choices = InputDistribution.choices()
    assert len(choices) == len(list(InputDistribution))


def test_cycleable_subset_of_all():
    cycleable = InputDistribution.cycleable()
    assert len(cycleable) >= 1
    assert all(isinstance(d, InputDistribution) for d in cycleable)


def test_parse_normalizes_string():
    assert InputDistribution.parse("random") == InputDistribution.RANDOM
    assert InputDistribution.parse("NEARLY_SORTED") == InputDistribution.NEARLY_SORTED
    assert InputDistribution.parse(None) == InputDistribution.RANDOM
    assert InputDistribution.parse("nonexistent") == InputDistribution.RANDOM


def test_parse_idempotent():
    dist = InputDistribution.GAUSSIAN
    assert InputDistribution.parse(dist) is dist


def test_distribution_label():
    label = distribution_label(InputDistribution.NEARLY_SORTED)
    assert "Nearly" in label or "nearly" in label.lower()
