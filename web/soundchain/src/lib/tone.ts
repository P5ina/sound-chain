// ToneGenerator using Web Audio API with iOS Safari support

type AudioContextType = typeof AudioContext;

function getAudioContextClass(): AudioContextType | null {
	if (typeof window === 'undefined') return null;
	return window.AudioContext || (window as unknown as { webkitAudioContext: AudioContextType }).webkitAudioContext || null;
}

export class ToneGenerator {
	private audioContext: AudioContext | null = null;
	private oscillator: OscillatorNode | null = null;
	private gainNode: GainNode | null = null;
	private isPlaying = false;
	private currentFrequency = 440;
	private isUnlocked = false;

	constructor() {
		// AudioContext will be created on first user interaction
	}

	private async initAudioContext(): Promise<boolean> {
		const AudioContextClass = getAudioContextClass();
		if (!AudioContextClass) {
			console.error('[ToneGenerator] Web Audio API not supported');
			return false;
		}

		if (!this.audioContext) {
			try {
				this.audioContext = new AudioContextClass();
				console.log('[ToneGenerator] AudioContext created, state:', this.audioContext.state);
			} catch (e) {
				console.error('[ToneGenerator] Failed to create AudioContext:', e);
				return false;
			}
		}

		// iOS Safari requires resume() to be called from a user gesture
		if (this.audioContext.state === 'suspended') {
			try {
				await this.audioContext.resume();
				console.log('[ToneGenerator] AudioContext resumed, state:', this.audioContext.state);
			} catch (e) {
				console.error('[ToneGenerator] Failed to resume AudioContext:', e);
				return false;
			}
		}

		// iOS Safari hack: play a silent buffer to "unlock" audio
		if (!this.isUnlocked && this.audioContext.state === 'running') {
			try {
				const silentBuffer = this.audioContext.createBuffer(1, 1, 22050);
				const source = this.audioContext.createBufferSource();
				source.buffer = silentBuffer;
				source.connect(this.audioContext.destination);
				source.start(0);
				this.isUnlocked = true;
				console.log('[ToneGenerator] Audio unlocked on iOS');
			} catch (e) {
				console.warn('[ToneGenerator] Silent buffer unlock failed:', e);
			}
		}

		return this.audioContext.state === 'running';
	}

	async play(frequency: number): Promise<boolean> {
		console.log('[ToneGenerator] play() called with frequency:', frequency);

		if (this.isPlaying) {
			this.stop();
		}

		const ready = await this.initAudioContext();
		if (!ready || !this.audioContext) {
			console.error('[ToneGenerator] AudioContext not ready');
			return false;
		}

		this.currentFrequency = frequency;

		try {
			// Create oscillator
			this.oscillator = this.audioContext.createOscillator();
			this.oscillator.type = 'sine';
			this.oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);

			// Create gain node for volume control
			this.gainNode = this.audioContext.createGain();
			this.gainNode.gain.setValueAtTime(0.5, this.audioContext.currentTime);

			// Connect: oscillator -> gain -> output
			this.oscillator.connect(this.gainNode);
			this.gainNode.connect(this.audioContext.destination);

			// Start the oscillator
			this.oscillator.start(0);
			this.isPlaying = true;
			console.log('[ToneGenerator] Tone started at', frequency, 'Hz');
			return true;
		} catch (e) {
			console.error('[ToneGenerator] Failed to start tone:', e);
			return false;
		}
	}

	stop(): void {
		console.log('[ToneGenerator] stop() called');

		if (this.oscillator) {
			try {
				this.oscillator.stop();
				this.oscillator.disconnect();
			} catch {
				// Ignore errors if already stopped
			}
			this.oscillator = null;
		}

		if (this.gainNode) {
			this.gainNode.disconnect();
			this.gainNode = null;
		}

		this.isPlaying = false;
	}

	setVolume(volume: number): void {
		if (this.gainNode && this.audioContext) {
			const clampedVolume = Math.max(0, Math.min(1, volume));
			this.gainNode.gain.setValueAtTime(clampedVolume, this.audioContext.currentTime);
		}
	}

	get playing(): boolean {
		return this.isPlaying;
	}

	get frequency(): number {
		return this.currentFrequency;
	}

	dispose(): void {
		this.stop();
		if (this.audioContext) {
			this.audioContext.close();
			this.audioContext = null;
		}
		this.isUnlocked = false;
	}
}

// Singleton instance
export const toneGenerator = new ToneGenerator();
