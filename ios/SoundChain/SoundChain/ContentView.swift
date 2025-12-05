//
//  ContentView.swift
//  SoundChain
//
//  Created by Timur Turatbekov on 05.12.2025.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var appState = AppState()

    var body: some View {
        Group {
            if appState.connectionState == .joined {
                MainTabView()
            } else {
                ConnectionView()
            }
        }
        .environmentObject(appState)
    }
}

struct MainTabView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        TabView(selection: $appState.currentScreen) {
            NavigationStack {
                LobbyView()
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(AppScreen.lobby)

            NavigationStack {
                WalletView()
            }
            .tabItem {
                Label("Wallet", systemImage: "wallet.pass")
            }
            .tag(AppScreen.wallet)

            if appState.isMiner {
                NavigationStack {
                    MiningView()
                }
                .tabItem {
                    Label("Mining", systemImage: "waveform")
                }
                .tag(AppScreen.mining)
            }

            NavigationStack {
                LeaderboardView()
            }
            .tabItem {
                Label("Ranks", systemImage: "chart.bar")
            }
            .tag(AppScreen.leaderboard)
        }
        .overlay(alignment: .top) {
            if let error = appState.errorMessage {
                ErrorBanner(message: error) {
                    appState.errorMessage = nil
                }
            }
        }
    }
}

struct ErrorBanner: View {
    let message: String
    let onDismiss: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.yellow)

            Text(message)
                .font(.subheadline)

            Spacer()

            Button {
                onDismiss()
            } label: {
                Image(systemName: "xmark")
                    .font(.caption)
            }
        }
        .padding()
        .background(.red.opacity(0.9), in: RoundedRectangle(cornerRadius: 12))
        .foregroundStyle(.white)
        .padding()
        .transition(.move(edge: .top).combined(with: .opacity))
    }
}

#Preview {
    ContentView()
}
