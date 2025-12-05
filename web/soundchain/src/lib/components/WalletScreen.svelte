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

<div class="min-h-screen bg-[var(--ios-bg-secondary)] pb-24 pt-2">
	<div class="mx-auto max-w-lg px-4">
		<!-- Header -->
		<h1 class="mb-4 px-1 text-[28px] font-bold text-[var(--ios-text-primary)]">Wallet</h1>

		<!-- Balance Card -->
		<div class="ios-card mb-6 overflow-hidden">
			<div class="bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)] p-5">
				<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Your Balance</p>
				<p class="text-[42px] font-bold tracking-tight text-white">{formatBalance(app.userWallet?.balance || 0)}</p>
				<p class="mb-4 text-[15px] text-white/60">coins</p>

				<button
					onclick={copyAddress}
					class="flex w-full items-center justify-between rounded-xl bg-white/10 p-3 transition-colors active:bg-white/20"
				>
					<p class="font-mono text-[13px] text-white/80">
						{truncateAddress(app.userWallet?.address || '')}
					</p>
					{#if copied}
						<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					{:else}
						<svg class="h-5 w-5 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75" />
						</svg>
					{/if}
				</button>
			</div>
		</div>

		<!-- Pending Transactions -->
		{#if app.gameState.pendingTx > 0}
			<div class="mb-6 flex items-center gap-3 rounded-xl bg-[var(--ios-orange)]/10 p-4">
				<svg class="h-6 w-6 text-[var(--ios-orange)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
				<span class="text-[15px] text-[var(--ios-orange)]">{app.gameState.pendingTx} pending transaction(s)</span>
			</div>
		{/if}

		<!-- Send Section -->
		<div>
			<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
				Send Coins
			</h2>

			<div class="ios-list">
				{#if getOtherUsers().length > 0}
					{#each getOtherUsers() as user}
						<button
							onclick={() => openSendModal(user)}
							class="ios-list-item flex w-full items-center justify-between"
						>
							<div class="flex items-center gap-3">
								<div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)]">
									<span class="text-[17px] font-semibold text-white">{user.name.charAt(0).toUpperCase()}</span>
								</div>
								<div class="text-left">
									<p class="text-[17px] text-[var(--ios-text-primary)]">{user.name}</p>
									<p class="text-[13px] text-[var(--ios-text-tertiary)]">{formatBalance(user.wallet.balance)} coins</p>
								</div>
							</div>
							<svg class="h-5 w-5 text-[var(--ios-gray-3)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</button>
					{/each}
				{:else}
					<div class="ios-list-item">
						<p class="text-center text-[15px] text-[var(--ios-text-tertiary)]">No other users to send coins to</p>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<Navigation />
</div>

<!-- Send Modal -->
{#if showSendModal && selectedRecipient}
	<div class="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
		<div class="w-full max-w-lg animate-[slideUp_0.3s_ease-out] rounded-t-2xl bg-[var(--ios-bg-primary)] pb-8">
			<!-- Handle -->
			<div class="flex justify-center py-3">
				<div class="h-1 w-10 rounded-full bg-[var(--ios-gray-4)]"></div>
			</div>

			<div class="px-6">
				<div class="mb-6 flex items-center justify-between">
					<h3 class="text-[20px] font-semibold text-[var(--ios-text-primary)]">Send to {selectedRecipient.name}</h3>
					<button onclick={closeSendModal} class="text-[17px] text-[var(--ios-blue)]">
						Cancel
					</button>
				</div>

				<div class="space-y-5">
					<div>
						<label for="amount" class="mb-1.5 block text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
							Amount
						</label>
						<input
							id="amount"
							type="number"
							bind:value={sendAmount}
							placeholder="0.00"
							step="0.01"
							min="0"
							max={getMaxSendable()}
							class="ios-input bg-[var(--ios-bg-secondary)]"
						/>
						<p class="mt-1 text-[13px] text-[var(--ios-text-tertiary)]">Max: {getMaxSendable().toFixed(2)} coins</p>
					</div>

					<div>
						<label for="fee" class="mb-1.5 block text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
							Transaction Fee
						</label>
						<input
							id="fee"
							type="number"
							bind:value={sendFee}
							placeholder="0.1"
							step="0.01"
							min="0.01"
							class="ios-input bg-[var(--ios-bg-secondary)]"
						/>
						<p class="mt-1 text-[13px] text-[var(--ios-text-tertiary)]">Fee goes to miners</p>
					</div>

					{#if isInsufficientBalance()}
						<div class="rounded-xl bg-[var(--ios-red)]/10 p-4">
							<p class="text-[15px] text-[var(--ios-red)]">Insufficient balance</p>
						</div>
					{/if}

					<button
						onclick={handleSend}
						disabled={!sendAmount || parseFloat(sendAmount) <= 0 || isInsufficientBalance()}
						class="ios-button-primary w-full text-[17px]"
					>
						Send {sendAmount || '0'} coins
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	@keyframes slideUp {
		from {
			transform: translateY(100%);
		}
		to {
			transform: translateY(0);
		}
	}
</style>
