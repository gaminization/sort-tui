"""
sortui.audio — pitch-mapped tones via ALSA ctypes.

Backend: ALSA libasound.so.2 via ctypes (confirmed working on this machine).
Fallbacks: ossaudiodev, /dev/audio.
Degrades silently if nothing works.
Rate-limited to one tone per 50ms.
"""

from __future__ import annotations
import ctypes
import ctypes.util
import math
import os
import struct
import threading
import time
from typing import Optional


# ---------------------------------------------------------------------------
# Tone generation — pure Python, no numpy
# ---------------------------------------------------------------------------

def generate_tone(
    frequency: float,
    duration: float = 0.06,
    sample_rate: int = 44100,
    volume: float = 0.3,
) -> bytes:
    """Return signed 16-bit little-endian PCM for a sine tone."""
    n = int(sample_rate * duration)
    tau = 2.0 * math.pi * frequency / sample_rate
    return b"".join(
        struct.pack("<h", max(-32768, min(32767,
            int(volume * 32767 * math.sin(tau * i)))))
        for i in range(n)
    )


def value_to_frequency(value: int, lo: int, hi: int) -> float:
    """Map value linearly to 200–2000 Hz."""
    if hi == lo:
        return 440.0
    return 200.0 + (value - lo) / (hi - lo) * 1800.0


# ---------------------------------------------------------------------------
# ALSA backend via ctypes
# ---------------------------------------------------------------------------

def _try_alsa(pcm16: bytes, device: bytes = b"default") -> bool:
    """Write PCM16 to ALSA. Returns True on success."""
    try:
        lib = ctypes.util.find_library("asound")
        if not lib:
            return False
        alsa = ctypes.CDLL(lib)

        SND_PCM_STREAM_PLAYBACK   = 0
        SND_PCM_FORMAT_S16_LE     = 2
        SND_PCM_ACCESS_RW_INTERLEAVED = 3

        pcm_p = ctypes.c_void_p()
        if alsa.snd_pcm_open(
            ctypes.byref(pcm_p), device, SND_PCM_STREAM_PLAYBACK, 0
        ) != 0:
            return False

        alsa.snd_pcm_set_params(
            pcm_p,
            SND_PCM_FORMAT_S16_LE,
            SND_PCM_ACCESS_RW_INTERLEAVED,
            ctypes.c_uint(1),        # mono
            ctypes.c_uint(44100),    # sample rate
            ctypes.c_int(1),         # soft resample allowed
            ctypes.c_uint(100_000),  # latency: 100ms in µs
        )

        n_frames = len(pcm16) // 2
        buf = ctypes.create_string_buffer(pcm16)
        alsa.snd_pcm_writei(pcm_p, buf, ctypes.c_ulong(n_frames))
        alsa.snd_pcm_drain(pcm_p)
        alsa.snd_pcm_close(pcm_p)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# OSS fallback
# ---------------------------------------------------------------------------

def _try_oss(pcm16: bytes) -> bool:
    try:
        import ossaudiodev  # type: ignore[import]
        dsp = ossaudiodev.open("w")
        dsp.setparameters(ossaudiodev.AFMT_S16_LE, 1, 44100, True)
        dsp.write(pcm16)
        dsp.flush()
        dsp.close()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# /dev/audio fallback (mu-law)
# ---------------------------------------------------------------------------

def _pcm16_to_mulaw(pcm16: bytes) -> bytes:
    BIAS = 33
    out = []
    for i in range(0, len(pcm16) - 1, 2):
        s = struct.unpack_from("<h", pcm16, i)[0]
        sign = 0x80 if s < 0 else 0
        s = min(abs(s) + BIAS, 32767)
        exp = 7
        for exp in range(7, 0, -1):
            if s >= (1 << (exp + 3)):
                break
        mantissa = (s >> (exp + 3)) & 0x0F
        out.append((~(sign | (exp << 4) | mantissa)) & 0xFF)
    return bytes(out)


def _try_dev_audio(pcm16: bytes) -> bool:
    try:
        with open("/dev/audio", "wb") as f:
            f.write(_pcm16_to_mulaw(pcm16))
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# AudioPlayer
# ---------------------------------------------------------------------------

class AudioPlayer:
    """Thread-safe, rate-limited, auto-detecting audio player."""

    # ALSA devices to try in order — default works on this machine
    _ALSA_DEVICES = [b"default", b"pulse", b"pipewire", b"plughw:0,0"]

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._available: Optional[bool] = None
        self._backend: Optional[str] = None
        self._alsa_device: bytes = b"default"
        self._last_play: float = 0.0

    def _detect(self) -> Optional[str]:
        """Try each backend and return the first working one."""
        # ALSA
        try:
            lib = ctypes.util.find_library("asound")
            if lib:
                alsa = ctypes.CDLL(lib)
                pcm = ctypes.c_void_p()
                for dev in self._ALSA_DEVICES:
                    ret = alsa.snd_pcm_open(
                        ctypes.byref(pcm), dev, 0, 0
                    )
                    if ret == 0:
                        alsa.snd_pcm_close(pcm)
                        self._alsa_device = dev
                        return "alsa"
        except Exception:
            pass

        # OSS
        try:
            import ossaudiodev as _oss  # type: ignore[import]
            dsp = _oss.open("w")
            dsp.close()
            return "oss"
        except Exception:
            pass

        # /dev/audio
        if os.path.exists("/dev/audio"):
            return "dev_audio"

        return None

    @property
    def available(self) -> bool:
        if self._available is None:
            self._backend = self._detect()
            self._available = self._backend is not None
        return self._available

    def play(self, value: int, lo: int, hi: int) -> None:
        """Non-blocking pitch-mapped tone. Never raises."""
        if not self.available:
            return
        now = time.monotonic()
        with self._lock:
            if now - self._last_play < 0.05:
                return
            self._last_play = now
        freq = value_to_frequency(value, lo, hi)
        threading.Thread(
            target=self._play_tone, args=(freq,), daemon=True
        ).start()

    def _play_tone(self, frequency: float) -> None:
        try:
            data = generate_tone(frequency)
            if self._backend == "alsa":
                if _try_alsa(data, self._alsa_device):
                    return
                # ALSA failed mid-session — try others
                if _try_oss(data):
                    self._backend = "oss"
                    return
            elif self._backend == "oss":
                if _try_oss(data):
                    return
            _try_dev_audio(data)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Module-level singleton + public API
# ---------------------------------------------------------------------------

_player: Optional[AudioPlayer] = None
_init_lock = threading.Lock()


def get_player() -> AudioPlayer:
    global _player
    if _player is None:
        with _init_lock:
            if _player is None:
                _player = AudioPlayer()
    return _player


def play_note(value: int, lo: int, hi: int) -> None:
    """Called by controller on each swap/compare frame."""
    get_player().play(value, lo, hi)


def is_available() -> bool:
    return get_player().available


def backend_name() -> Optional[str]:
    p = get_player()
    _ = p.available  # trigger detection
    return p._backend
