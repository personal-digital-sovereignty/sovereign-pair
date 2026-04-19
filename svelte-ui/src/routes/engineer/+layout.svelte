<script lang="ts">
    import { page } from '$app/state';
    let { children }: { children: import('svelte').Snippet } = $props();
</script>

<div class="flex h-full w-full gap-6 px-2 pb-4">
    <!-- Main Content Canvas -->
    <div class="flex-1 min-w-0 h-full flex flex-col bg-white dark:bg-[#0c1324] rounded-2xl border border-slate-200/50 dark:border-slate-800/50 shadow-sm transition-colors overflow-hidden">
        
        <!-- Fixed Header Section across Engineer Hub -->
        <header class="w-full flex items-center justify-between px-8 py-6 border-b border-outline-variant/10 shrink-0 bg-white/80 dark:bg-[#0c1324]/80 backdrop-blur-md z-10">
            <div class="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full w-[400px] border border-outline-variant/10 shadow-sm relative">
                <span class="material-symbols-outlined text-on-surface-variant text-[20px] absolute left-4">search</span>
                <input class="bg-transparent border-none focus:ring-0 text-sm w-full pl-8 placeholder:text-on-surface-variant/70 text-on-surface outline-none" placeholder="Search pipeline nodes..." type="text" />
            </div>
            <div class="flex items-center gap-2 bg-surface-container-low p-1.5 rounded-xl border border-outline-variant/10">
                <a href="/engineer/fine-tuning" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/fine-tuning') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">Fine-Tuning</a>
                <a href="/engineer/distillation" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/distillation') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">Distillation</a>
                <!-- TODO(v1.3.0 MOCK HIDDEN): Reflection Lab & Unsloth Monitor
                <a href="/engineer/reflection" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/reflection') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">Reflection Lab</a>
                -->
                <a href="/engineer/rag-pipeline" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/rag-pipeline') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">RAG Pipeline</a>
                <!--
                <a href="/engineer/unsloth" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/unsloth') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">Unsloth Monitor</a>
                -->
                <a href="/engineer/analytics" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors {page.url.pathname.includes('/analytics') ? 'bg-blue-600 dark:bg-[#74b0ff]/20 text-white dark:text-[#74b0ff]' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">Analytics</a>
                <a href="/engineer/system-logs" class="px-4 py-2 text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-1.5 {page.url.pathname.includes('/system-logs') ? 'bg-amber-600 dark:bg-amber-500/20 text-white dark:text-amber-400' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1d253b] shadow-none'}">
                    <span class="w-1.5 h-1.5 rounded-full {page.url.pathname.includes('/system-logs') ? 'bg-amber-400 animate-pulse' : 'bg-slate-400'}"></span>
                    System Logs
                </a>
            </div>
        </header>

        <div class="flex-1 overflow-y-auto custom-scrollbar">
            {@render children()}
        </div>
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
</style>
