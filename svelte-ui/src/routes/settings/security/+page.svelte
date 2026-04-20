<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Loader2, X } from 'lucide-svelte';

    // SecOps Vault
    let tenantApiKeys = $state<{id: string, provider_name: string, created_at: string}[]>([]);
    let newProviderName = $state('');
    let newApiKeyValue = $state('');
    let isLoadingKeys = $state(false);

    // P2P Mesh
    let p2pTargetIp = $state('');
    let p2pPort = $state(38001);
    let p2pMeshKey = $state('');
    let isSavingMesh = $state(false);

    // OCI Cloud Sandboxing
    let cloudHostIp = $state('');
    let cloudPemKey = $state('');
    let isSavingCloud = $state(false);

    onMount(async () => {
        await loadTenantKeys();
        await loadMeshSettings();
        await loadCloudSettings();
    });

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

    // --- P2P Mesh Features ---
    async function loadMeshSettings() {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/p2p_mesh`);
            if (res.ok) {
                const data = await res.json();
                p2pTargetIp = data.target_ip || '';
                p2pPort = data.port || 38001;
                p2pMeshKey = data.mesh_key || '';
            }
        } catch(e) {}
    }

    async function connectMesh() {
        if (!p2pTargetIp) { alert("Target IP cannot be empty."); return; }
        isSavingMesh = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/p2p_mesh`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ target_ip: p2pTargetIp, port: Number(p2pPort), mesh_key: p2pMeshKey })
            });
            if (res.ok) {
                alert("Sovereign Mesh P2P Handshake Successful! Connection secured.");
            } else {
                const data = await res.json();
                alert(data.message || "Failed to secure Mesh Handshake.");
            }
        } catch(e) {
            alert("Network Error during handshake.");
        } finally {
            isSavingMesh = false;
        }
    }

    // --- OCI Cloud Targeting ---
    async function loadCloudSettings() {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/cloud_target`);
            if (res.ok) {
                const data = await res.json();
                cloudHostIp = data.host_ip || '';
                cloudPemKey = data.pem_key || '';
            }
        } catch(e) {}
    }

    async function sealCloudCredentials() {
        if (!cloudHostIp || !cloudPemKey) { alert("OCI Host IP and PEM key are required."); return; }
        isSavingCloud = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/cloud_target`, {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ host_ip: cloudHostIp, pem_key: cloudPemKey })
            });
            if (res.ok) {
                alert("OCI Sandboxing Credentials sealed with AES-GCM.");
            } else {
                alert("Failed to seal OCI credentials.");
            }
        } catch(e) {
             alert("Error connecting to Vault.");
        } finally {
            isSavingCloud = false;
        }
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

        <!-- Row 2: Sandboxing and P2P Mesh -->
        <div class="grid grid-cols-12 gap-6 pb-12">
            <!-- Left: Dynamic Tunneling (P2P Mesh) -->
            <div class="col-span-12 xl:col-span-6 space-y-6">
                <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 relative overflow-hidden group hover:border-primary/20 transition-colors">
                    <div class="absolute -right-16 -top-16 w-48 h-48 rounded-full bg-primary/10 blur-[40px] opacity-70 group-hover:bg-primary/20 transition-all"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between mb-8 pb-6 border-b border-outline-variant/10">
                            <div class="flex items-center gap-4">
                                <div class="p-3 bg-primary-container/30 text-on-primary-container rounded-2xl shadow-inner border border-primary/10">
                                    <span class="material-symbols-outlined text-[24px]">cast_connected</span>
                                </div>
                                <div>
                                    <h3 class="text-xl font-bold text-on-surface">Dynamic Tunneling</h3>
                                    <p class="text-[11px] font-medium text-on-surface-variant mt-1 tracking-wider uppercase">Sovereign Mesh P2P</p>
                                </div>
                            </div>
                        </div>

                        <p class="text-xs text-on-surface-variant/80 mb-6 font-medium leading-relaxed">Establish a secure WebSocket/HTTP bridge with a remote Cibrid pair. Requires 2-way handshake.</p>
                        
                        <div class="space-y-4">
                            <div class="grid grid-cols-3 gap-4">
                                <div class="col-span-2 flex flex-col gap-1.5">
                                    <label class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/70">WSS IP Target</label>
                                    <input type="text" bind:value={p2pTargetIp} placeholder="192.168.1.100 or ngrok.io"
                                        class="w-full bg-surface-container-low border border-outline-variant/20 rounded-xl px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/30 outline-none focus:ring-2 focus:ring-primary font-mono" />
                                </div>
                                <div class="col-span-1 flex flex-col gap-1.5">
                                    <label class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/70">Port</label>
                                    <input type="number" bind:value={p2pPort} placeholder="38001"
                                        class="w-full bg-surface-container-low border border-outline-variant/20 rounded-xl px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/30 outline-none focus:ring-2 focus:ring-primary font-mono text-center" />
                                </div>
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/70">Security Mesh Key</label>
                                <input type="password" bind:value={p2pMeshKey} placeholder="msh-..."
                                    class="w-full bg-surface-container-low border border-outline-variant/20 rounded-xl px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/30 outline-none focus:ring-2 focus:ring-primary font-mono" />
                            </div>
                            
                            <button onclick={connectMesh} disabled={isSavingMesh}
                                class="mt-4 w-full py-3 bg-primary text-on-primary font-bold text-xs uppercase tracking-widest rounded-xl shadow-md hover:shadow-lg active:scale-95 transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2">
                                {#if isSavingMesh}
                                    <Loader2 class="w-4 h-4 animate-spin" /> Handshaking...
                                {:else}
                                    <span class="material-symbols-outlined text-[18px]">satellite_alt</span> Secure Handshake
                                {/if}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: OCI Sandboxing (Cloud Container Isolation) -->
            <div class="col-span-12 xl:col-span-6 space-y-6">
                <div class="bg-gradient-to-br from-[#1a140a] to-[#2b1b05] text-white p-8 rounded-3xl relative overflow-hidden shadow-lg border border-warning/20 group">
                    <div class="absolute -left-16 -bottom-16 w-56 h-56 rounded-full bg-warning/20 blur-[50px] opacity-40 group-hover:opacity-60 transition-opacity"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between mb-8 pb-6 border-b border-warning/10">
                            <div class="flex items-center gap-4">
                                <div class="p-3 bg-warning/20 text-[#f59e0b] rounded-2xl shadow-inner border border-warning/10">
                                    <span class="material-symbols-outlined text-[24px]">cloud_lock</span>
                                </div>
                                <div>
                                    <h3 class="text-xl font-bold text-white">OCI Sandboxing</h3>
                                    <p class="text-[11px] font-medium text-warning mt-1 tracking-wider uppercase">Cloud Container Isolation</p>
                                </div>
                            </div>
                        </div>

                        <div class="space-y-4">
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-warning/50">Oracle Cloud Instance IP</label>
                                <input type="text" bind:value={cloudHostIp} placeholder="129.150.xxx.xxx"
                                    class="w-full bg-black/30 border border-warning/20 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/20 outline-none focus:ring-2 focus:ring-warning font-mono" />
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-[10px] font-bold uppercase tracking-widest text-warning/50">Secret PEM Key (RSA)</label>
                                <textarea bind:value={cloudPemKey} placeholder="-----BEGIN RSA PRIVATE KEY-----..." rows="4"
                                    class="w-full bg-black/30 border border-warning/20 rounded-xl px-4 py-3 text-xs text-warning/80 placeholder:text-white/10 outline-none focus:ring-2 focus:ring-warning font-mono resize-y custom-scrollbar"></textarea>
                            </div>
                            
                            <button onclick={sealCloudCredentials} disabled={isSavingCloud}
                                class="mt-4 w-full py-3 bg-warning text-yellow-950 font-bold text-xs uppercase tracking-widest rounded-xl shadow-md hover:shadow-lg shadow-warning/20 active:scale-95 transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2">
                                {#if isSavingCloud}
                                    <Loader2 class="w-4 h-4 animate-spin text-yellow-950" /> Sealing...
                                {:else}
                                    <span class="material-symbols-outlined text-[18px]">enhanced_encryption</span> Seal OCI Sandbox
                                {/if}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
</style>
