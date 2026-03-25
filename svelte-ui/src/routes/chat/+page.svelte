<script>
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import ChatHistorySidebar from '$lib/components/ChatHistorySidebar.svelte';
    import { MessageSquare, Settings, Plus } from 'lucide-svelte';
    import { settingsState } from '$lib/settings.svelte';
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] font-sans">
    <header class="mb-6 px-10 pt-10 w-full flex items-center justify-between shrink-0">
        <h1 class="font-extrabold text-2xl text-[#191c1d] tracking-tight flex items-center gap-3">
            <MessageSquare class="w-6 h-6 text-primary" />
            Sovereign Cíbrid Chat
        </h1>
    </header>

    <div class="flex-1 flex overflow-hidden px-10 pb-6 w-full gap-6">
        <aside class="w-80 shrink-0 border border-slate-200/60 rounded-2xl overflow-hidden flex flex-col bg-white/90 backdrop-blur-md shadow-sm z-10">
            <ChatHistorySidebar />
        </aside>
        <main class="flex-1 flex flex-col relative min-w-0 bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
            <ChatPanel />
        </main>
    </div>
</div>
