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

from config import SAMPLE_RATE, CHUNK_SIZE, FFT_WINDOW, AUDIO_DEVICE


class AudioAnalyzer:
    """
    Audio analyzer that detects pure sine tones from phones and measures their frequencies.

    New mechanics:
    - Each miner controls their tone frequency via a slider
    - Server detects the frequency being played and compares to target
    - Pure sine tones are distinguished from voice/noise by checking spectral purity
    """

    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = CHUNK_SIZE
        self.fft_window = FFT_WINDOW

        # Frequency detection parameters
        self.min_freq = 200  # Hz - minimum detectable frequency
        self.max_freq = 2000  # Hz - maximum detectable frequency
        self.min_power_threshold = 5.0  # Minimum FFT power to consider a tone
        self.purity_threshold = 0.6  # Minimum purity to consider it a sine tone (0-1)

        self._audio_queue: queue.Queue = queue.Queue()
        self._running = False
        self._stream = None
        self._thread: Optional[threading.Thread] = None

        # Detected tones: list of (frequency, power, purity) for each detected pure tone
        self.detected_tones: list[tuple[float, float, float]] = []

        # Miner frequency assignments (user_id -> their current frequency from slider)
        self.miner_frequencies: dict[str, float] = {}

        self._last_log_time: float = 0.0
        self._log_interval: float = 2.0

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")
        self._audio_queue.put(indata.copy())

    def _calculate_spectral_purity(self, fft_result: np.ndarray, freqs: np.ndarray,
                                    peak_freq: float, peak_power: float) -> float:
        """
        Calculate how 'pure' a tone is (sine wave vs complex sound like voice).

        Pure sine wave: energy concentrated in fundamental frequency
        Voice/noise: energy spread across harmonics and other frequencies

        Returns 0-1 where 1 is a perfect sine wave.
        """
        if peak_power < self.min_power_threshold:
            return 0.0

        # Define bandwidth around fundamental (±20 Hz)
        fundamental_bandwidth = 20
        mask_fundamental = (freqs >= peak_freq - fundamental_bandwidth) & \
                          (freqs <= peak_freq + fundamental_bandwidth)

        # Energy in fundamental region
        fundamental_energy = np.sum(fft_result[mask_fundamental] ** 2)

        # Total energy in detectable range
        mask_range = (freqs >= self.min_freq) & (freqs <= self.max_freq)
        total_energy = np.sum(fft_result[mask_range] ** 2)

        if total_energy < 1e-10:
            return 0.0

        # Purity = ratio of fundamental energy to total energy
        purity = fundamental_energy / total_energy

        # Also check harmonics - pure sine should have minimal harmonic content
        harmonic_penalty = 0.0
        for harmonic in [2, 3, 4]:  # Check 2nd, 3rd, 4th harmonics
            harmonic_freq = peak_freq * harmonic
            if harmonic_freq > self.max_freq:
                break
            mask_harmonic = (freqs >= harmonic_freq - fundamental_bandwidth) & \
                           (freqs <= harmonic_freq + fundamental_bandwidth)
            if np.any(mask_harmonic):
                harmonic_power = np.max(fft_result[mask_harmonic])
                # Penalize if harmonics are significant relative to fundamental
                if harmonic_power > peak_power * 0.1:  # More than 10% of fundamental
                    harmonic_penalty += 0.1

        purity = max(0.0, purity - harmonic_penalty)
        return min(1.0, purity)

    def _find_pure_tones(self, fft_result: np.ndarray, freqs: np.ndarray) -> list[tuple[float, float, float]]:
        """
        Find all pure sine tones in the spectrum.
        Returns list of (frequency, power, purity) tuples.
        """
        tones = []

        # Mask for valid frequency range
        mask = (freqs >= self.min_freq) & (freqs <= self.max_freq)
        valid_freqs = freqs[mask]
        valid_fft = fft_result[mask]

        if len(valid_fft) == 0:
            return tones

        # Find local maxima (peaks)
        peaks = []
        for i in range(1, len(valid_fft) - 1):
            if valid_fft[i] > valid_fft[i-1] and valid_fft[i] > valid_fft[i+1]:
                if valid_fft[i] > self.min_power_threshold:
                    peaks.append((valid_freqs[i], valid_fft[i]))

        # Sort by power and take top peaks
        peaks.sort(key=lambda x: x[1], reverse=True)
        peaks = peaks[:10]  # Max 10 peaks to analyze

        for freq, power in peaks:
            purity = self._calculate_spectral_purity(fft_result, freqs, freq, power)
            if purity >= self.purity_threshold:
                # This is likely a pure sine tone from a phone
                tones.append((freq, power, purity))

        return tones

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

                # Find all pure tones
                self.detected_tones = self._find_pure_tones(fft_result, freqs)

                # Periodic logging
                now = time.time()
                if now - self._last_log_time >= self._log_interval:
                    self._last_log_time = now
                    rms = np.sqrt(np.mean(mono ** 2))

                    if self.detected_tones:
                        tones_str = " | ".join([f"{f:.0f}Hz (pwr:{p:.1f}, pur:{r:.2f})"
                                               for f, p, r in self.detected_tones])
                        print(f"[Audio] RMS:{rms:.4f} | Pure tones: {tones_str}")
                    else:
                        # Show top FFT peaks for debugging when no pure tones found
                        top_indices = np.argsort(fft_result)[-3:][::-1]
                        top_peaks = [(int(freqs[i]), float(fft_result[i])) for i in top_indices if freqs[i] >= self.min_freq]
                        if top_peaks:
                            peaks_str = " ".join([f"{f}Hz={p:.0f}" for f, p in top_peaks])
                            print(f"[Audio] RMS:{rms:.4f} | No pure tones | Top peaks: {peaks_str}")

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

            device_info = sd.query_devices(AUDIO_DEVICE, 'input') if AUDIO_DEVICE is not None else sd.query_devices(kind='input')
            print(f"Audio analyzer started on device {AUDIO_DEVICE}: {device_info['name']}")

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

    def set_miner_frequency(self, user_id: str, frequency: float):
        """Update a miner's current frequency (from their slider control)"""
        self.miner_frequencies[user_id] = frequency

    def remove_miner(self, user_id: str):
        """Remove a miner from tracking"""
        if user_id in self.miner_frequencies:
            del self.miner_frequencies[user_id]

    def get_miner_contributions(self, target_frequency: float, tolerance_hz: float = 50.0) -> dict[str, dict]:
        """
        Calculate contributions for all miners based on frequency matching.

        For each miner, we:
        1. Check if there's a detected pure tone near their frequency
        2. Calculate how close that tone is to the target frequency
        3. Return contribution based on accuracy

        Returns: {user_id: {frequency: float, detected: bool, accuracy: float, contribution: float}}
        """
        result = {}

        for user_id, miner_freq in self.miner_frequencies.items():
            # Find if there's a detected pure tone near the miner's frequency
            best_match = None
            best_distance = float('inf')

            for tone_freq, power, purity in self.detected_tones:
                distance = abs(tone_freq - miner_freq)
                if distance < tolerance_hz and distance < best_distance:
                    best_match = (tone_freq, power, purity)
                    best_distance = distance

            if best_match:
                detected_freq, power, purity = best_match
                # Calculate accuracy: how close the detected tone is to target
                freq_error = abs(detected_freq - target_frequency)
                # Accuracy is 1.0 at target, decreasing linearly
                # At ±100 Hz from target, accuracy = 0
                max_error = 100.0  # Hz
                accuracy = max(0.0, 1.0 - (freq_error / max_error))
                contribution = accuracy * purity  # Weight by purity

                result[user_id] = {
                    'frequency': detected_freq,
                    'detected': True,
                    'accuracy': accuracy,
                    'purity': purity,
                    'contribution': contribution
                }
            else:
                result[user_id] = {
                    'frequency': miner_freq,
                    'detected': False,
                    'accuracy': 0.0,
                    'purity': 0.0,
                    'contribution': 0.0
                }

        return result

    def get_detected_tones(self) -> list[tuple[float, float, float]]:
        """Get list of detected pure tones (frequency, power, purity)"""
        return self.detected_tones.copy()

    def simulate_tone(self, frequency: float, power: float = 20.0, purity: float = 0.9):
        """For testing without real audio - simulate a detected tone"""
        self.detected_tones = [(frequency, power, purity)]


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
