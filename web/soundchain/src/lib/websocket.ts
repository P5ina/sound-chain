// WebSocket client for connecting to the SoundChain server

import type { ServerMessage } from './types';

export type MessageHandler = (message: ServerMessage) => void;
export type ConnectionHandler = () => void;
export type ErrorHandler = (error: string) => void;

export class WebSocketClient {
	private socket: WebSocket | null = null;
	private messageHandlers: Set<MessageHandler> = new Set();
	private connectHandlers: Set<ConnectionHandler> = new Set();
	private disconnectHandlers: Set<ConnectionHandler> = new Set();
	private errorHandlers: Set<ErrorHandler> = new Set();
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectDelay = 1000;
	private url: string = '';

	connect(host: string): Promise<void> {
		return new Promise((resolve, reject) => {
			try {
				// Use wss:// for HTTPS pages, ws:// for HTTP
				const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws';
				this.url = `${protocol}://${host}`;
				console.log(`[WebSocket] Attempting to connect to: ${this.url}`);
				console.log(`[WebSocket] Page protocol: ${typeof window !== 'undefined' ? window.location.protocol : 'unknown'}`);
				this.socket = new WebSocket(this.url);

				this.socket.onopen = () => {
					console.log(`[WebSocket] Connected successfully to ${this.url}`);
					this.reconnectAttempts = 0;
					this.connectHandlers.forEach((handler) => handler());
					resolve();
				};

				this.socket.onmessage = (event) => {
					try {
						const message = JSON.parse(event.data) as ServerMessage;
						this.messageHandlers.forEach((handler) => handler(message));
					} catch (e) {
						console.error('[WebSocket] Failed to parse message:', e);
					}
				};

				this.socket.onclose = (event) => {
					console.log(`[WebSocket] Connection closed. Code: ${event.code}, Reason: ${event.reason || 'none'}, Clean: ${event.wasClean}`);
					this.disconnectHandlers.forEach((handler) => handler());
					this.attemptReconnect();
				};

				this.socket.onerror = (event) => {
					const errorDetails = [
						`URL: ${this.url}`,
						`ReadyState: ${this.socket?.readyState}`,
						`Protocol: ${protocol}`,
						`Host: ${host}`
					].join(', ');
					console.error(`[WebSocket] Connection error. ${errorDetails}`, event);
					const error = `WebSocket error connecting to ${this.url}. Check if server is running and accessible.`;
					this.errorHandlers.forEach((handler) => handler(error));
					reject(new Error(error));
				};
			} catch (e) {
				console.error('[WebSocket] Exception during connect:', e);
				reject(e);
			}
		});
	}

	private attemptReconnect(): void {
		if (this.reconnectAttempts < this.maxReconnectAttempts && this.url) {
			this.reconnectAttempts++;
			setTimeout(() => {
				console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
				// Strip protocol prefix for reconnection
				const host = this.url.replace(/^wss?:\/\//, '');
				this.connect(host).catch(() => {
					// Will retry on close
				});
			}, this.reconnectDelay * this.reconnectAttempts);
		}
	}

	disconnect(): void {
		this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
	}

	send(message: Record<string, unknown>): void {
		if (this.socket?.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify(message));
		} else {
			console.error('WebSocket is not connected');
		}
	}

	// Message sending helpers
	join(name: string, deviceId: string): void {
		this.send({ type: 'join', name, device_id: deviceId });
	}

	becomeMiner(): void {
		this.send({ type: 'become_miner' });
	}

	leaveMining(): void {
		this.send({ type: 'leave_mining' });
	}

	transfer(to: string, amount: number, fee: number): void {
		this.send({ type: 'transfer', to, amount, fee });
	}

	getState(): void {
		this.send({ type: 'get_state' });
	}

	getLeaderboard(): void {
		this.send({ type: 'get_leaderboard' });
	}

	// Event handlers
	onMessage(handler: MessageHandler): () => void {
		this.messageHandlers.add(handler);
		return () => this.messageHandlers.delete(handler);
	}

	onConnect(handler: ConnectionHandler): () => void {
		this.connectHandlers.add(handler);
		return () => this.connectHandlers.delete(handler);
	}

	onDisconnect(handler: ConnectionHandler): () => void {
		this.disconnectHandlers.add(handler);
		return () => this.disconnectHandlers.delete(handler);
	}

	onError(handler: ErrorHandler): () => void {
		this.errorHandlers.add(handler);
		return () => this.errorHandlers.delete(handler);
	}

	get isConnected(): boolean {
		return this.socket?.readyState === WebSocket.OPEN;
	}
}

// Singleton instance
export const wsClient = new WebSocketClient();
