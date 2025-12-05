//
//  WebSocketClient.swift
//  SoundChain
//

import Foundation

protocol WebSocketClientDelegate: AnyObject {
    func didConnect()
    func didDisconnect(error: Error?)
    func didReceive(message: ServerMessage)
}

class WebSocketClient: NSObject {
    weak var delegate: WebSocketClientDelegate?

    private var webSocketTask: URLSessionWebSocketTask?
    private var urlSession: URLSession?
    private let serverURL: URL

    var isConnected: Bool {
        webSocketTask?.state == .running
    }

    init(serverURL: URL) {
        self.serverURL = serverURL
        super.init()
    }

    func connect() {
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: .main)
        urlSession = session
        webSocketTask = session.webSocketTask(with: serverURL)
        webSocketTask?.resume()
        receiveMessage()
    }

    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        urlSession?.invalidateAndCancel()
        urlSession = nil
    }

    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if let data = text.data(using: .utf8) {
                        let serverMessage = ServerMessage.parse(from: data)
                        self?.delegate?.didReceive(message: serverMessage)
                    }
                case .data(let data):
                    let serverMessage = ServerMessage.parse(from: data)
                    self?.delegate?.didReceive(message: serverMessage)
                @unknown default:
                    break
                }
                self?.receiveMessage()
            case .failure(let error):
                self?.delegate?.didDisconnect(error: error)
            }
        }
    }

    func send(_ dictionary: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: dictionary),
              let text = String(data: data, encoding: .utf8) else {
            return
        }
        webSocketTask?.send(.string(text)) { error in
            if let error = error {
                print("WebSocket send error: \(error)")
            }
        }
    }

    func join(name: String, deviceId: String) {
        send(["type": "join", "name": name, "device_id": deviceId])
    }

    func becomeMiner() {
        send(["type": "become_miner"])
    }

    func leaveMining() {
        send(["type": "leave_mining"])
    }

    func transfer(to userId: String, amount: Double, fee: Double) {
        send([
            "type": "transfer",
            "to": userId,
            "amount": amount,
            "fee": fee
        ])
    }

    func getState() {
        send(["type": "get_state"])
    }

    func getLeaderboard() {
        send(["type": "get_leaderboard"])
    }
}

extension WebSocketClient: URLSessionWebSocketDelegate {
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        delegate?.didConnect()
    }

    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        delegate?.didDisconnect(error: nil)
    }
}
