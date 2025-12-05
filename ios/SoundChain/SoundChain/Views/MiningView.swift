//
//  MiningView.swift
//  SoundChain
//

import SwiftUI

struct MiningView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                frequencyCard
                targetSection
                controlSection
                contributionsSection
                recentBlocksSection
            }
            .padding()
        }
        .navigationTitle("Mining")
        .onDisappear {
            if !appState.isMiner {
                appState.stopTone()
            }
        }
    }

    private var frequencyCard: some View {
        VStack(spacing: 8) {
            Text("\(appState.minerFrequency ?? 0)")
                .font(.system(size: 72, weight: .bold, design: .rounded))

            Text("Hz")
                .font(.title)
                .foregroundStyle(.secondary)

            Text("Slot \(appState.minerSlot.map { $0 + 1 } ?? 0)")
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(.blue, in: Capsule())
                .foregroundStyle(.white)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 32)
        .background(
            appState.isTonePlaying
                ? AnyShapeStyle(LinearGradient(
                    colors: [.green.opacity(0.3), .blue.opacity(0.3)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                ))
                : AnyShapeStyle(Color.secondary.opacity(0.1)),
            in: RoundedRectangle(cornerRadius: 20)
        )
        .overlay {
            if appState.isTonePlaying {
                RoundedRectangle(cornerRadius: 20)
                    .stroke(.green, lineWidth: 2)
            }
        }
    }

    private var targetSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Mining Target")
                .font(.headline)

            if let status = appState.miningStatus {
                VStack(spacing: 16) {
                    HStack {
                        Text("Target")
                        Spacer()
                        Text("\(Int(status.target * 100))%")
                            .fontWeight(.medium)
                    }

                    ProgressView(value: status.current, total: 1.0)
                        .tint(progressColor(current: status.current, target: status.target, tolerance: status.tolerance))

                    HStack {
                        Text("Current: \(Int(status.current * 100))%")
                            .font(.caption)
                            .foregroundStyle(.secondary)

                        Spacer()

                        Text("Tolerance: ±\(Int(status.tolerance * 100))%")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }

                    if abs(status.current - status.target) <= status.tolerance {
                        Label("In range - Block mining!", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                            .font(.subheadline)
                    }
                }
                .padding()
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                Text("Waiting for mining data...")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    private var controlSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Tone Control")
                .font(.headline)

            VStack(spacing: 16) {
                HStack(spacing: 16) {
                    Button {
                        if appState.isTonePlaying {
                            appState.stopTone()
                        } else {
                            appState.startTone()
                        }
                    } label: {
                        Label(
                            appState.isTonePlaying ? "Stop" : "Start",
                            systemImage: appState.isTonePlaying ? "stop.fill" : "play.fill"
                        )
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(appState.isTonePlaying ? .red : .green)
                    .controlSize(.large)

                    Button {
                        appState.leaveMining()
                    } label: {
                        Label("Leave", systemImage: "xmark")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.large)
                }
            }
            .padding()
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
        }
    }

    private var contributionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Miner Contributions")
                .font(.headline)

            if let contributions = appState.miningStatus?.contributions, !contributions.isEmpty {
                ForEach(Array(contributions.keys.sorted()), id: \.self) { minerId in
                    if let contribution = contributions[minerId] {
                        let isMe = minerId == appState.userId
                        HStack {
                            Circle()
                                .fill(isMe ? .green : .blue)
                                .frame(width: 8, height: 8)

                            Text(isMe ? "You" : String(minerId.prefix(8)))
                                .fontWeight(isMe ? .medium : .regular)

                            Spacer()

                            Text("\(Int(contribution * 100))%")
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 8))
                    }
                }
            } else {
                Text("No contributions yet")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    private var recentBlocksSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Blocks")
                .font(.headline)

            if appState.recentBlocks.isEmpty {
                Text("No blocks mined yet")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                ForEach(appState.recentBlocks.prefix(5)) { block in
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Block #\(block.index)")
                                .fontWeight(.medium)
                            Text("\(block.transactions.count) transactions")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()

                        Text("\(block.totalReward, specifier: "%.1f")")
                            .font(.subheadline)
                            .foregroundStyle(.green)
                    }
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 8))
                }
            }
        }
    }

    private func progressColor(current: Double, target: Double, tolerance: Double) -> Color {
        let diff = abs(current - target)
        if diff <= tolerance {
            return .green
        } else if diff <= tolerance * 2 {
            return .yellow
        } else {
            return .red
        }
    }
}

#Preview {
    NavigationStack {
        MiningView()
            .environmentObject(AppState())
    }
}
