//
//  LobbyView.swift
//  SoundChain
//

import SwiftUI

struct LobbyView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                headerSection
                statsSection
                minerSection
                usersSection
            }
            .padding()
        }
        .navigationTitle("SoundChain")
    }

    private var headerSection: some View {
        VStack(spacing: 8) {
            if let wallet = appState.wallet {
                Text("\(wallet.balance, specifier: "%.2f")")
                    .font(.system(size: 48, weight: .bold, design: .rounded))

                Text("coins")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 24)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }

    private var statsSection: some View {
        HStack(spacing: 16) {
            StatCard(title: "Chain", value: "\(appState.gameState?.chainLength ?? 0)", icon: "link")
            StatCard(title: "Pending", value: "\(appState.gameState?.pendingTx ?? 0)", icon: "clock")
            StatCard(title: "Reward", value: String(format: "%.1f", appState.gameState?.blockReward ?? 0), icon: "gift")
        }
    }

    private var minerSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Miners")
                    .font(.headline)

                Spacer()

                Text("\(appState.availableMinerSlots) slots available")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            if appState.isMiner {
                HStack {
                    VStack(alignment: .leading) {
                        Text("You are mining")
                            .font(.subheadline)
                            .fontWeight(.medium)
                        Text("\(appState.minerFrequency ?? 0) Hz")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }

                    Spacer()

                    Button("Stop Mining") {
                        appState.leaveMining()
                    }
                    .buttonStyle(.bordered)
                    .tint(.red)
                }
                .padding()
                .background(.green.opacity(0.1), in: RoundedRectangle(cornerRadius: 12))
            } else if appState.availableMinerSlots > 0 {
                Button {
                    appState.becomeMiner()
                } label: {
                    Label("Become a Miner", systemImage: "waveform")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            } else {
                Text("All miner slots are occupied")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            }

            if let miners = appState.gameState?.miners, !miners.isEmpty {
                ForEach(miners) { miner in
                    MinerRow(miner: miner, isCurrentUser: miner.id == appState.userId)
                }
            }
        }
    }

    private var usersSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Users")
                .font(.headline)

            if appState.otherUsers.isEmpty {
                Text("No other users connected")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                ForEach(appState.otherUsers) { user in
                    UserRow(user: user)
                }
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundStyle(.blue)

            Text(value)
                .font(.title2)
                .fontWeight(.bold)

            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

struct MinerRow: View {
    let miner: User
    let isCurrentUser: Bool

    var body: some View {
        HStack {
            Circle()
                .fill(.green)
                .frame(width: 8, height: 8)

            VStack(alignment: .leading) {
                HStack {
                    Text(miner.name)
                        .fontWeight(.medium)
                    if isCurrentUser {
                        Text("(you)")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                Text("\(miner.frequency ?? 0) Hz")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Text("\(miner.wallet.balance, specifier: "%.2f")")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

struct UserRow: View {
    let user: User

    var body: some View {
        HStack {
            Image(systemName: "person.circle.fill")
                .foregroundStyle(.blue)

            Text(user.name)
                .fontWeight(.medium)

            Spacer()

            Text("\(user.wallet.balance, specifier: "%.2f")")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    NavigationStack {
        LobbyView()
            .environmentObject(AppState())
    }
}
