<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import ConnectionScreen from '$lib/components/ConnectionScreen.svelte';
	import LobbyScreen from '$lib/components/LobbyScreen.svelte';
	import WalletScreen from '$lib/components/WalletScreen.svelte';
	import MiningScreen from '$lib/components/MiningScreen.svelte';
	import LeaderboardScreen from '$lib/components/LeaderboardScreen.svelte';

	const app = getAppState();
</script>

<svelte:head>
	<title>SoundChain - Proof-of-Sound Blockchain</title>
	<meta name="description" content="A creative proof-of-work blockchain where you mine cryptocurrency through sound frequencies" />
</svelte:head>

<!-- Error Toast -->
{#if app.errorMessage}
	<div class="fixed left-4 right-4 top-4 z-50 mx-auto max-w-md">
		<div class="flex items-center gap-3 rounded-lg bg-red-500 p-4 shadow-lg">
			<svg class="h-5 w-5 flex-shrink-0 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<p class="flex-1 text-sm text-white">{app.errorMessage}</p>
			<button onclick={() => app.clearError()} aria-label="Dismiss error" class="text-white/80 hover:text-white">
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>
	</div>
{/if}

<!-- Screen Router -->
{#if app.currentScreen === 'connection'}
	<ConnectionScreen />
{:else if app.currentScreen === 'lobby'}
	<LobbyScreen />
{:else if app.currentScreen === 'wallet'}
	<WalletScreen />
{:else if app.currentScreen === 'mining'}
	<MiningScreen />
{:else if app.currentScreen === 'leaderboard'}
	<LeaderboardScreen />
{/if}
