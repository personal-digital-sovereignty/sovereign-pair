<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Loader2, X } from 'lucide-svelte';

    // Unified SecOps Vault
    let vaultSecrets = $state<{id: string, name: string, key_type: string, created_at: string}[]>([]);
    
    let newName = $state('');
    let newKeyType = $state('API_KEY');
    let newValue = $state('');
    let isLoading = $state(false);

    const KEY_TYPES = [
        'API_KEY',
        'SSH_KEY',
        'PEM_KEY',
        'CERTIFICATE',
        'URL',
        'IP_ADDRESS',
        'ENDPOINT'
    ];

    onMount(async () => {
        await loadVaultSecrets();
    });

    async function loadVaultSecrets() {
        isLoading = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/secops_vault`);
            if (res.ok) vaultSecrets = await res.json();
        } catch(e) { console.error("Failed to load SecOps Vault", e); }
        finally { isLoading = false; }
    }

    async function addSecret() {
        if (!newName || !newValue) { alert("Nome e Valor não podem estar vazios"); return; }
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/secops_vault`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: newName, key_type: newKeyType, secret_value: newValue })
            });
            if (res.ok) { 
                newName = ''; 
                newValue = ''; 
                alert("Segredo/Endpoint selado com sucesso."); 
                loadVaultSecrets(); 
            }
            else { alert("Erro ao salvar Key/Endpoint."); }
        } catch(e) { console.error("Failed to save Secret", e); }
    }

    async function deleteSecret(id: string) {
        if (!confirm("Obliteração Irreversível. Destruir entrada permanentemente?")) return;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/secops_vault/${id}`, { method: 'DELETE' });
            if (res.ok) loadVaultSecrets();
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
                    <span class="text-error font-extrabold">Security & Vault</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Unified SecOps Vault</h2>
                <p class="text-sm text-on-surface-variant mt-2 font-medium">Gestão centralizada de Chaves, Endpoints e Certificados com isolamento AES-GCM local.</p>
            </div>
            <div class="flex items-center gap-2 px-4 py-2 bg-error-container/10 text-error rounded-full border border-error/20">
                <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-error"></span>
                </span>
                <span class="text-[12px] font-bold tracking-tight">AES-GCM Encrypted at-rest</span>
            </div>
        </div>

        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left: Unified Injection -->
            <div class="col-span-12 xl:col-span-5 space-y-6">
                <div class="bg-gradient-to-br from-[#3b0a0a] to-[#1a0505] text-white p-8 rounded-3xl relative overflow-hidden shadow-lg border border-error/20">
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-8">
                            <span class="text-[10px] font-extrabold tracking-[0.25em] uppercase text-white/60">Asset Injection</span>
                            <div class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm">
                                <span class="material-symbols-outlined text-white/90">vpn_key</span>
                            </div>
                        </div>
                        <h4 class="text-2xl font-extrabold mb-2 leading-none">Register Asset</h4>
                        <p class="text-xs text-white/70 mb-6 font-medium leading-relaxed">Adicione chaves de API, IPs remotos, Certificados PEM ou URLs essenciais. Tudo centralizado.</p>

                        <div class="space-y-4">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-white/50">Asset Type</label>
                                <select bind:value={newKeyType} class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-white outline-none focus:ring-2 focus:ring-error font-mono appearance-none">
                                    {#each KEY_TYPES as kt}
                                        <option value={kt} class="bg-[#1a0505] text-white">{kt.replace('_', ' ')}</option>
                                    {/each}
                                </select>
                            </div>
                            
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-white/50">Asset Name / Identifier</label>
                                <input type="text" bind:value={newName} placeholder="Ex: OCI_PROD_IP ou OPENAI_KEY"
                                    class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-error font-mono" />
                            </div>
                            
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-white/50">Value / Payload</label>
                                {#if newKeyType === 'PEM_KEY' || newKeyType === 'CERTIFICATE'}
                                    <textarea bind:value={newValue} placeholder="-----BEGIN CERTIFICATE-----..." rows="4"
                                        class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-xs text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-error font-mono resize-y"></textarea>
                                {:else}
                                    <input type="password" bind:value={newValue} placeholder="sk-... ou 123.45.67.89"
                                        class="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-error font-mono" />
                                {/if}
                            </div>

                            <button onclick={addSecret}
                                class="w-full py-3 bg-error text-on-error font-bold text-xs uppercase tracking-widest rounded-xl shadow-md shadow-error/30 hover:shadow-lg active:scale-95 transition-all cursor-pointer flex items-center justify-center gap-2 mt-4">
                                <span class="material-symbols-outlined text-[18px]">lock</span>
                                Seal Asset
                            </button>
                        </div>
                    </div>
                    <div class="absolute -right-20 -bottom-20 w-64 h-64 rounded-full bg-error blur-[60px] opacity-10"></div>
                </div>
            </div>

            <!-- Right: Unified Vault Table -->
            <div class="col-span-12 xl:col-span-7 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 h-full flex flex-col">
                    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                        <div class="p-3 bg-error-container/30 rounded-2xl shadow-inner">
                            <span class="material-symbols-outlined text-error text-[28px]" style="font-variation-settings: 'FILL' 1;">shield_lock</span>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-on-surface">Registered Assets</h3>
                            <p class="text-[11px] font-medium text-on-surface-variant mt-1">{vaultSecrets.length} items securely sealed in the Vault.</p>
                        </div>
                    </div>

                    <div class="overflow-x-auto rounded-2xl border border-outline-variant/10 flex-1">
                        <table class="w-full text-left text-sm text-on-surface">
                            <thead class="text-[10px] uppercase bg-surface-container-high/50 text-on-surface-variant tracking-widest">
                                <tr>
                                    <th class="px-4 py-3.5 font-semibold">Type</th>
                                    <th class="px-4 py-3.5 font-semibold">Identifier</th>
                                    <th class="px-4 py-3.5 font-semibold">Cipher</th>
                                    <th class="px-4 py-3.5 font-semibold">Created</th>
                                    <th class="px-4 py-3.5 font-semibold text-center w-20">Destroy</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-outline-variant/10">
                                {#if isLoading}
                                <tr><td colspan="5" class="p-6 text-center"><Loader2 class="w-5 h-5 animate-spin mx-auto text-error"/></td></tr>
                                {:else if vaultSecrets.length === 0}
                                <tr><td colspan="5" class="p-6 text-center text-on-surface-variant italic text-xs">The vault is empty. No assets found.</td></tr>
                                {:else}
                                    {#each vaultSecrets as secret (secret.id)}
                                    <tr class="hover:bg-surface-container-low/50 transition-colors">
                                        <td class="px-4 py-3 font-mono text-[10px] tracking-wider font-bold text-error">
                                            <span class="bg-error/10 text-error px-2 py-1 rounded-md border border-error/20">
                                                {secret.key_type.replace('_', ' ')}
                                            </span>
                                        </td>
                                        <td class="px-4 py-3 font-mono font-bold text-on-surface">{secret.name}</td>
                                        <td class="px-4 py-3 font-mono text-on-surface-variant/70 text-xs">••••••••••••••••</td>
                                        <td class="px-4 py-3 text-on-surface-variant text-[11px]">{new Date(secret.created_at).toLocaleString()}</td>
                                        <td class="px-4 py-3 text-center">
                                            <button onclick={() => deleteSecret(secret.id)}
                                                class="text-on-surface-variant/50 hover:text-error transition-colors cursor-pointer p-1 rounded hover:bg-error-container/20" title="Obliterate">
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
