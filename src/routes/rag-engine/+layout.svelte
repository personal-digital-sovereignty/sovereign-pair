<script lang="ts">
    import { page } from '$app/stores';
    import { Database } from 'lucide-svelte';
</script>

<div class="w-full h-full print:h-auto flex flex-col bg-[#F4F7FA] font-sans">
    <header class="mb-4 px-10 pt-10 w-full flex items-center justify-between shrink-0">
        <h1 class="font-extrabold text-2xl text-[#191c1d] tracking-tight flex items-center gap-3">
            <Database class="w-6 h-6 text-primary" />
            RAG Engine
        </h1>
        <div class="flex items-center gap-1 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
            <a href="/rag-engine/routing" class="px-4 py-2 {$page.url.pathname.includes('/routing') ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container-high'} font-bold text-xs rounded-lg transition-colors cursor-pointer block">
                Routing & Resilience
            </a>
            <a href="/rag-engine/quality" class="px-4 py-2 {$page.url.pathname.includes('/quality') ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-surface-variant hover:bg-surface-container-high'} font-bold text-xs rounded-lg transition-colors cursor-pointer block">
                Quality & Gaps
            </a>
        </div>
    </header>

    <!-- Main Content Canvas -->
    <div class="flex-1 w-full min-w-0 overflow-y-auto print:overflow-visible px-10 pb-12 custom-scrollbar">
        <slot />
    </div>
</div>
