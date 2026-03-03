<script>
    import { onMount } from "svelte";

    let history = [];
    let loading = true;

    async function loadHistory() {
        loading = true;
        try {
            const res = await fetch("/api/history");
            const data = await res.json();
            if (Array.isArray(data)) history = data;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(() => loadHistory());
</script>

<header class="mb-8 flex justify-between items-center">
    <div>
        <h1 class="text-3xl font-bold tracking-tight mb-2">Sent History</h1>
        <p class="text-muted">
            A comprehensive log of all dispatched campaigns.
        </p>
    </div>
    <button
        on:click={loadHistory}
        class="bg-white/5 hover:bg-white/10 border border-white/10 px-5 py-2.5 rounded-lg flex items-center gap-2 transition-colors"
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
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            ></path></svg
        >
        Refresh Table
    </button>
</header>

<div class="glass-card rounded-xl overflow-hidden shadow-2xl">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr
                    class="bg-black/30 border-b border-white/5 text-xs uppercase tracking-wider text-muted font-semibold"
                >
                    <th class="py-4 px-6 font-medium">Recipient Target</th>
                    <th class="py-4 px-6 font-medium">Timestamp</th>
                    <th class="py-4 px-6 font-medium">Sender Alias</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
                {#if loading}
                    <tr
                        ><td colspan="3" class="py-8 text-center text-muted"
                            >Fetching records...</td
                        ></tr
                    >
                {:else if history.length === 0}
                    <tr
                        ><td colspan="3" class="py-12 text-center">
                            <div
                                class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/5 mb-3"
                            >
                                <svg
                                    class="w-6 h-6 text-gray-500"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                                    ></path></svg
                                >
                            </div>
                            <p class="text-muted">
                                No emails have been sent yet.
                            </p>
                        </td></tr
                    >
                {:else}
                    {#each history as item}
                        <tr class="hover:bg-white/[0.02] transition-colors">
                            <td
                                class="py-4 px-6 font-medium text-gray-200 flex items-center gap-3"
                            >
                                <div
                                    class="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold uppercase border border-blue-500/20"
                                >
                                    {item.email ? item.email.charAt(0) : "?"}
                                </div>
                                {item.email || "Unknown"}
                            </td>
                            <td class="py-4 px-6">
                                <span
                                    class="px-3 py-1 bg-white/5 rounded-md text-sm border border-white/5 text-gray-300"
                                >
                                    {item.date}
                                </span>
                            </td>
                            <td
                                class="py-4 px-6 text-muted text-sm flex items-center gap-2"
                            >
                                <span
                                    class="w-2 h-2 rounded-full bg-emerald-500"
                                ></span>
                                {item.sender}
                            </td>
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>
