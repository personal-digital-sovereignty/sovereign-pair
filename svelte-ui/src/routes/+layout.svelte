<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

  import '../app.css';
  import { globalState } from '$lib/state.svelte.js';
  import { telemetryState, connectTelemetry, disconnectTelemetry } from '$lib/telemetry.svelte';
  import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, Activity, Database, Bell, Network, User } from 'lucide-svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { onMount, onDestroy } from 'svelte';
  import InlineSpotlight from '$lib/components/InlineSpotlight.svelte';
  import SettingsModal from '$lib/components/SettingsModal.svelte';
  import ChangelogModal from '$lib/components/ChangelogModal.svelte';
  import ManualModal from '$lib/components/ManualModal.svelte';
  import NotificationBell from '$lib/components/NotificationBell.svelte';
  import { settingsState, loadSettings } from '$lib/settings.svelte';

  // Versão injetada pelo Vite em build-time via package.json (vite.config.ts → define)
  // @ts-ignore — __APP_VERSION__ é definido em vite.config.ts via `define`
  let appVersion: string = typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : "0.0.0";
  let isChangelogOpen = $state(false);
  let { children } = $props();

  onMount(async () => {
    connectTelemetry();
    fetchWorkspaces();
    loadSettings();

    // Sovereign Boot Preference Interception
    if (window.location.pathname === '/') {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings`);
            if (res.ok) {
                const data = await res.json();
                if (data.default_route && data.default_route !== '/dashboard') {
                    goto(data.default_route);
                } else {
                    goto('/dashboard');
                }
            } else {
                goto('/dashboard');
            }
        } catch (e) {
            goto('/dashboard');
        }
    }
  });

  $effect(() => {
    if (typeof document !== 'undefined') {
        if (settingsState.theme === 'Dark Mode') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }
  });

  async function fetchWorkspaces() {
      try {
          const res = await fetch(`${API_BASE_URL}/v1/workspaces`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` } });
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

{#if routeId === '/spotlight'}
  {@render children()}
{:else}
<div class="h-screen print:h-auto print:overflow-visible w-full flex overflow-hidden antialiased text-slate-800 dark:text-slate-200 bg-[#F4F5F7] dark:bg-[#080e1d] font-sans">
  
  <InlineSpotlight />

  <aside class="{globalState.isSidebarOpen ? 'w-[280px]' : 'w-[80px]'} bg-[#2C3E50] dark:bg-[#0c1324] text-[#CBD5E1] flex flex-col h-full print:hidden flex-shrink-0 relative z-20 shadow-[4px_0_24px_-4px_rgba(0,0,0,0.1)] m-2 rounded-2xl overflow-hidden transition-all duration-300">
    <!-- Sidebar Header (Sovereign Origin Icon Preserved) -->
    <div class="h-16 flex items-center {globalState.isSidebarOpen ? 'px-6' : 'justify-center'} border-b border-white/5 shrink-0">
      <button onclick={() => globalState.isSidebarOpen = !globalState.isSidebarOpen} title="Toggle Sidebar" aria-label="Toggle Sidebar" class="flex items-center justify-center cursor-pointer hover:opacity-80 transition-opacity">
        <svg class="w-8 h-8 text-indigo-400 {globalState.isSidebarOpen ? 'mr-3' : ''} shrink-0" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.3"/>
        </svg>
      </button>
      {#if globalState.isSidebarOpen}
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold tracking-wide text-white">Control Hub</h1>
        <button onclick={() => isChangelogOpen = true} class="text-[9px] font-mono font-bold bg-white/10 text-white/50 px-1.5 py-0.5 rounded shadow-inner ml-1 hover:bg-white/20 hover:text-white transition-colors cursor-pointer" title="Ver Changelog de Versões">v{appVersion}</button>
      </div>
      {/if}
    </div>

    <!-- Main Navigation Container -->
    <nav class="flex-1 overflow-y-auto flex flex-col {globalState.isSidebarOpen ? 'px-4 py-6 gap-2' : 'px-2 items-center py-4 gap-3'}">
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-3 rounded-xl transition-colors {routeId.includes('/dashboard') || routeId === '/' ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/dashboard">
        <Home class="w-5 h-5 {globalState.isSidebarOpen ? 'mr-4' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-[15px]">Home</span>{/if}
      </a>
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-3 rounded-xl transition-colors {routeId.includes('/chat') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/chat">
        <MessageCircle class="w-5 h-5 {globalState.isSidebarOpen ? 'mr-4' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-[15px]">Chat</span>{/if}
      </a>
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-3 rounded-xl transition-colors {routeId.includes('/vault') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/vault">
        <Folder class="w-5 h-5 {globalState.isSidebarOpen ? 'mr-4' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-[15px]">Vault</span>{/if}
      </a>
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-3 rounded-xl transition-colors {routeId.includes('/projects') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/projects">
        <LayoutGrid class="w-5 h-5 {globalState.isSidebarOpen ? 'mr-4' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-[15px]">Projects</span>{/if}
      </a>

      <!-- System Modules Category -->
      {#if globalState.isSidebarOpen}
      <div class="mt-8 mb-2 px-4">
        <h2 class="text-[11px] font-bold text-[#64748B] uppercase tracking-widest">System Modules</h2>
      </div>
      {:else}
      <div class="w-10 h-px bg-white/10 my-4 mx-auto"></div>
      {/if}
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-2.5 rounded-lg transition-colors {routeId.includes('/graph') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/graph">
        <Network class="w-4 h-4 {globalState.isSidebarOpen ? 'mr-3' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-sm">Cognitive Graph</span>{/if}
      </a>
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-2.5 rounded-lg transition-colors {routeId.includes('/engineer') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/engineer/analytics">
        <Activity class="w-4 h-4 {globalState.isSidebarOpen ? 'mr-3' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-sm">Engineer</span>{/if}
      </a>
      
      <div class="mt-auto shrink-0 min-h-[1rem]"></div>

      <!-- BEGIN: Hardware Telemetry Widget (Flow Positioned) -->
      {#if globalState.isSidebarOpen}
      <div class="w-full bg-white dark:bg-[#1d253b] rounded-xl shadow-lg p-4 border border-slate-100 dark:border-[#424859]/20 print:hidden transition-all duration-300 mb-2">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Hardware Telemetry</h3>
          <Activity class="w-3 h-3 {telemetryState.connected ? 'text-indigo-500 dark:text-[#74b0ff] animate-pulse' : 'text-slate-400 dark:text-slate-600'}" />
        </div>

        <div class="space-y-4">
          {#if Math.floor(telemetryState.ramTotalGB) === 0}
            <!-- Loading Skeleton -->
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
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex flex-col gap-2">
                        <div class="h-2.5 bg-slate-200 rounded w-12"></div>
                        <div class="h-4 bg-slate-200 rounded w-20"></div>
                    </div>
                </div>
            </div>
          {:else}
          <!-- Sys RAM Component -->
          <div>
            <div class="flex justify-between items-end mb-1">
              <div>
                <div class="text-[10px] text-slate-500 dark:text-slate-400 font-medium">SYS RAM:</div>
                <div class="text-lg font-bold leading-none text-slate-800 dark:text-slate-200">{telemetryState.ramUsageMB.toFixed(0)} MB <span class="text-sm font-normal text-slate-500 dark:text-slate-400">/ {telemetryState.ramTotalGB} GB</span></div>
              </div>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div class="bg-indigo-400 dark:bg-[#5ea3f8] h-full rounded-full transition-all duration-300" style="width: {Math.min(100, (telemetryState.ramUsageMB / (telemetryState.ramTotalGB * 1024)) * 100)}%"></div>
            </div>
          </div>

          <!-- VRAM Component -->
          {#if telemetryState.vramTotalMB > 0 || telemetryState.unifiedMemory}
          <div>
            <div class="flex justify-between items-end mb-1">
              <div>
                <div class="text-[10px] text-slate-500 dark:text-slate-400 font-medium">{telemetryState.unifiedMemory ? 'UNIFIED MEM:' : 'GPU VRAM:'}</div>
                <div class="text-lg font-bold leading-none text-emerald-600 dark:text-emerald-400">{(telemetryState.vramTotalMB / 1024).toFixed(1)} GB <span class="text-sm font-normal text-slate-500 dark:text-slate-400 truncate w-12" title={telemetryState.gpuName}>/ {telemetryState.gpuName.substring(0, 10)}</span></div>
              </div>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div class="bg-emerald-400 dark:bg-emerald-500 h-full rounded-full transition-all duration-300" style="width: {telemetryState.vramTotalMB > 0 ? '100%' : '0%'}"></div>
            </div>
          </div>
          {/if}
          
          <!-- Tokens/Sec Simulated Bar -->
          <div class="flex items-center justify-between">
            <div>
              <div class="text-[10px] text-slate-500 dark:text-slate-400 font-medium">TOKENS/SEC:</div>
              <div class="text-lg font-bold leading-none {telemetryState.tokensPerSecond > 20 ? 'text-emerald-500 dark:text-emerald-400' : 'text-slate-800 dark:text-slate-200'}">
                {telemetryState.tokensPerSecond.toFixed(1)} <span class="text-sm font-normal text-slate-500 dark:text-slate-400">T/s</span>
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
          <div class="flex items-center justify-between mt-2">
            <div>
              <div class="text-[10px] text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap overflow-hidden text-ellipsis w-[120px]">MODEL:</div>
              <div class="text-sm font-bold leading-none text-slate-800 dark:text-slate-300 truncate max-w-[120px]" title={telemetryState.activeModel}>{telemetryState.activeModel || 'Idle'}</div>
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
      {/if}
      <!-- END: Hardware Telemetry Widget -->

      <!-- System Settings (Move to very bottom under telemetry) -->
      <a class="flex items-center {globalState.isSidebarOpen ? 'px-4 justify-start' : 'p-3 justify-center'} py-3 rounded-xl transition-colors {routeId.includes('/settings') ? 'bg-white/10 text-white font-medium shadow-sm' : 'text-[#94A3B8] hover:bg-white/5 hover:text-white'}" href="/settings">
        <Settings class="w-5 h-5 {globalState.isSidebarOpen ? 'mr-3' : ''}" />
        {#if globalState.isSidebarOpen}<span class="font-medium text-[15px]">System Settings</span>{/if}
      </a>
      
    </nav>
  </aside>
  <!-- END: Sidebar Master -->

  <!-- BEGIN: Main Viewport (Header + Route Children) -->
  <div class="flex-1 flex flex-col h-full print:h-auto print:overflow-visible overflow-hidden relative min-w-0 transition-all duration-300 ease-in-out" style="padding-right: {globalState?.layout?.isRightAuxPanelOpen ? '420px' : '0'}">
    
    <!-- Top Main Header -->
    <header class="h-16 flex items-center justify-between px-6 shrink-0 mt-2 z-[100] relative print:hidden">
      <!-- Active Workspace Selector -->
      <label for="workspace-select" class="flex items-center bg-white dark:bg-[#12192b] rounded-lg shadow-sm px-4 py-2 border border-slate-100 dark:border-[#424859]/20 cursor-pointer hover:bg-slate-50 dark:hover:bg-[#1d253b] transition-colors max-w-sm flex-shrink min-w-0">
        <div class="flex flex-col mr-4 w-full">
          <span class="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wide font-medium leading-none mb-1">Active Workspace</span>
          <select 
            id="workspace-select"
            class="text-sm font-semibold text-slate-700 dark:text-slate-200 leading-none bg-transparent outline-none appearance-none cursor-pointer p-0 border-0 focus:ring-0 truncate w-full"
            value={globalState.activeWorkspaceId}
            onchange={handleWorkspaceChange}
          >
            {#each globalState.workspaces as ws}
              <option value={ws.id}>{ws.name}</option>
            {/each}
          </select>
        </div>
        <Database class="w-4 h-4 text-slate-400 dark:text-slate-500 shrink-0 pointer-events-none" />
      </label>

      <!-- Account / Notifications Actions -->
      <div class="flex items-center bg-white dark:bg-[#12192b] rounded-full shadow-sm pr-2 pl-4 py-1.5 border border-slate-100 dark:border-[#424859]/20 h-12 flex-shrink-0">
        <NotificationBell />
        <button onclick={() => settingsState.isOpen = true} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 mr-4 transition-colors focus:outline-none">
          <Settings class="w-5 h-5" />
        </button>
        <div class="h-6 w-px bg-slate-200 dark:bg-slate-700 mr-4"></div>
        <div class="flex items-center">
          <div class="w-9 h-9 rounded-full bg-slate-900 border-[1.5px] border-indigo-400/50 flex items-center justify-center mr-3 hidden sm:flex shrink-0 shadow-[0_0_15px_rgba(99,102,241,0.2)] dark:shadow-[0_0_15px_rgba(116,176,255,0.1)]" title="System Operator">
             <User class="w-5 h-5 text-indigo-300 dark:text-[#74b0ff]" />
          </div>
          <div class="flex flex-col pr-2">
            <span class="text-sm font-bold text-slate-800 dark:text-slate-200 leading-none mb-1">{settingsState.userName}</span>
            <span class="text-[10px] text-slate-500 dark:text-slate-400 leading-none tracking-widest uppercase">{settingsState.userProfession}</span>
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
<ManualModal bind:isOpen={globalState.isManualOpen} />
{/if}
