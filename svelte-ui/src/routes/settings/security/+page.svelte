<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Loader2, X } from 'lucide-svelte';

    let tenantApiKeys = $state<{id: string, provider_name: string, created_at: string}[]>([]);
    let newProviderName = $state('');
    let newApiKeyValue = $state('');
    let isLoadingKeys = $state(false);

    onMount(async () => { await loadTenantKeys(); });

    async function loadTenantKeys() {
        isLoadingKeys = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys`);
            if (res.ok) tenantApiKeys = await res.json();
        } catch(e) { console.error("Failed to load SecOps Vault", e); }
        finally { isLoadingKeys = false; }
    }

    async function addTenantKey() {
        if (!newProviderName || !newApiKeyValue) { alert("Providers e Chaves não podem estar vazios"); return; }
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ provider_name: newProviderName, api_key_value: newApiKeyValue })
            });
            if (res.ok) { newProviderName = ''; newApiKeyValue = ''; alert("API Key selada com AES-GCM no SecOps Vault."); loadTenantKeys(); }
            else { alert("Erro ao salvar Key."); }
        } catch(e) { console.error("Failed to save Key", e); }
    }

    async function deleteTenantKey(id: string) {
        if (!confirm("Obliteração Irreversível. Destruir API Key permanentemente?")) return;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/tenant_keys/${id}`, { method: 'DELETE' });
            if (res.ok) loadTenantKeys();
        } catch(e) {}
    }
</script>

<div class="p-8 h-full flex flex-col">
    <div class="w-full space-y-10 flex-1">
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Settings</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-error font-extrabold">Security</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Sovereign SecOps Vault</h2>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 bg-error-container/10 text-error rounded-full border border-error/20">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-error"></span>
                </span>
                <span class="text-[12px] font-bold tracking-tight">AES-GCM Encrypted</span>
            </div>
        </div>

        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left: Key Injection -->
            <div class="col-span-12 xl:col-span-5 space-y-6">
                <div class="bg-gradient-to-br from-[#3b0a0a] to-[#1a0505] text-white p-8 rounded-3xl relative overflow-hidden shadow-lg border border-error/20">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Key Injection</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                <span class="material-symbols-outlined text-white/90">key</span>
                            </div>
                        </div>
                        <h4 class="text-2xl font-extrabold mb-2 leading-none">Inject API Key</h4>
                        <p class="text-xs text-white/70 mb-6 font-medium leading-relaxed">Keys (TMDB, OpenAI, Anthropic, IGDB) são criptografadas at-rest com AES-GCM no SQLite local. Nenhuma transita em texto plano.</p>

                        <div class="space-y-3">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-white/50">Provider</label>
                                <input type="text" bind:value={newProviderName} placeholder="TMDB_API_KEY"
                                    class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-error font-mono" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-white/50">Secret Payload</label>
                                <input type="password" bind:value={newApiKeyValue} placeholder="sk-..."
                                    class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-error font-mono" />
                            </div>
                            <button onclick={addTenantKey}
                                class="w-full py-3 bg-error text-on-error font-bold text-xs uppercase tracking-widest rounded-xl shadow-md shadow-error/30 hover:shadow-lg active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-2 mt-2">
                                <span class="material-symbols-outlined text-[18px]">lock</span>
                                Seal & Encrypt
                            </button>
                        </div>
                    </div>
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-error blur-[60px] opacity-10"></div>
                </div>
            </div>

            <!-- Right: Vault Table -->
            <div class="col-span-12 xl:col-span-7 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10">
                    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-error-container/30 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-error text-[28px]" style="font-variation-settings: 'FILL' 1;">shield_lock</span>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-on-surface">Registered Keys</h3>
                            <p class="text-[11px] font-medium text-on-surface-variant mt-1">{tenantApiKeys.length} keys sealed in the local vault.</p>
                        </div>
                    </div>

                    <div class="overflow-x-auto rounded-2xl border border-outline-variant/10">
                        <table class="w-full text-left text-sm text-on-surface">
                            <thead class="text-[10px] uppercase bg-surface-container-high/50 text-on-surface-variant tracking-widest">
                                <tr>
                                    <th class="px-4 py-3.5 font-semibold">Provider</th>
                                    <th class="px-4 py-3.5 font-semibold">Cipher</th>
                                    <th class="px-4 py-3.5 font-semibold">Created</th>
                                    <th class="px-4 py-3.5 font-semibold text-center w-20">Destroy</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-outline-variant/10">
                                {#if isLoadingKeys}
                                <tr><td colspan="4" class="p-6 text-center"><Loader2 class="w-5 h-5 animate-spin mx-auto text-error"/></td></tr>
                                {:else if tenantApiKeys.length === 0}
                                <tr><td colspan="4" class="p-6 text-center text-on-surface-variant italic text-xs">The vault is empty. No keys found.</td></tr>
                                {:else}
                                    {#each tenantApiKeys as key (key.id)}
                                    <tr class="hover:bg-surface-container-low/50 transition-colors">
                                        <td class="px-4 py-3 font-mono font-bold text-error">{key.provider_name}</td>
                                        <td class="px-4 py-3 font-mono text-on-surface-variant">••••••••••••••••</td>
                                        <td class="px-4 py-3 text-on-surface-variant text-xs">{new Date(key.created_at).toLocaleString()}</td>
                                        <td class="px-4 py-3 text-center">
                                            <button onclick={() => deleteTenantKey(key.id)}
                                                class="text-on-surface-variant/50 hover:text-error transition-colors cursor-pointer p-1 rounded hover:bg-error-container/20" title="Obliterate Key">
                                                <X class="w-4 h-4" />
                                            </button>
                                        </td>
                                    </tr>
                                    {/each}
                                {/if}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
</style>
