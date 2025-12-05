<script lang="ts">
	import { getAppState } from '$lib/store.svelte';

	const app = getAppState();

	let name = $state('');
	let host = $state('raspberrypi.local:8765');
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

<div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-4">
	<div class="w-full max-w-md">
		<div class="mb-8 text-center">
			<div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-pink-500">
				<svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
				</svg>
			</div>
			<h1 class="text-3xl font-bold text-white">SoundChain</h1>
			<p class="mt-2 text-gray-400">Proof-of-Sound Blockchain</p>
		</div>

		<div class="rounded-2xl bg-gray-800/50 p-6 backdrop-blur-sm">
			<div class="space-y-4">
				<div>
					<label for="name" class="mb-2 block text-sm font-medium text-gray-300">Your Name</label>
					<input
						id="name"
						type="text"
						bind:value={name}
						onkeypress={handleKeyPress}
						placeholder="Enter your name"
						class="w-full rounded-lg border border-gray-600 bg-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
					/>
				</div>

				<button
					type="button"
					onclick={() => (showAdvanced = !showAdvanced)}
					class="flex items-center gap-2 text-sm text-gray-400 hover:text-white"
				>
					<svg
						class="h-4 w-4 transition-transform {showAdvanced ? 'rotate-90' : ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
					Advanced Settings
				</button>

				{#if showAdvanced}
					<div class="space-y-2 rounded-lg bg-gray-700/50 p-4">
						<label for="host" class="mb-2 block text-sm font-medium text-gray-300">Server Host</label>
						<input
							id="host"
							type="text"
							bind:value={host}
							placeholder="raspberrypi.local:8765"
							class="w-full rounded-lg border border-gray-600 bg-gray-700 px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
						/>
					</div>
				{/if}

				{#if app.connectionError}
					<div class="rounded-lg bg-red-500/20 p-3 text-sm text-red-300">
						{app.connectionError}
					</div>
				{/if}

				<button
					onclick={handleConnect}
					disabled={!name.trim() || app.isConnecting}
					class="w-full rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 font-semibold text-white transition-all hover:from-purple-600 hover:to-pink-600 disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if app.isConnecting}
						<span class="flex items-center justify-center gap-2">
							<svg class="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
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
</div>
