<script>
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import ChatHistorySidebar from '$lib/components/ChatHistorySidebar.svelte';
</script>

<div class="h-full w-full flex overflow-hidden">
    <aside class="w-72 shrink-0 border-r border-slate-200 flex flex-col bg-slate-50 z-10">
        <ChatHistorySidebar />
    </aside>
    <main class="flex-1 flex flex-col relative min-w-0">
        <ChatPanel />
    </main>
</div>
