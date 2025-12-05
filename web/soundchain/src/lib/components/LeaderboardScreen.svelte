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
				return 'from-gray-400 to-gray-500';
		}
	}

	function getPodiumHeight(rank: number): string {
		switch (rank) {
			case 1:
				return 'h-20';
			case 2:
				return 'h-14';
			case 3:
				return 'h-10';
			default:
				return 'h-8';
		}
	}
</script>

<div class="min-h-screen bg-[var(--ios-bg-secondary)] pb-24 pt-2">
	<div class="mx-auto max-w-lg px-4">
		<!-- Header -->
		<div class="mb-4 flex items-center justify-between px-1">
			<h1 class="text-[28px] font-bold text-[var(--ios-text-primary)]">Leaderboard</h1>
			<button
				onclick={() => app.refreshLeaderboard()}
				aria-label="Refresh leaderboard"
				class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-bg-tertiary)] text-[var(--ios-blue)] shadow-sm"
			>
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
			</button>
		</div>

		{#if app.leaderboard.length === 0}
			<div class="flex flex-col items-center justify-center py-20 text-center">
				<div class="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-[var(--ios-gray-5)]">
					<svg class="h-10 w-10 text-[var(--ios-gray-2)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m3.044-1.35a6.726 6.726 0 01-2.748 1.35m0 0a6.772 6.772 0 01-3.044 0" />
					</svg>
				</div>
				<p class="text-[17px] text-[var(--ios-text-tertiary)]">Loading leaderboard...</p>
			</div>
		{:else}
			<!-- Podium -->
			<div class="ios-card mb-6 overflow-hidden p-6">
				<div class="flex items-end justify-center gap-3">
					{#each [1, 0, 2] as orderIndex}
						{@const entry = getTopThree()[orderIndex]}
						{#if entry}
							<div class="flex flex-col items-center">
								<!-- Avatar -->
								<div
									class="mb-2 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br {getMedalColor(entry.rank)} text-[20px] font-bold text-white shadow-lg"
								>
									{entry.name.charAt(0).toUpperCase()}
								</div>

								<!-- Name & Balance -->
								<p class="mb-0.5 text-[15px] font-medium text-[var(--ios-text-primary)]">
									{entry.name}
									{#if entry.userId === app.userId}
										<span class="text-[var(--ios-blue)]">*</span>
									{/if}
								</p>
								<p class="mb-2 text-[13px] tabular-nums text-[var(--ios-text-tertiary)]">{formatBalance(entry.balance)}</p>

								<!-- Miner badge -->
								{#if entry.isMiner}
									<div class="mb-2 flex h-5 w-5 items-center justify-center rounded-full bg-[var(--ios-purple)]/10">
										<svg class="h-3 w-3 text-[var(--ios-purple)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
										</svg>
									</div>
								{/if}

								<!-- Podium -->
								<div
									class="flex w-20 items-center justify-center rounded-t-lg bg-gradient-to-br {getMedalColor(entry.rank)} {getPodiumHeight(entry.rank)}"
								>
									<span class="text-[24px] font-bold text-white">{entry.rank}</span>
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>

			<!-- Rest of the list -->
			{#if getRest().length > 0}
				<div>
					<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
						Others
					</h2>
					<div class="ios-list">
						{#each getRest() as entry}
							<div class="ios-list-item flex items-center justify-between">
								<div class="flex items-center gap-3">
									<span class="w-8 text-center text-[17px] font-bold text-[var(--ios-text-tertiary)]">#{entry.rank}</span>
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-gray-5)]">
										<span class="text-[17px] font-semibold text-[var(--ios-text-secondary)]">{entry.name.charAt(0).toUpperCase()}</span>
									</div>
									<div>
										<p class="text-[17px] text-[var(--ios-text-primary)]">
											{entry.name}
											{#if entry.userId === app.userId}
												<span class="text-[var(--ios-blue)]"> (you)</span>
											{/if}
										</p>
										{#if entry.isMiner}
											<p class="flex items-center gap-1 text-[13px] text-[var(--ios-purple)]">
												<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
												</svg>
												Miner
											</p>
										{/if}
									</div>
								</div>
								<p class="text-[17px] tabular-nums font-semibold text-[var(--ios-text-primary)]">{formatBalance(entry.balance)}</p>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<Navigation />
</div>
