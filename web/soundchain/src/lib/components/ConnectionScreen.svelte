<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import { browser } from '$app/environment';

	const app = getAppState();

	function getDefaultHost(): string {
		if (browser) {
			const hostname = window.location.hostname;
			if (hostname !== 'localhost' && !hostname.includes('vercel.app')) {
				return `${hostname}:8765`;
			}
		}
		return 'raspberrypi.local:8765';
	}

	let name = $state('');
	let host = $state(getDefaultHost());
	let showAdvanced = $state(false);

	async function handleConnect() {
		if (!name.trim()) return;
		await app.connect(name.trim(), host);
	}

	function handleKeyPress(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			handleConnect();
		}
	}
</script>

<div class="flex min-h-screen flex-col bg-[var(--ios-bg-secondary)]">
	<!-- Header area with icon -->
	<div class="flex flex-1 flex-col items-center justify-center px-6 pb-8">
		<!-- App Icon -->
		<div class="mb-6 flex h-24 w-24 items-center justify-center rounded-[22px] bg-gradient-to-br from-[var(--ios-purple)] to-[var(--ios-pink)] shadow-lg">
			<svg class="h-12 w-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
			</svg>
		</div>

		<h1 class="mb-1 text-[28px] font-bold tracking-tight text-[var(--ios-text-primary)]">SoundChain</h1>
		<p class="mb-8 text-[15px] text-[var(--ios-text-tertiary)]">Proof-of-Sound Blockchain</p>

		<!-- Form Card -->
		<div class="ios-card w-full max-w-sm p-5">
			<div class="space-y-4">
				<!-- Name Input -->
				<div>
					<label for="name" class="mb-1.5 block text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
						Your Name
					</label>
					<input
						id="name"
						type="text"
						bind:value={name}
						onkeypress={handleKeyPress}
						placeholder="Enter your name"
						class="ios-input"
					/>
				</div>

				<!-- Advanced Toggle -->
				<button
					type="button"
					onclick={() => (showAdvanced = !showAdvanced)}
					class="flex w-full items-center justify-between py-2 text-[15px] text-[var(--ios-blue)]"
				>
					<span>Advanced Settings</span>
					<svg
						class="h-4 w-4 transition-transform {showAdvanced ? 'rotate-90' : ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</button>

				{#if showAdvanced}
					<div class="rounded-xl bg-[var(--ios-bg-secondary)] p-4">
						<label for="host" class="mb-1.5 block text-[13px] font-medium uppercase tracking-wide text-[var(--ios-text-tertiary)]">
							Server Host
						</label>
						<input
							id="host"
							type="text"
							bind:value={host}
							placeholder="raspberrypi.local:8765"
							class="ios-input bg-[var(--ios-bg-tertiary)]"
						/>
					</div>
				{/if}

				<!-- Error Message -->
				{#if app.connectionError}
					<div class="rounded-xl bg-[var(--ios-red)]/10 p-4">
						<p class="text-[15px] text-[var(--ios-red)]">{app.connectionError}</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Connect Button -->
		<div class="mt-6 w-full max-w-sm">
			<button
				onclick={handleConnect}
				disabled={!name.trim() || app.isConnecting}
				class="ios-button-primary w-full text-[17px]"
			>
				{#if app.isConnecting}
					<span class="flex items-center justify-center gap-2">
						<svg class="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Connecting...
					</span>
				{:else}
					Connect
				{/if}
			</button>
		</div>
	</div>
</div>
