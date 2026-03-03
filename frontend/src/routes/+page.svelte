<script>
    import { onMount, onDestroy } from "svelte";

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

    let pollInterval;
    let logsInterval;

    async function fetchStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            status = data;
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
                logs = [...logs, "Starting engine initialization..."];
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

<header class="mb-8 flex justify-between items-center">
    <div>
        <h1 class="text-3xl font-bold tracking-tight mb-2">
            Campaign Overview
        </h1>
        <p class="text-muted">
            Monitor and control your lead generation engine.
        </p>
    </div>
    <div class="glass-card px-4 py-2 flex items-center gap-3">
        <div class="relative flex h-3 w-3">
            <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 {status.is_running
                    ? 'bg-purple-400'
                    : 'bg-gray-500'}"
            ></span>
            <span
                class="relative inline-flex rounded-full h-3 w-3 {status.is_running
                    ? 'bg-purple-500'
                    : 'bg-gray-500'}"
            ></span>
        </div>
        <span
            class="font-bold tracking-widest text-sm {status.is_running
                ? 'text-purple-400'
                : 'text-gray-400'}"
        >
            {status.is_running ? "RUNNING" : "IDLE"}
        </span>
    </div>
</header>

<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div class="glass-card p-6 border-l-4 border-l-blue-500">
        <h3
            class="text-muted text-sm font-semibold uppercase tracking-wider mb-2"
        >
            Target Niche
        </h3>
        <p class="text-3xl font-bold">{status.current_niche || "None"}</p>
    </div>

    <div class="glass-card p-6 border-l-4 border-l-emerald-500 relative">
        <h3
            class="text-muted text-sm font-semibold uppercase tracking-wider mb-2"
        >
            Verified Emails Found
        </h3>
        <p class="text-3xl font-bold text-emerald-400">{status.emails_found}</p>
        <p class="text-xs text-muted mt-2 truncate">
            City: {status.current_city}
        </p>

        {#if status.emails_skipped > 0}
            <div class="absolute top-6 right-6 text-right">
                <span
                    class="text-[10px] font-semibold text-red-400 uppercase tracking-widest block mb-1"
                    >Prevented Bounces</span
                >
                <span class="text-xl font-bold text-red-500"
                    >{status.emails_skipped}</span
                >
            </div>
        {/if}
    </div>

    <div class="glass-card p-6 border-l-4 border-l-purple-500">
        <h3
            class="text-muted text-sm font-semibold uppercase tracking-wider mb-2"
        >
            Successfully Sent
        </h3>
        <p class="text-3xl font-bold text-purple-400">{status.emails_sent}</p>
    </div>

    <div class="glass-card p-6 border-l-4 border-l-amber-500">
        <h3
            class="text-muted text-sm font-semibold uppercase tracking-wider mb-2"
        >
            Queue Buffer
        </h3>
        <p class="text-3xl font-bold text-amber-400">{status.queue_size}</p>
        <p class="text-xs text-muted mt-2">Waiting to send securely</p>
    </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div
        class="glass-card p-8 lg:col-span-1 flex flex-col justify-center h-[500px]"
    >
        <h2 class="text-xl font-bold mb-6">Engine Controls</h2>

        <div class="mb-6">
            <label class="block text-sm font-semibold text-muted mb-2"
                >Target Niche Keyword</label
            >
            <input
                type="text"
                bind:value={nicheInput}
                disabled={status.is_running}
                class="w-full input-glass rounded-lg px-4 py-3"
                placeholder="e.g. plumbers, real estate agents"
            />
        </div>

        <div class="flex gap-4">
            <button
                on:click={startCampaign}
                disabled={status.is_running}
                class="flex-1 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-bold py-3 px-4 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <i class="fa-solid fa-play mr-2"></i> Ignite Engine
            </button>
            <button
                on:click={stopCampaign}
                disabled={!status.is_running}
                class="flex-1 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 text-white font-bold py-3 px-4 rounded-lg shadow-[0_0_15px_rgba(239,68,68,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <i class="fa-solid fa-stop mr-2"></i> Stop
            </button>
        </div>
    </div>

    <!-- Terminal -->
    <div class="glass-card lg:col-span-2 flex flex-col h-[500px]">
        <div
            class="flex items-center justify-between px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-black/20"
        >
            <h2 class="font-semibold flex items-center gap-2">
                <svg
                    class="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    ></path></svg
                >
                Live Output Stream
            </h2>
            <button
                on:click={() => (logs = ["Logs cleared"])}
                class="text-xs text-muted hover:text-white transition-colors"
                >Clear</button
            >
        </div>
        <div
            class="flex-1 overflow-y-auto p-6 font-mono text-sm bg-black/30 rounded-b-xl flex flex-col gap-2"
        >
            {#each logs as log}
                <div
                    class="
                    py-1 break-words
                    {log.toLowerCase().includes('error') ||
                    log.toLowerCase().includes('failed')
                        ? 'text-red-400'
                        : ''}
                    {log.toLowerCase().includes('success') ||
                    log.includes('✅') ||
                    log.includes('🚀')
                        ? 'text-emerald-400'
                        : ''}
                    {log.toLowerCase().includes('warning')
                        ? 'text-amber-400'
                        : ''}
                "
                >
                    {log}
                </div>
            {/each}
        </div>
    </div>
</div>
