<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import Navigation from './Navigation.svelte';

	const app = getAppState();

	function formatBalance(balance: number): string {
		return balance.toFixed(2);
	}

	function getFrequencyNote(freq: number): string {
		const notes: Record<number, string> = {
			440: 'A4',
			587: 'D5',
			784: 'G5',
			1047: 'C6'
		};
		return notes[freq] || '';
	}

	function getProgressPercentage(): number {
		if (!app.miningStatus?.target) return 0;
		return Math.min(100, (app.miningStatus.current / 1) * 100);
	}

	function getTargetPosition(): number {
		if (!app.miningStatus?.target) return 50;
		return app.miningStatus.target * 100;
	}

	function isInTargetRange(): boolean {
		if (!app.miningStatus?.target) return false;
		const { current, target, tolerance } = app.miningStatus;
		return Math.abs(current - target) <= tolerance;
	}

	function getMyContribution(): number {
		if (!app.miningStatus?.contributions || !app.userId) return 0;
		return app.miningStatus.contributions[app.userId] || 0;
	}
</script>

<div class="min-h-screen bg-[var(--ios-bg-secondary)] pb-24 pt-2">
	<div class="mx-auto max-w-lg px-4">
		<!-- Header -->
		<h1 class="mb-4 px-1 text-[28px] font-bold text-[var(--ios-text-primary)]">Mining</h1>

		<!-- Frequency Card -->
		<div class="ios-card mb-6 overflow-hidden">
			<div
				class="p-5 transition-colors {app.isPlayingTone
					? 'bg-[var(--ios-green)]'
					: 'bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)]'}"
			>
				<div class="flex items-start justify-between">
					<div>
						<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Your Frequency</p>
						<p class="text-[48px] font-bold tracking-tight text-white">{app.minerFrequency}</p>
						<p class="text-[17px] text-white/80">Hz ({getFrequencyNote(app.minerFrequency || 0)})</p>
					</div>
					<div class="text-right">
						<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Slot</p>
						<p class="text-[32px] font-bold text-white">#{app.minerSlot}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Mining Target -->
		<div class="mb-6">
			<div class="mb-2 flex items-center justify-between px-4">
				<h2 class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Mining Target</h2>
				<span class="flex items-center gap-1 text-[13px] text-[var(--ios-orange)]">
					<span class="h-2 w-2 animate-pulse rounded-full bg-[var(--ios-orange)]"></span>
					DRIFTING
				</span>
			</div>

			<div class="ios-card p-4">
				{#if app.miningStatus?.target !== null && app.miningStatus?.target !== undefined}
					<!-- Progress Bar -->
					<div class="relative mb-3 h-10 overflow-hidden rounded-xl bg-[var(--ios-gray-5)]">
						<!-- Current level -->
						<div
							class="absolute left-0 top-0 h-full transition-all duration-100 {isInTargetRange()
								? 'bg-[var(--ios-green)]'
								: 'bg-[var(--ios-purple)]'}"
							style="width: {getProgressPercentage()}%"
						></div>

						<!-- Target indicator -->
						<div
							class="absolute top-0 h-full w-1 bg-[var(--ios-orange)] shadow-[0_0_8px_rgba(255,149,0,0.6)] transition-all duration-100"
							style="left: {getTargetPosition()}%"
						></div>

						<!-- Tolerance range -->
						<div
							class="absolute top-0 h-full bg-[var(--ios-orange)]/20"
							style="left: {getTargetPosition() - (app.miningStatus?.tolerance || 0.05) * 100}%; width: {(app.miningStatus?.tolerance || 0.05) * 200}%"
						></div>
					</div>

					<div class="flex justify-between text-[15px]">
						<span class="text-[var(--ios-text-tertiary)]">Current: {(app.miningStatus.current * 100).toFixed(1)}%</span>
						<span class="text-[var(--ios-orange)]">Target: {(app.miningStatus.target * 100).toFixed(1)}%</span>
					</div>

					{#if isInTargetRange()}
						<div class="mt-3 flex items-center gap-2 rounded-xl bg-[var(--ios-green)]/10 p-3">
							<svg class="h-5 w-5 text-[var(--ios-green)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							<span class="text-[15px] text-[var(--ios-green)]">In valid range! Mining block...</span>
						</div>
					{/if}
				{:else}
					<div class="flex items-center justify-center gap-2 py-4">
						<svg class="h-6 w-6 text-[var(--ios-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span class="text-[15px] text-[var(--ios-text-tertiary)]">Waiting for transactions to mine...</span>
					</div>
				{/if}
			</div>
		</div>

		<!-- Tone Control -->
		<div class="mb-6 flex gap-3">
			<button
				onclick={() => app.toggleTone()}
				class="flex flex-1 items-center justify-center gap-2 rounded-xl py-4 text-[17px] font-semibold text-white transition-colors {app.isPlayingTone
					? 'bg-[var(--ios-red)]'
					: 'bg-[var(--ios-green)]'}"
			>
				{#if app.isPlayingTone}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
					</svg>
					Stop Tone
				{:else}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Play Tone
				{/if}
			</button>

			<button
				onclick={() => app.leaveMining()}
				class="rounded-xl bg-[var(--ios-gray-5)] px-6 py-4 text-[17px] font-semibold text-[var(--ios-text-primary)] transition-colors active:bg-[var(--ios-gray-4)]"
			>
				Leave
			</button>
		</div>

		<!-- Miner Contributions -->
		{#if app.miningStatus && Object.keys(app.miningStatus.contributions).length > 0}
			<div class="mb-6">
				<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
					Contributions
				</h2>
				<div class="ios-card p-4">
					<div class="space-y-3">
						{#each Object.entries(app.miningStatus.contributions) as [minerId, contribution]}
							{@const miner = app.gameState.miners.find((m) => m.id === minerId)}
							<div class="flex items-center justify-between">
								<span class="text-[15px] text-[var(--ios-text-primary)]">
									{miner?.name || 'Unknown'}
									{#if minerId === app.userId}
										<span class="text-[var(--ios-blue)]"> (you)</span>
									{/if}
								</span>
								<div class="flex items-center gap-3">
									<div class="h-2 w-20 overflow-hidden rounded-full bg-[var(--ios-gray-5)]">
										<div
											class="h-full bg-[var(--ios-purple)] transition-all"
											style="width: {(contribution as number) * 100}%"
										></div>
									</div>
									<span class="w-10 text-right text-[15px] tabular-nums text-[var(--ios-text-secondary)]">{((contribution as number) * 100).toFixed(0)}%</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		<!-- Recent Blocks -->
		{#if app.recentBlocks.length > 0}
			<div>
				<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
					Recent Blocks
				</h2>
				<div class="ios-list">
					{#each app.recentBlocks as block}
						<div class="ios-list-item">
							<div class="flex items-center justify-between">
								<div>
									<span class="text-[17px] font-medium text-[var(--ios-text-primary)]">Block #{block.index}</span>
									<p class="text-[13px] text-[var(--ios-text-tertiary)]">{block.transactions.length} transaction(s)</p>
								</div>
								<span class="text-[17px] font-semibold text-[var(--ios-green)]">+{formatBalance(block.totalReward)}</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>

	<Navigation />
</div>
