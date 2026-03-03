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

<div class="flex h-screen overflow-hidden bg-dark selection:bg-purple-500/30">
	<!-- Sidebar Overlay (Mobile) -->
	{#if isSidebarOpen}
		<div
			class="lg:hidden fixed inset-0 bg-black/80 backdrop-blur-md z-40 opacity-100 transition-all duration-500"
			on:click={toggleSidebar}
		></div>
	{/if}

	<!-- Floating Sidebar Container -->
	<aside
		class="
		fixed lg:static inset-y-0 left-0 w-72 p-4 z-50 flex flex-col transform transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]
		{isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
	"
	>
		<div
			class="h-full glass-card flex flex-col border-white/10 shadow-purple-500/5"
		>
			<div class="px-8 py-10">
				<div class="flex items-center gap-3">
					<div
						class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-purple-500/20"
					>
						<svg
							class="w-6 h-6 text-white"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2.5"
								d="M13 10V3L4 14h7v7l9-11h-7z"
							/>
						</svg>
					</div>
					<div>
						<h2
							class="text-xl font-bold tracking-tight text-white leading-none"
						>
							LeadEngine
						</h2>
						<div
							class="text-[10px] font-bold text-muted mt-1 uppercase tracking-[0.2em] opacity-60"
						>
							SaaS Portal
						</div>
					</div>
				</div>
			</div>

			<nav class="flex-1 px-4 space-y-1.5 overflow-y-auto no-scrollbar">
				{#each navItems as item}
					<a
						href={item.path}
						class="flex items-center gap-3.5 px-5 py-3.5 rounded-2xl transition-all duration-300 group relative
						{$page.url.pathname === item.path
							? 'bg-purple-500/10 text-white border border-purple-500/20 shadow-lg shadow-purple-500/5'
							: 'text-zinc-400 hover:text-white hover:bg-white/[0.03] border border-transparent'}"
					>
						{#if $page.url.pathname === item.path}
							<div
								class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-purple-500 rounded-r-full"
							></div>
						{/if}
						<svg
							class="w-5 h-5 transition-transform duration-300 group-hover:scale-110
							{$page.url.pathname === item.path
								? 'text-purple-400'
								: 'text-zinc-500 group-hover:text-zinc-300'}"
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
						<span class="font-medium tracking-wide text-sm"
							>{item.label}</span
						>
					</a>
				{/each}
			</nav>

			<div class="p-6">
				<div
					class="p-4 rounded-3xl bg-white/[0.02] border border-white/[0.05] flex items-center gap-4 group cursor-pointer hover:bg-white/[0.04] transition-all"
				>
					<div class="relative">
						<div
							class="w-11 h-11 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center font-bold text-lg shadow-lg"
						>
							S
						</div>
						<div
							class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-[#121216] shadow-sm"
						></div>
					</div>
					<div class="flex-1 overflow-hidden">
						<div
							class="text-sm font-bold text-zinc-100 truncate text-left"
						>
							Sangam P.
						</div>
						<div
							class="text-[10px] font-bold text-emerald-400 flex items-center gap-1 uppercase tracking-wider"
						>
							Pro Membership
						</div>
					</div>
				</div>
			</div>
		</div>
	</aside>

	<!-- Main Content Area -->
	<div class="flex-1 flex flex-col min-w-0">
		<!-- Top Bar (Mobile Only Header) -->
		<header
			class="lg:hidden h-20 px-6 flex items-center justify-between z-30 bg-dark/50 backdrop-blur-xl border-b border-white/5"
		>
			<div class="flex items-center gap-3">
				<div
					class="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-500 to-cyan-500 flex items-center justify-center"
				>
					<svg
						class="w-5 h-5 text-white"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2.5"
							d="M13 10V3L4 14h7v7l9-11h-7z"
						/>
					</svg>
				</div>
				<h2 class="text-lg font-bold tracking-tight text-white">
					LeadEngine
				</h2>
			</div>
			<button
				on:click={toggleSidebar}
				class="p-2.5 rounded-xl bg-white/5 border border-white/10 text-white active:scale-95 transition-all"
			>
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
			</button>
		</header>

		<main
			class="flex-1 relative overflow-y-auto overflow-x-hidden p-6 sm:p-10 lg:p-12"
		>
			<!-- Animated background blobs -->
			<div
				class="fixed top-0 right-0 -z-10 w-[500px] h-[500px] bg-purple-500/10 blur-[120px] rounded-full translate-x-1/2 -translate-y-1/2"
			></div>
			<div
				class="fixed bottom-0 left-0 -z-10 w-[400px] h-[400px] bg-cyan-500/5 blur-[100px] rounded-full -translate-x-1/2 translate-y-1/2"
			></div>

			<div class="max-w-6xl mx-auto pb-20">
				<slot />
			</div>
		</main>
	</div>
</div>
