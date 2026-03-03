<script>
    import { onMount } from "svelte";
    import { fade, fly, scale } from "svelte/transition";

    let accounts = [];
    let loading = true;
    let toastMsg = "";
    let toastErr = false;

    async function fetchAccounts() {
        try {
            const res = await fetch("/api/accounts");
            accounts = await res.json();
            if (accounts.error) accounts = [];
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        fetchAccounts();
    });

    function addAccount() {
        accounts = [
            ...accounts,
            {
                email: "",
                app_password: "",
                sender_name: "Lead Gen Pro",
                daily_limit: 150,
            },
        ];
    }

    function removeAccount(index) {
        accounts.splice(index, 1);
        accounts = [...accounts];
    }

    async function saveAccounts() {
        try {
            const res = await fetch("/api/accounts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(accounts),
            });
            const data = await res.json();
            if (data.success) {
                showToast("Vault synchronized successfully!");
            } else {
                showToast("Synchronization failure.", true);
            }
        } catch (e) {
            console.error(e);
            showToast("Network error.", true);
        }
    }

    function showToast(msg, error = false) {
        toastMsg = msg;
        toastErr = error;
        setTimeout(() => (toastMsg = ""), 3000);
    }
</script>

<div class="space-y-10">
    <header
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
    >
        <div>
            <h1
                class="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-2"
            >
                Sender Profiles
            </h1>
            <p class="text-zinc-400 font-medium">
                Configure your rotating SMTP delivery network.
            </p>
        </div>
        <div class="flex flex-wrap gap-3 w-full md:w-auto">
            <button
                on:click={addAccount}
                class="flex-1 md:flex-none px-5 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-white font-bold hover:bg-white/[0.06] transition-all flex items-center justify-center gap-2"
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
                        d="M12 4v16m8-8H4"
                    /></svg
                >
                Add Account
            </button>
            <button
                on:click={saveAccounts}
                class="btn-premium flex-1 md:flex-none"
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
                        d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                    /></svg
                >
                Sync Changes
            </button>
        </div>
    </header>

    {#if toastMsg}
        <div
            in:fly={{ y: -20 }}
            out:fade
            class="fixed top-6 right-6 px-6 py-3.5 rounded-2xl border {toastErr
                ? 'border-red-500 bg-red-500/10 text-red-400'
                : 'border-purple-500 bg-purple-500/10 text-purple-400'} backdrop-blur-2xl z-[100] shadow-2xl flex items-center gap-3"
        >
            <div
                class="w-2 h-2 rounded-full {toastErr
                    ? 'bg-red-500'
                    : 'bg-purple-500'} animate-pulse"
            ></div>
            <span class="font-bold text-sm tracking-wide">{toastMsg}</span>
        </div>
    {/if}

    {#if loading}
        <div
            class="glass-card p-20 text-center text-zinc-500 font-bold uppercase tracking-[0.2em] italic"
        >
            Initializing Vault...
        </div>
    {:else if accounts.length === 0}
        <div
            class="glass-card p-16 text-center flex flex-col items-center justify-center border-dashed border-white/5 bg-transparent"
            in:fade
        >
            <div
                class="w-20 h-20 rounded-3xl bg-white/[0.02] border border-white/5 flex items-center justify-center text-3xl text-zinc-600 mb-6"
            >
                <svg
                    class="w-10 h-10 opacity-20"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    ></path></svg
                >
            </div>
            <h3 class="text-2xl font-bold text-white mb-3">
                No Sending Assets
            </h3>
            <p class="text-zinc-500 max-w-sm mx-auto mb-8 font-medium">
                Link an SMTP profile (Gmail + App Password) to power your
                engine's outreach capabilities.
            </p>
            <button
                on:click={addAccount}
                class="text-purple-400 font-bold hover:text-purple-300 flex items-center gap-2 group"
            >
                Provision first slot
                <svg
                    class="w-4 h-4 group-hover:translate-x-1 transition-transform"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2.5"
                        d="M14 5l7 7m0 0l-7 7m7-7H3"
                    /></svg
                >
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {#each accounts as acc, i (i)}
                <div
                    in:scale={{ duration: 300, start: 0.95 }}
                    class="glass-card relative overflow-hidden group border-white/5 hover:border-purple-500/30"
                >
                    <button
                        on:click={() => removeAccount(i)}
                        class="absolute top-5 right-5 w-9 h-9 flex items-center justify-center rounded-xl bg-red-500/5 text-red-500/40 opacity-0 group-hover:opacity-100 transition-all hover:bg-red-500 hover:text-white border border-red-500/10"
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
                            ></path></svg
                        >
                    </button>

                    <div class="p-8 pb-10">
                        <div class="flex items-center gap-4 mb-8">
                            <div
                                class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-500/10 to-indigo-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 font-black text-xl shadow-lg shadow-purple-500/5"
                            >
                                {i + 1}
                            </div>
                            <div>
                                <div
                                    class="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em] mb-0.5"
                                >
                                    Hardware Slot
                                </div>
                                <div
                                    class="text-sm font-bold text-zinc-100 uppercase tracking-widest"
                                >
                                    {acc.sender_name || "PENDING"}
                                </div>
                            </div>
                        </div>

                        <div class="space-y-6">
                            <div class="space-y-2">
                                <label
                                    class="block text-[10px] font-bold text-zinc-600 uppercase tracking-widest ml-1"
                                    >SMTP Endpoint</label
                                >
                                <input
                                    type="email"
                                    bind:value={acc.email}
                                    class="w-full input-glass py-3 px-4 text-sm font-medium"
                                    placeholder="sender@gmail.com"
                                />
                            </div>
                            <div class="space-y-2">
                                <label
                                    class="block text-[10px] font-bold text-zinc-600 uppercase tracking-widest ml-1"
                                    >App Secret</label
                                >
                                <input
                                    type="password"
                                    bind:value={acc.app_password}
                                    class="w-full input-glass py-3 px-4 text-sm font-medium tracking-[0.3em]"
                                    placeholder="••••••••••••••••"
                                />
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="space-y-2">
                                    <label
                                        class="block text-[10px] font-bold text-zinc-600 uppercase tracking-widest ml-1 text-left"
                                        >Display Alias</label
                                    >
                                    <input
                                        type="text"
                                        bind:value={acc.sender_name}
                                        class="w-full input-glass py-3 px-4 text-xs font-bold"
                                        placeholder="Founder"
                                    />
                                </div>
                                <div class="space-y-2">
                                    <label
                                        class="block text-[10px] font-bold text-zinc-600 uppercase tracking-widest ml-1 text-left"
                                        >Safety Limit</label
                                    >
                                    <input
                                        type="number"
                                        bind:value={acc.daily_limit}
                                        class="w-full input-glass py-3 px-4 text-xs font-bold"
                                        placeholder="150"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Interactive bottom status -->
                    <div
                        class="bg-white/[0.03] px-8 py-3.5 flex items-center justify-between border-t border-white/5"
                    >
                        <div class="flex items-center gap-2">
                            <div
                                class="w-1.5 h-1.5 rounded-full bg-emerald-500"
                            ></div>
                            <span
                                class="text-[10px] font-black text-emerald-500/80 uppercase tracking-tighter"
                                >Ready to rotate</span
                            >
                        </div>
                        <svg
                            class="w-3 h-3 text-zinc-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="3"
                                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                            /></svg
                        >
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>
