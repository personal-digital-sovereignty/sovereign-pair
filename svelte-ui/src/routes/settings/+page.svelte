<script lang="ts">
    import { ChevronDown, Server, Cpu, Shield, User, GlobeLock, Cloud, Download, Upload } from 'lucide-svelte';

    let expandedCard = $state<string | null>('mesh');

    function toggleCard(cardId: string) {
        expandedCard = expandedCard === cardId ? null : cardId;
    }

    // Mock profiles based on Mesh Router engine
    let activeNodes = [
        { id: '1', hostname: 'oracle-a1-max', role: 'The Doctor', hardware: '24GB RAM, ARM64', location: 'Cloud' },
        { id: '2', hostname: 'ryzen-local-alpha', role: 'The Coder (Sandbox)', hardware: '32GB RAM, Ryzen 9', location: 'Local Network' }
    ];

    let fileInput: HTMLInputElement | undefined = $state(undefined);

    async function handleFileImport(e: Event) {
        const input = e.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) return;
        
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target?.result as string;
            try {
                const res = await fetch('http://localhost:38001/v1/system/import_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'text/plain' },
                    body: content
                });
                if (res.ok) {
                    alert('Sovereign Cortex successfully imported. The system and mesh nodes are synchronized.');
                    window.location.reload();
                } else {
                    alert('Failed to absorb Cybrid Cortex. File may be corrupted.');
                }
            } catch (err) {
                console.error(err);
                alert('P2P Hub offline or unreachable.');
            }
        };
        reader.readAsText(file);
    }
</script>

<div class="h-full w-full max-w-4xl mx-auto p-4 md:p-8 flex flex-col gap-6 overflow-y-auto">
    
    <!-- Settings Header -->
    <header class="flex flex-col gap-1 mb-2">
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-surface-50">Sovereign Settings</h1>
        <p class="text-surface-400 text-sm">Configure Identity, Telemetry, and Mesh Sandboxes</p>
    </header>

    <!-- Material/iOS Style Cards -->
    <main class="flex flex-col gap-4 pb-12">
        
        <!-- CARD 1: Identity -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-surface-700/50 overflow-hidden shadow-lg transition-all duration-300">
            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('identity')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-primary-500/20 text-primary-400 rounded-lg">
                        <User class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-surface-100 text-lg">Sovereign Identity</h2>
                        <p class="text-sm text-surface-400">Master user, Pin Codes, UI Preferences</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'identity' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'identity'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-4">
                <p class="text-sm text-surface-400">Manage your local Identity parameters and export your entire Sovereign configuration to securely roam between multiple nodes.</p>
                
                <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 flex flex-col gap-3">
                    <h3 class="text-surface-200 font-bold text-sm tracking-widest uppercase mb-1">Cortex Continuity (Backup)</h3>
                    <p class="text-xs text-surface-400 mb-2">A file with the `.cybrid` extension contains fully encrypted O.S State (Global Workspaces, Mesh Keys, Node Preferences) to instantly synchronize a new machine.</p>
                    
                    <input type="file" bind:this={fileInput} accept=".cybrid" class="hidden" onchange={handleFileImport} />

                    <div class="flex gap-2 w-full">
                        <button onclick={() => fileInput?.click()} class="flex-1 py-2 rounded-lg bg-surface-700 text-surface-200 hover:bg-surface-600 transition-colors flex items-center justify-center gap-2 cursor-pointer border border-surface-600">
                            <Upload class="w-4 h-4" />
                            <span class="text-sm">Import Config</span>
                        </button>
                        <a href="http://localhost:38001/v1/system/export_config" target="_blank" class="flex-1 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-500 transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                            <Download class="w-4 h-4" />
                            <span class="text-sm">Export .cybrid</span>
                        </a>
                    </div>
                </div>
            </div>
            {/if}
        </section>

        <!-- CARD 2: Sovereign Mesh (Highlight as requested) -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-primary-500/30 overflow-hidden shadow-[0_0_20px_rgba(16,185,129,0.05)] transition-all duration-300 relative">
            <!-- Active Glow Indicator -->
            <div class="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 blur-[50px] pointer-events-none"></div>

            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('mesh')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 bg-primary-500/20 text-primary-400 rounded-lg">
                        <Server class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-primary-50 text-lg">Sovereign Mesh P2P</h2>
                        <p class="text-sm text-primary-400/80">Active Tunnels & Hardware Profiles</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'mesh' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'mesh'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30 flex flex-col gap-4">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {#each activeNodes as node}
                    <div class="bg-surface-800 p-4 rounded-xl border border-surface-700 hover:border-surface-600 transition-colors">
                        <div class="flex items-start justify-between mb-3">
                            <span class="font-semibold text-surface-200">{node.hostname}</span>
                            <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-surface-700 text-surface-300">{node.location}</span>
                        </div>
                        <div class="flex flex-col gap-2 text-sm text-surface-400">
                            <div class="flex items-center gap-2">
                                <Shield class="w-4 h-4 text-emerald-500" />
                                <span>{node.role}</span>
                            </div>
                            <div class="flex items-center gap-2">
                                <Cpu class="w-4 h-4 text-emerald-500" />
                                <span>{node.hardware}</span>
                            </div>
                        </div>
                    </div>
                    {/each}
                </div>

                <button class="mt-2 w-full py-3 rounded-xl border border-dashed border-surface-600 text-surface-300 flex items-center justify-center gap-2 hover:bg-surface-800 transition-colors cursor-pointer">
                    <GlobeLock class="w-4 h-4" />
                    <span>Establish New P2P Tunnel</span>
                </button>
            </div>
            {/if}
        </section>

        <!-- CARD 3: Fallback Cloud OCI -->
        <section class="bg-surface-800/80 backdrop-blur-md rounded-2xl border border-surface-700/50 overflow-hidden shadow-lg transition-all duration-300">
            <button class="w-full flex items-center justify-between p-5 text-left hover:bg-surface-700/30 cursor-pointer" onclick={() => toggleCard('cloud')}>
                <div class="flex items-center gap-4">
                    <div class="p-2 border border-surface-600/50 text-surface-400 rounded-lg">
                        <Cloud class="w-6 h-6" />
                    </div>
                    <div>
                        <h2 class="font-semibold text-surface-100 text-lg">Cloud Sandboxing (OCI)</h2>
                        <p class="text-sm text-surface-400">Oracle credentials & Default Execution Pipeline</p>
                    </div>
                </div>
                <ChevronDown class="w-5 h-5 text-surface-500 transition-transform duration-300 transform {expandedCard === 'cloud' ? 'rotate-180' : ''}" />
            </button>
            {#if expandedCard === 'cloud'}
            <div class="p-5 border-t border-surface-700/50 bg-surface-900/30">
                <p class="text-sm text-surface-400 mb-4">Fallback Execution node when Sovereign Mesh is unavailable.</p>
                <div class="flex flex-col gap-3">
                    <input type="text" placeholder="OCI Public IP" class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2 text-surface-200 outline-none focus:border-primary-500 transition-colors">
                    <input type="password" placeholder="OCI Secret Key Path" class="w-full bg-surface-800 border border-surface-600 rounded-lg px-4 py-2 text-surface-200 outline-none focus:border-primary-500 transition-colors">
                </div>
            </div>
            {/if}
        </section>

    </main>
</div>
