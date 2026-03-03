<script>
    import { onMount } from 'svelte';

    let accounts = [];
    let loading = true;
    let toastMsg = '';
    let toastErr = false;

    async function fetchAccounts() {
        try {
            const res = await fetch('/api/accounts');
            accounts = await res.json();
            if(accounts.error) accounts = [];
        } catch(e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        fetchAccounts();
    });

    function addAccount() {
        accounts = [...accounts, {
            email: '',
            app_password: '',
            sender_name: 'Lead Generation Specialist',
            daily_limit: 150
        }];
    }

    function removeAccount(index) {
        accounts.splice(index, 1);
        accounts = [...accounts];
    }

    async function saveAccounts() {
        try {
            const res = await fetch('/api/accounts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(accounts)
            });
            const data = await res.json();
            if(data.success) {
                showToast('Accounts saved securely!');
            } else {
                showToast('Save failed.', true);
            }
        } catch(e) {
            console.error(e);
            showToast('Save failed.', true);
        }
    }

    function showToast(msg, error=false) {
        toastMsg = msg;
        toastErr = error;
        setTimeout(() => toastMsg = '', 3000);
    }
</script>

<header class="mb-8 flex justify-between items-center">
    <div>
        <h1 class="text-3xl font-bold tracking-tight mb-2">Setup Accounts</h1>
        <p class="text-muted">Manage your rotating SMTP sender profiles.</p>
    </div>
    <div class="flex gap-3">
        <button on:click={addAccount} class="bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.1)] border border-[rgba(255,255,255,0.1)] text-white px-4 py-2 rounded-lg transition-colors">
            <i class="fa-solid fa-plus mr-2"></i> Add Account
        </button>
        <button on:click={saveAccounts} class="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-400 hover:to-blue-400 text-white font-semibold px-6 py-2 rounded-lg shadow-[0_0_15px_rgba(107,70,193,0.3)] transition-all">
            <i class="fa-solid fa-floppy-disk mr-2"></i> Save Changes
        </button>
    </div>
</header>

{#if toastMsg}
    <div class="fixed top-6 right-6 px-6 py-3 rounded-xl border {toastErr ? 'border-red-500 bg-red-500/10 text-red-400' : 'border-emerald-500 bg-emerald-500/10 text-emerald-400'} backdrop-blur-md z-50 transition-all flex items-center gap-3">
        <span class="font-bold">{toastMsg}</span>
    </div>
{/if}

{#if loading}
    <div class="glass-card p-12 text-center text-muted">Loading accounts...</div>
{:else if accounts.length === 0}
    <div class="glass-card p-12 text-center flex flex-col items-center justify-center">
        <div class="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-2xl text-muted mb-4">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
        </div>
        <h3 class="text-xl font-bold mb-2">No Sending Accounts</h3>
        <p class="text-muted mb-6">Add an SMTP account (like a Gmail with an App Password) to begin outreach.</p>
        <button on:click={addAccount} class="text-purple-400 hover:text-purple-300 font-semibold underline underline-offset-4">Add your first account</button>
    </div>
{:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each accounts as acc, i}
            <div class="glass-card relative overflow-hidden group">
                <button on:click={() => removeAccount(i)} title="Remove" class="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-lg bg-red-500/10 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500 hover:text-white border border-red-500/20">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
                <div class="p-6">
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-500/20 to-purple-500/20 border border-[rgba(255,255,255,0.1)] flex items-center justify-center text-purple-400">
                            <span class="font-bold text-lg">{i + 1}</span>
                        </div>
                        <div class="text-sm font-semibold tracking-wider uppercase text-muted">Account Slot</div>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-muted mb-1 ml-1 uppercase">Email Address</label>
                            <input type="email" bind:value={acc.email} class="w-full input-glass rounded-lg px-4 py-2 text-sm" placeholder="sender@gmail.com">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-muted mb-1 ml-1 uppercase">App Password</label>
                            <input type="password" bind:value={acc.app_password} class="w-full input-glass rounded-lg px-4 py-2 text-sm" placeholder="••••••••••••••••">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-muted mb-1 ml-1 uppercase">Display Name</label>
                            <input type="text" bind:value={acc.sender_name} class="w-full input-glass rounded-lg px-4 py-2 text-sm" placeholder="John Doe">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-muted mb-1 ml-1 uppercase">Daily Limit</label>
                            <input type="number" bind:value={acc.daily_limit} class="w-full input-glass rounded-lg px-4 py-2 text-sm" placeholder="150">
                        </div>
                    </div>
                </div>
                <!-- Status bar decoration -->
                <div class="h-1 w-full bg-gradient-to-r from-purple-500 to-blue-500 opacity-50"></div>
            </div>
        {/each}
    </div>
{/if}
