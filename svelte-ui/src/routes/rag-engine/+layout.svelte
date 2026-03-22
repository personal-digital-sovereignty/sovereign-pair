<script lang="ts">
    import { page } from '$app/stores';
</script>

<div class="w-full h-full flex flex-col">
    <!-- Horizontal Navigation Tabs -->
    <div class="flex gap-8 border-b border-slate-200/60 mb-8 mt-2 shrink-0">
        <a href="/rag-engine/routing" class="flex items-center gap-2 pb-4 border-b-2 transition-all {$page.url.pathname.includes('/routing') ? 'border-indigo-500 text-indigo-700 font-bold' : 'border-transparent text-slate-500 font-medium hover:text-slate-800 hover:border-slate-300'}">
            <span class="material-symbols-outlined text-[20px] {$page.url.pathname.includes('/routing') ? 'text-indigo-600' : ''}">directions_alt</span>
            Model Routing & Resilience
        </a>
        <a href="/rag-engine/quality" class="flex items-center gap-2 pb-4 border-b-2 transition-all {$page.url.pathname.includes('/quality') ? 'border-emerald-500 text-emerald-700 font-bold' : 'border-transparent text-slate-500 font-medium hover:text-slate-800 hover:border-slate-300'}">
            <span class="material-symbols-outlined text-[20px] {$page.url.pathname.includes('/quality') ? 'text-emerald-600' : ''}">analytics</span>
            Quality & Knowledge Gaps
        </a>
    </div>

    <!-- Main Content Canvas -->
    <div class="flex-1 w-full min-w-0">
        <slot />
    </div>
</div>
