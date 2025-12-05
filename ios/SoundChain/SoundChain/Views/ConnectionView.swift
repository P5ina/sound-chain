//
//  ConnectionView.swift
//  SoundChain
//

import SwiftUI

struct ConnectionView: View {
    @EnvironmentObject var appState: AppState
    @State private var name: String = ""
    @State private var serverHost: String = "raspberrypi.local"
    @State private var showAdvanced = false

    var body: some View {
        VStack(spacing: 32) {
            Spacer()

            logoSection

            Spacer()

            inputSection

            if showAdvanced {
                advancedSection
            }

            connectButton

            advancedToggle

            Spacer()
        }
        .padding()
        .alert("Error", isPresented: .constant(appState.errorMessage != nil)) {
            Button("OK") {
                appState.errorMessage = nil
            }
        } message: {
            if let error = appState.errorMessage {
                Text(error)
            }
        }
    }

    private var logoSection: some View {
        VStack(spacing: 16) {
            Image(systemName: "waveform.circle.fill")
                .font(.system(size: 80))
                .foregroundStyle(.blue)

            Text("SoundChain")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("Proof-of-Sound Mining")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }

    private var inputSection: some View {
        VStack(spacing: 16) {
            TextField("Your Name", text: $name)
                .textFieldStyle(.roundedBorder)
                .textContentType(.name)
                .autocorrectionDisabled()
                .padding(.horizontal)
        }
    }

    private var advancedSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Server")
                .font(.caption)
                .foregroundStyle(.secondary)

            TextField("Server Host", text: $serverHost)
                .textFieldStyle(.roundedBorder)
                .autocorrectionDisabled()
                .textInputAutocapitalization(.never)
                .keyboardType(.URL)
        }
        .padding(.horizontal)
    }

    private var connectButton: some View {
        Button {
            connect()
        } label: {
            Group {
                if appState.connectionState == .connecting {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                } else {
                    Text("Connect")
                }
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .disabled(name.isEmpty || appState.connectionState == .connecting)
        .padding(.horizontal)
    }

    private var advancedToggle: some View {
        Button {
            withAnimation {
                showAdvanced.toggle()
            }
        } label: {
            HStack {
                Text("Advanced Settings")
                Image(systemName: showAdvanced ? "chevron.up" : "chevron.down")
            }
            .font(.caption)
            .foregroundStyle(.secondary)
        }
    }

    private func connect() {
        appState.serverHost = serverHost
        appState.connect()

        // Wait for connection then join
        Task {
            while appState.connectionState == .connecting {
                try? await Task.sleep(nanoseconds: 100_000_000)
            }

            if appState.connectionState == .connected {
                appState.join(name: name)
            }
        }
    }
}

#Preview {
    ConnectionView()
        .environmentObject(AppState())
}
