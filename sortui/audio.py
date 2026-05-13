import math
import os
import struct
import threading
import time

def generate_tone(frequency: float, duration: float = 0.04,
                  sample_rate: int = 44100, volume: float = 0.3) -> bytes:
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        val = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        val = max(-32768, min(32767, val))
        samples.append(struct.pack('<h', val))
    return b''.join(samples)

def value_to_frequency(value: int, min_val: int, max_val: int) -> float:
    # Map value range to 200Hz-2000Hz (audible, not annoying)
    if max_val == min_val:
        return 440.0
    ratio = (value - min_val) / (max_val - min_val)
    return 200.0 + ratio * 1800.0

class AudioPlayer:
    def __init__(self):
        self._available = self._check_available()
        self._last_play = 0.0

    def _check_available(self) -> bool:
        try:
            import ossaudiodev
            return True
        except ImportError:
            pass
        try:
            return os.path.exists('/dev/audio')
        except Exception:
            return False

    def play(self, value: int, min_val: int, max_val: int) -> None:
        """Play a short tone for the given value. Non-blocking. Never raises."""
        if not self._available:
            return
        now = time.monotonic()
        if now - self._last_play < 0.05:
            return
        self._last_play = now
        freq = value_to_frequency(value, min_val, max_val)
        threading.Thread(
            target=self._play_tone,
            args=(freq,),
            daemon=True
        ).start()

    def _play_tone(self, frequency: float) -> None:
        try:
            data = generate_tone(frequency)
            self._write_audio(data)
        except Exception:
            pass  # never surface audio errors to the user

    def _write_audio(self, data: bytes) -> None:
        try:
            import ossaudiodev
            dsp = ossaudiodev.open('w')
            try:
                dsp.setparameters(ossaudiodev.AFMT_S16_LE, 1, 44100, True)
                dsp.write(data)
                dsp.flush()
            finally:
                dsp.close()
            return
        except Exception:
            pass
        try:
            with open('/dev/audio', 'wb') as f:
                f.write(self._to_mulaw(data))
        except Exception:
            pass

    def _to_mulaw(self, pcm16: bytes) -> bytes:
        """Convert 16-bit PCM to 8-bit mu-law for /dev/audio."""
        import struct
        MULAW_BIAS = 33
        result = []
        for i in range(0, len(pcm16) - 1, 2):
            sample = struct.unpack_from('<h', pcm16, i)[0]
            sign = 0 if sample >= 0 else 0x80
            sample = abs(sample)
            sample = min(sample + MULAW_BIAS, 32767)
            exp = 7
            for exp_val in range(7, 0, -1):
                if sample >= (1 << (exp_val + 3)):
                    exp = exp_val
                    break
            mantissa = (sample >> (exp + 3)) & 0x0F
            result.append(~(sign | (exp << 4) | mantissa) & 0xFF)
        return bytes(result)

# Module-level singleton
_player: AudioPlayer | None = None

def get_player() -> AudioPlayer:
    global _player
    if _player is None:
        _player = AudioPlayer()
    return _player

def play_note(value: int, min_val: int, max_val: int) -> None:
    """Called by controller on each swap/compare frame when audio enabled."""
    get_player().play(value, min_val, max_val)

def is_available() -> bool:
    return get_player()._available
