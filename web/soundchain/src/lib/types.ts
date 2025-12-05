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

export interface MinerContribution {
	frequency: number;      // Current frequency the miner is playing (Hz)
	detected: boolean;      // Whether their tone was detected
	accuracy: number;       // How close to target (0-1)
	contribution: number;   // Final contribution score (0-1)
}

export interface DetectedTone {
	frequency: number;
	power: number;
	purity: number;
}

export interface MiningStatus {
	targetFrequency: number | null;  // Target frequency to match (Hz)
	toleranceHz: number;             // Tolerance in Hz
	contributions: Record<string, MinerContribution>;
	avgContribution: number;         // Average contribution (0-1)
	detectedTones: DetectedTone[];   // Pure tones detected by server
	pendingTx: number;
	minFrequency: number;            // Min slider value (Hz)
	maxFrequency: number;            // Max slider value (Hz)
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
