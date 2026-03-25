<script lang="ts">
  import '../app.css';
  import { globalState } from '$lib/state.svelte.js';
  
  let appVersion = "0.9.7";
  import { telemetryState, connectTelemetry, disconnectTelemetry } from '$lib/telemetry.svelte';
  import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, Activity, Database, Bell, Network, User } from 'lucide-svelte';
  import { page } from '$app/state';
  import { onMount, onDestroy } from 'svelte';
  import InlineSpotlight from '$lib/components/InlineSpotlight.svelte';
  import SettingsModal from '$lib/components/SettingsModal.svelte';
  import ChangelogModal from '$lib/components/ChangelogModal.svelte';
  
  let isChangelogOpen = $state(false);
  import NotificationBell from '$lib/components/NotificationBell.svelte';
  import { settingsState, loadSettings } from '$lib/settings.svelte';

  let { children } = $props();

  onMount(() => {
    connectTelemetry();
    fetchWorkspaces();
    loadSettings();
  });

  async function fetchWorkspaces() {
      try {
          const res = await fetch('http://localhost:38001/v1/workspaces', { headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` } });
          if (res.ok) {
              const data = await res.json();
              globalState.workspaces = Array.isArray(data) ? data : (data.workspaces || []);
              if (globalState.workspaces.length === 0) {
                  globalState.workspaces = [{ id: 'mesh_roaming', name: 'Sovereign Mesh Roaming' }];
              }
              const exists = globalState.workspaces.find((w: any) => w.id === globalState.activeWorkspaceId);
              if (!exists) {
                  globalState.activeWorkspaceId = globalState.workspaces[0].id;
                  globalState.activeWorkspaceName = globalState.workspaces[0].name;
              }
          }
      } catch (e) {
          console.error("Failed to load workspaces via Rust API:", e);
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

  let routeId = $derived(page.route.id || '');
</script>

<div class="h-screen print:h-auto print:overflow-visible w-full flex overflow-hidden antialiased text-slate-800 bg-[#F4F5F7] font-sans">
  
  <InlineSpotlight />

  <aside class="w-[280px] bg-[#2C3E50] text-[#CBD5E1] flex flex-col h-full print:hidden flex-shrink-0 relative z-20 shadow-[4px_0_24px_-4px_rgba(0,0,0,0.1)] m-2 rounded-2xl overflow-hidden transition-all duration-300">
    <!-- Sidebar Header (Sovereign Origin Icon Preserved) -->
    <div class="h-16 flex items-center px-6 border-b border-white/5 shrink-0">
      <svg class="w-8 h-8 text-indigo-400 mr-3 shrink-0" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
        <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
      </svg>
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold tracking-wide text-white">Control Hub</h1>
        <button onclick={() => isChangelogOpen = true} class="text-[9px] font-mono font-bold bg-white/10 text-white/50 px-1.5 py-0.5 rounded shadow-inner ml-1 hover:bg-white/20 hover:text-white transition-colors cursor-pointer" title="Ver Changelog de Versões">v{appVersion}</button>
      </div>
    </div>

    <!-- Main Navigation Container -->
    <nav class="flex-1 overflow-y-auto py-6 flex flex-col px-4 gap-1.5 pt-4">
      <a class="flex items-center px-4 py-3 rounded-xl transition-colors {routeId.includes('/dashboard') || routeId === '/' ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/dashboard">
        <Home class="w-5 h-5 mr-4" />
        <span class="font-medium text-[15px]">Home</span>
      </a>
      <a class="flex items-center px-4 py-3 rounded-xl transition-colors {routeId.includes('/chat') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/chat">
        <MessageCircle class="w-5 h-5 mr-4" />
        <span class="font-medium text-[15px]">Chat</span>
      </a>
      <a class="flex items-center px-4 py-3 rounded-xl transition-colors {routeId.includes('/vault') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/vault">
        <Folder class="w-5 h-5 mr-4" />
        <span class="font-medium text-[15px]">Vault</span>
      </a>
      <a class="flex items-center px-4 py-3 rounded-xl transition-colors {routeId.includes('/projects') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/projects">
        <LayoutGrid class="w-5 h-5 mr-4" />
        <span class="font-medium text-[15px]">Projects</span>
      </a>

      <!-- System Modules Category -->
      <div class="mt-8 mb-2 px-4">
        <h2 class="text-[11px] font-bold text-[#64748B] uppercase tracking-widest">System Modules</h2>
      </div>
      <a class="flex items-center px-4 py-2.5 rounded-lg transition-colors {routeId.includes('/graph') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/graph">
        <Network class="w-4 h-4 mr-3" />
        <span class="font-medium text-sm">Cognitive Graph</span>
      </a>
      <a class="flex items-center px-4 py-2.5 rounded-lg transition-colors {routeId.includes('/rag-engine') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/rag-engine/routing">
        <span class="font-medium text-sm pl-7">RAG Engine</span>
      </a>
      <a class="flex items-center px-4 py-2.5 rounded-lg transition-colors {routeId.includes('/model-trainer') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/model-trainer/fine-tuning">
        <span class="font-medium text-sm pl-7">Model Trainer</span>
      </a>
      <a class="flex items-center px-4 py-2.5 rounded-lg transition-colors {routeId.includes('/analytics') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/analytics">
        <span class="font-medium text-sm pl-7">Analytics</span>
      </a>
      
      <!-- Sticky Settings Anchor -->
      <div class="mt-auto pt-4 mb-2 border-t border-white/5">
         <a class="flex items-center px-4 py-3 rounded-xl transition-colors {routeId.includes('/settings') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/settings">
           <Settings class="w-5 h-5 mr-4 shrink-0" />
           <span class="font-medium text-[15px]">System Settings</span>
         </a>
      </div>
    </nav>
  </aside>
  <!-- END: Sidebar Master -->

  <!-- BEGIN: Hardware Telemetry Widget Overlay -->
  <div class="absolute bottom-4 left-4 w-[264px] bg-white rounded-xl shadow-lg p-4 z-30 border border-slate-100 print:hidden">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Hardware Telemetry</h3>
      <Activity class="w-3 h-3 {telemetryState.connected ? 'text-indigo-500 animate-pulse' : 'text-slate-400'}" />
    </div>

    <div class="space-y-4">
      {#if Math.floor(telemetryState.ramTotalGB) === 0}
        <!-- Loading Skeleton / Bootstrapping State -->
        <div class="animate-pulse space-y-5 pt-1 pb-2">
            <div class="flex flex-col gap-2">
                <div class="h-2.5 bg-slate-200 rounded w-16"></div>
                <div class="h-5 bg-slate-200 rounded w-24"></div>
                <div class="h-1.5 bg-slate-100 rounded-full w-full"></div>
            </div>
            <div class="flex items-center justify-between">
                <div class="flex flex-col gap-2">
                    <div class="h-2.5 bg-slate-200 rounded w-20"></div>
                    <div class="h-5 bg-slate-200 rounded w-16"></div>
                </div>
                <div class="flex items-end gap-1 h-6">
                    {#each [1,2,3,4,5] as _}
                        <div class="w-1.5 h-full bg-slate-100 rounded-t-sm"></div>
                    {/each}
                </div>
            </div>
            <div class="flex items-center justify-between">
                <div class="flex flex-col gap-2">
                    <div class="h-2.5 bg-slate-200 rounded w-12"></div>
                    <div class="h-4 bg-slate-200 rounded w-20"></div>
                </div>
                <div class="flex items-end gap-1 h-6">
                    {#each [1,2,3,4,5] as _}
                        <div class="w-1.5 h-full bg-slate-100 rounded-t-sm"></div>
                    {/each}
                </div>
            </div>
        </div>
      {:else}
      <!-- VRAM Component -->
      <div>
        <div class="flex justify-between items-end mb-1">
          <div>
            <div class="text-[10px] text-slate-500 font-medium">SYS RAM:</div>
            <div class="text-lg font-bold leading-none text-slate-800">{telemetryState.ramUsageMB.toFixed(0)} MB <span class="text-sm font-normal text-slate-500">/ {telemetryState.ramTotalGB} GB</span></div>
          </div>
        </div>
        <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
          <div class="bg-indigo-400 h-full rounded-full transition-all duration-300" style="width: {Math.min(100, (telemetryState.ramUsageMB / (telemetryState.ramTotalGB * 1024)) * 100)}%"></div>
        </div>
      </div>
      
      <!-- Tokens/Sec Simulated Bar -->
      <div class="flex items-center justify-between">
        <div>
          <div class="text-[10px] text-slate-500 font-medium">TOKENS/SEC:</div>
          <div class="text-lg font-bold leading-none {telemetryState.tokensPerSecond > 20 ? 'text-emerald-500' : 'text-slate-800'}">
            {telemetryState.tokensPerSecond.toFixed(1)} <span class="text-sm font-normal text-slate-500">T/s</span>
          </div>
        </div>
        <div class="flex items-end h-6 gap-[2px]">
            <div class="w-1.5 bg-slate-200 h-[30%] rounded-t-sm" class:!bg-indigo-300={telemetryState.tokensPerSecond > 2}></div>
            <div class="w-1.5 bg-slate-200 h-[50%] rounded-t-sm" class:!bg-indigo-400={telemetryState.tokensPerSecond > 8}></div>
            <div class="w-1.5 bg-slate-200 h-[80%] rounded-t-sm" class:!bg-indigo-500={telemetryState.tokensPerSecond > 15}></div>
            <div class="w-1.5 bg-slate-200 h-[100%] rounded-t-sm" class:!bg-indigo-600={telemetryState.tokensPerSecond > 30}></div>
            <div class="w-1.5 bg-slate-200 h-[60%] rounded-t-sm" class:!bg-indigo-400={telemetryState.tokensPerSecond > 45}></div>
        </div>
      </div>

      <!-- GPU / Temp Mock with active model name -->
      <div class="flex items-center justify-between">
        <div>
          <div class="text-[10px] text-slate-500 font-medium whitespace-nowrap overflow-hidden text-ellipsis w-[120px]">MODEL:</div>
          <div class="text-sm font-bold leading-none text-slate-800 truncate max-w-[120px]" title={telemetryState.activeModel}>{telemetryState.activeModel || 'Idle'}</div>
        </div>
        <div class="flex items-end h-6 gap-[2px]">
          <div class="w-1.5 bg-emerald-400 h-[40%] rounded-t-sm"></div>
          <div class="w-1.5 bg-emerald-400 h-[50%] rounded-t-sm"></div>
          <div class="w-1.5 bg-emerald-400 h-[60%] rounded-t-sm"></div>
          <div class="w-1.5 bg-emerald-400 h-[65%] rounded-t-sm"></div>
          <div class="w-1.5 bg-emerald-400 h-[68%] rounded-t-sm"></div>
        </div>
      </div>
      {/if}
    </div>
  </div>
  <!-- END: Hardware Telemetry Widget -->

  <!-- BEGIN: Main Viewport (Header + Route Children) -->
  <div class="flex-1 flex flex-col h-full print:h-auto print:overflow-visible overflow-hidden relative min-w-0 transition-all duration-300 ease-in-out" style="padding-right: {globalState?.layout?.isRightAuxPanelOpen ? '420px' : '0'}">
    
    <!-- Top Main Header -->
    <header class="h-16 flex items-center justify-between px-6 shrink-0 mt-2 z-[100] relative print:hidden">
      <!-- Active Workspace Selector -->
      <label for="workspace-select" class="flex items-center bg-white rounded-lg shadow-sm px-4 py-2 border border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors max-w-sm flex-shrink min-w-0">
        <div class="flex flex-col mr-4 w-full">
          <span class="text-[10px] text-slate-500 uppercase tracking-wide font-medium leading-none mb-1">Active Workspace</span>
          <select 
            id="workspace-select"
            class="text-sm font-semibold text-slate-700 leading-none bg-transparent outline-none appearance-none cursor-pointer p-0 border-0 focus:ring-0 truncate w-full"
            value={globalState.activeWorkspaceId}
            onchange={handleWorkspaceChange}
          >
            {#each globalState.workspaces as ws}
              <option value={ws.id}>{ws.name}</option>
            {/each}
          </select>
        </div>
        <Database class="w-4 h-4 text-slate-400 shrink-0 pointer-events-none" />
      </label>

      <!-- Account / Notifications Actions -->
      <div class="flex items-center bg-white rounded-full shadow-sm pr-2 pl-4 py-1.5 border border-slate-100 h-12 flex-shrink-0">
        <NotificationBell />
        <button onclick={() => settingsState.isOpen = true} class="text-slate-400 hover:text-slate-600 mr-4 transition-colors focus:outline-none">
          <Settings class="w-5 h-5" />
        </button>
        <div class="h-6 w-px bg-slate-200 mr-4"></div>
        <div class="flex items-center">
          <div class="w-9 h-9 rounded-full bg-slate-900 border-[1.5px] border-indigo-400/50 flex items-center justify-center mr-3 hidden sm:flex shrink-0 shadow-[0_0_15px_rgba(99,102,241,0.2)]" title="System Operator">
             <User class="w-5 h-5 text-indigo-300" />
          </div>
          <div class="flex flex-col pr-2">
            <span class="text-sm font-bold text-slate-800 leading-none mb-1">{settingsState.userName}</span>
            <span class="text-[10px] text-slate-500 leading-none tracking-widest uppercase">{settingsState.userProfession}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Page Content (Slot Injection) -->
    <main class="flex-1 pb-4 px-4 overflow-hidden print:h-auto print:overflow-visible flex flex-col relative z-20">
         {@render children()}
    </main>
  </div>
</div>
<SettingsModal />
<ChangelogModal bind:isOpen={isChangelogOpen} />
