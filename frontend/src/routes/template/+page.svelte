<script>
    import { onMount } from "svelte";

    let settings = {
        subject: "",
        plain_text: "",
    };
    let htmlContent = "";

    let toastMsg = "";
    let toastErr = false;

    let aiPrompt = "";
    let apiKey = "";
    let isGenerating = false;

    async function loadData() {
        const tReq = fetch("/api/template").then((r) => r.json());
        const sReq = fetch("/api/settings").then((r) => r.json());

        try {
            const [tData, sData] = await Promise.all([tReq, sReq]);
            if (tData && tData.content) htmlContent = tData.content;
            if (sData) {
                if (sData.subject) settings.subject = sData.subject;
                if (sData.plain_text) settings.plain_text = sData.plain_text;
                if (sData.api_key) apiKey = sData.api_key;
            }
        } catch (e) {
            console.error(e);
        }
    }

    onMount(() => loadData());

    async function saveAll() {
        try {
            // Also save API key back to settings
            const settingsToSave = { ...settings, api_key: apiKey };
            const tRes = await fetch("/api/template", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: htmlContent }),
            });
            const sRes = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settingsToSave),
            });

            const tr = await tRes.json();
            const sr = await sRes.json();

            if (tr.success && sr.success) {
                showToast("Content Studio saved!");
            } else {
                showToast("Failed to save", true);
            }
        } catch (e) {
            console.error(e);
            showToast("Failed to save", true);
        }
    }

    function showToast(msg, error = false) {
        toastMsg = msg;
        toastErr = error;
        setTimeout(() => (toastMsg = ""), 3000);
    }

    async function generateTemplate() {
        if (!apiKey) {
            showToast("Gemini API Key is required to generate!", true);
            return;
        }
        if (!aiPrompt) {
            showToast("Please enter a prompt first.", true);
            return;
        }

        isGenerating = true;
        try {
            const res = await fetch("/api/generate-template", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: aiPrompt, api_key: apiKey }),
            });
            const data = await res.json();

            if (data.success) {
                settings.subject = data.subject || settings.subject;
                settings.plain_text = data.plain_text || settings.plain_text;
                htmlContent = data.html_body || htmlContent;
                showToast("✨ AI Magic successfully applied!");
            } else {
                showToast(data.error || "Generation failed", true);
            }
        } catch (e) {
            console.error(e);
            showToast("Network error generating template", true);
        } finally {
            isGenerating = false;
        }
    }
</script>

<header
    class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
>
    <div>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight mb-2">
            Content Studio
        </h1>
        <p class="text-sm text-muted">
            Variables: <code class="bg-white/5 px-1 rounded"
                >&#123;&#123;first_name&#125;&#125;</code
            >,
            <code class="bg-white/5 px-1 rounded"
                >&#123;&#123;city&#125;&#125;</code
            >,
            <code class="bg-white/5 px-1 rounded"
                >&#123;&#123;niche&#125;&#125;</code
            >,
            <code class="bg-white/5 px-1 rounded"
                >&#123;&#123;sender_name&#125;&#125;</code
            >
        </p>
    </div>
    <div class="w-full md:w-auto">
        <button
            on:click={saveAll}
            class="w-full md:w-auto bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-semibold px-6 py-2 rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all flex items-center justify-center gap-2"
        >
            <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                ></path></svg
            >
            Save Content
        </button>
    </div>
</header>

{#if toastMsg}
    <div
        class="fixed top-6 right-6 px-6 py-3 rounded-xl border {toastErr
            ? 'border-red-500 bg-red-500/10 text-red-400'
            : 'border-emerald-500 bg-emerald-500/10 text-emerald-400'} backdrop-blur-md z-50 transition-all flex items-center gap-3"
    >
        <span class="font-bold">{toastMsg}</span>
    </div>
{/if}

<!-- ✨ AI Magic Writer Section -->
<div
    class="glass-card p-4 sm:p-6 mb-6 border-l-4 border-l-purple-500 relative overflow-hidden"
>
    <div
        class="absolute -right-20 -top-20 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"
    ></div>

    <div
        class="flex items-center gap-2 mb-4 text-purple-400 font-bold tracking-wide uppercase text-xs sm:text-sm"
    >
        <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            ><path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
            ></path></svg
        >
        AI Magic Writer
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div class="md:col-span-3">
            <textarea
                bind:value={aiPrompt}
                class="w-full input-glass rounded-lg px-4 py-3 text-sm font-medium resize-none h-20 md:h-24"
                placeholder="E.g. 'Write a short, punchy 3-line email pitching our SEO services to plumbers. Offer a free audit.'"
            ></textarea>
        </div>
        <div class="md:col-span-1">
            <label
                class="block text-[10px] font-semibold text-muted mb-1 ml-1 uppercase"
                >Gemini Free API Key</label
            >
            <input
                bind:value={apiKey}
                type="password"
                class="w-full input-glass rounded-lg px-4 py-2 text-sm"
                placeholder="AIzaSy..."
            />
            <button
                on:click={generateTemplate}
                disabled={isGenerating}
                class="mt-2 w-full bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 disabled:text-gray-400 text-white font-bold py-3 md:py-2 px-4 rounded-lg transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(147,51,234,0.3)] text-sm"
            >
                {#if isGenerating}
                    <svg
                        class="animate-spin h-4 w-4 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        ><circle
                            class="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            stroke-width="4"
                        ></circle><path
                            class="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path></svg
                    >
                    Generating...
                {:else}
                    <svg
                        class="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M13 10V3L4 14h7v7l9-11h-7z"
                        ></path></svg
                    >
                    Generate Magic
                {/if}
            </button>
        </div>
    </div>
</div>

<div class="glass-card p-6 mb-6">
    <label
        class="block font-semibold text-muted uppercase tracking-wide text-sm mb-2"
        >Subject Line</label
    >
    <input
        bind:value={settings.subject}
        type="text"
        class="w-full input-glass rounded-lg px-4 py-3 text-lg font-medium"
        placeholder="Message for &#123;&#123;first_name&#125;&#125;"
    />
</div>

<div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
    <div
        class="glass-card p-0 flex flex-col h-[600px] border border-[rgba(255,255,255,0.1)]"
    >
        <div
            class="px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-black/20 flex gap-2 items-center"
        >
            <div class="w-3 h-3 rounded-full bg-red-500/50"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500/50"></div>
            <div class="w-3 h-3 rounded-full bg-green-500/50"></div>
            <span class="ml-2 font-semibold text-sm text-gray-300"
                >HTML Template (Primary)</span
            >
        </div>
        <textarea
            bind:value={htmlContent}
            class="flex-1 w-full bg-transparent text-gray-300 font-mono text-sm p-6 focus:outline-none resize-none"
            spellcheck="false"
            placeholder="<h1>Hello</h1>"
        ></textarea>
    </div>

    <div
        class="glass-card p-0 flex flex-col h-[600px] border border-[rgba(255,255,255,0.1)]"
    >
        <div
            class="px-6 py-4 border-b border-[rgba(255,255,255,0.08)] bg-black/20 flex gap-2 items-center"
        >
            <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6h16M4 12h16M4 18h7"
                ></path></svg
            >
            <span class="ml-2 font-semibold text-sm text-gray-300"
                >Plain Text (Fallback)</span
            >
        </div>
        <textarea
            bind:value={settings.plain_text}
            class="flex-1 w-full bg-transparent text-gray-300 font-mono text-sm p-6 focus:outline-none resize-none leading-relaxed"
            spellcheck="false"
            placeholder="Plain text fallback..."
        ></textarea>
    </div>
</div>
