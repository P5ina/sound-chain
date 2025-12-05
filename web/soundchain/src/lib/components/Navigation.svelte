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

<nav class="ios-tabbar fixed bottom-0 left-0 right-0">
	<div class="mx-auto flex max-w-lg justify-around px-2 pb-1 pt-2">
		{#each getVisibleItems() as item}
			<button
				onclick={() => app.setScreen(item.id)}
				class="flex min-w-[64px] flex-col items-center gap-0.5 px-3 py-1 transition-colors {app.currentScreen === item.id
					? 'text-[var(--ios-blue)]'
					: 'text-[var(--ios-gray-1)]'}"
			>
				{#if item.icon === 'home'}
					<svg class="h-7 w-7" fill={app.currentScreen === item.id ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
					</svg>
				{:else if item.icon === 'wallet'}
					<svg class="h-7 w-7" fill={app.currentScreen === item.id ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12m18 0v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 9m18 0V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v3" />
					</svg>
				{:else if item.icon === 'mining'}
					<svg class="h-7 w-7" fill={app.currentScreen === item.id ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
					</svg>
				{:else if item.icon === 'trophy'}
					<svg class="h-7 w-7" fill={app.currentScreen === item.id ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 002.748 1.35m3.044-1.35a6.726 6.726 0 01-2.748 1.35m0 0a6.772 6.772 0 01-3.044 0" />
					</svg>
				{/if}
				<span class="text-[10px] font-medium">{item.label}</span>
			</button>
		{/each}
	</div>
</nav>
