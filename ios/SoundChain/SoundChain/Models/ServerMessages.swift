//
//  ServerMessages.swift
//  SoundChain
//

import Foundation

enum ServerMessage {
    case joined(userId: String, role: String, wallet: Wallet)
    case becameMiner(frequency: Int, slot: Int)
    case leftMining
    case state(GameState)
    case miningStatus(MiningStatus)
    case blockMined(block: Block, rewards: [String: Double], blockTime: Double)
    case transactionPending(transaction: Transaction)
    case transactionConfirmed(transaction: Transaction)
    case leaderboard(entries: [LeaderboardEntry])
    case error(message: String)
    case unknown

    struct GameState: Codable, Equatable {
        let chainLength: Int
        let pendingTx: Int
        let miners: [User]
        let users: [User]
        let blockReward: Double
        let pendingFees: Double

        enum CodingKeys: String, CodingKey {
            case chainLength = "chain_length"
            case pendingTx = "pending_tx"
            case miners
            case users
            case blockReward = "block_reward"
            case pendingFees = "pending_fees"
        }
    }
}

extension ServerMessage {
    static func parse(from data: Data) -> ServerMessage {
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else {
            return .unknown
        }

        let decoder = JSONDecoder()

        switch type {
        case "joined":
            guard let userId = json["user_id"] as? String,
                  let role = json["role"] as? String,
                  let walletData = try? JSONSerialization.data(withJSONObject: json["wallet"] ?? [:]),
                  let wallet = try? decoder.decode(Wallet.self, from: walletData) else {
                return .unknown
            }
            return .joined(userId: userId, role: role, wallet: wallet)

        case "became_miner":
            guard let frequency = json["frequency"] as? Int,
                  let slot = json["slot"] as? Int else {
                return .unknown
            }
            return .becameMiner(frequency: frequency, slot: slot)

        case "left_mining":
            return .leftMining

        case "state":
            guard let stateData = try? JSONSerialization.data(withJSONObject: json),
                  let state = try? decoder.decode(GameState.self, from: stateData) else {
                return .unknown
            }
            return .state(state)

        case "mining_status":
            guard let statusData = try? JSONSerialization.data(withJSONObject: json),
                  let status = try? decoder.decode(MiningStatus.self, from: statusData) else {
                return .unknown
            }
            return .miningStatus(status)

        case "block_mined":
            guard let blockData = try? JSONSerialization.data(withJSONObject: json["block"] ?? [:]),
                  let block = try? decoder.decode(Block.self, from: blockData),
                  let rewards = json["rewards"] as? [String: Double],
                  let blockTime = json["block_time"] as? Double else {
                return .unknown
            }
            return .blockMined(block: block, rewards: rewards, blockTime: blockTime)

        case "transaction_pending":
            guard let txData = try? JSONSerialization.data(withJSONObject: json["tx"] ?? [:]),
                  let tx = try? decoder.decode(Transaction.self, from: txData) else {
                return .unknown
            }
            return .transactionPending(transaction: tx)

        case "transaction_confirmed":
            guard let txData = try? JSONSerialization.data(withJSONObject: json["tx"] ?? [:]),
                  let tx = try? decoder.decode(Transaction.self, from: txData) else {
                return .unknown
            }
            return .transactionConfirmed(transaction: tx)

        case "leaderboard":
            guard let entriesData = try? JSONSerialization.data(withJSONObject: json["entries"] ?? []),
                  let entries = try? decoder.decode([LeaderboardEntry].self, from: entriesData) else {
                return .unknown
            }
            return .leaderboard(entries: entries)

        case "error":
            let message = json["message"] as? String ?? "Unknown error"
            return .error(message: message)

        default:
            return .unknown
        }
    }
}
