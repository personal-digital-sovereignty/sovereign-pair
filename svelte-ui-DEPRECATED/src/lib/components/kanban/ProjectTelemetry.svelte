<script lang="ts">
    import { updateProjectAPI, type Project } from '$lib/projects.svelte';
    import { CheckCircle2, Clock, PlayCircle, CircleDashed, CalendarDays } from 'lucide-svelte';

    let { project }: { project: Project } = $props();

    let columns = $derived(JSON.parse(project.columns_json || '["To Do", "In Progress", "Done"]'));
    
    // Dinamicamente tentar encontrar as colunas de início e fim
    let firstCol = $derived(columns[0] || 'To Do');
    let lastCol = $derived(columns[columns.length - 1] || 'Done');

    let todoCount = $derived(project.tasks?.filter(t => t.status === firstCol).length || 0);
    let doneCount = $derived(project.tasks?.filter(t => t.status === lastCol).length || 0);
    let inProgCount = $derived((project.tasks?.length || 0) - todoCount - doneCount);
    
    let startString = $derived(project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Desconhecido');
    let deadlineString = $derived(project.deadline ? new Date(project.deadline).toLocaleDateString() : 'Adicionar Prazo');
    let isEditingDeadline = $state(false);
    let editDeadlineVal = $state('');

    async function saveDeadline() {
        await updateProjectAPI(project.id, { deadline: editDeadlineVal || undefined });
        isEditingDeadline = false;
    }
</script>

<div class="flex flex-wrap items-center gap-3 w-full">
    <div class="bg-slate-50 dark:bg-[#0c1324] border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 flex items-center gap-2 transition-colors">
        <CircleDashed class="w-4 h-4 text-slate-400 dark:text-slate-500" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-slate-400 dark:text-slate-500 leading-none mb-0.5 transition-colors">A Fazer</span>
            <span class="text-sm font-black text-slate-700 dark:text-slate-300 leading-none transition-colors">{todoCount}</span>
        </div>
    </div>
    
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50 rounded-lg px-3 py-1.5 flex items-center gap-2 transition-colors">
        <PlayCircle class="w-4 h-4 text-blue-500 dark:text-blue-400" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-blue-500/70 dark:text-blue-400/80 leading-none mb-0.5 transition-colors">Em Progresso</span>
            <span class="text-sm font-black text-blue-700 dark:text-blue-300 leading-none transition-colors">{inProgCount}</span>
        </div>
    </div>

    <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/50 rounded-lg px-3 py-1.5 flex items-center gap-2 transition-colors">
        <CheckCircle2 class="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
        <div class="flex flex-col">
            <span class="text-[9px] uppercase font-bold text-emerald-500/70 dark:text-emerald-400/80 leading-none mb-0.5 transition-colors">Concluídas</span>
            <span class="text-sm font-black text-emerald-700 dark:text-emerald-300 leading-none transition-colors">{doneCount}</span>
        </div>
    </div>

    <div class="flex gap-2 ml-auto">
        <div class="bg-slate-50 dark:bg-[#0c1324] border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-1.5 flex items-center gap-2 opacity-70 transition-colors">
            <Clock class="w-4 h-4 text-slate-400 dark:text-slate-500" />
            <div class="flex flex-col">
                <span class="text-[9px] uppercase font-bold text-slate-400 dark:text-slate-500 leading-none mb-0.5 transition-colors">Em Fluxo Desde</span>
                <span class="text-sm font-black text-slate-600 dark:text-slate-400 leading-none transition-colors">{startString}</span>
            </div>
        </div>
        <!-- Deadline Pill -->
        {#if isEditingDeadline}
            <div class="bg-amber-100 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700/50 rounded-lg px-3 py-1.5 flex items-center gap-2 animate-in fade-in transition-colors">
                <CalendarDays class="w-4 h-4 text-amber-600 dark:text-amber-500" />
                <input 
                    type="date" 
                    bind:value={editDeadlineVal} 
                    onkeydown={(e) => e.key === 'Enter' && saveDeadline()}
                    onblur={saveDeadline}
                    class="bg-transparent text-sm font-black text-amber-800 dark:text-amber-300 outline-none w-32 cursor-pointer transition-colors color-scheme-dark"
                />
            </div>
        {:else}
            <button onclick={() => { editDeadlineVal = project.deadline || ''; isEditingDeadline = true; }} class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg px-3 py-1.5 flex items-center gap-2 hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors cursor-pointer text-left">
                <CalendarDays class="w-4 h-4 text-amber-500 dark:text-amber-400" />
                <div class="flex flex-col">
                    <span class="text-[9px] uppercase font-bold text-amber-500/70 dark:text-amber-400/80 leading-none mb-0.5 transition-colors">Prazo Final</span>
                    <span class="text-sm font-black text-amber-700 dark:text-amber-300 leading-none transition-colors">{deadlineString}</span>
                </div>
            </button>
        {/if}
    </div>
</div>
