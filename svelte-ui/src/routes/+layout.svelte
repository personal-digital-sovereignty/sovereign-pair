<script lang="ts">
  import '../app.css';
  import { globalState, toggleSidebar, setSidebarWidth } from '$lib/state.svelte.js';
  import { telemetryState, connectTelemetry, disconnectTelemetry } from '$lib/telemetry.svelte';
  import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, CloudOff, Activity, Database } from 'lucide-svelte';
  import { page } from '$app/state';
  import { onMount, onDestroy } from 'svelte';

  let { children } = $props();

  onMount(() => {
    connectTelemetry();
    fetchWorkspaces();
  });

  async function fetchWorkspaces() {
      try {
          const res = await fetch('http://localhost:38001/v1/workspaces', { headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` } });
          if (res.ok) {
              const data = await res.json();
              globalState.workspaces = data.workspaces || [];
              if (globalState.workspaces.length === 0) {
                  globalState.workspaces = [{ id: 'mesh_roaming', name: 'Sovereign Mesh Roaming' }];
              }
              // If current mapped workspace isn't in list, select the first
              const exists = globalState.workspaces.find((w: any) => w.id === globalState.activeWorkspaceId);
              if (!exists) {
                  globalState.activeWorkspaceId = globalState.workspaces[0].id;
                  globalState.activeWorkspaceName = globalState.workspaces[0].name;
              }
          }
      } catch (e) {
          console.error("Failed to load workspaces via Rust Mesh:", e);
      }
  }

  function handleWorkspaceChange(e: Event) {
      const select = e.target as HTMLSelectElement;
      globalState.activeWorkspaceId = select.value;
      const ws = globalState.workspaces.find((w: any) => w.id === select.value);
      if (ws) globalState.activeWorkspaceName = ws.name;
  }

  onDestroy(() => {
    disconnectTelemetry();
  });

  let isResizing = $state(false);

  function startResize(e: MouseEvent) {
    e.preventDefault();
    isResizing = true;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopResize);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }

  function handleMouseMove(e: MouseEvent) {
    if (!isResizing) return;
    const newWidth = e.clientX - 64; 
    setSidebarWidth(newWidth);
  }

  function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResize);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }

  let routeId = $derived(page.route.id || '');
</script>

<div class="flex w-full h-screen bg-surface-900 text-surface-200 overflow-hidden font-sans">
  <!-- 1. Permanent Activity Bar (Using rem for scaling: w-16 = 4rem) -->
  <nav class="w-16 bg-surface-900 border-r border-surface-700 flex flex-col h-full shrink-0 z-30 relative py-3">
    <!-- Top Identity Logo -->
    <div class="flex items-center justify-center border-b border-surface-700 pb-3 mb-3 shrink-0">
      <button aria-label="Toggle Navigation" onclick={toggleSidebar} class="text-primary-500 hover:scale-110 transition-transform p-2 rounded-lg cursor-pointer">
         <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" class="shrink-0">
           <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
           <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
         </svg>
      </button>
    </div>

    <!-- Navigation Icons -->
    <div class="flex flex-col gap-2 shrink-0 items-center px-2 flex-1">
      <a href="/dashboard" class="flex items-center justify-center w-full aspect-square rounded-xl transition-all overflow-hidden {routeId.includes('/dashboard') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'}">
        <Home class="w-6 h-6 shrink-0" />
      </a>
      <a href="/chat" class="flex items-center justify-center w-full aspect-square rounded-xl transition-all overflow-hidden {routeId.includes('/chat') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'}">
        <MessageCircle class="w-6 h-6 shrink-0" />
      </a>
      <a href="/vault" class="flex items-center justify-center w-full aspect-square rounded-xl transition-all overflow-hidden {routeId.includes('/vault') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'}">
        <Folder class="w-6 h-6 shrink-0" />
      </a>
      <a href="/settings" class="flex items-center justify-center w-full aspect-square rounded-xl transition-all overflow-hidden mt-auto mb-2 {routeId.includes('/settings') ? 'text-primary-400 bg-surface-800 shadow-[inset_3px_0_0_0_currentColor]' : 'text-surface-400 hover:text-surface-200 hover:bg-surface-800/50'}">
        <Settings class="w-6 h-6 shrink-0" />
      </a>
    </div>
  </nav>

  <!-- 2. Sliding Context Panel -->
  <aside 
    class="bg-surface-800 flex flex-col h-full transition-all duration-300 relative z-20 shrink-0 overflow-x-hidden overflow-y-auto border-r border-surface-700"
    class:border-r-0={!globalState.isSidebarOpen}
    class:pointer-events-none={!globalState.isSidebarOpen}
    class:opacity-0={!globalState.isSidebarOpen}
    style="width: {globalState.isSidebarOpen ? `${globalState.sidebarWidth}px` : '0px'}"
  >
    <div class="flex flex-col h-full shrink-0" style="width: {globalState.sidebarWidth}px; min-width: {globalState.sidebarWidth}px">
      <!-- Context Header -->
      <div class="h-16 px-4 flex flex-col justify-center border-b border-surface-700 shrink-0 gap-1 bg-surface-800/80 backdrop-blur-sm z-10 sticky top-0">
        <label for="workspace-selector" class="text-[9px] uppercase font-bold tracking-widest text-primary-500 flex items-center gap-1">
          <Database class="w-3 h-3" />
          Active Workspace
        </label>
        <select 
          id="workspace-selector"
          value={globalState.activeWorkspaceId}
          onchange={handleWorkspaceChange}
          class="bg-surface-900 border border-surface-600 text-surface-200 text-sm rounded-lg block w-full outline-none focus:border-primary-500 p-1 cursor-pointer appearance-none transition-colors"
        >
          {#each globalState.workspaces as ws}
            <option value={ws.id}>{ws.name}</option>
          {/each}
        </select>
        <!-- Custom invisible caret for pristine OS uniform looks -->
        <div class="pointer-events-none absolute inset-y-0 right-6 bottom-0 flex items-center justify-center pt-4">
           <svg class="w-3 h-3 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </div>
      </div>
      <!-- Context Area (Dynamic Route Content + Telemetry Array) -->
      <div class="flex-1 w-full overflow-hidden flex flex-col relative min-h-0">
        
        <div class="flex-1 p-4 text-xs text-surface-400 overflow-y-auto custom-scrollbar">
           <!-- Render sub-navigation or specific route tree here later -->
           <span class="block mb-4 tracking-widest uppercase opacity-50 font-bold">O.S Route: {routeId.replace('/', '') || 'ROOT'}</span>
        </div>

        <!-- Sticky Telemetry Dashboard (Bottom of context panel) -->
        <div class="p-4 border-t border-surface-700 bg-surface-900/50 flex flex-col gap-3 shrink-0">
            <div class="text-[10px] font-bold uppercase tracking-widest text-surface-500 mb-1 flex items-center justify-between">
                <span>Hardware Telemetry</span>
                <Activity class="w-3 h-3 {telemetryState.connected ? 'text-primary-500 animate-pulse' : 'text-surface-600'}" />
            </div>

            <!-- T/s Speedometer -->
            <div class="flex flex-col gap-1">
                <div class="flex justify-between items-end">
                    <span class="text-xs text-surface-400">Tokens/sec</span>
                    <span class="text-lg font-mono font-bold {telemetryState.tokensPerSecond > 20 ? 'text-emerald-400' : 'text-primary-400'}">
                        {telemetryState.tokensPerSecond.toFixed(1)} <span class="text-[10px] text-surface-500 uppercase">T/s</span>
                    </span>
                </div>
                <div class="w-full h-1 bg-surface-800 rounded-full overflow-hidden">
                    <div class="h-full bg-primary-500 transition-all duration-300" style="width: {Math.min(100, (telemetryState.tokensPerSecond / 80) * 100)}%"></div>
                </div>
            </div>

            <!-- Memory Specs -->
            <div class="flex justify-between items-center text-xs font-mono text-surface-400">
                <span>VRAM</span>
                <span class={telemetryState.vramUsageMB > 12000 ? 'text-amber-400 font-bold' : ''}>{telemetryState.vramUsageMB} MB</span>
            </div>

            <div class="text-[10px] text-surface-600 uppercase tracking-widest truncate" title={telemetryState.activeModel}>
                {telemetryState.activeModel}
            </div>
        </div>
      </div>
    </div>
  </aside>

  <!-- Resizer Handle -->
  {#if globalState.isSidebarOpen}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div 
      class="w-1.5 h-full cursor-col-resize hover:bg-primary-500/50 active:bg-primary-500 transition-colors z-40 relative flex-shrink-0 -ml-1.5"
      onmousedown={startResize}
    ></div>
  {/if}

  <!-- Main Area -->
  <main class="flex-1 flex flex-col overflow-hidden relative min-w-0 focus:outline-none bg-surface-900 shadow-[inset_10px_0_30px_rgba(0,0,0,0.5)]">
    {@render children()}
  </main>
</div>
