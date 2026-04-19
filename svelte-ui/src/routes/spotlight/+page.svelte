<script lang="ts">
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import { Search } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte.js';
    import { onMount } from 'svelte';
    import { getCurrentWindow } from '@tauri-apps/api/window';

    function closeSpotlight() {
        getCurrentWindow().close();
    }

    onMount(() => {
        // Spotlight always opens to an empty chat initially
        globalState.chat.activeSessionId = null;

        const handleKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                closeSpotlight();
            }
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    });
</script>

<div class="h-screen w-full bg-transparent flex flex-col items-center justify-start p-2 pb-2 overflow-hidden antialiased text-slate-800 dark:text-slate-200 font-sans">
    <div class="w-full h-full bg-[#080e1d]/90 backdrop-blur-md rounded-xl shadow-2xl flex flex-col overflow-hidden">
        
        <!-- Draggable Title Bar -->
        <div data-tauri-drag-region class="h-9 bg-[#0c1324]/80 border-b border-[#424859]/30 flex items-center justify-between px-4 cursor-grab shrink-0">
            <div data-tauri-drag-region class="text-[10px] font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2 pointer-events-none">
                <Search size={12} class="text-[#74b0ff]" />
                Sovereign Spotlight
            </div>
            <div class="flex gap-2 relative z-50">
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div class="w-3 h-3 rounded-full bg-red-500/80 hover:bg-red-500 cursor-pointer transition-colors shadow-sm" onclick={closeSpotlight} title="Fechar"></div>
                <div class="w-3 h-3 rounded-full bg-yellow-500/80 shadow-sm opacity-50"></div>
                <div class="w-3 h-3 rounded-full bg-green-500/80 shadow-sm opacity-50"></div>
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
