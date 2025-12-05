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

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 pb-20 pt-4">
	<div class="mx-auto max-w-md px-4">
		<!-- Header -->
		<h1 class="mb-6 text-xl font-bold text-white">Mining</h1>

		<!-- Frequency Card -->
		<div
			class="mb-6 rounded-2xl p-6 transition-all {app.isPlayingTone
				? 'bg-gradient-to-br from-green-500 to-emerald-600'
				: 'bg-gradient-to-br from-purple-500 to-pink-500'}"
		>
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-white/80">Your Frequency</p>
					<p class="text-5xl font-bold text-white">{app.minerFrequency}</p>
					<p class="text-lg text-white/80">Hz ({getFrequencyNote(app.minerFrequency || 0)})</p>
				</div>
				<div class="text-right">
					<p class="text-sm text-white/80">Slot</p>
					<p class="text-3xl font-bold text-white">#{app.minerSlot}</p>
				</div>
			</div>
		</div>

		<!-- Mining Target -->
		<div class="mb-6 rounded-xl bg-gray-800/50 p-4">
			<div class="mb-3 flex items-center justify-between">
				<h2 class="font-semibold text-white">Mining Target</h2>
				<span class="flex items-center gap-1 text-xs text-orange-400">
					<svg class="h-3 w-3 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
						<path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z"/>
						<path d="M10 5a1 1 0 011 1v3.586l2.707 2.707a1 1 0 01-1.414 1.414l-3-3A1 1 0 019 10V6a1 1 0 011-1z"/>
					</svg>
					DRIFTING
				</span>
			</div>

			{#if app.miningStatus?.target !== null && app.miningStatus?.target !== undefined}
				<div class="mb-4">
					<!-- Progress Bar -->
					<div class="relative mb-2 h-8 overflow-hidden rounded-full bg-gray-700">
						<!-- Current level -->
						<div
							class="absolute left-0 top-0 h-full transition-all duration-100 {isInTargetRange()
								? 'bg-green-500'
								: 'bg-purple-500'}"
							style="width: {getProgressPercentage()}%"
						></div>

						<!-- Target indicator (animated to show drift) -->
						<div
							class="absolute top-0 h-full w-1 bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.8)] transition-all duration-100"
							style="left: {getTargetPosition()}%"
						></div>

						<!-- Tolerance range -->
						<div
							class="absolute top-0 h-full bg-yellow-400/20"
							style="left: {getTargetPosition() - (app.miningStatus?.tolerance || 0.05) * 100}%; width: {(app.miningStatus?.tolerance || 0.05) * 200}%"
						></div>
					</div>

					<div class="flex justify-between text-sm">
						<span class="text-gray-400">Current: {(app.miningStatus.current * 100).toFixed(1)}%</span>
						<span class="text-yellow-400">Target: {(app.miningStatus.target * 100).toFixed(1)}%</span>
					</div>

					{#if isInTargetRange()}
						<div class="mt-2 flex items-center gap-2 rounded-lg bg-green-500/20 p-2">
							<svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							<span class="text-sm text-green-300">In valid range! Mining block...</span>
						</div>
					{/if}
				</div>
			{:else}
				<div class="flex items-center gap-2 rounded-lg bg-gray-700/50 p-4 text-center">
					<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span class="text-gray-400">Waiting for transactions to mine...</span>
				</div>
			{/if}
		</div>

		<!-- Tone Control -->
		<div class="mb-6 flex gap-3">
			<button
				onclick={() => app.toggleTone()}
				class="flex-1 rounded-xl px-4 py-4 font-semibold text-white transition-all {app.isPlayingTone
					? 'bg-red-500 hover:bg-red-600'
					: 'bg-green-500 hover:bg-green-600'}"
			>
				{#if app.isPlayingTone}
					<span class="flex items-center justify-center gap-2">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
						</svg>
						Stop Tone
					</span>
				{:else}
					<span class="flex items-center justify-center gap-2">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Play Tone
					</span>
				{/if}
			</button>

			<button
				onclick={() => app.leaveMining()}
				class="rounded-xl bg-gray-700 px-4 py-4 font-semibold text-white transition-all hover:bg-gray-600"
			>
				Leave
			</button>
		</div>

		<!-- Miner Contributions -->
		{#if app.miningStatus && Object.keys(app.miningStatus.contributions).length > 0}
			<div class="mb-6 rounded-xl bg-gray-800/50 p-4">
				<h2 class="mb-3 font-semibold text-white">Miner Contributions</h2>
				<div class="space-y-2">
					{#each Object.entries(app.miningStatus.contributions) as [minerId, contribution]}
						{@const miner = app.gameState.miners.find((m) => m.id === minerId)}
						<div class="flex items-center justify-between">
							<span class="text-sm text-gray-300">
								{miner?.name || 'Unknown'}
								{#if minerId === app.userId}
									<span class="text-purple-400">(you)</span>
								{/if}
							</span>
							<div class="flex items-center gap-2">
								<div class="h-2 w-24 overflow-hidden rounded-full bg-gray-700">
									<div
										class="h-full bg-purple-500 transition-all"
										style="width: {(contribution as number) * 100}%"
									></div>
								</div>
								<span class="w-12 text-right text-sm text-white">{((contribution as number) * 100).toFixed(0)}%</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Recent Blocks -->
		{#if app.recentBlocks.length > 0}
			<div class="rounded-xl bg-gray-800/50 p-4">
				<h2 class="mb-3 font-semibold text-white">Recent Blocks</h2>
				<div class="space-y-2">
					{#each app.recentBlocks as block}
						<div class="rounded-lg bg-gray-700/50 p-3">
							<div class="flex items-center justify-between">
								<span class="font-medium text-white">Block #{block.index}</span>
								<span class="text-sm text-green-400">+{formatBalance(block.totalReward)} coins</span>
							</div>
							<p class="text-xs text-gray-400">{block.transactions.length} transaction(s)</p>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>

	<Navigation />
</div>
