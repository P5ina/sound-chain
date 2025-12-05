// App state store using Svelte 5 runes

import type {
	User,
	Wallet,
	MiningStatus,
	GameState,
	LeaderboardEntry,
	Screen,
	Block,
	ServerMessage
} from './types';
import { wsClient } from './websocket';
import { toneGenerator } from './tone';
import { getOrCreateDeviceId } from './deviceId';

// Connection state
let isConnected = $state(false);
let isConnecting = $state(false);
let connectionError = $state<string | null>(null);
let serverHost = $state('raspberrypi.local:8765');

// User state
let userId = $state<string | null>(null);
let userName = $state<string | null>(null);
let userWallet = $state<Wallet | null>(null);

// Miner state
let isMiner = $state(false);
let minerFrequency = $state<number | null>(null);
let minerSlot = $state<number | null>(null);
let isPlayingTone = $state(false);

// Game state
let gameState = $state<GameState>({
	chainLength: 0,
	pendingTx: 0,
	miners: [],
	users: [],
	blockReward: 50,
	pendingFees: 0
});

// Mining status
let miningStatus = $state<MiningStatus | null>(null);

// Recent blocks
let recentBlocks = $state<Block[]>([]);

// Leaderboard
let leaderboard = $state<LeaderboardEntry[]>([]);

// Current screen
let currentScreen = $state<Screen>('connection');

// Error message
let errorMessage = $state<string | null>(null);

// Message handler
function handleServerMessage(message: ServerMessage): void {
	switch (message.type) {
		case 'joined': {
			userId = message.user_id as string;
			const walletData = message.wallet as { address: string; balance: number };
			userWallet = {
				address: walletData.address,
				balance: walletData.balance
			};
			currentScreen = 'lobby';
			wsClient.getState();
			break;
		}

		case 'became_miner': {
			isMiner = true;
			minerFrequency = message.frequency as number;
			minerSlot = message.slot as number;
			wsClient.getState();
			break;
		}

		case 'left_mining': {
			isMiner = false;
			minerFrequency = null;
			minerSlot = null;
			if (isPlayingTone) {
				toneGenerator.stop();
				isPlayingTone = false;
			}
			wsClient.getState();
			break;
		}

		case 'state': {
			const miners = (message.miners as Array<Record<string, unknown>>)?.map((m) => ({
				id: m.user_id as string,
				name: m.name as string,
				wallet: {
					address: (m.wallet as Record<string, unknown>)?.address as string,
					balance: (m.wallet as Record<string, unknown>)?.balance as number
				},
				isMiner: true,
				minerSlot: m.miner_slot as number,
				frequency: m.frequency as number
			})) || [];

			const users = (message.users as Array<Record<string, unknown>>)?.map((u) => ({
				id: u.user_id as string,
				name: u.name as string,
				wallet: {
					address: (u.wallet as Record<string, unknown>)?.address as string,
					balance: (u.wallet as Record<string, unknown>)?.balance as number
				},
				isMiner: false
			})) || [];

			gameState = {
				chainLength: message.chain_length as number || 0,
				pendingTx: message.pending_tx as number || 0,
				miners,
				users,
				blockReward: message.block_reward as number || 50,
				pendingFees: message.pending_fees as number || 0
			};

			// Update own wallet balance
			const me = [...miners, ...users].find((u) => u.id === userId);
			if (me && userWallet) {
				userWallet = { ...userWallet, balance: me.wallet.balance };
			}
			break;
		}

		case 'mining_status': {
			miningStatus = {
				contributions: message.contributions as Record<string, number> || {},
				target: message.target as number | null,
				current: message.current as number || 0,
				tolerance: message.tolerance as number || 0.05,
				pendingTx: message.pending_tx as number || 0
			};
			break;
		}

		case 'block_mined': {
			const blockData = message.block as Record<string, unknown>;
			if (blockData) {
				const block: Block = {
					index: blockData.index as number,
					timestamp: blockData.timestamp as number,
					transactions: (blockData.transactions as Array<Record<string, unknown>>)?.map((t) => ({
						id: t.id as string,
						fromAddress: t.from_address as string,
						toAddress: t.to_address as string,
						amount: t.amount as number,
						fee: t.fee as number,
						timestamp: t.timestamp as number
					})) || [],
					previousHash: blockData.previous_hash as string,
					minerContributions: blockData.miner_contributions as Record<string, number> || {},
					totalReward: blockData.total_reward as number || 0,
					hash: blockData.hash as string
				};
				recentBlocks = [block, ...recentBlocks.slice(0, 4)];
			}
			wsClient.getState();
			break;
		}

		case 'transaction_pending':
		case 'transaction_confirmed': {
			wsClient.getState();
			break;
		}

		case 'leaderboard': {
			leaderboard = (message.entries as Array<Record<string, unknown>>)?.map((e, index) => ({
				userId: e.user_id as string,
				name: e.name as string,
				balance: e.balance as number,
				isMiner: e.is_miner as boolean,
				rank: index + 1
			})) || [];
			break;
		}

		case 'error': {
			errorMessage = message.message as string;
			setTimeout(() => {
				errorMessage = null;
			}, 5000);
			break;
		}
	}
}

// Actions
async function connect(name: string, host: string): Promise<void> {
	if (isConnecting) return;

	isConnecting = true;
	connectionError = null;
	serverHost = host;
	userName = name;

	try {
		wsClient.onMessage(handleServerMessage);

		wsClient.onDisconnect(() => {
			isConnected = false;
			if (currentScreen !== 'connection') {
				connectionError = 'Disconnected from server';
			}
		});

		wsClient.onError((error) => {
			connectionError = error;
		});

		await wsClient.connect(host);
		isConnected = true;
		const deviceId = getOrCreateDeviceId();
		wsClient.join(name, deviceId);
	} catch (e) {
		const errorMsg = e instanceof Error ? e.message : 'Unknown error';
		connectionError = `Failed to connect: ${errorMsg}`;
		console.error('[Store] Connection failed:', e);
		isConnected = false;
	} finally {
		isConnecting = false;
	}
}

function disconnect(): void {
	wsClient.disconnect();
	toneGenerator.stop();

	// Reset state
	isConnected = false;
	userId = null;
	userName = null;
	userWallet = null;
	isMiner = false;
	minerFrequency = null;
	minerSlot = null;
	isPlayingTone = false;
	miningStatus = null;
	currentScreen = 'connection';
}

function becomeMiner(): void {
	wsClient.becomeMiner();
}

function leaveMining(): void {
	toneGenerator.stop();
	isPlayingTone = false;
	wsClient.leaveMining();
}

async function toggleTone(): Promise<void> {
	if (!minerFrequency) return;

	if (isPlayingTone) {
		toneGenerator.stop();
		isPlayingTone = false;
	} else {
		const success = await toneGenerator.play(minerFrequency);
		if (success) {
			isPlayingTone = true;
		} else {
			errorMessage = 'Failed to play audio. Please check your device volume and try again.';
			setTimeout(() => {
				errorMessage = null;
			}, 5000);
		}
	}
}

function sendCoins(toUserId: string, amount: number, fee: number): void {
	wsClient.transfer(toUserId, amount, fee);
}

function refreshLeaderboard(): void {
	wsClient.getLeaderboard();
}

function setScreen(screen: Screen): void {
	currentScreen = screen;
	if (screen === 'leaderboard') {
		refreshLeaderboard();
	}
}

function clearError(): void {
	errorMessage = null;
}

// Export reactive getters
export function getAppState() {
	return {
		// Connection
		get isConnected() {
			return isConnected;
		},
		get isConnecting() {
			return isConnecting;
		},
		get connectionError() {
			return connectionError;
		},
		get serverHost() {
			return serverHost;
		},

		// User
		get userId() {
			return userId;
		},
		get userName() {
			return userName;
		},
		get userWallet() {
			return userWallet;
		},

		// Miner
		get isMiner() {
			return isMiner;
		},
		get minerFrequency() {
			return minerFrequency;
		},
		get minerSlot() {
			return minerSlot;
		},
		get isPlayingTone() {
			return isPlayingTone;
		},

		// Game
		get gameState() {
			return gameState;
		},
		get miningStatus() {
			return miningStatus;
		},
		get recentBlocks() {
			return recentBlocks;
		},
		get leaderboard() {
			return leaderboard;
		},

		// UI
		get currentScreen() {
			return currentScreen;
		},
		get errorMessage() {
			return errorMessage;
		},

		// Actions
		connect,
		disconnect,
		becomeMiner,
		leaveMining,
		toggleTone,
		sendCoins,
		refreshLeaderboard,
		setScreen,
		clearError
	};
}
