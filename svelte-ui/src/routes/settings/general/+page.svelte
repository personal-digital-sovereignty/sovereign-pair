<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Download, Upload } from 'lucide-svelte';

    let aiSettings = $state({
        temperature: 0.7,
        top_k: 40,
        system_prompt: "",
        default_route: "/dashboard"
    });

    let corporaVaultPath = $state('/Vault/Offline_Corpus');
    let offlineCorpora = $state([
        { id: 'fineweb', name: 'FineWeb / FineWeb-Edu (Parquet)', size: '2.4 TB', active: false, priority: 1, type: 'HuggingFace' },
        { id: 'oscar', name: 'OSCAR Corpus (JSONL)', size: '850 GB', active: false, priority: 2, type: 'Multilingual' },
        { id: 'redpajama', name: 'RedPajama-Data-v2', size: '1.2 TB', active: false, priority: 3, type: 'Web Crawl' },
        { id: 'zim-wiki', name: 'Wikipedia Integral (Kiwix ZIM)', size: '98 GB', active: true, priority: 4, type: 'ZIM Dump' },
        { id: 'zim-stack', name: 'StackOverflow (Kiwix ZIM)', size: '145 GB', active: false, priority: 5, type: 'ZIM Dump' },
        { id: 'zim-pubmed', name: 'PubMed Central (Kiwix ZIM)', size: '320 GB', active: false, priority: 6, type: 'ZIM Dump' }
    ]);

    const PREDEFINED_PERSONAS = [
        { label: "1. The Sovereign Practitioner (Padrão)", prompt: "" },
        { label: "2. The Code Architect (Engenheiro Sênior)", prompt: "Você é O Arquiteto de Código. Forneça código impecável, idiomático e altamente documentado." },
        { label: "3. The Security Auditor (DevSecOps)", prompt: "Você é um Auditor de Segurança implacável." },
        { label: "4. The Financial Analyst (Quant)", prompt: "Você é um analista financeiro quantitativo." },
    ];

    let fileInput: HTMLInputElement | undefined = $state(undefined);

    onMount(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings`);
            if (res.ok) {
                const data = await res.json();
                if (data.temperature !== undefined) aiSettings.temperature = data.temperature;
                if (data.top_k !== undefined) aiSettings.top_k = data.top_k;
                if (data.system_prompt) aiSettings.system_prompt = data.system_prompt;
                if (data.default_route) aiSettings.default_route = data.default_route;
            }
        } catch(e) { console.error("Agent offline:", e); }

        try {
            const csRes = await fetch(`${API_BASE_URL}/v1/settings/cold_storage`);
            if (csRes.ok) {
                const data = await csRes.json();
                if (data.corporaVaultPath) corporaVaultPath = data.corporaVaultPath;
                if (data.offlineCorpora && data.offlineCorpora.length > 0) offlineCorpora = data.offlineCorpora;
            }
        } catch(e) {}
    });

    async function saveAiSettings() {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings`);
            let data = res.ok ? await res.json() : {};
            data.temperature = Number(aiSettings.temperature);
            data.top_k = Number(aiSettings.top_k);
            data.system_prompt = aiSettings.system_prompt;
            data.default_route = aiSettings.default_route;
            const postRes = await fetch(`${API_BASE_URL}/v1/settings`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (postRes.ok) alert('AI Core Settings Synchronized!');
        } catch(e) { alert('Failed to reach Sovereign Core.'); }
    }

    async function handleFileImport(e: Event) {
        const input = e.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target?.result as string;
            try {
                const payload = JSON.parse(content);
                const postRes = await fetch(`${API_BASE_URL}/v1/system/import_config`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (postRes.ok) { alert('Config imported! Restart the engine.'); location.reload(); }
            } catch (err) { alert('Invalid .cybrid file.'); }
        };
        reader.readAsText(file);
    }
</script>

<div class="p-8 h-full flex flex-col">
    <div class="w-full space-y-10 flex-1">
        <!-- Header & Breadcrumbs -->
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Settings</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-primary font-extrabold">General</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Identity & Preferences</h2>
            </div>
        </div>

        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left: Identity & Export -->
            <div class="col-span-12 xl:col-span-6 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-primary-fixed/50 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-primary text-[28px]" style="font-variation-settings: 'FILL' 1;">person</span>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-on-surface">Sovereign Identity</h3>
                            <p class="text-[11px] font-medium text-on-surface-variant mt-1">Master user preferences, startup page, and configuration backup.</p>
                        </div>
                    </div>
                    
                    <div class="space-y-6">
                        <!-- Landing Page -->
                        <div class="flex flex-col gap-1.5">
                            <label for="default_route" class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Startup Landing Page</label>
                            <select id="default_route" bind:value={aiSettings.default_route} onchange={() => saveAiSettings()}
                                class="w-full bg-surface-container border border-outline-variant/30 rounded-2xl px-4 py-3 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary shadow-sm cursor-pointer">
                                <option value="/dashboard">Home (Dashboard)</option>
                                <option value="/chat">Chat Interface</option>
                                <option value="/vault">Vault Explorer</option>
                                <option value="/projects">Projects (Kanban)</option>
                            </select>
                            <p class="text-[10px] text-on-surface-variant/70 font-medium">Sovereign Pair will boot directly to this page.</p>
                        </div>

                        <!-- System Prompt -->
                        <div class="flex flex-col gap-1.5">
                            <label for="system_prompt" class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">System Prompt (Persona)</label>
                            <textarea id="system_prompt" bind:value={aiSettings.system_prompt} rows="4" placeholder="Leave empty for default Sovereign Practitioner..."
                                class="w-full bg-surface-container-high border border-outline-variant/30 rounded-2xl p-4 text-sm font-medium text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary outline-none resize-none custom-scrollbar"></textarea>
                        </div>

                        <!-- Temperature -->
                        <div class="flex items-center gap-6">
                            <div class="flex-1 flex flex-col gap-1.5">
                                <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Temperature: {aiSettings.temperature}</label>
                                <input type="range" min="0" max="2" step="0.1" bind:value={aiSettings.temperature}
                                    class="w-full accent-primary" />
                            </div>
                            <div class="flex-1 flex flex-col gap-1.5">
                                <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Top-K: {aiSettings.top_k}</label>
                                <input type="range" min="1" max="100" step="1" bind:value={aiSettings.top_k}
                                    class="w-full accent-primary" />
                            </div>
                        </div>

                        <button onclick={saveAiSettings}
                            class="w-full py-3 bg-gradient-to-br from-[#001360] to-[#002395] text-white text-xs font-bold uppercase tracking-widest rounded-xl shadow-md shadow-primary/20 hover:shadow-lg active:scale-95 transition-all cursor-pointer">
                            Save Settings
                        </button>
                    </div>
                </div>
            </div>

            <!-- Right: Export/Import -->
            <div class="col-span-12 xl:col-span-6 space-y-6">
                <div class="bg-gradient-to-br from-[#001360] to-[#002395] text-white p-8 rounded-3xl relative overflow-hidden shadow-lg shadow-primary/10 border border-primary/20">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Cortex Continuity</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                <span class="material-symbols-outlined text-white/90">cloud_sync</span>
                            </div>
                        </div>
                        <h4 class="text-2xl font-extrabold mb-2 leading-none">Backup & Restore</h4>
                        <p class="text-xs text-white/70 mb-8 font-medium leading-relaxed">A `.cybrid` file contains fully encrypted O.S State (Workspaces, Mesh Keys, Preferences) to instantly synchronize a new node.</p>
                        
                        <input type="file" bind:this={fileInput} accept=".cybrid" class="hidden" onchange={handleFileImport} />

                        <div class="flex gap-3">
                            <button onclick={() => fileInput?.click()} class="flex-1 py-3 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors flex items-center justify-center gap-2 cursor-pointer border border-white/20 text-sm font-bold">
                                <Upload class="w-4 h-4" /> Import
                            </button>
                            <a href="{API_BASE_URL}/v1/system/export_config" target="_blank" class="flex-1 py-3 rounded-xl bg-white text-[#001360] hover:bg-white/90 transition-colors flex items-center justify-center gap-2 cursor-pointer text-sm font-bold shadow-md">
                                <Download class="w-4 h-4" /> Export .cybrid
                            </a>
                        </div>
                    </div>
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-primary-fixed blur-[60px] opacity-30"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
</style>
