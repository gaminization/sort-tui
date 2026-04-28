from sortui.algorithms import get_algorithm
from sortui.export import export_run
from sortui.stats import SortStats
from sortui.time_travel import TimeTravelEngine


def test_advance_rewind_round_trip_and_seek():
    engine = TimeTravelEngine(get_algorithm("bubble")(), [3, 2, 1])
    first = engine.advance()
    second = engine.advance()
    assert second is not None
    assert engine.rewind() == first
    assert engine.seek(0) == first


def test_export_and_load_replay_are_deterministic(tmp_path):
    engine = TimeTravelEngine(get_algorithm("insertion")(), [4, 1, 3, 2])
    stats = SortStats()
    while True:
        frame = engine.advance()
        if frame is None:
            break
        stats.update(frame)
    path = export_run(engine, get_algorithm("insertion")(), stats, tmp_path / "run.json")
    replay = TimeTravelEngine.load_replay(str(path))
    replay_frames = []
    while True:
        frame = replay.advance()
        if frame is None:
            break
        replay_frames.append(frame)
    assert [frame.array for frame in replay_frames] == [frame.array for frame in engine._history]


def test_history_never_exceeds_max_history():
    engine = TimeTravelEngine(get_algorithm("bubble")(), [5, 4, 3, 2, 1])
    engine.max_history = 3
    for _ in range(20):
        if engine.advance() is None:
            break
    assert engine.buffered <= 3

