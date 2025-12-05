//
//  LeaderboardView.swift
//  SoundChain
//

import SwiftUI

struct LeaderboardView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                if appState.leaderboard.isEmpty {
                    emptyState
                } else {
                    podium
                    leaderboardList
                }
            }
            .padding()
        }
        .navigationTitle("Leaderboard")
        .refreshable {
            appState.refreshLeaderboard()
        }
        .onAppear {
            appState.refreshLeaderboard()
        }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.bar.xaxis")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)

            Text("No rankings yet")
                .font(.headline)

            Text("Start mining or make transactions to appear on the leaderboard")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 48)
    }

    private var podium: some View {
        HStack(alignment: .bottom, spacing: 8) {
            if appState.leaderboard.count > 1 {
                podiumPlace(entry: appState.leaderboard[1], place: 2, height: 80)
            }

            if !appState.leaderboard.isEmpty {
                podiumPlace(entry: appState.leaderboard[0], place: 1, height: 100)
            }

            if appState.leaderboard.count > 2 {
                podiumPlace(entry: appState.leaderboard[2], place: 3, height: 60)
            }
        }
        .padding(.bottom, 16)
    }

    private func podiumPlace(entry: LeaderboardEntry, place: Int, height: CGFloat) -> some View {
        VStack(spacing: 8) {
            Text(medalEmoji(for: place))
                .font(.title)

            Text(entry.name)
                .font(.subheadline)
                .fontWeight(.medium)
                .lineLimit(1)

            Text("\(entry.balance, specifier: "%.1f")")
                .font(.caption)
                .foregroundStyle(.secondary)

            Rectangle()
                .fill(podiumColor(for: place))
                .frame(height: height)
                .overlay(alignment: .center) {
                    Text("\(place)")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundStyle(.white)
                }
        }
        .frame(maxWidth: .infinity)
    }

    private var leaderboardList: some View {
        VStack(spacing: 8) {
            ForEach(appState.leaderboard) { entry in
                HStack {
                    Text("\(entry.rank)")
                        .font(.headline)
                        .frame(width: 32)
                        .foregroundStyle(entry.rank <= 3 ? podiumColor(for: entry.rank) : .secondary)

                    if entry.isMiner {
                        Image(systemName: "waveform")
                            .foregroundStyle(.green)
                            .font(.caption)
                    }

                    Text(entry.name)
                        .fontWeight(.medium)

                    Spacer()

                    Text("\(entry.balance, specifier: "%.2f")")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding()
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    private func medalEmoji(for place: Int) -> String {
        switch place {
        case 1: return "🥇"
        case 2: return "🥈"
        case 3: return "🥉"
        default: return ""
        }
    }

    private func podiumColor(for place: Int) -> Color {
        switch place {
        case 1: return .yellow
        case 2: return .gray
        case 3: return .orange
        default: return .secondary
        }
    }
}

#Preview {
    NavigationStack {
        LeaderboardView()
            .environmentObject(AppState())
    }
}
