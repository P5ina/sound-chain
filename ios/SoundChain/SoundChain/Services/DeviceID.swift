//
//  DeviceID.swift
//  SoundChain
//

import Foundation

/// Manages a persistent unique device ID stored in UserDefaults
enum DeviceID {
    private static let key = "soundchain_device_id"

    /// Gets the device ID, generating and storing one if it doesn't exist
    static func getOrCreate() -> String {
        if let existing = UserDefaults.standard.string(forKey: key) {
            return existing
        }

        let newID = UUID().uuidString
        UserDefaults.standard.set(newID, forKey: key)
        return newID
    }

    /// Gets the stored device ID (may be nil if not yet created)
    static func get() -> String? {
        UserDefaults.standard.string(forKey: key)
    }
}
