// Core data types matching the mobile app

export interface Wallet {
	address: string;
	balance: number;
}

export interface User {
	id: string;
	name: string;
	wallet: Wallet;
	isMiner: boolean;
	minerSlot?: number;
	frequency?: number;
}

export interface Transaction {
	id: string;
	fromAddress: string;
	toAddress: string;
	amount: number;
	fee: number;
	timestamp: number;
}

export interface Block {
	index: number;
	timestamp: number;
	transactions: Transaction[];
	previousHash: string;
	minerContributions: Record<string, number>;
	totalReward: number;
	hash: string;
}

export interface MiningStatus {
	contributions: Record<string, number>;
	target: number | null;
	current: number;
	tolerance: number;
	pendingTx: number;
}

export interface LeaderboardEntry {
	userId: string;
	name: string;
	balance: number;
	isMiner: boolean;
	rank: number;
}

export interface GameState {
	chainLength: number;
	pendingTx: number;
	miners: User[];
	users: User[];
	blockReward: number;
	pendingFees: number;
}

// WebSocket message types
export type ServerMessageType =
	| 'joined'
	| 'became_miner'
	| 'left_mining'
	| 'state'
	| 'mining_status'
	| 'block_mined'
	| 'transaction_pending'
	| 'transaction_confirmed'
	| 'leaderboard'
	| 'error';

export interface ServerMessage {
	type: ServerMessageType;
	[key: string]: unknown;
}

export type Screen = 'connection' | 'lobby' | 'wallet' | 'mining' | 'leaderboard';
