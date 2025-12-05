//
//  ToneGenerator.swift
//  SoundChain
//

import AVFoundation

class ToneGenerator {
    private var audioEngine: AVAudioEngine?
    private var sourceNode: AVAudioSourceNode?

    private var frequency: Double = 440.0
    private var amplitude: Double = 0.5
    private var phase: Double = 0.0
    private let sampleRate: Double = 44100.0

    private(set) var isPlaying = false

    init() {
        setupAudioSession()
    }

    private func setupAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .default, options: [])
            try session.setActive(true)
        } catch {
            print("Failed to setup audio session: \(error)")
        }
    }

    func start(frequency: Double, amplitude: Double = 0.5) {
        guard !isPlaying else {
            self.frequency = frequency
            self.amplitude = amplitude
            return
        }

        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = 0.0

        let engine = AVAudioEngine()
        let mainMixer = engine.mainMixerNode
        let outputFormat = mainMixer.outputFormat(forBus: 0)

        let sourceNode = AVAudioSourceNode { [weak self] _, _, frameCount, audioBufferList -> OSStatus in
            guard let self = self else { return noErr }

            let bufferList = UnsafeMutableAudioBufferListPointer(audioBufferList)
            let phaseIncrement = 2.0 * Double.pi * self.frequency / self.sampleRate

            for frame in 0..<Int(frameCount) {
                let sample = Float(sin(self.phase) * self.amplitude)
                self.phase += phaseIncrement
                if self.phase >= 2.0 * Double.pi {
                    self.phase -= 2.0 * Double.pi
                }

                for buffer in bufferList {
                    let ptr = buffer.mData?.assumingMemoryBound(to: Float.self)
                    ptr?[frame] = sample
                }
            }

            return noErr
        }

        engine.attach(sourceNode)
        engine.connect(sourceNode, to: mainMixer, format: outputFormat)

        do {
            try engine.start()
            self.audioEngine = engine
            self.sourceNode = sourceNode
            self.isPlaying = true
        } catch {
            print("Failed to start audio engine: \(error)")
        }
    }

    func stop() {
        audioEngine?.stop()
        if let node = sourceNode {
            audioEngine?.detach(node)
        }
        audioEngine = nil
        sourceNode = nil
        isPlaying = false
    }

    func setAmplitude(_ amplitude: Double) {
        self.amplitude = max(0.0, min(1.0, amplitude))
    }

    func setFrequency(_ frequency: Double) {
        self.frequency = frequency
    }

    deinit {
        stop()
    }
}
