<script>
    import { onMount } from "svelte";
    import { fade, fly } from "svelte/transition";

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

<div class="space-y-10">
    <header
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
    >
        <div>
            <h1
                class="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-2"
            >
                Dispatch Logs
            </h1>
            <p class="text-zinc-400 font-medium">
                Complete audit trail of all successful outreach deliveries.
            </p>
        </div>
        <button
            on:click={loadHistory}
            class="px-5 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-white font-bold hover:bg-white/[0.06] transition-all flex items-center justify-center gap-2"
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
            Sync Logs
        </button>
    </header>

    <div
        class="glass-card overflow-hidden shadow-2xl border-white/5 bg-white/[0.01]"
    >
        <div class="overflow-x-auto no-scrollbar">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-white/[0.02] border-b border-white/5">
                        <th
                            class="py-5 px-8 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500"
                            >Recipient Account</th
                        >
                        <th
                            class="py-5 px-8 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500"
                            >Delivery Hash / Type</th
                        >
                        <th
                            class="py-5 px-8 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500"
                            >Node Timestamp</th
                        >
                        <th
                            class="py-5 px-8 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500"
                            >Origin Sender</th
                        >
                    </tr>
                </thead>
                <tbody class="divide-y divide-white/[0.03]">
                    {#if loading}
                        <tr>
                            <td
                                colspan="4"
                                class="py-20 text-center font-bold text-zinc-600 uppercase tracking-widest italic"
                            >
                                Decrypting logs...
                            </td>
                        </tr>
                    {:else if history.length === 0}
                        <tr>
                            <td colspan="4" class="py-24 text-center">
                                <div
                                    class="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-white/[0.02] border border-white/5 mb-6 opacity-40"
                                >
                                    <svg
                                        class="w-8 h-8 text-zinc-500"
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
                                <p
                                    class="text-zinc-500 font-bold uppercase tracking-widest text-sm"
                                >
                                    Quiet Terminal: No Dispatches Yet
                                </p>
                            </td>
                        </tr>
                    {:else}
                        {#each history as item, i}
                            <tr
                                class="hover:bg-white/[0.02] transition-colors group"
                            >
                                <td class="py-5 px-8">
                                    <div class="flex items-center gap-4">
                                        <div
                                            class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-500/10 to-indigo-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-black uppercase shadow-lg group-hover:scale-110 transition-transform"
                                        >
                                            {item.email
                                                ? item.email.charAt(0)
                                                : "∅"}
                                        </div>
                                        <div class="flex flex-col">
                                            <span
                                                class="text-sm font-bold text-zinc-100"
                                                >{item.email || "System"}</span
                                            >
                                            <span
                                                class="text-[10px] font-bold text-zinc-600 uppercase tracking-widest"
                                                >External Lead</span
                                            >
                                        </div>
                                    </div>
                                </td>
                                <td class="py-5 px-8">
                                    <span
                                        class="px-3 py-1 bg-emerald-500/5 text-emerald-400 text-[10px] font-black rounded-lg border border-emerald-500/10 uppercase tracking-widest"
                                    >
                                        Delivered
                                    </span>
                                </td>
                                <td
                                    class="py-5 px-8 text-xs font-mono text-zinc-500"
                                >
                                    {item.date}
                                </td>
                                <td class="py-5 px-8">
                                    <div class="flex items-center gap-2.5">
                                        <div
                                            class="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.4)]"
                                        ></div>
                                        <span
                                            class="text-sm font-bold text-zinc-300"
                                            >{item.sender}</span
                                        >
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    {/if}
                </tbody>
            </table>
        </div>
    </div>
</div>
