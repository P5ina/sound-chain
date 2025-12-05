<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import Navigation from './Navigation.svelte';

	const app = getAppState();

	function formatBalance(balance: number): string {
		return balance.toFixed(2);
	}

	function getAvailableSlots(): number {
		return 4 - app.gameState.miners.length;
	}
</script>

<div class="min-h-screen bg-[var(--ios-bg-secondary)] pb-24 pt-2">
	<div class="mx-auto max-w-lg px-4">
		<!-- Header -->
		<div class="mb-4 flex items-center justify-between px-1">
			<h1 class="text-[28px] font-bold text-[var(--ios-text-primary)]">Welcome, {app.userName}</h1>
			<button
				onclick={() => app.disconnect()}
				class="text-[17px] text-[var(--ios-blue)]"
			>
				Disconnect
			</button>
		</div>

		<!-- Balance Card -->
		<div class="ios-card mb-6 overflow-hidden">
			<div class="bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)] p-5">
				<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Your Balance</p>
				<p class="text-[42px] font-bold tracking-tight text-white">{formatBalance(app.userWallet?.balance || 0)}</p>
				<p class="text-[15px] text-white/60">coins</p>
			</div>
		</div>

		<!-- Stats Grid -->
		<div class="mb-6 grid grid-cols-3 gap-3">
			<div class="ios-card p-4 text-center">
				<p class="text-[28px] font-bold text-[var(--ios-text-primary)]">{app.gameState.chainLength}</p>
				<p class="text-[13px] text-[var(--ios-text-tertiary)]">Blocks</p>
			</div>
			<div class="ios-card p-4 text-center">
				<p class="text-[28px] font-bold text-[var(--ios-text-primary)]">{app.gameState.pendingTx}</p>
				<p class="text-[13px] text-[var(--ios-text-tertiary)]">Pending TX</p>
			</div>
			<div class="ios-card p-4 text-center">
				<p class="text-[28px] font-bold text-[var(--ios-text-primary)]">{app.gameState.blockReward.toFixed(1)}</p>
				<p class="text-[13px] text-[var(--ios-text-tertiary)]">Reward</p>
			</div>
		</div>

		<!-- Miner Section -->
		<div class="mb-6">
			<div class="mb-2 flex items-center justify-between px-4">
				<h2 class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Miners</h2>
				<span class="text-[13px] text-[var(--ios-text-tertiary)]">{getAvailableSlots()} slots available</span>
			</div>

			<div class="ios-list">
				{#if !app.isMiner && getAvailableSlots() > 0}
					<button
						onclick={() => app.becomeMiner()}
						class="ios-list-item flex w-full items-center justify-between"
					>
						<div class="flex items-center gap-3">
							<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-green)]/10">
								<svg class="h-5 w-5 text-[var(--ios-green)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
								</svg>
							</div>
							<span class="text-[17px] font-medium text-[var(--ios-green)]">Become a Miner</span>
						</div>
						<svg class="h-5 w-5 text-[var(--ios-gray-3)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
						</svg>
					</button>
				{:else if app.isMiner}
					<div class="ios-list-item flex items-center gap-3 bg-[var(--ios-green)]/5">
						<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-green)]/10">
							<svg class="h-5 w-5 text-[var(--ios-green)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
						</div>
						<span class="text-[17px] text-[var(--ios-green)]">Mining at {app.minerFrequency} Hz</span>
					</div>
				{/if}

				{#if app.gameState.miners.length > 0}
					{#each app.gameState.miners as miner}
						<div class="ios-list-item flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-purple)]/10">
									<svg class="h-5 w-5 text-[var(--ios-purple)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
									</svg>
								</div>
								<div>
									<p class="text-[17px] text-[var(--ios-text-primary)]">
										{miner.name}
										{#if miner.id === app.userId}
											<span class="text-[var(--ios-blue)]"> (you)</span>
										{/if}
									</p>
									<p class="text-[13px] text-[var(--ios-text-tertiary)]">{miner.frequency} Hz</p>
								</div>
							</div>
							<p class="text-[17px] tabular-nums text-[var(--ios-text-secondary)]">{formatBalance(miner.wallet.balance)}</p>
						</div>
					{/each}
				{:else if !app.isMiner || getAvailableSlots() === 0}
					<div class="ios-list-item">
						<p class="text-center text-[15px] text-[var(--ios-text-tertiary)]">No miners yet. Be the first!</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Users Section -->
		<div>
			<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
				Users ({app.gameState.users.length})
			</h2>

			<div class="ios-list">
				{#if app.gameState.users.length > 0}
					{#each app.gameState.users as user}
						<div class="ios-list-item flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-gray-5)]">
									<span class="text-[17px] font-semibold text-[var(--ios-text-secondary)]">{user.name.charAt(0).toUpperCase()}</span>
								</div>
								<p class="text-[17px] text-[var(--ios-text-primary)]">
									{user.name}
									{#if user.id === app.userId}
										<span class="text-[var(--ios-blue)]"> (you)</span>
									{/if}
								</p>
							</div>
							<p class="text-[17px] tabular-nums text-[var(--ios-text-secondary)]">{formatBalance(user.wallet.balance)}</p>
						</div>
					{/each}
				{:else}
					<div class="ios-list-item">
						<p class="text-center text-[15px] text-[var(--ios-text-tertiary)]">No other users connected</p>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<Navigation />
</div>
