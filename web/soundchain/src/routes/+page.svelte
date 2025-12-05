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
	<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-status-bar-style" content="default" />
</svelte:head>

<!-- Error Toast - iOS Style -->
{#if app.errorMessage}
	<div class="fixed left-4 right-4 top-4 z-50 mx-auto max-w-lg">
		<div class="flex items-center gap-3 rounded-2xl bg-[var(--ios-red)] p-4 shadow-lg">
			<div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white/20">
				<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
				</svg>
			</div>
			<p class="flex-1 text-[15px] font-medium text-white">{app.errorMessage}</p>
			<button onclick={() => app.clearError()} aria-label="Dismiss error" class="rounded-full p-1 text-white/80 transition-colors hover:bg-white/10 hover:text-white">
				<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
