<script>
    import { onMount } from "svelte";
    import { fade, fly, slide } from "svelte/transition";

    let subject = "";
    let htmlContent = "";
    let plainText = "";
    let aiPrompt = "";
    let apiKey = "";

    let isGenerating = false;
    let toastMsg = "";

    async function loadTemplate() {
        try {
            const res = await fetch("/api/template");
            const data = await res.json();
            subject = data.subject || "";
            htmlContent = data.html_template || "";
            plainText = data.plain_template || "";
        } catch (e) {
            console.error(e);
        }
    }

    onMount(() => {
        loadTemplate();
        apiKey = localStorage.getItem("gemini_api_key") || "";
    });

    async function saveAll() {
        try {
            const res = await fetch("/api/template", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    subject,
                    html_template: htmlContent,
                    plain_template: plainText,
                }),
            });
            const data = await res.json();
            if (data.success) {
                showToast("Template locked in!");
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function generateTemplate() {
        if (!aiPrompt) return;
        if (!apiKey) {
            alert("Please provide a Gemini API Key first.");
            return;
        }

        localStorage.setItem("gemini_api_key", apiKey);
        isGenerating = true;
        try {
            const res = await fetch("/api/ai/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: aiPrompt, api_key: apiKey }),
            });
            const data = await res.json();
            if (data.success) {
                subject = data.subject;
                htmlContent = data.html;
                plainText = data.plain;
                showToast("Magic writer finished!");
            } else {
                alert(data.error);
            }
        } catch (e) {
            console.error(e);
        } finally {
            isGenerating = false;
        }
    }

    function showToast(msg) {
        toastMsg = msg;
        setTimeout(() => (toastMsg = ""), 3000);
    }
</script>

<div class="space-y-10">
    <!-- Header -->
    <header
        class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6"
    >
        <div>
            <h1
                class="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-2"
            >
                Content Studio
            </h1>
            <div
                class="flex flex-wrap gap-2 text-zinc-500 font-medium text-sm items-center"
            >
                <span>Variables:</span>
                <code
                    class="px-2 py-0.5 bg-white/[0.03] border border-white/5 rounded-md text-purple-400"
                    >{"{{first_name}}"}</code
                >
                <code
                    class="px-2 py-0.5 bg-white/[0.03] border border-white/5 rounded-md text-emerald-400"
                    >{"{{city}}"}</code
                >
                <code
                    class="px-2 py-0.5 bg-white/[0.03] border border-white/5 rounded-md text-cyan-400"
                    >{"{{niche}}"}</code
                >
            </div>
        </div>
        <div class="w-full md:w-auto">
            <button
                on:click={saveAll}
                class="btn-premium w-full md:w-auto px-8"
            >
                <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2.5"
                        d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                    ></path></svg
                >
                Publish Campaign
            </button>
        </div>
    </header>

    {#if toastMsg}
        <div
            fixed
            in:fly={{ y: -20 }}
            out:fade
            class="fixed top-6 right-6 px-6 py-3.5 rounded-2xl border border-emerald-500 bg-emerald-500/10 text-emerald-400 backdrop-blur-2xl z-[100] shadow-2xl flex items-center gap-3"
        >
            <div
                class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"
            ></div>
            <span class="font-bold text-sm tracking-wide">{toastMsg}</span>
        </div>
    {/if}

    <!-- ✨ AI Magic Writer Section -->
    <div
        class="glass-card overflow-hidden relative border-purple-500/10 shadow-2xl shadow-purple-500/5"
    >
        <div
            class="absolute -right-20 -top-20 w-80 h-80 bg-purple-500/5 rounded-full blur-[100px] pointer-events-none"
        ></div>

        <div
            class="px-8 py-5 border-b border-white/5 flex items-center justify-between bg-white/[0.01]"
        >
            <div class="flex items-center gap-3">
                <div class="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                    <svg
                        class="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M13 10V3L4 14h7v7l9-11h-7z"
                        /></svg
                    >
                </div>
                <h3
                    class="text-xs font-black text-zinc-400 uppercase tracking-[0.2em]"
                >
                    GenAI Magic Writer
                </h3>
            </div>
            {#if isGenerating}
                <div
                    class="flex items-center gap-2 text-[10px] text-purple-400 font-bold uppercase tracking-wider animate-pulse"
                >
                    <div class="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                    Thinking...
                </div>
            {/if}
        </div>

        <div class="p-8 grid grid-cols-1 md:grid-cols-12 gap-8">
            <div class="md:col-span-8 flex flex-col gap-4">
                <textarea
                    bind:value={aiPrompt}
                    class="w-full h-28 input-glass px-5 py-4 text-sm font-medium resize-none placeholder:text-zinc-600"
                    placeholder="E.g. 'Write a short, punchy 3-line email pitching our SEO services to plumbers. Offer a free audit.'"
                ></textarea>
                <div
                    class="flex items-center gap-4 text-[10px] text-zinc-500 font-bold uppercase tracking-widest px-1"
                >
                    <div class="flex items-center gap-1.5">
                        <svg
                            class="w-3.5 h-3.5 text-emerald-500"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            ><path
                                fill-rule="evenodd"
                                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                clip-rule="evenodd"
                            /></svg
                        >
                        Variables Supported
                    </div>
                </div>
            </div>
            <div class="md:col-span-4 flex flex-col gap-4">
                <div class="space-y-2">
                    <label
                        class="block text-[10px] font-bold text-zinc-600 uppercase tracking-widest ml-1"
                        >Gemini Pro API Key</label
                    >
                    <input
                        bind:value={apiKey}
                        type="password"
                        class="w-full input-glass px-4 py-3 text-xs tracking-widest font-bold"
                        placeholder="AIzaSy..."
                    />
                </div>
                <button
                    on:click={generateTemplate}
                    disabled={isGenerating}
                    class="btn-premium w-full mt-auto disabled:opacity-50"
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
                        Synthesizing...
                    {:else}
                        Generate Template
                    {/if}
                </button>
            </div>
        </div>
    </div>

    <!-- ✍️ Manual Editor Section -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Main Subject & HTML -->
        <div class="lg:col-span-12 space-y-8">
            <div class="glass-card shadow-xl overflow-hidden min-h-[400px]">
                <div class="px-8 py-4 bg-white/[0.02] border-b border-white/5">
                    <input
                        bind:value={subject}
                        class="w-full bg-transparent border-none text-xl sm:text-2xl font-bold text-white focus:outline-none placeholder:text-zinc-700"
                        placeholder="Campaign Subject Line..."
                    />
                </div>

                <div class="flex flex-col md:flex-row h-full">
                    <!-- HTML Editor -->
                    <div class="flex-1 p-8 border-r border-white/5 space-y-4">
                        <div class="flex items-center justify-between mb-2">
                            <h4
                                class="text-xs font-black text-zinc-500 uppercase tracking-[0.2em]"
                            >
                                HTML Blueprint
                            </h4>
                            <div class="flex gap-1.5 opacity-20">
                                <div
                                    class="w-2 h-2 rounded-full bg-white"
                                ></div>
                                <div
                                    class="w-2 h-2 rounded-full bg-white"
                                ></div>
                            </div>
                        </div>
                        <textarea
                            bind:value={htmlContent}
                            class="w-full h-80 input-glass p-6 text-sm font-mono leading-relaxed"
                            placeholder="<h1>Hello {{ first_name }}</h1>..."
                        ></textarea>
                    </div>

                    <!-- Plain Text Backstop -->
                    <div class="flex-1 p-8 bg-black/20 space-y-4">
                        <div class="flex items-center justify-between mb-2">
                            <h4
                                class="text-xs font-black text-zinc-500 uppercase tracking-[0.2em]"
                            >
                                Plain Text Backstop
                            </h4>
                            <svg
                                class="w-3.5 h-3.5 text-zinc-600"
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
                        <textarea
                            bind:value={plainText}
                            class="w-full h-80 input-glass p-6 text-sm font-medium leading-relaxed bg-black/40 border-none"
                            placeholder="Hey {{
                                first_name,
                            }}, I saw you're in {{ city }}..."
                        ></textarea>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
