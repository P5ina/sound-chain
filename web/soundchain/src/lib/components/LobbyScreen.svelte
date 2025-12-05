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

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 pb-20 pt-4">
	<div class="mx-auto max-w-md px-4">
		<!-- Header -->
		<div class="mb-6 flex items-center justify-between">
			<h1 class="text-xl font-bold text-white">Welcome, {app.userName}</h1>
			<button
				onclick={() => app.disconnect()}
				class="rounded-lg px-3 py-1 text-sm text-gray-400 hover:bg-gray-800 hover:text-white"
			>
				Disconnect
			</button>
		</div>

		<!-- Balance Card -->
		<div class="mb-6 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 p-6">
			<p class="text-sm text-white/80">Your Balance</p>
			<p class="text-4xl font-bold text-white">{formatBalance(app.userWallet?.balance || 0)}</p>
			<p class="text-sm text-white/60">coins</p>
		</div>

		<!-- Stats Grid -->
		<div class="mb-6 grid grid-cols-3 gap-3">
			<div class="rounded-xl bg-gray-800/50 p-4 text-center">
				<p class="text-2xl font-bold text-white">{app.gameState.chainLength}</p>
				<p class="text-xs text-gray-400">Blocks</p>
			</div>
			<div class="rounded-xl bg-gray-800/50 p-4 text-center">
				<p class="text-2xl font-bold text-white">{app.gameState.pendingTx}</p>
				<p class="text-xs text-gray-400">Pending TX</p>
			</div>
			<div class="rounded-xl bg-gray-800/50 p-4 text-center">
				<p class="text-2xl font-bold text-white">{app.gameState.blockReward.toFixed(1)}</p>
				<p class="text-xs text-gray-400">Block Reward</p>
			</div>
		</div>

		<!-- Miner Section -->
		<div class="mb-6 rounded-xl bg-gray-800/50 p-4">
			<div class="mb-3 flex items-center justify-between">
				<h2 class="font-semibold text-white">Miners</h2>
				<span class="text-sm text-gray-400">{getAvailableSlots()} slots available</span>
			</div>

			{#if !app.isMiner && getAvailableSlots() > 0}
				<button
					onclick={() => app.becomeMiner()}
					class="mb-4 w-full rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 px-4 py-3 font-semibold text-white transition-all hover:from-green-600 hover:to-emerald-600"
				>
					Become a Miner
				</button>
			{:else if app.isMiner}
				<div class="mb-4 flex items-center gap-2 rounded-lg bg-green-500/20 p-3">
					<svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
					<span class="text-green-300">You are mining at {app.minerFrequency} Hz</span>
				</div>
			{/if}

			{#if app.gameState.miners.length > 0}
				<div class="space-y-2">
					{#each app.gameState.miners as miner}
						<div class="flex items-center justify-between rounded-lg bg-gray-700/50 p-3">
							<div class="flex items-center gap-3">
								<div class="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/30">
									<svg class="h-4 w-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
									</svg>
								</div>
								<div>
									<p class="text-sm font-medium text-white">
										{miner.name}
										{#if miner.id === app.userId}
											<span class="text-purple-400">(you)</span>
										{/if}
									</p>
									<p class="text-xs text-gray-400">{miner.frequency} Hz</p>
								</div>
							</div>
							<p class="text-sm font-semibold text-white">{formatBalance(miner.wallet.balance)}</p>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-center text-sm text-gray-400">No miners yet. Be the first!</p>
			{/if}
		</div>

		<!-- Users Section -->
		<div class="rounded-xl bg-gray-800/50 p-4">
			<h2 class="mb-3 font-semibold text-white">Users ({app.gameState.users.length})</h2>
			{#if app.gameState.users.length > 0}
				<div class="space-y-2">
					{#each app.gameState.users as user}
						<div class="flex items-center justify-between rounded-lg bg-gray-700/50 p-3">
							<div class="flex items-center gap-3">
								<div class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-600">
									<span class="text-sm font-medium text-white">{user.name.charAt(0).toUpperCase()}</span>
								</div>
								<p class="text-sm font-medium text-white">
									{user.name}
									{#if user.id === app.userId}
										<span class="text-purple-400">(you)</span>
									{/if}
								</p>
							</div>
							<p class="text-sm font-semibold text-white">{formatBalance(user.wallet.balance)}</p>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-center text-sm text-gray-400">No other users connected</p>
			{/if}
		</div>
	</div>

	<Navigation />
</div>
