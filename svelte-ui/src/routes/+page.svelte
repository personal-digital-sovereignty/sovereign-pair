<script lang="ts">
    import { onMount } from 'svelte';
    import { Activity, Cpu, Network, Database } from 'lucide-svelte';
    import CognitiveGraph from '$lib/components/CognitiveGraph.svelte';
    import { globalState } from '$lib/state.svelte';

    let nodes = $state([]);
    let links = $state([]);
    let loading = $state(true);
    let error = $state('');

    async function loadGraph() {
        loading = true;
        error = '';
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || '1';
            const res = await fetch(`http://localhost:38001/v1/vault/graph?workspace_id=${ws_id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if(res.ok) {
                const data = await res.json();
                nodes = data.nodes || [];
                links = data.links || [];
            } else {
                error = 'Failed to synchronize Sensus Cognitive Graph.';
            }
        } catch(e) {
            console.error(e);
            error = 'Sovereign Core offline or unreachable.';
        }
        loading = false;
    }

    onMount(() => {
        loadGraph();
    });

    $effect(() => {
        if (globalState.activeWorkspaceId) {
            loadGraph();
        }
    });

    function handleNodeClick(node: any) {
        console.log("Navigating to Node:", node);
        if (node.type === 'file' && node.path) {
            globalState.vault.activeDocumentId = node.path;
            window.location.href = '/vault';
        }
    }
</script>

<div class="flex flex-col h-full bg-slate-50 w-full overflow-hidden">
    <!-- Header -->
    <header class="h-16 border-b border-slate-200 bg-white flex items-center px-6 shrink-0 justify-between shadow-sm z-10">
        <div class="flex items-center gap-3">
            <div class="bg-blue-600/10 p-2 rounded-lg">
                <Network class="w-5 h-5 text-blue-600" />
            </div>
            <h1 class="text-xl font-bold tracking-tight text-slate-800">Control Hub</h1>
            <span class="px-2.5 py-1 bg-slate-100 text-slate-600 text-[10px] uppercase tracking-widest font-bold rounded-full ml-2 border border-slate-200">Cognitive Graph</span>
        </div>
        
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-5 text-sm font-semibold text-slate-600 bg-slate-50 px-5 py-2 rounded-xl border border-slate-200 shadow-inner">
                <div class="flex items-center gap-2">
                    <Database class="w-4 h-4 text-emerald-500" />
                    <span class="text-slate-900">{nodes.length}</span> Nodes
                </div>
                <div class="w-px h-4 bg-slate-300"></div>
                <div class="flex items-center gap-2">
                    <Activity class="w-4 h-4 text-blue-500" />
                    <span class="text-slate-900">{links.length}</span> Synapses
                </div>
            </div>
        </div>
    </header>

    <!-- Main Graph Area -->
    <main class="flex-1 relative p-6 flex flex-col">
        <div class="w-full flex-1 rounded-2xl overflow-hidden shadow-2xl border border-slate-800/50 bg-[#0f172a] relative flex items-center justify-center">
            {#if loading}
                <div class="flex flex-col items-center gap-4 text-slate-400">
                    <Cpu class="w-10 h-10 animate-pulse text-blue-500" />
                    <span class="font-medium text-sm tracking-widest uppercase">Initializing Neural Link...</span>
                </div>
            {:else if error}
                <div class="flex flex-col items-center gap-2 text-red-400 p-6 bg-red-950/30 rounded-xl border border-red-900/50">
                    <Activity class="w-8 h-8" />
                    <span class="font-medium">{error}</span>
                </div>
            {:else}
                <CognitiveGraph {nodes} {links} onNodeClick={handleNodeClick} />
                
                <!-- Floating Controls Overlay -->
                <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-slate-800/80 backdrop-blur-xl border border-slate-600/50 px-8 py-5 rounded-2xl flex items-center gap-8 shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
                    <div class="flex flex-col gap-3">
                        <label for="graph-depth" class="text-xs font-bold text-slate-400 uppercase tracking-widest flex justify-between">
                            <span>Graph Depth</span>
                            <span class="text-blue-400">Max</span>
                        </label>
                        <input id="graph-depth" type="range" class="w-48 accent-blue-500 cursor-pointer" min="1" max="5" value="5" />
                    </div>
                    
                    <div class="w-px h-10 bg-slate-600/50"></div>
                    
                    <div class="flex flex-col gap-3">
                        <label for="data-history" class="text-xs font-bold text-slate-400 uppercase tracking-widest flex justify-between">
                            <span>Data Flow History</span>
                            <span class="text-emerald-400">All Time</span>
                        </label>
                        <input id="data-history" type="range" class="w-48 accent-emerald-500 cursor-pointer" min="0" max="100" value="100" />
                    </div>
                </div>
            {/if}
        </div>
    </main>
</div>
