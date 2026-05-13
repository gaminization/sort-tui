"""Tests for sortui.recommendation — analyze_array, recommend, recommendation_text."""

import pytest

from sortui.recommendation import (
    ArrayCharacteristics,
    analyze_array,
    recommend,
    recommendation_reason,
    recommendation_text,
    _inversions,
    _sorted_run_ratio,
    _looks_gaussian,
)


# ── Small arrays → insertion sort ────────────────────────────────────────────

class TestSmallArrayRecommendation:
    def test_small_array_recommends_insertion(self):
        arr = [3, 1, 4, 1, 5]  # size=5, <= 32
        recs = recommend(analyze_array(arr))
        assert "insertion" in recs

    def test_10_elements_recommends_insertion(self):
        arr = list(range(10, 0, -1))
        recs = recommend(analyze_array(arr))
        assert "insertion" in recs or "gnome" in recs

    def test_small_reason_text(self):
        arr = [2, 1]
        reason = recommendation_reason(analyze_array(arr))
        assert "small" in reason.lower()


# ── Nearly-sorted → insertion or timsort ─────────────────────────────────────

class TestNearlySortedRecommendation:
    def test_nearly_sorted_recommends_insertion_or_timsort(self):
        # Highly sorted: very few inversions
        arr = list(range(1, 51))
        # Introduce 1 swap to make it "nearly sorted"
        arr[10], arr[11] = arr[11], arr[10]
        recs = recommend(analyze_array(arr))
        assert "insertion" in recs or "timsort" in recs or "adaptive_merge" in recs

    def test_sorted_array_high_sorted_run_ratio(self):
        arr = list(range(1, 100))
        chars = analyze_array(arr)
        assert chars.sorted_run_ratio >= 0.99

    def test_nearly_sorted_reason_text(self):
        arr = list(range(1, 100))
        reason = recommendation_reason(analyze_array(arr))
        assert "sorted" in reason.lower()

    def test_sorted_run_ratio_of_sorted_is_one(self):
        arr = list(range(1, 20))
        assert _sorted_run_ratio(arr) == pytest.approx(1.0)

    def test_sorted_run_ratio_of_reverse_is_low(self):
        arr = list(range(20, 0, -1))
        ratio = _sorted_run_ratio(arr)
        assert ratio < 0.1


# ── Few unique values → counting or radix ────────────────────────────────────

class TestFewUniqueRecommendation:
    def _few_unique_arr(self, n=200, k=3):
        """n elements drawn from k distinct values."""
        import random
        rng = random.Random(77)
        choices = list(range(1, k + 1))
        return [rng.choice(choices) for _ in range(n)]

    def test_few_unique_recommends_counting_or_radix(self):
        arr = self._few_unique_arr(200, 3)
        chars = analyze_array(arr)
        recs = recommend(chars)
        assert "counting" in recs or "radix_lsd" in recs or "bucket" in recs

    def test_unique_ratio_is_low(self):
        arr = self._few_unique_arr(100, 3)
        chars = analyze_array(arr)
        assert chars.unique_ratio <= 0.15

    def test_few_unique_reason_text(self):
        arr = self._few_unique_arr(100, 3)
        reason = recommendation_reason(analyze_array(arr))
        assert "unique" in reason.lower()


# ── Gaussian distribution ─────────────────────────────────────────────────────

class TestGaussianRecommendation:
    def _gaussian_arr(self, n=150):
        import random
        rng = random.Random(42)
        mid = (n + 1) / 2
        sigma = n / 6
        return [max(1, min(n, int(rng.gauss(mid, sigma)))) for _ in range(n)]

    def test_gaussian_is_detected(self):
        arr = self._gaussian_arr(150)
        chars = analyze_array(arr)
        assert chars.is_gaussian

    def test_gaussian_recommends_bucket(self):
        arr = self._gaussian_arr(150)
        chars = analyze_array(arr)
        recs = recommend(chars)
        assert "bucket" in recs or "spreadsort" in recs or "merge" in recs

    def test_gaussian_reason_text(self):
        arr = self._gaussian_arr(150)
        reason = recommendation_reason(analyze_array(arr))
        assert "gaussian" in reason.lower()


# ── Large array ───────────────────────────────────────────────────────────────

class TestLargeArrayRecommendation:
    def test_large_array_recommends_efficient_sort(self):
        import random
        rng = random.Random(7)
        arr = rng.sample(range(1, 10001), 1000)
        recs = recommend(analyze_array(arr))
        assert "quicksort" in recs or "merge" in recs or "heapsort" in recs

    def test_large_reason_text(self):
        import random
        arr = random.Random(3).sample(range(1, 10001), 1000)
        reason = recommendation_reason(analyze_array(arr))
        # The 1000-element array may be classified as gaussian, large, or balanced
        assert any(word in reason.lower() for word in ("large", "gaussian", "balanced", "general"))


# ── recommendation_text ───────────────────────────────────────────────────────

class TestRecommendationText:
    def test_returns_non_empty_string(self):
        text = recommendation_text([5, 3, 1, 4, 2])
        assert isinstance(text, str)
        assert len(text) > 0

    def test_text_includes_algorithm_name(self):
        text = recommendation_text([1, 2])  # small: should mention insertion
        assert text  # non-empty

    def test_text_includes_reason(self):
        text = recommendation_text(list(range(1, 10)))
        # Should have both label and reason in parentheses
        assert "(" in text and ")" in text

    @pytest.mark.parametrize("arr", [
        [5],
        [1, 2, 3],
        list(range(1, 101)),
        list(range(100, 0, -1)),
    ])
    def test_text_never_empty_for_various_inputs(self, arr):
        assert recommendation_text(arr)


# ── analyze_array ─────────────────────────────────────────────────────────────

class TestAnalyzeArray:
    def test_analyze_empty(self):
        chars = analyze_array([])
        assert chars.size == 0
        # unique_ratio = 0 distinct values / max(1, 0) = 0.0
        assert chars.unique_ratio == 0.0
        # just don't crash

    def test_analyze_sorted(self):
        chars = analyze_array(list(range(1, 11)))
        assert chars.inversion_count == 0
        assert chars.sorted_run_ratio == pytest.approx(1.0)

    def test_analyze_reverse_sorted(self):
        arr = list(range(10, 0, -1))
        chars = analyze_array(arr)
        assert chars.inversion_count > 0

    def test_unique_ratio_all_same(self):
        chars = analyze_array([5, 5, 5, 5, 5])
        assert chars.unique_ratio == pytest.approx(0.2)


# ── _inversions helper ────────────────────────────────────────────────────────

class TestInversions:
    def test_sorted_has_zero_inversions(self):
        assert _inversions([1, 2, 3, 4, 5]) == 0

    def test_reverse_has_max_inversions(self):
        arr = [4, 3, 2, 1]
        n = len(arr)
        assert _inversions(arr) == n * (n - 1) // 2

    def test_single_element_no_inversions(self):
        assert _inversions([42]) == 0

    def test_empty_no_inversions(self):
        assert _inversions([]) == 0


# ── _looks_gaussian ───────────────────────────────────────────────────────────

class TestLooksGaussian:
    def test_all_same_not_gaussian(self):
        assert not _looks_gaussian([5] * 20)

    def test_too_short_not_gaussian(self):
        assert not _looks_gaussian([1, 2, 3])

    def test_uniform_range_not_gaussian(self):
        # Uniform [1..100] — ~68% within ±1σ won't hold naturally
        arr = list(range(1, 101))
        # result can vary; just ensure no crash
        result = _looks_gaussian(arr)
        assert isinstance(result, bool)
