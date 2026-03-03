<script>
	import "../app.css";
	import { page } from "$app/stores";
	import { onMount } from "svelte";

	let navItems = [
		{
			id: "dashboard",
			label: "Dashboard",
			icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
			path: "/",
		},
		{
			id: "accounts",
			label: "Setup Accounts",
			icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
			path: "/accounts",
		},
		{
			id: "template",
			label: "Content Studio",
			icon: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
			path: "/template",
		},
		{
			id: "history",
			label: "Sent History",
			icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
			path: "/history",
		},
	];

	let isSidebarOpen = false;

	function toggleSidebar() {
		isSidebarOpen = !isSidebarOpen;
	}

	// Close sidebar when navigating on mobile
	$: if ($page.url.pathname) {
		isSidebarOpen = false;
	}
</script>

<div class="flex h-screen overflow-hidden bg-dark text-white font-sans">
	<!-- Mobile Header -->
	<div
		class="lg:hidden fixed top-0 left-0 right-0 h-16 glass-card rounded-none border-x-0 border-t-0 z-50 flex items-center justify-between px-6"
	>
		<h2
			class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400"
		>
			LeadEngine
		</h2>
		<button
			on:click={toggleSidebar}
			class="p-2 text-muted hover:text-white transition-colors"
		>
			{#if isSidebarOpen}
				<svg
					class="w-6 h-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			{:else}
				<svg
					class="w-6 h-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h16m-7 6h7"
					/>
				</svg>
			{/if}
		</button>
	</div>

	<!-- Sidebar Overlay (Mobile) -->
	{#if isSidebarOpen}
		<div
			class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30 opacity-100 transition-opacity"
			on:click={toggleSidebar}
		></div>
	{/if}

	<!-- Sidebar -->
	<aside
		class="
		fixed lg:static inset-y-0 left-0 w-64 glass-card rounded-none border-y-0 border-l-0 border-r flex flex-col z-40 shrink-0 transform transition-transform duration-300 ease-in-out
		{isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
	"
	>
		<div class="px-6 py-8 hidden lg:block">
			<h2
				class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400"
			>
				LeadEngine
			</h2>
			<div class="text-xs text-muted mt-1 tracking-wider uppercase">
				SaaS Portal
			</div>
		</div>

		<nav
			class="flex-1 px-4 space-y-2 mt-20 lg:mt-4 overflow-y-auto no-scrollbar"
		>
			{#each navItems as item}
				<a
					href={item.path}
					class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group {$page
						.url.pathname === item.path
						? 'bg-purple-600/20 text-white shadow-[inset_0_0_0_1px_rgba(107,70,193,0.5)]'
						: 'text-gray-400 hover:text-white hover:bg-white/5'}"
				>
					<svg
						class="w-5 h-5
						{$page.url.pathname === item.path
							? 'text-purple-400'
							: 'text-gray-500 group-hover:text-gray-300'}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d={item.icon}
						/>
					</svg>
					<span class="font-medium">{item.label}</span>
				</a>
			{/each}
		</nav>

		<div class="p-4 border-t border-[rgba(255,255,255,0.08)]">
			<div class="flex items-center gap-3 px-2">
				<div
					class="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-600 to-blue-600 flex items-center justify-center font-bold shadow-lg"
				>
					U
				</div>
				<div class="flex-1 overflow-hidden">
					<div class="text-sm font-semibold truncate">SaaS User</div>
					<div class="text-xs text-green-400 flex items-center gap-1">
						<span class="w-2 h-2 rounded-full bg-green-400"></span> Pro
						Plan
					</div>
				</div>
			</div>
		</div>
	</aside>

	<!-- Main Content Area -->
	<main
		class="flex-1 relative overflow-y-auto overflow-x-hidden p-4 sm:p-6 lg:p-8 z-10 pt-20 lg:pt-8"
	>
		<div class="max-w-6xl mx-auto">
			<slot />
		</div>
	</main>
</div>
