<script lang="ts">
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import { Search } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte.js';
    import { onMount } from 'svelte';

    onMount(() => {
        // Spotlight always opens to an empty chat initially
        globalState.chat.activeSessionId = null;
    });
</script>

<div class="h-screen w-full bg-transparent flex flex-col items-center justify-start p-2 pb-2 overflow-hidden antialiased text-slate-800 dark:text-slate-200 font-sans">
    <div class="w-full h-full bg-[#080e1d]/90 backdrop-blur-md border border-[#424859]/50 rounded-xl shadow-2xl flex flex-col overflow-hidden ring-1 ring-blue-500/20">
        
        <!-- Draggable Title Bar -->
        <div data-tauri-drag-region class="h-9 bg-[#0c1324]/80 border-b border-[#424859]/50 flex items-center justify-between px-4 cursor-grab shrink-0">
            <div data-tauri-drag-region class="text-[10px] font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2 pointer-events-none">
                <Search size={12} class="text-[#74b0ff]" />
                Sovereign Spotlight
            </div>
            <div data-tauri-drag-region class="flex gap-1.5 pointer-events-none">
                <div class="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
                <div class="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
                <div class="w-2.5 h-2.5 rounded-full bg-slate-600"></div>
            </div>
        </div>

        <div class="flex-1 w-full flex overflow-hidden relative">
            <ChatPanel />
        </div>
    </div>
</div>

<style>
    :global(html), :global(body) {
        background-color: transparent !important;
        overflow: hidden;
    }
</style>
