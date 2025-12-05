// Manages a persistent unique device ID stored in localStorage

const STORAGE_KEY = 'soundchain_device_id';

/**
 * Generates a UUID v4 with fallback for browsers without crypto.randomUUID
 */
function generateUUID(): string {
	if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
		return crypto.randomUUID();
	}
	// Fallback for older browsers
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
		const r = (Math.random() * 16) | 0;
		const v = c === 'x' ? r : (r & 0x3) | 0x8;
		return v.toString(16);
	});
}

/**
 * Gets the device ID, generating and storing one if it doesn't exist
 */
export function getOrCreateDeviceId(): string {
	const existing = localStorage.getItem(STORAGE_KEY);
	if (existing) {
		return existing;
	}

	const newId = generateUUID();
	localStorage.setItem(STORAGE_KEY, newId);
	return newId;
}

/**
 * Gets the stored device ID (may be null if not yet created)
 */
export function getDeviceId(): string | null {
	return localStorage.getItem(STORAGE_KEY);
}
