<script lang="ts">
    import { page } from '$app/state';
    let { children }: { children: import('svelte').Snippet } = $props();
</script>

<div class="flex h-full w-full gap-6 px-2 pb-4">

    <!-- Main Content Canvas -->
    <div class="flex-1 min-w-0 h-full overflow-y-auto custom-scrollbar bg-white dark:bg-[#0c1324] rounded-2xl border border-slate-200/50 dark:border-slate-800/50 shadow-sm transition-colors">
        {@render children()}
    </div>
</div>

<style>
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
</style>
