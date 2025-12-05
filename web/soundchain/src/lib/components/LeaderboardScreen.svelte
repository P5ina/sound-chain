<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import Navigation from './Navigation.svelte';

	const app = getAppState();

	function formatBalance(balance: number): string {
		return balance.toFixed(2);
	}

	function getTopThree() {
		return app.leaderboard.slice(0, 3);
	}

	function getRest() {
		return app.leaderboard.slice(3);
	}

	function getMedalColor(rank: number): string {
		switch (rank) {
			case 1:
				return 'from-yellow-400 to-yellow-600';
			case 2:
				return 'from-gray-300 to-gray-500';
			case 3:
				return 'from-orange-400 to-orange-600';
			default:
				return 'from-gray-600 to-gray-700';
		}
	}

	function getPodiumHeight(rank: number): string {
		switch (rank) {
			case 1:
				return 'h-24';
			case 2:
				return 'h-16';
			case 3:
				return 'h-12';
			default:
				return 'h-8';
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 pb-20 pt-4">
	<div class="mx-auto max-w-md px-4">
		<!-- Header -->
		<div class="mb-6 flex items-center justify-between">
			<h1 class="text-xl font-bold text-white">Leaderboard</h1>
			<button
				onclick={() => app.refreshLeaderboard()}
				aria-label="Refresh leaderboard"
				class="rounded-lg bg-gray-800 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700"
			>
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
			</button>
		</div>

		{#if app.leaderboard.length === 0}
			<div class="flex flex-col items-center justify-center py-20 text-center">
				<svg class="mb-4 h-16 w-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
				</svg>
				<p class="text-gray-400">Loading leaderboard...</p>
			</div>
		{:else}
			<!-- Podium -->
			<div class="mb-8 flex items-end justify-center gap-4">
				{#each [1, 0, 2] as orderIndex}
					{@const entry = getTopThree()[orderIndex]}
					{#if entry}
						<div class="flex flex-col items-center">
							<!-- Avatar -->
							<div
								class="mb-2 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br {getMedalColor(entry.rank)} text-lg font-bold text-white shadow-lg"
							>
								{entry.name.charAt(0).toUpperCase()}
							</div>

							<!-- Name & Balance -->
							<p class="mb-1 text-sm font-medium text-white">
								{entry.name}
								{#if entry.userId === app.userId}
									<span class="text-purple-400">*</span>
								{/if}
							</p>
							<p class="mb-2 text-xs text-gray-400">{formatBalance(entry.balance)}</p>

							<!-- Miner badge -->
							{#if entry.isMiner}
								<svg class="mb-2 h-4 w-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
								</svg>
							{/if}

							<!-- Podium -->
							<div
								class="flex w-20 items-center justify-center rounded-t-lg bg-gradient-to-br {getMedalColor(entry.rank)} {getPodiumHeight(entry.rank)}"
							>
								<span class="text-2xl font-bold text-white">{entry.rank}</span>
							</div>
						</div>
					{/if}
				{/each}
			</div>

			<!-- Rest of the list -->
			{#if getRest().length > 0}
				<div class="rounded-xl bg-gray-800/50 p-4">
					<div class="space-y-2">
						{#each getRest() as entry}
							<div class="flex items-center justify-between rounded-lg bg-gray-700/50 p-3">
								<div class="flex items-center gap-3">
									<span class="w-8 text-center text-lg font-bold text-gray-400">#{entry.rank}</span>
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-600">
										<span class="font-medium text-white">{entry.name.charAt(0).toUpperCase()}</span>
									</div>
									<div>
										<p class="font-medium text-white">
											{entry.name}
											{#if entry.userId === app.userId}
												<span class="text-purple-400">(you)</span>
											{/if}
										</p>
										{#if entry.isMiner}
											<p class="flex items-center gap-1 text-xs text-purple-400">
												<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
												</svg>
												Miner
											</p>
										{/if}
									</div>
								</div>
								<p class="font-semibold text-white">{formatBalance(entry.balance)}</p>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<Navigation />
</div>
