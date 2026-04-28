from sortui.algorithms import ALGORITHMS
from sortui.algorithms.base import SortFrame
from sortui.algorithms.specialized import JOKE_ALGORITHMS


def test_joke_algorithms_terminate_and_yield_frames():
    for key in sorted(JOKE_ALGORITHMS):
        frames = list(ALGORITHMS[key]().sort([3, 1, 2]))
        assert frames, key
        assert len(frames) <= 100_005, key
        assert all(isinstance(frame, SortFrame) for frame in frames), key
        assert frames[-1].operation == "done", key


def test_required_joke_metadata():
    stalin_frames = list(ALGORITHMS["stalin"]().sort([1, 3, 2, 4]))
    assert any("purged" in frame.metadata for frame in stalin_frames)

    thanos_frames = list(ALGORITHMS["thanos"]().sort([3, 1, 2]))
    assert any(frame.metadata.get("snap") for frame in thanos_frames)

    quantum_frames = list(ALGORITHMS["quantum_bogosort"]().sort([3, 1, 2]))
    assert sum(1 for frame in quantum_frames if frame.metadata.get("multiverse")) >= 5

    waiting_frames = list(ALGORITHMS["heat_death"]().sort([3, 1, 2]))
    assert sum(1 for frame in waiting_frames if frame.metadata.get("waiting")) == 200


def test_stooge_sort_is_real_algorithm():
    from sortui.algorithms.specialized import StoogeSort

    frames = list(StoogeSort().sort([3, 1, 2]))
    assert frames[-1].array == [1, 2, 3]
    assert any(f.recursion_depth > 0 for f in frames)


def test_slowsort_recurses():
    from sortui.algorithms.specialized import SlowSort

    frames = list(SlowSort().sort([3, 1, 2, 4]))
    assert frames[-1].array == [1, 2, 3, 4]
    assert any(f.recursion_depth > 0 for f in frames)


def test_icantbelieve_sorts():
    from sortui.algorithms.specialized import ICantBelieveSort

    frames = list(ICantBelieveSort().sort([4, 2, 3, 1]))
    assert frames[-1].array == [1, 2, 3, 4]
