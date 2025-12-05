//
//  WalletView.swift
//  SoundChain
//

import SwiftUI

struct WalletView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedRecipient: User?
    @State private var amount: String = ""
    @State private var fee: String = "0.1"
    @State private var showingTransferSheet = false

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                balanceCard
                sendSection
                pendingSection
            }
            .padding()
        }
        .navigationTitle("Wallet")
        .sheet(isPresented: $showingTransferSheet) {
            transferSheet
        }
    }

    private var balanceCard: some View {
        VStack(spacing: 16) {
            Text("Balance")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Text("\(appState.wallet?.balance ?? 0, specifier: "%.2f")")
                .font(.system(size: 56, weight: .bold, design: .rounded))

            Text("coins")
                .font(.title3)
                .foregroundStyle(.secondary)

            if let address = appState.wallet?.address {
                HStack {
                    Text(String(address.prefix(8)) + "...")
                        .font(.caption)
                        .monospaced()
                        .foregroundStyle(.secondary)

                    Button {
                        UIPasteboard.general.string = address
                    } label: {
                        Image(systemName: "doc.on.doc")
                            .font(.caption)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 32)
        .background(
            LinearGradient(
                colors: [.blue.opacity(0.2), .purple.opacity(0.2)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ),
            in: RoundedRectangle(cornerRadius: 20)
        )
    }

    private var sendSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Send Coins")
                .font(.headline)

            if appState.otherUsers.isEmpty {
                Text("No other users to send to")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                ForEach(appState.otherUsers) { user in
                    Button {
                        selectedRecipient = user
                        showingTransferSheet = true
                    } label: {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .foregroundStyle(.blue)
                                .font(.title2)

                            VStack(alignment: .leading) {
                                Text(user.name)
                                    .fontWeight(.medium)
                                    .foregroundStyle(.primary)
                                Text(String(user.id.prefix(8)) + "...")
                                    .font(.caption)
                                    .monospaced()
                                    .foregroundStyle(.secondary)
                            }

                            Spacer()

                            Image(systemName: "arrow.right.circle")
                                .foregroundStyle(.blue)
                        }
                        .padding()
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private var pendingSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Pending Transactions")
                    .font(.headline)

                Spacer()

                if let pending = appState.gameState?.pendingTx, pending > 0 {
                    Text("\(pending)")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(.orange, in: Capsule())
                        .foregroundStyle(.white)
                }
            }

            if appState.gameState?.pendingTx == 0 {
                Text("No pending transactions")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                Text("Waiting for next block...")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    private var transferSheet: some View {
        NavigationStack {
            Form {
                if let recipient = selectedRecipient {
                    Section("Recipient") {
                        HStack {
                            Image(systemName: "person.circle.fill")
                                .foregroundStyle(.blue)
                            Text(recipient.name)
                        }
                    }

                    Section("Amount") {
                        TextField("Amount", text: $amount)
                            .keyboardType(.decimalPad)
                    }

                    Section("Fee") {
                        TextField("Fee (min 0.01)", text: $fee)
                            .keyboardType(.decimalPad)
                    }

                    Section {
                        let amountValue = Double(amount) ?? 0
                        let feeValue = Double(fee) ?? 0
                        let total = amountValue + feeValue
                        let balance = appState.wallet?.balance ?? 0

                        HStack {
                            Text("Total")
                            Spacer()
                            Text("\(total, specifier: "%.2f") coins")
                                .foregroundStyle(total > balance ? .red : .primary)
                        }

                        if total > balance {
                            Text("Insufficient balance")
                                .foregroundStyle(.red)
                                .font(.caption)
                        }
                    }
                }
            }
            .navigationTitle("Send Coins")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        showingTransferSheet = false
                        resetForm()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Send") {
                        sendTransfer()
                    }
                    .disabled(!isValidTransfer)
                }
            }
        }
        .presentationDetents([.medium])
    }

    private var isValidTransfer: Bool {
        guard let recipient = selectedRecipient,
              let amountValue = Double(amount),
              let feeValue = Double(fee),
              amountValue > 0,
              feeValue >= 0.01 else {
            return false
        }
        let total = amountValue + feeValue
        return total <= (appState.wallet?.balance ?? 0) && recipient.id != appState.userId
    }

    private func sendTransfer() {
        guard let recipient = selectedRecipient,
              let amountValue = Double(amount),
              let feeValue = Double(fee) else {
            return
        }

        appState.transfer(to: recipient.id, amount: amountValue, fee: feeValue)
        showingTransferSheet = false
        resetForm()
    }

    private func resetForm() {
        amount = ""
        fee = "0.1"
        selectedRecipient = nil
    }
}

#Preview {
    NavigationStack {
        WalletView()
            .environmentObject(AppState())
    }
}
