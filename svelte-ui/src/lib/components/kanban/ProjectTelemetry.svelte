<script lang="ts">
    import type { Project } from '$lib/projects.svelte';
    import { CheckCircle2, Clock, PlayCircle, CircleDashed } from 'lucide-svelte';

    let { project }: { project: Project } = $props();

    let columns = $derived(JSON.parse(project.columns_json || '["To Do", "In Progress", "Done"]'));
    
    // Dinamicamente tentar encontrar as colunas de início e fim
    let firstCol = $derived(columns[0] || 'To Do');
    let lastCol = $derived(columns[columns.length - 1] || 'Done');

    let todoCount = $derived(project.tasks?.filter(t => t.status === firstCol).length || 0);
    let doneCount = $derived(project.tasks?.filter(t => t.status === lastCol).length || 0);
    let inProgCount = $derived((project.tasks?.length || 0) - todoCount - doneCount);
    
    let startString = $derived(project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Desconhecido');
</script>

<div class="flex flex-wrap items-center gap-3 w-full">
    <div class="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 flex items-center gap-2">
        <CircleDashed class="w-4 h-4 text-slate-400" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-slate-400 leading-none mb-0.5">A Fazer</span>
            <span class="text-sm font-black text-slate-700 leading-none">{todoCount}</span>
        </div>
    </div>
    
    <div class="bg-blue-50 border border-blue-200 rounded-lg px-3 py-1.5 flex items-center gap-2">
        <PlayCircle class="w-4 h-4 text-blue-500" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-blue-500/70 leading-none mb-0.5">Em Progresso</span>
            <span class="text-sm font-black text-blue-700 leading-none">{inProgCount}</span>
        </div>
    </div>

    <div class="bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-1.5 flex items-center gap-2">
        <CheckCircle2 class="w-4 h-4 text-emerald-500" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-emerald-500/70 leading-none mb-0.5">Concluídas</span>
            <span class="text-sm font-black text-emerald-700 leading-none">{doneCount}</span>
        </div>
    </div>

    <div class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5 flex items-center gap-2 ml-auto">
        <Clock class="w-4 h-4 text-amber-500" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-amber-500/70 leading-none mb-0.5">Em Fluxo Desde</span>
            <span class="text-sm font-black text-amber-700 leading-none">{startString}</span>
        </div>
    </div>
</div>
