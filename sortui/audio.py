from __future__ import annotations

import math
import os
import threading

SAMPLE_RATE = 8000
AUDIO_DEVICE = "/dev/audio"


def beep(freq: float, duration_ms: int = 30, volume: float = 0.3) -> None:
    """Write a short PCM sine tone to /dev/audio; silently no-op if unavailable."""
    if not os.path.exists(AUDIO_DEVICE):
        return
    freq = max(20.0, min(20_000.0, float(freq)))
    volume = max(0.0, min(1.0, float(volume)))
    sample_count = max(1, int(SAMPLE_RATE * duration_ms / 1000))
    data = bytearray()
    for i in range(sample_count):
        sample = math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE))
        data.append(max(0, min(255, int(128 + sample * 127 * volume))))
    try:
        with open(AUDIO_DEVICE, "wb", buffering=0) as fh:
            fh.write(data)
    except OSError:
        return


def value_to_frequency(
    value: int,
    max_value: int,
    *,
    min_freq: int = 200,
    max_freq: int = 1200,
) -> float:
    ratio = int(value) / max(1, int(max_value))
    return min_freq + ratio * (max_freq - min_freq)


def play_value_async(
    value: int,
    max_value: int,
    *,
    enabled: bool,
    min_freq: int = 200,
    max_freq: int = 1200,
) -> None:
    if not enabled:
        return
    freq = value_to_frequency(value, max_value, min_freq=min_freq, max_freq=max_freq)
    thread = threading.Thread(target=beep, args=(freq,), daemon=True)
    thread.start()

