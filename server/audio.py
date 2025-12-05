import numpy as np
from scipy.fft import rfft, rfftfreq
from typing import Optional
import threading
import queue

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    AUDIO_AVAILABLE = False

import time

from config import SAMPLE_RATE, CHUNK_SIZE, FFT_WINDOW, MINER_FREQUENCIES, AUDIO_DEVICE


class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = CHUNK_SIZE
        self.fft_window = FFT_WINDOW
        self.frequencies = MINER_FREQUENCIES
        self.frequency_bandwidth = 20  # Hz around each target frequency

        self._audio_queue: queue.Queue = queue.Queue()
        self._running = False
        self._stream = None
        self._thread: Optional[threading.Thread] = None

        # Latest analysis results
        self.contributions: dict[int, float] = {f: 0.0 for f in self.frequencies}
        self.total_level: float = 0.0
        self._last_log_time: float = 0.0
        self._log_interval: float = 2.0  # Log every 2 seconds

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")
        self._audio_queue.put(indata.copy())

    def _analysis_loop(self):
        buffer = np.zeros(self.fft_window)

        while self._running:
            try:
                data = self._audio_queue.get(timeout=0.1)
                mono = data[:, 0] if data.ndim > 1 else data
                mono = mono.flatten()

                # Shift buffer and add new data
                shift = min(len(mono), self.fft_window)
                buffer = np.roll(buffer, -shift)
                buffer[-shift:] = mono[:shift]

                # Apply Hanning window and perform FFT
                windowed = buffer * np.hanning(self.fft_window)
                fft_result = np.abs(rfft(windowed))
                freqs = rfftfreq(self.fft_window, 1.0 / self.sample_rate)

                # Analyze each miner frequency
                total = 0.0
                for freq in self.frequencies:
                    # Find indices within bandwidth
                    mask = (freqs >= freq - self.frequency_bandwidth) & (
                        freqs <= freq + self.frequency_bandwidth
                    )
                    if np.any(mask):
                        power = np.max(fft_result[mask])
                        # Normalize to 0-1 range (approximate)
                        normalized = min(1.0, power / 10000.0)
                        self.contributions[freq] = normalized
                        total += normalized
                    else:
                        self.contributions[freq] = 0.0

                # Total level (average of all contributions)
                self.total_level = total / len(self.frequencies) if self.frequencies else 0.0

                # Periodic logging
                now = time.time()
                if now - self._last_log_time >= self._log_interval:
                    self._last_log_time = now
                    rms = np.sqrt(np.mean(mono ** 2))
                    peak = np.max(np.abs(mono))
                    contrib_str = " ".join([f"{f}Hz:{v:.2f}" for f, v in self.contributions.items()])
                    print(f"[Audio] RMS:{rms:.4f} Peak:{peak:.4f} | {contrib_str} | Total:{self.total_level:.2f}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Analysis error: {e}")

    def start(self):
        if not AUDIO_AVAILABLE:
            print("Audio not available - running in simulation mode")
            self._running = True
            return

        try:
            # List available devices
            print("\n=== Available audio devices ===")
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    marker = " <-- SELECTED" if AUDIO_DEVICE is not None and i == AUDIO_DEVICE else ""
                    print(f"  [{i}] {dev['name']} (inputs: {dev['max_input_channels']}){marker}")
            print("===============================\n")

            self._running = True
            self._stream = sd.InputStream(
                device=AUDIO_DEVICE,
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            )
            self._stream.start()

            device_info = sd.query_devices(AUDIO_DEVICE, 'input') if AUDIO_DEVICE else sd.query_devices(kind='input')
            print(f"Audio analyzer started on: {device_info['name']}")

            self._thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self._thread.start()
        except Exception as e:
            print(f"Failed to start audio: {e}")
            self._running = False

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        print("Audio analyzer stopped")

    def get_contributions(self, active_miners: dict[str, int]) -> dict[str, float]:
        """Get contributions for active miners (user_id -> frequency mapping)"""
        result = {}
        for user_id, frequency in active_miners.items():
            result[user_id] = self.contributions.get(frequency, 0.0)
        return result

    def get_total_level(self) -> float:
        return self.total_level

    def simulate_contribution(self, frequency: int, level: float):
        """For testing without real audio"""
        if frequency in self.contributions:
            self.contributions[frequency] = max(0.0, min(1.0, level))
            self.total_level = sum(self.contributions.values()) / len(self.contributions)


class Buzzer:
    def __init__(self, pin: int):
        self.pin = pin
        self._available = False
        self._gpio = None

        try:
            import RPi.GPIO as GPIO
            self._gpio = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW)
            self._available = True
            print(f"Buzzer initialized on GPIO {pin}")
        except (ImportError, RuntimeError) as e:
            print(f"GPIO not available: {e}")

    def beep(self, duration: float = 0.2):
        if self._available and self._gpio:
            self._gpio.output(self.pin, self._gpio.HIGH)
            import time
            time.sleep(duration)
            self._gpio.output(self.pin, self._gpio.LOW)
        else:
            print("BEEP! (simulated)")

    def cleanup(self):
        if self._available and self._gpio:
            self._gpio.cleanup(self.pin)
