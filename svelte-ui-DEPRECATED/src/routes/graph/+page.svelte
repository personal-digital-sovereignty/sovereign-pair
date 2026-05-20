<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

    import { onMount } from 'svelte';
    import CognitiveGraph from '$lib/components/CognitiveGraph.svelte';
    import { Search, Play, Minus, Plus, Cpu, Activity, Network, Database } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte';

    let nodes = $state([]);
    let links = $state([]);
    let loading = $state(true);
    let error = $state('');

    let graphDepth = $state(5);
    let dataFlowHistory = $state(100);
    let isPlaying = $state(false);
    let progressTimer: any;

    function togglePlay() {
        if (isPlaying) {
            isPlaying = false;
            clearInterval(progressTimer);
        } else {
            isPlaying = true;
            if (Number(dataFlowHistory) >= 100) dataFlowHistory = 0;
            progressTimer = setInterval(() => {
                dataFlowHistory = Number(dataFlowHistory) + 1;
                if (Number(dataFlowHistory) >= 100) {
                    dataFlowHistory = 100;
                    isPlaying = false;
                    clearInterval(progressTimer);
                }
            }, 30);
        }
    }

    async function loadGraph() {
        loading = true;
        error = '';
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || '1';
            const res = await fetch(`${API_BASE_URL}/v1/vault/graph?workspace_id=${ws_id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if(res.ok) {
                const data = await res.json();
                nodes = (data.nodes || []).filter((n: any) => n.type !== 'folder' && n.type !== 'directory');
                const validNodeIds = new Set(nodes.map((n: any) => n.id));
                links = (data.links || []).filter((l: any) => validNodeIds.has(l.source) && validNodeIds.has(l.target));
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

<style>
  /* Premium Glassmorphic Sliders - Cross-Browser (WebKit + Firefox) */
  :global(.premium-slider) {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    background: transparent;
    cursor: pointer;
  }
  :global(.premium-slider:focus) {
    outline: none;
  }
  
  /* WebKit Track */
  :global(.premium-slider::-webkit-slider-runnable-track) {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
  }
  /* Firefox Track */
  :global(.premium-slider::-moz-range-track) {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
  }

  /* WebKit Thumb */
  :global(.premium-slider::-webkit-slider-thumb) {
    -webkit-appearance: none;
    appearance: none;
    height: 24px;
    width: 24px;
    background-color: transparent;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij4gPHBhdGggZD0iTTEyIDEyTDQgNE0xMiAxMkwyMCA2TTEyIDEyTDE1IDIxIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4gPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iOCIgZmlsbD0iIzNiODJmNiIgc3Ryb2tlPSIjMGYxNzJhIiBzdHJva2Utd2lkdGg9IjMiIC8+PC9zdmc+");
    background-repeat: no-repeat;
    background-position: center;
    border-radius: 50%;
    margin-top: -9px;
    border: none;
    box-shadow: none;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  /* Firefox Thumb */
  :global(.premium-slider::-moz-range-thumb) {
    appearance: none;
    height: 24px;
    width: 24px;
    background-color: transparent;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij4gPHBhdGggZD0iTTEyIDEyTDQgNE0xMiAxMkwyMCA2TTEyIDEyTDE1IDIxIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4gPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iOCIgZmlsbD0iIzNiODJmNiIgc3Ryb2tlPSIjMGYxNzJhIiBzdHJva2Utd2lkdGg9IjMiIC8+PC9zdmc+");
    background-repeat: no-repeat;
    background-position: center;
    border-radius: 50%;
    border: none;
    box-shadow: none;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  /* WebKit Thumb Emerald Override */
  :global(.slider-emerald::-webkit-slider-thumb) {
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij4gPHBhdGggZD0iTTEyIDEyTDQgNE0xMiAxMkwyMCA2TTEyIDEyTDE1IDIxIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4gPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iOCIgZmlsbD0iIzEwYjk4MSIgc3Ryb2tlPSIjMGYxNzJhIiBzdHJva2Utd2lkdGg9IjMiIC8+PC9zdmc+");
  }
  /* Firefox Thumb Emerald Override */
  :global(.slider-emerald::-moz-range-thumb) {
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij4gPHBhdGggZD0iTTEyIDEyTDQgNE0xMiAxMkwyMCA2TTEyIDEyTDE1IDIxIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4gPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iOCIgZmlsbD0iIzEwYjk4MSIgc3Ryb2tlPSIjMGYxNzJhIiBzdHJva2Utd2lkdGg9IjMiIC8+PC9zdmc+");
  }

  /* Hover States */
  :global(.premium-slider::-webkit-slider-thumb:hover) { transform: scale(1.3) rotate(15deg); }
  :global(.premium-slider::-moz-range-thumb:hover) { transform: scale(1.3) rotate(15deg); }
</style>

<div class="h-full w-full flex flex-col pb-2">
  <div class="bg-slate-900 rounded-2xl shadow-xl border border-slate-700 flex-1 flex flex-col relative overflow-hidden h-full">
    <!-- Inner Header: Title and Search -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 shrink-0 z-10 gap-4 bg-slate-800/80 backdrop-blur-sm border-b border-slate-700/50">
      <h2 class="text-2xl font-semibold text-white">Sovereign Cognitive Graph</h2>
      <div class="relative w-full sm:w-72">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input class="w-full pl-9 pr-4 py-2 bg-slate-800/50 border border-slate-600 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-slate-400 shadow-sm" placeholder="Search Sovereign Network..." type="text"/>
      </div>
    </div>

    <!-- Graph Area -->
    <div class="flex-1 flex flex-col items-center justify-center relative min-h-0">
      {#if loading}
          <div class="flex flex-col items-center gap-4 text-slate-400">
              <Cpu class="w-10 h-10 animate-pulse text-blue-500" />
              <span class="font-medium text-sm tracking-widest uppercase">Initializing Neural Link...</span>
          </div>
      {:else if error}
          <div class="flex flex-col items-center gap-4 text-red-400 bg-slate-800/50 p-8 rounded-2xl border border-red-900/50 shadow-2xl backdrop-blur-md">
              <div class="p-4 bg-red-950/50 rounded-full">
                <Activity class="w-10 h-10 animate-pulse" />
              </div>
              <div class="flex flex-col items-center text-center">
                  <span class="font-bold text-lg text-white mb-1">Neural Disconnect</span>
                  <span class="text-sm opacity-80">{error}</span>
              </div>
          </div>
      {:else}
          <CognitiveGraph {nodes} {links} {graphDepth} {dataFlowHistory} onNodeClick={handleNodeClick} />
      {/if}
    </div>

    <!-- Bottom Controls Bar -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-slate-800/80 backdrop-blur-xl border border-slate-600/50 px-8 py-5 rounded-2xl flex items-center gap-8 shadow-[0_8px_30px_rgb(0,0,0,0.5)] z-20 pointer-events-auto w-[650px] max-w-[90%]">
      <!-- Data Flow History Slider -->
      <div class="flex-1 flex items-center gap-4">
        <button onclick={togglePlay} class="w-10 h-10 shrink-0 flex items-center justify-center rounded-full bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-emerald-500/20 hover:text-emerald-400 hover:border-emerald-500/50 transition-all">
          <Play class="w-4 h-4 ml-0.5 {isPlaying ? 'text-emerald-400' : ''}" />
        </button>
        <div class="flex-1 flex flex-col gap-2">
          <div class="flex justify-between items-end px-1">
            <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Data Flow History</span>
            <span class="text-[10px] text-emerald-400 font-bold">{dataFlowHistory}%</span>
          </div>
          <input bind:value={dataFlowHistory} class="premium-slider slider-emerald w-full" type="range" min="0" max="100" />
        </div>
      </div>
      
      <!-- Vertical Divider -->
      <div class="w-px h-12 bg-slate-600/50 shrink-0"></div>
      
      <!-- Graph Depth Controls -->
      <div class="flex-1 flex items-center gap-4">
        <button onclick={() => graphDepth = Math.max(1, Number(graphDepth) - 1)} class="w-8 h-8 shrink-0 flex items-center justify-center rounded-full bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-blue-500/20 hover:text-blue-400 hover:border-blue-500/50 transition-all">
          <Minus class="w-4 h-4" />
        </button>
        <div class="flex-1 flex flex-col gap-2">
          <div class="flex justify-between items-end px-1">
             <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Graph Depth</span>
             <span class="text-[10px] text-blue-400 font-bold">{graphDepth == 5 ? 'Max (5)' : graphDepth}</span>
          </div>
          <input bind:value={graphDepth} class="premium-slider w-full" type="range" min="1" max="5" />
        </div>
        <button onclick={() => graphDepth = Math.min(5, Number(graphDepth) + 1)} class="w-8 h-8 shrink-0 flex items-center justify-center rounded-full bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-blue-500/20 hover:text-blue-400 hover:border-blue-500/50 transition-all">
          <Plus class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</div>
