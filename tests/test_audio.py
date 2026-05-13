import pytest
from unittest.mock import patch, MagicMock
from sortui.audio import AudioPlayer, generate_tone, value_to_frequency, play_note

def test_generate_tone_returns_bytes():
    data = generate_tone(440.0, duration=0.01)
    assert isinstance(data, bytes)
    assert len(data) > 0

def test_generate_tone_correct_length():
    data = generate_tone(440.0, duration=0.04, sample_rate=44100)
    # 0.04s * 44100 samples * 2 bytes per sample
    assert len(data) == pytest.approx(0.04 * 44100 * 2, abs=4)

def test_value_to_frequency_min():
    assert value_to_frequency(0, 0, 100) == pytest.approx(200.0)

def test_value_to_frequency_max():
    assert value_to_frequency(100, 0, 100) == pytest.approx(2000.0)

def test_value_to_frequency_equal_range():
    # min == max should not crash
    assert value_to_frequency(50, 50, 50) == 440.0

def test_play_note_does_not_raise_when_unavailable():
    player = AudioPlayer()
    player._available = False
    player.play(50, 0, 100)  # must not raise

def test_play_note_rate_limited():
    player = AudioPlayer()
    player._available = True
    player._last_play = float('inf')  # simulate recent play
    # Should return immediately without playing
    with patch.object(player, '_play_tone') as mock:
        player.play(50, 0, 100)
        mock.assert_not_called()

def test_play_tone_swallows_exceptions():
    player = AudioPlayer()
    with patch.object(player, '_write_audio', side_effect=OSError("no device")):
        player._play_tone(440.0)  # must not raise

def test_mulaw_conversion_returns_bytes():
    import struct
    pcm = struct.pack('<h', 1000) * 10
    player = AudioPlayer()
    result = player._to_mulaw(pcm)
    assert isinstance(result, bytes)

def test_is_available_returns_bool():
    from sortui.audio import is_available
    result = is_available()
    assert isinstance(result, bool)
