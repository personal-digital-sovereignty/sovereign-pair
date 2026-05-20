<script lang="ts">
    import { GripVertical, Calendar, CheckCircle, ArrowRight } from 'lucide-svelte';
    import { updateTaskAPI, type Task } from '$lib/projects.svelte';

    let { task, colStatus }: { task: Task, colStatus: string } = $props();
    let isEditing = $state(false);
    let editTitle = $state('');
    let editDesc = $state('');
    let editDeadline = $state('');
    let formattedDate = $derived(task.deadline ? new Date(task.deadline).toLocaleDateString() : 'Sem Prazo');

    $effect(() => {
        if (!isEditing) {
            editTitle = task.title;
            editDesc = task.description || '';
            editDeadline = task.deadline || '';
        }
    });

    async function saveCard() {
        await updateTaskAPI(task.id, { title: editTitle, description: editDesc, deadline: editDeadline });
        isEditing = false;
    }
</script>

{#if isEditing}
    <div class="bg-white dark:bg-[#12192b] p-3 rounded-lg shadow-xl border border-blue-400 dark:border-blue-500/50 z-50 transform scale-[1.02] transition-all w-full flex flex-col gap-2">
        <input type="text" bind:value={editTitle} class="w-full text-sm font-bold border-b border-slate-200 dark:border-slate-700 bg-transparent text-slate-800 dark:text-slate-200 focus:outline-none pb-1" placeholder="Título da Tarefa" onkeydown={(e) => e.key === 'Enter' && saveCard()} />
        <textarea bind:value={editDesc} class="w-full text-xs text-slate-600 dark:text-slate-400 bg-transparent focus:outline-none mt-1 resize-none h-20 custom-scrollbar" placeholder="Detalhes da tarefa... (Markdown suportado opcional)"></textarea>
        <div class="flex items-center gap-2 border-t border-slate-100 dark:border-slate-700 pt-2">
            <Calendar class="w-3 h-3 text-slate-400 dark:text-slate-500" />
            <input type="date" bind:value={editDeadline} class="text-[11px] text-slate-600 dark:text-slate-400 focus:outline-none bg-transparent style-color-scheme-dark" />
        </div>
        <div class="flex items-center gap-2 mt-1">
            <button onclick={saveCard} class="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white text-[11px] font-bold py-1.5 rounded-md cursor-pointer transition">Salvar</button>
            <button onclick={() => isEditing=false} class="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 px-3 py-1.5 rounded-md text-[11px] font-bold cursor-pointer transition">Cancelar</button>
        </div>
    </div>
{:else}
    <div 
        onclick={() => { editTitle = task.title; editDesc = task.description || ''; isEditing = true; }}
        onkeydown={(e) => e.key === 'Enter' && (isEditing = true)}
        role="button"
        tabindex="0"
        class="bg-white dark:bg-[#12192b] p-4 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-500/50 hover:shadow-md transition-all cursor-grab active:cursor-grabbing group text-left block w-full"
    >
        <div class="flex items-start justify-between gap-3 mb-3">
            <h3 class="font-bold text-slate-800 dark:text-slate-200 text-sm leading-tight pr-4 break-words">{task.title}</h3>
            <GripVertical class="w-4 h-4 text-slate-300 dark:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
        </div>
        {#if task.description}
            <p class="text-slate-500 dark:text-slate-400 text-xs mb-4 leading-relaxed line-clamp-3 break-words">{task.description}</p>
        {/if}
        <div class="flex items-center justify-between mt-auto pt-2 border-t border-slate-50 dark:border-slate-800/50">
            <div class="text-[10px] text-slate-400 dark:text-slate-500 font-bold flex items-center gap-1 uppercase tracking-wide truncate max-w-[60%]">
                <Calendar class="w-3 h-3 shrink-0" /> <span class="truncate">{formattedDate}</span>
            </div>
            <div class="flex items-center gap-1">
                <span class="{colStatus.toLowerCase() === 'done' || colStatus.toLowerCase().includes('conclu') ? 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-400 dark:border-emerald-800/50' : 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'} text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider">
                    {task.status}
                </span>
            </div>
        </div>
    </div>
{/if}
