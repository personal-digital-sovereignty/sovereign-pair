<script>
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import ChatHistorySidebar from '$lib/components/ChatHistorySidebar.svelte';
    import { MessageSquare, Settings, Plus } from 'lucide-svelte';
    import { settingsState } from '$lib/settings.svelte';

    // Start closed on small screens/windows logically, but let's default to open since it's desktop primary, 
    // but the user wants to reduce it. We'll default to open and let them close it cleanly.
    let isHistoryOpen = $state(true);
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] dark:bg-[#080e1d] font-sans">
    <header class="mb-6 px-4 md:px-10 pt-10 w-full flex items-center shrink-0">
        <h1 class="font-extrabold text-xl md:text-2xl text-[#191c1d] dark:text-slate-200 tracking-tight flex items-center gap-3">
            <button onclick={() => isHistoryOpen = !isHistoryOpen} class="p-1.5 -ml-1.5 hover:bg-slate-200/50 dark:hover:bg-[#1d253b] rounded-lg transition-colors cursor-pointer text-primary dark:text-[#74b0ff]" title="Alternar Histórico">
                <MessageSquare class="w-6 h-6" />
            </button>
            Sovereign Cíbrid Chat
        </h1>
    </header>

    <div class="flex-1 flex overflow-hidden px-4 md:px-10 pb-6 w-full gap-6">
        {#if isHistoryOpen}
        <aside class="w-72 md:w-80 shrink-0 border border-slate-200/60 dark:border-[#424859]/20 rounded-2xl overflow-hidden flex flex-col bg-white/90 dark:bg-[#12192b] backdrop-blur-md shadow-sm dark:shadow-none z-10 transition-all duration-300 animate-in slide-in-from-left-4 fade-in">
            <ChatHistorySidebar />
        </aside>
        {/if}
        <main class="flex-1 flex flex-col relative min-w-0 bg-white/90 dark:bg-[#12192b] backdrop-blur-md rounded-2xl border border-slate-200/60 dark:border-[#424859]/20 shadow-sm dark:shadow-none overflow-hidden transition-all duration-300">
            <ChatPanel />
        </main>
    </div>
</div>
