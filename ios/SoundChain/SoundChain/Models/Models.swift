//
//  Models.swift
//  SoundChain
//

import Foundation

struct Wallet: Codable, Equatable {
    let address: String
    var balance: Double
}

struct User: Codable, Identifiable, Equatable {
    let id: String
    let name: String
    var wallet: Wallet
    var isMiner: Bool
    var minerSlot: Int?
    var frequency: Int?

    enum CodingKeys: String, CodingKey {
        case id = "user_id"
        case name
        case wallet
        case isMiner = "is_miner"
        case minerSlot = "miner_slot"
        case frequency
    }
}

struct Transaction: Codable, Identifiable, Equatable {
    let id: String
    let fromAddress: String
    let toAddress: String
    let amount: Double
    let fee: Double
    let timestamp: Double

    enum CodingKeys: String, CodingKey {
        case id = "tx_id"
        case fromAddress = "from_address"
        case toAddress = "to_address"
        case amount
        case fee
        case timestamp
    }

    var date: Date {
        Date(timeIntervalSince1970: timestamp)
    }
}

struct Block: Codable, Identifiable, Equatable {
    let index: Int
    let timestamp: Double
    let transactions: [Transaction]
    let previousHash: String
    let minerContributions: [String: Double]
    let totalReward: Double
    let hash: String

    var id: Int { index }

    enum CodingKeys: String, CodingKey {
        case index
        case timestamp
        case transactions
        case previousHash = "previous_hash"
        case minerContributions = "miner_contributions"
        case totalReward = "total_reward"
        case hash
    }

    var date: Date {
        Date(timeIntervalSince1970: timestamp)
    }
}

struct LeaderboardEntry: Codable, Identifiable, Equatable {
    let rank: Int
    let name: String
    let balance: Double
    let isMiner: Bool

    var id: Int { rank }

    enum CodingKeys: String, CodingKey {
        case rank
        case name
        case balance
        case isMiner = "is_miner"
    }
}

struct MiningStatus: Codable, Equatable {
    let contributions: [String: Double]
    let target: Double?  // nil when no pending transactions
    let current: Double
    let tolerance: Double
    let pendingTx: Int

    enum CodingKeys: String, CodingKey {
        case contributions
        case target
        case current
        case tolerance
        case pendingTx = "pending_tx"
    }
}
