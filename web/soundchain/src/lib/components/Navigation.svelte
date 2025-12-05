<script lang="ts">
	import { getAppState } from '$lib/store.svelte';
	import type { Screen } from '$lib/types';

	const app = getAppState();

	interface NavItem {
		id: Screen;
		label: string;
		icon: string;
		showIf?: () => boolean;
	}

	const navItems: NavItem[] = [
		{ id: 'lobby', label: 'Home', icon: 'home' },
		{ id: 'wallet', label: 'Wallet', icon: 'wallet' },
		{ id: 'mining', label: 'Mining', icon: 'mining', showIf: () => app.isMiner },
		{ id: 'leaderboard', label: 'Ranks', icon: 'trophy' }
	];

	function getVisibleItems() {
		return navItems.filter((item) => !item.showIf || item.showIf());
	}
</script>

<nav class="fixed bottom-0 left-0 right-0 border-t border-gray-700 bg-gray-900/95 backdrop-blur-sm">
	<div class="mx-auto flex max-w-md justify-around px-4 py-2">
		{#each getVisibleItems() as item}
			<button
				onclick={() => app.setScreen(item.id)}
				class="flex flex-col items-center gap-1 px-4 py-2 transition-colors {app.currentScreen === item.id
					? 'text-purple-400'
					: 'text-gray-400 hover:text-white'}"
			>
				{#if item.icon === 'home'}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
					</svg>
				{:else if item.icon === 'wallet'}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
					</svg>
				{:else if item.icon === 'mining'}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
					</svg>
				{:else if item.icon === 'trophy'}
					<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
					</svg>
				{/if}
				<span class="text-xs">{item.label}</span>
			</button>
		{/each}
	</div>
</nav>
