from sortui.algorithms import ALGORITHMS
from sortui.stability import stability_violations, tag_duplicates


def test_stable_algorithms_preserve_duplicate_order():
    original = tag_duplicates([5, 3, 5, 3, 5, 1])
    for key, cls in sorted(ALGORITHMS.items()):
        if not cls.stable:
            continue
        frames = list(cls().sort(original[:], ascending=True))
        assert frames, key
        assert stability_violations(original, frames[-1].array) == 0, key


def test_tag_duplicates_uses_letter_suffixes():
    tagged = tag_duplicates([5, 3, 5, 3])
    assert [str(value) for value in tagged] == ["5a", "3a", "5b", "3b"]

