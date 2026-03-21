<script lang="ts">
    import { GripVertical, Calendar, CheckCircle, ArrowRight } from 'lucide-svelte';
    import { updateTaskAPI, type Task } from '$lib/projects.svelte';

    let { task, colStatus }: { task: Task, colStatus: string } = $props();
    let isEditing = $state(false);
    let editTitle = $state('');
    let editDesc = $state('');

    $effect(() => {
        if (!isEditing) {
            editTitle = task.title;
            editDesc = task.description || '';
        }
    });

    async function saveCard() {
        await updateTaskAPI(task.id, { title: editTitle, description: editDesc });
        isEditing = false;
    }
</script>

{#if isEditing}
    <div class="bg-white p-3 rounded-lg shadow-xl border border-blue-400 z-50 transform scale-[1.02] transition-all w-full flex flex-col gap-2">
        <input type="text" bind:value={editTitle} class="w-full text-sm font-bold border-b border-slate-200 text-slate-800 focus:outline-none pb-1" placeholder="Título da Tarefa" onkeydown={(e) => e.key === 'Enter' && saveCard()} />
        <textarea bind:value={editDesc} class="w-full text-xs text-slate-600 focus:outline-none mt-1 resize-none h-20 custom-scrollbar" placeholder="Detalhes da tarefa... (Markdown suportado opcional)"></textarea>
        <div class="flex items-center gap-2 mt-1">
            <button onclick={saveCard} class="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white text-[11px] font-bold py-1.5 rounded-md cursor-pointer transition">Salvar</button>
            <button onclick={() => isEditing=false} class="bg-slate-100 hover:bg-slate-200 text-slate-500 px-3 py-1.5 rounded-md text-[11px] font-bold cursor-pointer transition">Cancelar</button>
        </div>
    </div>
{:else}
    <article 
        onclick={() => { editTitle = task.title; editDesc = task.description || ''; isEditing = true; }}
        onkeydown={(e) => e.key === 'Enter' && (isEditing = true)}
        role="button"
        tabindex="0"
        class="bg-white p-4 rounded-lg shadow-sm border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-grab active:cursor-grabbing group"
    >
        <div class="flex items-start justify-between gap-3 mb-3">
            <h3 class="font-bold text-slate-800 text-sm leading-tight pr-4 break-words">{task.title}</h3>
            <GripVertical class="w-4 h-4 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
        </div>
        {#if task.description}
            <p class="text-slate-500 text-xs mb-4 leading-relaxed line-clamp-3 break-words">{task.description}</p>
        {/if}
        <div class="flex items-center justify-between mt-auto pt-2 border-t border-slate-50">
            <div class="text-[10px] text-slate-400 font-bold flex items-center gap-1 uppercase tracking-wide">
                <Calendar class="w-3 h-3" /> Hoje
            </div>
            <div class="flex items-center gap-1">
                <span class="{colStatus.toLowerCase() === 'done' || colStatus.toLowerCase().includes('conclu') ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'} text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider">
                    {task.status}
                </span>
            </div>
        </div>
    </article>
{/if}
