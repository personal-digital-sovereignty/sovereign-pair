<script lang="ts">
  import '../app.css';
  import { globalState, toggleSidebar, setSidebarWidth } from '$lib/state.svelte';
  import { Home, MessageCircle, Folder, LayoutGrid, Settings, Cloud, CloudOff } from 'lucide-svelte';
  import { page } from '$app/state';

  let { children } = $props();

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
      <button onclick={toggleSidebar} class="text-primary-500 hover:scale-110 transition-transform p-2 rounded-lg cursor-pointer">
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
      <div class="h-14 px-4 flex items-center border-b border-surface-700 shrink-0">
        <span class="font-semibold text-surface-300 tracking-wide text-sm truncate uppercase">
          {routeId.replace('/', '') || 'SOVEREIGN'}
        </span>
      </div>
      <!-- Context Area -->
      <div class="flex-1 w-full overflow-hidden flex flex-col relative min-h-0 p-4 text-xs text-surface-400">
        <span>Sensus System Active.</span>
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
