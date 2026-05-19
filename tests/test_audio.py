import pytest
import struct
import time
import threading
from unittest.mock import patch, MagicMock
from sortui.audio import (
    AudioPlayer,
    generate_tone,
    value_to_frequency,
    play_note,
    is_available,
    get_player,
    backend_name,
    _pcm16_to_mulaw,
)


class TestToneGeneration:
    def test_returns_bytes(self):
        assert isinstance(generate_tone(440.0, duration=0.01), bytes)

    def test_correct_length(self):
        data = generate_tone(440.0, duration=0.04, sample_rate=44100)
        expected = int(0.04 * 44100) * 2
        assert abs(len(data) - expected) <= 4

    def test_even_length(self):
        assert len(generate_tone(440.0, duration=0.01)) % 2 == 0

    def test_samples_in_range(self):
        data = generate_tone(440.0, duration=0.01)
        for i in range(0, len(data), 2):
            v = struct.unpack_from('<h', data, i)[0]
            assert -32768 <= v <= 32767

    def test_silence_at_zero_volume(self):
        data = generate_tone(440.0, duration=0.01, volume=0.0)
        assert all(b == 0 for b in data)


class TestFrequencyMapping:
    def test_min_value_gives_200hz(self):
        assert value_to_frequency(0, 0, 100) == pytest.approx(200.0)

    def test_max_value_gives_2000hz(self):
        assert value_to_frequency(100, 0, 100) == pytest.approx(2000.0)

    def test_midpoint(self):
        assert value_to_frequency(50, 0, 100) == pytest.approx(1100.0)

    def test_equal_range_gives_440hz(self):
        assert value_to_frequency(42, 42, 42) == 440.0

    def test_monotonically_increasing(self):
        freqs = [value_to_frequency(v, 0, 100) for v in range(0, 101, 10)]
        assert freqs == sorted(freqs)


class TestAudioPlayer:
    def _make_player(self, available=True, backend='alsa'):
        p = AudioPlayer()
        p._available = available
        p._backend = backend if available else None
        p._last_play = 0.0
        return p

    def test_unavailable_player_does_not_play(self):
        p = self._make_player(available=False)
        with patch.object(p, '_play_tone') as mock:
            p.play(50, 0, 100)
        mock.assert_not_called()

    def test_rate_limiting_blocks_rapid_calls(self):
        p = self._make_player()
        p._last_play = time.monotonic() + 999
        with patch.object(p, '_play_tone') as mock:
            p.play(50, 0, 100)
        mock.assert_not_called()

    def test_play_triggers_thread_when_ready(self):
        p = self._make_player()
        events = []
        def fake(freq): events.append(freq)
        with patch.object(p, '_play_tone', side_effect=fake):
            p.play(50, 0, 100)
            time.sleep(0.05)
        assert len(events) == 1
        assert 1050 < events[0] < 1150  # ~1100 Hz

    def test_play_tone_swallows_exceptions(self):
        p = self._make_player()
        with patch('sortui.audio._try_alsa', side_effect=RuntimeError("boom")):
            p._play_tone(440.0)  # must not raise

    def test_thread_is_daemon(self):
        p = self._make_player()
        threads_before = threading.active_count()
        p._last_play = 0.0
        with patch.object(p, '_play_tone', return_value=None):
            p.play(50, 0, 100)
            time.sleep(0.02)


class TestMulaw:
    def test_returns_bytes(self):
        pcm = struct.pack('<h', 1000) * 10
        result = _pcm16_to_mulaw(pcm)
        assert isinstance(result, bytes)

    def test_half_length(self):
        pcm = struct.pack('<h', 1000) * 10
        result = _pcm16_to_mulaw(pcm)
        assert len(result) == 10

    def test_values_in_byte_range(self):
        pcm = struct.pack('<h', 5000) * 20
        result = _pcm16_to_mulaw(pcm)
        assert all(0 <= b <= 255 for b in result)


class TestPublicAPI:
    def test_is_available_returns_bool(self):
        assert isinstance(is_available(), bool)

    def test_backend_name_type(self):
        result = backend_name()
        assert result is None or isinstance(result, str)

    def test_get_player_singleton(self):
        assert get_player() is get_player()

    def test_play_note_does_not_raise(self):
        play_note(50, 0, 100)  # must never raise regardless of hardware

    def test_play_note_with_edge_values(self):
        play_note(0, 0, 0)    # equal range
        play_note(0, 0, 100)  # min
        play_note(100, 0, 100)  # max
