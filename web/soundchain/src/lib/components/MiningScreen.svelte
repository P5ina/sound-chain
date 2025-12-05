<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import Navigation from './Navigation.svelte';

	const app = getAppState();

	function formatBalance(balance: number): string {
		return balance.toFixed(2);
	}

	function getTargetPosition(): number {
		if (!app.miningStatus?.targetFrequency) return 50;
		const { targetFrequency, minFrequency, maxFrequency } = app.miningStatus;
		return ((targetFrequency - minFrequency) / (maxFrequency - minFrequency)) * 100;
	}

	function getSliderPosition(): number {
		if (!app.minerFrequency) return 50;
		return ((app.minerFrequency - app.minFrequency) / (app.maxFrequency - app.minFrequency)) * 100;
	}

	function getMyContribution() {
		if (!app.miningStatus?.contributions || !app.userId) return null;
		return app.miningStatus.contributions[app.userId] || null;
	}

	function isInTargetRange(): boolean {
		if (!app.miningStatus?.targetFrequency) return false;
		const myContrib = getMyContribution();
		if (!myContrib) return false;
		return myContrib.accuracy >= 0.7; // 70% accuracy = good
	}

	function handleSliderInput(event: Event) {
		const target = event.target as HTMLInputElement;
		const value = parseInt(target.value, 10);
		app.setFrequency(value);
	}
</script>

<div class="min-h-screen bg-[var(--ios-bg-secondary)] pb-24 pt-2">
	<div class="mx-auto max-w-lg px-4">
		<!-- Header -->
		<h1 class="mb-4 px-1 text-[28px] font-bold text-[var(--ios-text-primary)]">Mining</h1>

		<!-- Frequency Control Card -->
		<div class="ios-card mb-6 overflow-hidden">
			<div
				class="p-5 transition-colors {app.isPlayingTone
					? isInTargetRange()
						? 'bg-[var(--ios-green)]'
						: 'bg-[var(--ios-purple)]'
					: 'bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)]'}"
			>
				<div class="flex items-start justify-between">
					<div>
						<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Your Frequency</p>
						<p class="text-[48px] font-bold tracking-tight text-white">{app.minerFrequency || 440}</p>
						<p class="text-[17px] text-white/80">Hz</p>
					</div>
					<div class="text-right">
						{#if getMyContribution()?.detected}
							<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Accuracy</p>
							<p class="text-[32px] font-bold text-white">{((getMyContribution()?.accuracy || 0) * 100).toFixed(0)}%</p>
						{:else}
							<p class="text-[13px] font-medium uppercase tracking-wide text-white/70">Status</p>
							<p class="text-[17px] font-bold text-white/80">
								{app.isPlayingTone ? 'Not Detected' : 'Not Playing'}
							</p>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Frequency Slider -->
		<div class="mb-6">
			<div class="mb-2 flex items-center justify-between px-4">
				<h2 class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Frequency Control</h2>
				<span class="text-[13px] text-[var(--ios-text-secondary)]">
					{app.minFrequency}Hz - {app.maxFrequency}Hz
				</span>
			</div>

			<div class="ios-card p-4">
				<!-- Visual frequency bar with target indicator -->
				<div class="relative mb-4 h-12 overflow-hidden rounded-xl bg-[var(--ios-gray-5)]">
					<!-- Target frequency indicator -->
					{#if app.miningStatus?.targetFrequency}
						<div
							class="absolute top-0 h-full w-1.5 bg-[var(--ios-orange)] shadow-[0_0_12px_rgba(255,149,0,0.8)] transition-all duration-100"
							style="left: calc({getTargetPosition()}% - 3px)"
						></div>
						<!-- Tolerance zone -->
						<div
							class="absolute top-0 h-full bg-[var(--ios-orange)]/20 transition-all duration-100"
							style="left: {getTargetPosition() - (app.miningStatus.toleranceHz / (app.miningStatus.maxFrequency - app.miningStatus.minFrequency)) * 100}%; width: {(app.miningStatus.toleranceHz * 2 / (app.miningStatus.maxFrequency - app.miningStatus.minFrequency)) * 100}%"
						></div>
					{/if}

					<!-- Current frequency indicator (slider position) -->
					<div
						class="absolute top-0 h-full w-2 transition-all duration-75 {isInTargetRange()
							? 'bg-[var(--ios-green)] shadow-[0_0_12px_rgba(52,199,89,0.8)]'
							: 'bg-[var(--ios-purple)] shadow-[0_0_8px_rgba(175,82,222,0.6)]'}"
						style="left: calc({getSliderPosition()}% - 4px)"
					></div>
				</div>

				<!-- Actual slider input -->
				<input
					type="range"
					min={app.minFrequency}
					max={app.maxFrequency}
					value={app.minerFrequency || 440}
					oninput={handleSliderInput}
					class="frequency-slider w-full"
				/>

				<!-- Labels -->
				<div class="mt-2 flex justify-between text-[13px]">
					<span class="text-[var(--ios-text-tertiary)]">{app.minFrequency} Hz</span>
					{#if app.miningStatus?.targetFrequency}
						<span class="font-medium text-[var(--ios-orange)]">
							Target: {app.miningStatus.targetFrequency.toFixed(0)} Hz
						</span>
					{/if}
					<span class="text-[var(--ios-text-tertiary)]">{app.maxFrequency} Hz</span>
				</div>
			</div>
		</div>

		<!-- Mining Status -->
		<div class="mb-6">
			<div class="mb-2 flex items-center justify-between px-4">
				<h2 class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Mining Target</h2>
				{#if app.miningStatus?.targetFrequency}
					<span class="flex items-center gap-1 text-[13px] text-[var(--ios-orange)]">
						<span class="h-2 w-2 animate-pulse rounded-full bg-[var(--ios-orange)]"></span>
						DRIFTING
					</span>
				{/if}
			</div>

			<div class="ios-card p-4">
				{#if app.miningStatus?.targetFrequency}
					<!-- Mining progress -->
					<div class="mb-3 flex items-center justify-between">
						<span class="text-[15px] text-[var(--ios-text-secondary)]">Avg Contribution</span>
						<span class="text-[17px] font-semibold {app.miningStatus.avgContribution >= 0.3 ? 'text-[var(--ios-green)]' : 'text-[var(--ios-text-primary)]'}">
							{(app.miningStatus.avgContribution * 100).toFixed(0)}%
						</span>
					</div>

					<!-- Progress bar -->
					<div class="relative mb-3 h-3 overflow-hidden rounded-full bg-[var(--ios-gray-5)]">
						<div
							class="h-full transition-all duration-200 {app.miningStatus.avgContribution >= 0.3
								? 'bg-[var(--ios-green)]'
								: 'bg-[var(--ios-purple)]'}"
							style="width: {app.miningStatus.avgContribution * 100}%"
						></div>
						<!-- Threshold marker at 30% -->
						<div class="absolute top-0 h-full w-0.5 bg-[var(--ios-orange)]" style="left: 30%"></div>
					</div>

					<p class="text-[13px] text-[var(--ios-text-tertiary)]">
						Need 30% contribution to mine a block
					</p>

					{#if app.miningStatus.avgContribution >= 0.3}
						<div class="mt-3 flex items-center gap-2 rounded-xl bg-[var(--ios-green)]/10 p-3">
							<svg class="h-5 w-5 text-[var(--ios-green)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
							<span class="text-[15px] text-[var(--ios-green)]">Mining block...</span>
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
					Miners
				</h2>
				<div class="ios-card p-4">
					<div class="space-y-3">
						{#each Object.entries(app.miningStatus.contributions) as [minerId, contrib]}
							{@const miner = app.gameState.miners.find((m) => m.id === minerId)}
							<div class="flex items-center justify-between">
								<div>
									<span class="text-[15px] text-[var(--ios-text-primary)]">
										{miner?.name || 'Unknown'}
										{#if minerId === app.userId}
											<span class="text-[var(--ios-blue)]"> (you)</span>
										{/if}
									</span>
									<p class="text-[13px] text-[var(--ios-text-tertiary)]">
										{contrib.frequency.toFixed(0)} Hz
										{#if contrib.detected}
											<span class="text-[var(--ios-green)]">• Detected</span>
										{/if}
									</p>
								</div>
								<div class="flex items-center gap-3">
									<div class="h-2 w-20 overflow-hidden rounded-full bg-[var(--ios-gray-5)]">
										<div
											class="h-full transition-all {contrib.accuracy >= 0.7
												? 'bg-[var(--ios-green)]'
												: contrib.accuracy >= 0.3
													? 'bg-[var(--ios-orange)]'
													: 'bg-[var(--ios-purple)]'}"
											style="width: {contrib.contribution * 100}%"
										></div>
									</div>
									<span class="w-10 text-right text-[15px] tabular-nums text-[var(--ios-text-secondary)]">{(contrib.contribution * 100).toFixed(0)}%</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		<!-- Detected Tones (Debug info) -->
		{#if app.miningStatus?.detectedTones && app.miningStatus.detectedTones.length > 0}
			<div class="mb-6">
				<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
					Detected Tones
				</h2>
				<div class="ios-card p-4">
					<div class="flex flex-wrap gap-2">
						{#each app.miningStatus.detectedTones as tone}
							<span class="rounded-lg bg-[var(--ios-purple)]/20 px-3 py-1 text-[13px] text-[var(--ios-purple)]">
								{tone.frequency.toFixed(0)} Hz
								<span class="text-[var(--ios-text-tertiary)]">({(tone.purity * 100).toFixed(0)}% pure)</span>
							</span>
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

<style>
	.frequency-slider {
		-webkit-appearance: none;
		appearance: none;
		height: 8px;
		background: var(--ios-gray-5);
		border-radius: 4px;
		outline: none;
	}

	.frequency-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 28px;
		height: 28px;
		background: var(--ios-purple);
		border-radius: 50%;
		cursor: pointer;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.frequency-slider::-moz-range-thumb {
		width: 28px;
		height: 28px;
		background: var(--ios-purple);
		border-radius: 50%;
		cursor: pointer;
		border: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}
</style>
