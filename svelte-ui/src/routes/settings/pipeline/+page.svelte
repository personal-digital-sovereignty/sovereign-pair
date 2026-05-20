<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Loader2 } from 'lucide-svelte';

    // Scrape Limits
    let scrapeLimits = $state({ max_links_chat: 6, max_links_deep_research: 7, max_links_per_search: 7 });
    let isSavingScrape = $state(false);

    // Mesh Nodes
    let activeNodes = $state<{id: string, name?: string, url?: string, role?: string, location?: string}[]>([]);

    onMount(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/scrape_limits`);
            if (res.ok) scrapeLimits = await res.json();
        } catch(e) {}

        try {
            const meshRes = await fetch(`${API_BASE_URL}/v1/settings/ollama_clusters`);
            if (meshRes.ok) {
                const data = await meshRes.json();
                if (data.clusters && data.clusters.length > 0) {
                    activeNodes = data.clusters.map((c: any) => ({
                        id: c.id, name: c.name || c.url, url: c.url, role: 'Cognitive Node',
                        location: c.url?.includes('localhost') || c.url?.includes('127.0.0.1') ? 'Local' : 'Cloud'
                    }));
                }
            }
        } catch(e) {}
    });

    async function saveScrapeLimits() {
        isSavingScrape = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/scrape_limits`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scrapeLimits)
            });
            if (res.ok) { const data = await res.json(); if (data.limits) scrapeLimits = data.limits; }
        } catch(e) {}
        finally { isSavingScrape = false; }
    }

    const SCRAPE_FIELDS = [
        { key: 'max_links_chat' as const, label: 'Chat (Tool Call)', desc: 'Links scraped per tool-call in Chat conversations', icon: 'chat' },
        { key: 'max_links_deep_research' as const, label: 'Deep Research', desc: 'Links scraped per query in the Trainer pipeline', icon: 'travel_explore' },
        { key: 'max_links_per_search' as const, label: 'Per Search Engine', desc: 'Links returned per search engine query (Yahoo/Brave/SearXNG)', icon: 'search' },
    ];
</script>

<div class="p-8 h-full flex flex-col">
    <div class="w-full space-y-10 flex-1">
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Settings</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-primary font-extrabold">Pipeline</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Pipeline & Mesh Config</h2>
            </div>
        </div>

        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left: Scrape Limits -->
            <div class="col-span-12 xl:col-span-7 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-tertiary-container/30 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-on-tertiary-container text-[28px]" style="font-variation-settings: 'FILL' 1;">bolt</span>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-on-surface">Scrape Intensity Control</h3>
                            <p class="text-[11px] font-medium text-on-surface-variant mt-1">Tune how many links the system scrapes per context. Lower = faster, less VRAM. Range: 1-30.</p>
                        </div>
                    </div>

                    <div class="space-y-6">
                        {#each SCRAPE_FIELDS as field}
                        <div class="flex items-center justify-between p-5 bg-surface-container-low rounded-2xl group border border-outline-variant/5 hover:border-outline-variant/20 transition-colors">
                            <div class="flex items-center gap-4">
                                <div class="w-10 h-10 rounded-xl bg-surface-container flex items-center justify-center text-on-surface-variant border border-outline-variant/10">
                                    <span class="material-symbols-outlined text-[20px]">{field.icon}</span>
                                </div>
                                <div class="flex flex-col">
                                    <span class="text-[13px] font-bold text-on-surface">{field.label}</span>
                                    <span class="text-[10px] text-on-surface-variant mt-0.5">{field.desc}</span>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <input type="number" min="1" max="30" bind:value={scrapeLimits[field.key]}
                                    class="w-16 bg-surface-container border border-outline-variant/30 rounded-xl px-3 py-2 text-sm text-on-surface text-center outline-none focus:ring-2 focus:ring-primary font-mono font-bold" />
                            </div>
                        </div>
                        {/each}

                        <button onclick={saveScrapeLimits} disabled={isSavingScrape}
                            class="w-full py-3 bg-gradient-to-br from-[#001360] to-[#002395] text-white text-xs font-bold uppercase tracking-widest rounded-xl shadow-md shadow-primary/20 hover:shadow-lg active:scale-95 transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2">
                            {#if isSavingScrape}<Loader2 class="w-4 h-4 animate-spin" />{:else}<span class="material-symbols-outlined text-[18px]">save</span>{/if}
                            Save Limits
                        </button>
                    </div>
                </div>
            </div>

            <!-- Right: Mesh Status -->
            <div class="col-span-12 xl:col-span-5 space-y-6">
                <div class="bg-gradient-to-br from-[#001360] to-[#002395] text-white p-8 rounded-3xl relative overflow-hidden shadow-lg shadow-primary/10 border border-primary/20">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Mesh Network</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                <span class="material-symbols-outlined text-white/90">dns</span>
                            </div>
                        </div>
                        <h4 class="text-5xl font-extrabold mb-2 leading-none font-mono">{activeNodes.length}</h4>
                        <p class="text-xs font-bold text-white/70 mb-8 uppercase tracking-widest">{activeNodes.length > 0 ? 'Active Nodes' : 'No Nodes Connected'}</p>

                        <div class="space-y-3">
                            {#each activeNodes as node}
                            <div class="flex justify-between items-center text-[11px] border-b border-white/10 pb-3 font-mono">
                                <span class="text-white/60">{node.name}</span>
                                <span class="font-bold text-white px-2 py-0.5 bg-white/10 rounded">{node.location}</span>
                            </div>
                            {:else}
                            <div class="text-[11px] text-white/40 text-center py-4 border border-dashed border-white/20 rounded-xl">
                                Fallback: localhost:11434
                            </div>
                            {/each}
                        </div>
                    </div>
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-primary-fixed blur-[60px] opacity-30"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
</style>
