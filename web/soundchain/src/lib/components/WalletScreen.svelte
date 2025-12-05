<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import Navigation from './Navigation.svelte';

	const app = getAppState();

	let showSendModal = $state(false);
	let selectedRecipient = $state<{ id: string; name: string } | null>(null);
	let sendAmount = $state('');
	let sendFee = $state('0.1');
	let copied = $state(false);

	function formatBalance(balance: number): string {
		return balance.toFixed(2);
	}

	function truncateAddress(address: string): string {
		if (!address) return '';
		return `${address.slice(0, 8)}...${address.slice(-8)}`;
	}

	async function copyAddress() {
		if (app.userWallet?.address) {
			await navigator.clipboard.writeText(app.userWallet.address);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		}
	}

	function openSendModal(user: { id: string; name: string }) {
		selectedRecipient = user;
		sendAmount = '';
		sendFee = '0.1';
		showSendModal = true;
	}

	function closeSendModal() {
		showSendModal = false;
		selectedRecipient = null;
	}

	function handleSend() {
		if (!selectedRecipient || !sendAmount) return;

		const amount = parseFloat(sendAmount);
		const fee = parseFloat(sendFee) || 0.1;

		if (isNaN(amount) || amount <= 0) return;
		if ((app.userWallet?.balance || 0) < amount + fee) return;

		app.sendCoins(selectedRecipient.id, amount, fee);
		closeSendModal();
	}

	function getOtherUsers() {
		const allUsers = [...app.gameState.miners, ...app.gameState.users];
		return allUsers.filter((u) => u.id !== app.userId);
	}

	function getMaxSendable(): number {
		const fee = parseFloat(sendFee) || 0.1;
		return Math.max(0, (app.userWallet?.balance || 0) - fee);
	}

	function isInsufficientBalance(): boolean {
		const amount = parseFloat(sendAmount) || 0;
		const fee = parseFloat(sendFee) || 0.1;
		return (app.userWallet?.balance || 0) < amount + fee;
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 pb-20 pt-4">
	<div class="mx-auto max-w-md px-4">
		<!-- Header -->
		<h1 class="mb-6 text-xl font-bold text-white">Wallet</h1>

		<!-- Balance Card -->
		<div class="mb-6 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 p-6">
			<p class="text-sm text-white/80">Your Balance</p>
			<p class="text-4xl font-bold text-white">{formatBalance(app.userWallet?.balance || 0)}</p>
			<p class="mb-4 text-sm text-white/60">coins</p>

			<div class="flex items-center gap-2 rounded-lg bg-black/20 p-3">
				<p class="flex-1 font-mono text-xs text-white/80">
					{truncateAddress(app.userWallet?.address || '')}
				</p>
				<button onclick={copyAddress} class="rounded p-1 hover:bg-white/10" title="Copy address">
					{#if copied}
						<svg class="h-5 w-5 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					{:else}
						<svg class="h-5 w-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
						</svg>
					{/if}
				</button>
			</div>
		</div>

		<!-- Pending Transactions -->
		{#if app.gameState.pendingTx > 0}
			<div class="mb-6 flex items-center gap-2 rounded-lg bg-yellow-500/20 p-3">
				<svg class="h-5 w-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<span class="text-sm text-yellow-300">{app.gameState.pendingTx} pending transaction(s)</span>
			</div>
		{/if}

		<!-- Send Section -->
		<div class="rounded-xl bg-gray-800/50 p-4">
			<h2 class="mb-3 font-semibold text-white">Send Coins</h2>

			{#if getOtherUsers().length > 0}
				<div class="space-y-2">
					{#each getOtherUsers() as user}
						<button
							onclick={() => openSendModal(user)}
							class="flex w-full items-center justify-between rounded-lg bg-gray-700/50 p-3 text-left transition-colors hover:bg-gray-700"
						>
							<div class="flex items-center gap-3">
								<div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-500">
									<span class="font-medium text-white">{user.name.charAt(0).toUpperCase()}</span>
								</div>
								<div>
									<p class="font-medium text-white">{user.name}</p>
									<p class="text-xs text-gray-400">{formatBalance(user.wallet.balance)} coins</p>
								</div>
							</div>
							<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</button>
					{/each}
				</div>
			{:else}
				<p class="text-center text-sm text-gray-400">No other users to send coins to</p>
			{/if}
		</div>
	</div>

	<Navigation />
</div>

<!-- Send Modal -->
{#if showSendModal && selectedRecipient}
	<div class="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
		<div class="w-full max-w-md rounded-t-2xl bg-gray-800 p-6 sm:rounded-2xl">
			<div class="mb-4 flex items-center justify-between">
				<h3 class="text-lg font-semibold text-white">Send to {selectedRecipient.name}</h3>
				<button onclick={closeSendModal} aria-label="Close modal" class="rounded-full p-1 hover:bg-gray-700">
					<svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<div class="space-y-4">
				<div>
					<label for="amount" class="mb-2 block text-sm font-medium text-gray-300">Amount</label>
					<input
						id="amount"
						type="number"
						bind:value={sendAmount}
						placeholder="0.00"
						step="0.01"
						min="0"
						max={getMaxSendable()}
						class="w-full rounded-lg border border-gray-600 bg-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
					/>
					<p class="mt-1 text-xs text-gray-400">Max: {getMaxSendable().toFixed(2)} coins</p>
				</div>

				<div>
					<label for="fee" class="mb-2 block text-sm font-medium text-gray-300">Transaction Fee</label>
					<input
						id="fee"
						type="number"
						bind:value={sendFee}
						placeholder="0.1"
						step="0.01"
						min="0.01"
						class="w-full rounded-lg border border-gray-600 bg-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
					/>
					<p class="mt-1 text-xs text-gray-400">Fee goes to miners</p>
				</div>

				{#if isInsufficientBalance()}
					<div class="rounded-lg bg-red-500/20 p-3 text-sm text-red-300">
						Insufficient balance
					</div>
				{/if}

				<button
					onclick={handleSend}
					disabled={!sendAmount || parseFloat(sendAmount) <= 0 || isInsufficientBalance()}
					class="w-full rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 font-semibold text-white transition-all hover:from-purple-600 hover:to-pink-600 disabled:cursor-not-allowed disabled:opacity-50"
				>
					Send {sendAmount || '0'} coins
				</button>
			</div>
		</div>
	</div>
{/if}
