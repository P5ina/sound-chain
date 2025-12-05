//
//  AppState.swift
//  SoundChain
//

import SwiftUI
import Combine

enum ConnectionState: Equatable {
    case disconnected
    case connecting
    case connected
    case joined
}

enum AppScreen: Hashable {
    case lobby
    case wallet
    case mining
    case leaderboard
}

@MainActor
class AppState: ObservableObject {
    @Published var connectionState: ConnectionState = .disconnected
    @Published var currentScreen: AppScreen = .lobby
    @Published var errorMessage: String?

    @Published var userId: String?
    @Published var userName: String = ""
    @Published var wallet: Wallet?
    @Published var isMiner: Bool = false
    @Published var minerFrequency: Int?
    @Published var minerSlot: Int?

    @Published var gameState: ServerMessage.GameState?
    @Published var miningStatus: MiningStatus?
    @Published var leaderboard: [LeaderboardEntry] = []
    @Published var recentBlocks: [Block] = []

    @Published var isTonePlaying: Bool = false

    private var webSocket: WebSocketClient?
    private let toneGenerator = ToneGenerator()

    var serverHost: String = "raspberrypi.local"
    var serverPort: Int = 8765

    var allUsers: [User] {
        let users = gameState?.users ?? []
        let miners = gameState?.miners ?? []
        return users + miners
    }

    var currentUser: User? {
        guard let userId = userId else { return nil }
        return allUsers.first { $0.id == userId }
    }

    var otherUsers: [User] {
        guard let userId = userId else { return allUsers }
        return allUsers.filter { $0.id != userId }
    }

    var availableMinerSlots: Int {
        4 - (gameState?.miners.count ?? 0)
    }

    func connect() {
        guard let url = URL(string: "ws://\(serverHost):\(serverPort)") else {
            errorMessage = "Invalid server URL"
            return
        }

        connectionState = .connecting
        webSocket = WebSocketClient(serverURL: url)
        webSocket?.delegate = self
        webSocket?.connect()
    }

    func disconnect() {
        stopTone()
        webSocket?.disconnect()
        webSocket = nil
        connectionState = .disconnected
        resetState()
    }

    func join(name: String) {
        userName = name
        let deviceId = DeviceID.getOrCreate()
        webSocket?.join(name: name, deviceId: deviceId)
    }

    func becomeMiner() {
        webSocket?.becomeMiner()
    }

    func leaveMining() {
        stopTone()
        webSocket?.leaveMining()
    }

    func transfer(to userId: String, amount: Double, fee: Double) {
        webSocket?.transfer(to: userId, amount: amount, fee: fee)
    }

    func refreshLeaderboard() {
        webSocket?.getLeaderboard()
    }

    func startTone(amplitude: Double = 1.0) {
        guard let frequency = minerFrequency else { return }
        toneGenerator.start(frequency: Double(frequency), amplitude: amplitude)
        isTonePlaying = true
    }

    func stopTone() {
        toneGenerator.stop()
        isTonePlaying = false
    }

    func setToneAmplitude(_ amplitude: Double) {
        toneGenerator.setAmplitude(amplitude)
    }

    private func resetState() {
        userId = nil
        wallet = nil
        isMiner = false
        minerFrequency = nil
        minerSlot = nil
        gameState = nil
        miningStatus = nil
        leaderboard = []
        recentBlocks = []
        isTonePlaying = false
    }
}

extension AppState: WebSocketClientDelegate {
    nonisolated func didConnect() {
        Task { @MainActor in
            self.connectionState = .connected
        }
    }

    nonisolated func didDisconnect(error: Error?) {
        Task { @MainActor in
            self.connectionState = .disconnected
            if let error = error {
                self.errorMessage = "Disconnected: \(error.localizedDescription)"
            }
            self.stopTone()
        }
    }

    nonisolated func didReceive(message: ServerMessage) {
        Task { @MainActor in
            self.handleMessage(message)
        }
    }

    private func handleMessage(_ message: ServerMessage) {
        switch message {
        case .joined(let userId, _, let wallet):
            self.userId = userId
            self.wallet = wallet
            self.connectionState = .joined

        case .becameMiner(let frequency, let slot):
            self.isMiner = true
            self.minerFrequency = frequency
            self.minerSlot = slot
            self.currentScreen = .mining

        case .leftMining:
            self.isMiner = false
            self.minerFrequency = nil
            self.minerSlot = nil
            self.miningStatus = nil
            self.currentScreen = .lobby

        case .state(let state):
            self.gameState = state
            let allUsers = state.users + state.miners
            if let user = allUsers.first(where: { $0.id == self.userId }) {
                self.wallet = user.wallet
                self.isMiner = user.isMiner
                self.minerFrequency = user.frequency
                self.minerSlot = user.minerSlot
            }

        case .miningStatus(let status):
            self.miningStatus = status

        case .blockMined(let block, let rewards, _):
            self.recentBlocks.insert(block, at: 0)
            if self.recentBlocks.count > 10 {
                self.recentBlocks.removeLast()
            }
            if let myReward = rewards[self.userId ?? ""], myReward > 0 {
                // Could show notification here
            }

        case .transactionPending:
            // Transaction is pending confirmation
            break

        case .transactionConfirmed:
            // Transaction confirmed
            break

        case .leaderboard(let entries):
            self.leaderboard = entries

        case .error(let message):
            self.errorMessage = message

        case .unknown:
            break
        }
    }
}
