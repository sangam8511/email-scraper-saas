<script>
    import { onMount, onDestroy } from "svelte";
    import { fade, slide, fly } from "svelte/transition";

    let status = {
        is_running: false,
        current_niche: "",
        current_city: "-",
        emails_found: 0,
        emails_sent: 0,
        emails_skipped: 0,
        queue_size: 0,
    };

    let logs = [];
    let nicheInput = "";
    let isInitialLoad = true;

    let pollInterval;
    let logsInterval;

    async function fetchStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            status = data;
            isInitialLoad = false;
        } catch (e) {
            console.error(e);
        }
    }

    async function fetchLogs() {
        try {
            const res = await fetch("/api/logs");
            const data = await res.json();
            if (data && data.logs) {
                logs = data.logs;
            }
        } catch (e) {
            console.error(e);
        }
    }

    onMount(() => {
        fetchStatus();
        fetchLogs();
        pollInterval = setInterval(fetchStatus, 1500);
        logsInterval = setInterval(fetchLogs, 2000);
    });

    onDestroy(() => {
        clearInterval(pollInterval);
        clearInterval(logsInterval);
    });

    async function startCampaign() {
        if (!nicheInput) nicheInput = "plumbers";
        try {
            const res = await fetch("/api/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ niche: nicheInput }),
            });
            const data = await res.json();
            if (data.success) {
                logs = [...logs, "🚀 Ignition sequence started..."];
                fetchStatus();
            } else {
                alert(data.error);
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function stopCampaign() {
        try {
            await fetch("/api/stop", { method: "POST" });
        } catch (e) {
            console.error(e);
        }
    }
</script>

<div class="space-y-10">
    <!-- Welcome Header -->
    <header
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
    >
        <div>
            <h1
                class="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-2"
            >
                Engine Dashboard
            </h1>
            <p class="text-zinc-400 font-medium">
                Monitor your automated outreach in real-time.
            </p>
        </div>

        <div
            class="glass-card px-5 py-3 flex items-center gap-3.5 border-white/5 bg-white/[0.02]"
        >
            <div class="relative flex h-3 w-3">
                <span
                    class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 {status.is_running
                        ? 'bg-purple-400'
                        : 'bg-zinc-600'}"
                ></span>
                <span
                    class="relative inline-flex rounded-full h-3 w-3 {status.is_running
                        ? 'bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]'
                        : 'bg-zinc-700'}"
                ></span>
            </div>
            <span
                class="font-bold tracking-[0.15em] text-xs {status.is_running
                    ? 'text-purple-400'
                    : 'text-zinc-500'}"
            >
                {status.is_running ? "ENGINE RUNNING" : "SYSTEM IDLE"}
            </span>
        </div>
    </header>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Niche -->
        <div
            class="glass-card p-6 flex flex-col justify-between group overflow-hidden relative"
        >
            <div
                class="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-all"
            ></div>
            <div>
                <div class="flex items-center justify-between mb-4">
                    <span
                        class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest"
                        >Active Niche</span
                    >
                    <svg
                        class="w-4 h-4 text-blue-500/50"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        /></svg
                    >
                </div>
                <p class="text-2xl font-bold truncate text-white">
                    {status.current_niche || "None"}
                </p>
            </div>
            <div class="mt-4 pt-4 border-t border-white/[0.03]">
                <span
                    class="text-[10px] text-zinc-500 font-medium uppercase truncate block"
                    >Target Area: {status.current_city}</span
                >
            </div>
        </div>

        <!-- Emails Found -->
        <div
            class="glass-card p-6 flex flex-col justify-between group overflow-hidden relative"
        >
            <div
                class="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-all"
            ></div>
            <div>
                <div class="flex items-center justify-between mb-4">
                    <span
                        class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest text-left"
                        >Leads Discovered</span
                    >
                    <svg
                        class="w-4 h-4 text-emerald-500/50"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                        /></svg
                    >
                </div>
                <p class="text-3xl font-bold text-emerald-400">
                    {status.emails_found}
                </p>
            </div>
            <div
                class="mt-4 pt-4 border-t border-white/[0.03] flex justify-between items-center"
            >
                <span class="text-[10px] text-zinc-500 font-medium uppercase"
                    >Bounce Protection</span
                >
                <span class="text-[10px] text-red-500 font-bold"
                    >-{status.emails_skipped}</span
                >
            </div>
        </div>

        <!-- Successfully Sent -->
        <div
            class="glass-card p-6 flex flex-col justify-between group overflow-hidden relative"
        >
            <div
                class="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/5 rounded-full blur-2xl group-hover:bg-purple-500/10 transition-all"
            ></div>
            <div>
                <div class="flex items-center justify-between mb-4">
                    <span
                        class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest"
                        >Delivered</span
                    >
                    <svg
                        class="w-4 h-4 text-purple-500/50"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                        /></svg
                    >
                </div>
                <p class="text-3xl font-bold text-purple-400">
                    {status.emails_sent}
                </p>
            </div>
            <div class="mt-4 pt-4 border-t border-white/[0.03]">
                <div
                    class="w-full bg-white/[0.02] h-1 rounded-full overflow-hidden"
                >
                    <div
                        class="bg-purple-500 h-full transition-all duration-1000"
                        style="width: {status.is_running ? '40%' : '0%'}"
                    ></div>
                </div>
            </div>
        </div>

        <!-- Queue -->
        <div
            class="glass-card p-6 flex flex-col justify-between group overflow-hidden relative"
        >
            <div
                class="absolute -right-4 -top-4 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl group-hover:bg-amber-500/10 transition-all"
            ></div>
            <div>
                <div class="flex items-center justify-between mb-4">
                    <span
                        class="text-[10px] font-bold text-zinc-500 uppercase tracking-widest text-left"
                        >Queue Buffer</span
                    >
                    <svg
                        class="w-4 h-4 text-amber-500/50"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        /></svg
                    >
                </div>
                <p class="text-3xl font-bold text-amber-500">
                    {status.queue_size}
                </p>
            </div>
            <div class="mt-4 pt-4 border-t border-white/[0.03]">
                <span class="text-[10px] text-zinc-500 font-medium uppercase"
                    >Smart Throttling: ON</span
                >
            </div>
        </div>
    </div>

    <!-- Main Section: Controls & Terminal -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Engine Controls -->
        <div class="lg:col-span-4 space-y-6">
            <div class="glass-card p-8 border-white/10 shadow-xl">
                <h3
                    class="text-lg font-bold text-white mb-6 flex items-center gap-2"
                >
                    <svg
                        class="w-5 h-5 text-purple-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37a1.724 1.724 0 002.572-1.065z"
                        /><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        /></svg
                    >
                    Engine Controls
                </h3>

                <div class="space-y-6">
                    <div>
                        <label
                            class="block text-[11px] font-bold text-zinc-500 uppercase tracking-widest mb-3"
                            for="niche"
                        >
                            Niche Targeted
                        </label>
                        <div class="relative">
                            <input
                                id="niche"
                                type="text"
                                bind:value={nicheInput}
                                disabled={status.is_running}
                                class="w-full input-glass py-3.5 pl-4 pr-10 text-sm font-medium focus:ring-2 focus:ring-purple-500/20"
                                placeholder="e.g. Roofers, HVAC, SaaS"
                            />
                            <div
                                class="absolute right-3.5 top-1/2 -translate-y-1/2 opacity-30"
                            >
                                <svg
                                    class="w-4 h-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                    /></svg
                                >
                            </div>
                        </div>
                    </div>

                    <div class="flex flex-col gap-3">
                        <button
                            on:click={startCampaign}
                            disabled={status.is_running}
                            class="btn-premium group disabled:opacity-50 disabled:translate-y-0 disabled:scale-100"
                        >
                            <svg
                                class="w-4 h-4 transition-transform group-hover:rotate-12"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2.5"
                                    d="M13 10V3L4 14h7v7l9-11h-7z"
                                /></svg
                            >
                            Ignite Output
                        </button>
                        <button
                            on:click={stopCampaign}
                            disabled={!status.is_running}
                            class="flex items-center justify-center gap-2 py-3 border border-red-500/20 text-red-400 font-bold rounded-xl hover:bg-red-500/5 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                            <svg
                                class="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2.5"
                                    d="M6 18L18 6M6 6l12 12"
                                /></svg
                            >
                            Terminate Loop
                        </button>
                    </div>
                </div>
            </div>

            <div
                class="glass-card p-6 bg-gradient-to-br from-purple-500/5 to-cyan-500/5 border-white/5"
            >
                <p
                    class="text-[11px] text-zinc-500 leading-relaxed text-center italic"
                >
                    All scrapes are fully DNS-verified to ensure zero bounce
                    rates on the Neon Database.
                </p>
            </div>
        </div>

        <!-- Terminal Output -->
        <div class="lg:col-span-8">
            <div
                class="glass-card flex flex-col h-[550px] shadow-2xl relative border-white/10 overflow-hidden"
            >
                <div
                    class="flex items-center justify-between px-6 py-4 bg-white/[0.03] border-b border-white/5"
                >
                    <div class="flex items-center gap-4">
                        <div class="flex gap-1.5">
                            <div
                                class="w-3 h-3 rounded-full bg-red-500/50"
                            ></div>
                            <div
                                class="w-3 h-3 rounded-full bg-amber-500/50"
                            ></div>
                            <div
                                class="w-3 h-3 rounded-full bg-emerald-500/50"
                            ></div>
                        </div>
                        <div class="h-4 w-[1px] bg-white/10 mx-1"></div>
                        <h2
                            class="text-xs font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-2"
                        >
                            System Output
                            {#if status.is_running}
                                <span
                                    class="text-[10px] text-purple-400 lowercase italic animate-pulse"
                                    >listening...</span
                                >
                            {/if}
                        </h2>
                    </div>
                    <button
                        on:click={() =>
                            (logs = ["- Terminal instance cleared -"])}
                        class="text-[10px] font-bold text-zinc-500 hover:text-white transition-colors uppercase tracking-widest px-3 py-1 rounded-md bg-white/5"
                    >
                        Clear
                    </button>
                </div>

                <div
                    class="flex-1 overflow-y-auto p-6 font-mono text-[13px] bg-[#050507]/40 no-scrollbar space-y-1.5"
                >
                    {#each logs as log, i}
                        <div
                            in:fly={{ y: 10, duration: 300, delay: 0 }}
                            class="flex gap-4 group hover:bg-white/[0.02]"
                        >
                            <span class="text-zinc-700 w-8 select-none"
                                >{i + 1}</span
                            >
                            <div
                                class="
                                break-words flex-1
                                {log.toLowerCase().includes('error')
                                    ? 'text-red-400 bg-red-400/5 px-1 rounded'
                                    : ''}
                                {log.includes('🚀') ||
                                log.includes('✅') ||
                                log.toLowerCase().includes('success')
                                    ? 'text-emerald-400'
                                    : ''}
                                {log.toLowerCase().includes('warning')
                                    ? 'text-amber-400 px-1 rounded bg-amber-400/5'
                                    : 'text-zinc-400'}
                            "
                            >
                                {log}
                            </div>
                        </div>
                    {/each}
                    {#if logs.length === 0}
                        <div
                            class="h-full flex flex-col items-center justify-center text-zinc-700 space-y-3"
                        >
                            <svg
                                class="w-12 h-12 opacity-10"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                /></svg
                            >
                            <p
                                class="text-xs font-bold uppercase tracking-[0.2em] opacity-30"
                            >
                                Awaiting Ignition
                            </p>
                        </div>
                    {/if}
                </div>

                <!-- Decoration -->
                <div
                    class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"
                ></div>
            </div>
        </div>
    </div>
</div>
