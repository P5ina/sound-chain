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

	function getFrequencyDiff(): number | null {
		const myContrib = getMyContribution();
		if (!myContrib || !app.miningStatus?.targetFrequency) return null;
		return myContrib.frequency - app.miningStatus.targetFrequency;
	}

	function getAccuracyLevel(): 'perfect' | 'good' | 'close' | 'far' | 'none' {
		const myContrib = getMyContribution();
		if (!myContrib || !myContrib.detected) return 'none';
		if (myContrib.accuracy >= 0.9) return 'perfect';
		if (myContrib.accuracy >= 0.7) return 'good';
		if (myContrib.accuracy >= 0.4) return 'close';
		return 'far';
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

		<!-- Big Status Indicator -->
		{#if app.isPlayingTone && app.miningStatus?.targetFrequency}
			{@const myContrib = getMyContribution()}
			{@const diff = getFrequencyDiff()}
			{@const level = getAccuracyLevel()}

			<div class="ios-card mb-6 overflow-hidden">
				<div class="p-6 text-center transition-colors duration-200
					{level === 'perfect' ? 'bg-[var(--ios-green)]' : ''}
					{level === 'good' ? 'bg-[var(--ios-green)]/80' : ''}
					{level === 'close' ? 'bg-[var(--ios-orange)]' : ''}
					{level === 'far' ? 'bg-[var(--ios-red)]/80' : ''}
					{level === 'none' ? 'bg-[var(--ios-gray-4)]' : ''}"
				>
					<!-- Status Icon -->
					<div class="mb-3">
						{#if level === 'perfect'}
							<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
								<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
								</svg>
							</div>
						{:else if level === 'good'}
							<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
								<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
							</div>
						{:else if level === 'close' && diff !== null}
							<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
								{#if diff > 0}
									<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7" />
									</svg>
								{:else}
									<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" />
									</svg>
								{/if}
							</div>
						{:else if level === 'far' && diff !== null}
							<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
								{#if diff > 0}
									<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
									</svg>
								{:else}
									<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
									</svg>
								{/if}
							</div>
						{:else}
							<div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/20">
								<svg class="h-10 w-10 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
						{/if}
					</div>

					<!-- Status Text -->
					<p class="text-[24px] font-bold text-white">
						{#if level === 'perfect'}
							PERFECT!
						{:else if level === 'good'}
							Good!
						{:else if level === 'close'}
							Close...
						{:else if level === 'far'}
							Keep trying
						{:else}
							Not detected
						{/if}
					</p>

					<!-- Frequency difference -->
					{#if myContrib?.detected && diff !== null}
						<p class="mt-1 text-[17px] text-white/80">
							{#if Math.abs(diff) < 5}
								On target!
							{:else if diff > 0}
								{Math.abs(diff).toFixed(0)} Hz too high
							{:else}
								{Math.abs(diff).toFixed(0)} Hz too low
							{/if}
						</p>
					{:else}
						<p class="mt-1 text-[17px] text-white/60">
							Your tone is not being detected
						</p>
					{/if}

					<!-- Accuracy bar -->
					{#if myContrib?.detected}
						<div class="mx-auto mt-4 h-2 w-48 overflow-hidden rounded-full bg-white/20">
							<div
								class="h-full bg-white transition-all duration-200"
								style="width: {myContrib.accuracy * 100}%"
							></div>
						</div>
						<p class="mt-2 text-[13px] text-white/70">
							{(myContrib.accuracy * 100).toFixed(0)}% accuracy
						</p>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Frequency Display -->
		<div class="ios-card mb-6 overflow-hidden">
			<div class="flex items-center justify-between p-4">
				<div>
					<p class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Your Frequency</p>
					<p class="text-[32px] font-bold text-[var(--ios-text-primary)]">{app.minerFrequency || 440} <span class="text-[17px] font-normal text-[var(--ios-text-secondary)]">Hz</span></p>
				</div>
				{#if app.miningStatus?.targetFrequency}
					<div class="text-right">
						<p class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">Target</p>
						<p class="text-[32px] font-bold text-[var(--ios-orange)]">{app.miningStatus.targetFrequency.toFixed(0)} <span class="text-[17px] font-normal">Hz</span></p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Frequency Slider -->
		<div class="mb-6">
			<div class="ios-card p-4">
				<!-- Visual frequency bar with target indicator -->
				<div class="relative mb-4 h-14 overflow-hidden rounded-xl bg-[var(--ios-gray-5)]">
					<!-- Target frequency indicator and zone -->
					{#if app.miningStatus?.targetFrequency}
						<!-- Tolerance zone -->
						<div
							class="absolute top-0 h-full bg-[var(--ios-green)]/30 transition-all duration-100"
							style="left: {Math.max(0, getTargetPosition() - 5)}%; width: 10%"
						></div>
						<!-- Target line -->
						<div
							class="absolute top-0 h-full w-1 bg-[var(--ios-orange)] shadow-[0_0_12px_rgba(255,149,0,0.8)] transition-all duration-100"
							style="left: calc({getTargetPosition()}% - 2px)"
						></div>
					{/if}

					<!-- Current frequency indicator -->
					<div
						class="absolute top-1 bottom-1 w-3 rounded-full transition-all duration-75
							{getAccuracyLevel() === 'perfect' || getAccuracyLevel() === 'good' ? 'bg-[var(--ios-green)] shadow-[0_0_12px_rgba(52,199,89,0.8)]' : ''}
							{getAccuracyLevel() === 'close' ? 'bg-[var(--ios-orange)] shadow-[0_0_12px_rgba(255,149,0,0.8)]' : ''}
							{getAccuracyLevel() === 'far' ? 'bg-[var(--ios-red)] shadow-[0_0_12px_rgba(255,59,48,0.8)]' : ''}
							{getAccuracyLevel() === 'none' ? 'bg-[var(--ios-purple)] shadow-[0_0_8px_rgba(175,82,222,0.6)]' : ''}"
						style="left: calc({getSliderPosition()}% - 6px)"
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
				<div class="mt-2 flex justify-between text-[13px] text-[var(--ios-text-tertiary)]">
					<span>{app.minFrequency} Hz</span>
					<span>{app.maxFrequency} Hz</span>
				</div>
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

		<!-- All Miners Status -->
		{#if app.miningStatus && Object.keys(app.miningStatus.contributions).length > 0}
			<div class="mb-6">
				<div class="mb-2 flex items-center justify-between px-4">
					<h2 class="text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
						All Miners
					</h2>
					{#if app.miningStatus.targetFrequency}
						<span class="flex items-center gap-1 text-[13px] text-[var(--ios-orange)]">
							<span class="h-2 w-2 animate-pulse rounded-full bg-[var(--ios-orange)]"></span>
							Target: {app.miningStatus.targetFrequency.toFixed(0)} Hz
						</span>
					{/if}
				</div>
				<div class="ios-card overflow-hidden">
					{#each Object.entries(app.miningStatus.contributions) as [minerId, contrib], i}
						{@const miner = app.gameState.miners.find((m) => m.id === minerId)}
						{@const isMe = minerId === app.userId}
						{@const freqDiff = app.miningStatus?.targetFrequency ? contrib.frequency - app.miningStatus.targetFrequency : 0}
						<div class="flex items-center gap-3 p-4 {i > 0 ? 'border-t border-[var(--ios-separator)]' : ''}">
							<!-- Status indicator -->
							<div class="flex-shrink-0">
								{#if contrib.detected && contrib.accuracy >= 0.7}
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-green)]">
										<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
										</svg>
									</div>
								{:else if contrib.detected && contrib.accuracy >= 0.3}
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-orange)]">
										<span class="text-[17px] font-bold text-white">~</span>
									</div>
								{:else if contrib.detected}
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-red)]">
										<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
										</svg>
									</div>
								{:else}
									<div class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ios-gray-4)]">
										<span class="text-[17px] text-[var(--ios-text-tertiary)]">?</span>
									</div>
								{/if}
							</div>

							<!-- Name and frequency -->
							<div class="flex-1 min-w-0">
								<p class="text-[17px] font-medium text-[var(--ios-text-primary)] {isMe ? 'text-[var(--ios-blue)]' : ''}">
									{miner?.name || 'Unknown'}{isMe ? ' (you)' : ''}
								</p>
								<p class="text-[13px] text-[var(--ios-text-tertiary)]">
									{contrib.frequency.toFixed(0)} Hz
									{#if contrib.detected && app.miningStatus?.targetFrequency}
										<span class="{freqDiff > 0 ? 'text-[var(--ios-orange)]' : freqDiff < 0 ? 'text-[var(--ios-blue)]' : 'text-[var(--ios-green)]'}">
											({freqDiff > 0 ? '+' : ''}{freqDiff.toFixed(0)})
										</span>
									{/if}
								</p>
							</div>

							<!-- Accuracy -->
							<div class="text-right">
								{#if contrib.detected}
									<p class="text-[20px] font-bold tabular-nums
										{contrib.accuracy >= 0.7 ? 'text-[var(--ios-green)]' : ''}
										{contrib.accuracy >= 0.3 && contrib.accuracy < 0.7 ? 'text-[var(--ios-orange)]' : ''}
										{contrib.accuracy < 0.3 ? 'text-[var(--ios-red)]' : ''}"
									>
										{(contrib.accuracy * 100).toFixed(0)}%
									</p>
								{:else}
									<p class="text-[15px] text-[var(--ios-text-tertiary)]">—</p>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Mining Progress -->
		{#if app.miningStatus?.targetFrequency}
			<div class="mb-6">
				<h2 class="mb-2 px-4 text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
					Block Progress
				</h2>
				<div class="ios-card p-4">
					<div class="mb-2 flex items-center justify-between">
						<span class="text-[15px] text-[var(--ios-text-secondary)]">Team Contribution</span>
						<span class="text-[20px] font-bold tabular-nums {app.miningStatus.avgContribution >= 0.3 ? 'text-[var(--ios-green)]' : 'text-[var(--ios-text-primary)]'}">
							{(app.miningStatus.avgContribution * 100).toFixed(0)}%
						</span>
					</div>
					<div class="relative h-4 overflow-hidden rounded-full bg-[var(--ios-gray-5)]">
						<div
							class="h-full transition-all duration-300 {app.miningStatus.avgContribution >= 0.3
								? 'bg-[var(--ios-green)]'
								: 'bg-[var(--ios-purple)]'}"
							style="width: {Math.min(100, app.miningStatus.avgContribution * 100)}%"
						></div>
						<!-- 30% threshold -->
						<div class="absolute top-0 h-full w-0.5 bg-[var(--ios-orange)]" style="left: 30%"></div>
					</div>
					<p class="mt-2 text-[13px] text-[var(--ios-text-tertiary)]">
						{#if app.miningStatus.avgContribution >= 0.3}
							Mining block...
						{:else}
							Need 30% to mine
						{/if}
					</p>
				</div>
			</div>
		{:else}
			<div class="mb-6">
				<div class="ios-card p-6 text-center">
					<svg class="mx-auto mb-2 h-8 w-8 text-[var(--ios-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<p class="text-[15px] text-[var(--ios-text-tertiary)]">Waiting for transactions...</p>
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
									<p class="text-[13px] text-[var(--ios-text-tertiary)]">{block.transactions.length} tx</p>
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
		width: 32px;
		height: 32px;
		background: var(--ios-purple);
		border-radius: 50%;
		cursor: pointer;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}

	.frequency-slider::-moz-range-thumb {
		width: 32px;
		height: 32px;
		background: var(--ios-purple);
		border-radius: 50%;
		cursor: pointer;
		border: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
	}
</style>
