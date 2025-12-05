// Manages a persistent unique device ID stored in localStorage

const STORAGE_KEY = 'soundchain_device_id';

/**
 * Gets the device ID, generating and storing one if it doesn't exist
 */
export function getOrCreateDeviceId(): string {
	const existing = localStorage.getItem(STORAGE_KEY);
	if (existing) {
		return existing;
	}

	const newId = crypto.randomUUID();
	localStorage.setItem(STORAGE_KEY, newId);
	return newId;
}

/**
 * Gets the stored device ID (may be null if not yet created)
 */
export function getDeviceId(): string | null {
	return localStorage.getItem(STORAGE_KEY);
}
