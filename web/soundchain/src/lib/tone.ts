// ToneGenerator using Web Audio API

export class ToneGenerator {
	private audioContext: AudioContext | null = null;
	private oscillator: OscillatorNode | null = null;
	private gainNode: GainNode | null = null;
	private isPlaying = false;
	private currentFrequency = 440;

	constructor() {
		// AudioContext will be created on first user interaction
	}

	private async initAudioContext(): Promise<void> {
		if (!this.audioContext) {
			this.audioContext = new AudioContext();
		}
		if (this.audioContext.state === 'suspended') {
			await this.audioContext.resume();
		}
	}

	async play(frequency: number): Promise<void> {
		if (this.isPlaying) {
			this.stop();
		}

		await this.initAudioContext();

		if (!this.audioContext) return;

		this.currentFrequency = frequency;

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
		this.oscillator.start();
		this.isPlaying = true;
	}

	stop(): void {
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
	}
}

// Singleton instance
export const toneGenerator = new ToneGenerator();
