<script>
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import ChatHistorySidebar from '$lib/components/ChatHistorySidebar.svelte';
    import { MessageSquare, Settings, Plus, Menu } from 'lucide-svelte';
    import { settingsState } from '$lib/settings.svelte';

    // Start closed on small screens/windows logically, but let's default to open since it's desktop primary, 
    // but the user wants to reduce it. We'll default to open and let them close it cleanly.
    let isHistoryOpen = $state(true);
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] dark:bg-[#080e1d] font-sans">
    <header class="mb-6 px-4 md:px-10 pt-10 w-full flex items-center shrink-0 gap-4">
        <button onclick={() => isHistoryOpen = !isHistoryOpen} class="p-2 md:p-3 bg-white/50 hover:bg-white dark:bg-[#12192b]/50 dark:hover:bg-[#1d253b] border border-slate-200/60 dark:border-[#424859]/30 rounded-xl text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-[#74b0ff] transition-all shadow-sm dark:shadow-none cursor-pointer flex-shrink-0" title="Toggle Chat History">
            <Menu class="w-5 h-5 md:w-6 md:h-6" />
        </button>
        <h1 class="font-extrabold text-xl md:text-2xl text-[#191c1d] dark:text-slate-200 tracking-tight flex items-center gap-2 md:gap-3">
            <MessageSquare class="w-5 h-5 md:w-6 md:h-6 text-primary dark:text-[#74b0ff] hidden md:block" />
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
