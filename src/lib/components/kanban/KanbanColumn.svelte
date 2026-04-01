<script lang="ts">
    import { Settings, Plus, Trash2, Edit2 } from 'lucide-svelte';
    import KanbanCard from './KanbanCard.svelte';
    import { updateProjectTasks, createTask, updateProjectAPI, type Project } from '$lib/projects.svelte';
    import { dndzone } from 'svelte-dnd-action';
    import { flip } from 'svelte/animate';

    let { colStatus, project, columns }: { colStatus: string, project: Project, columns: string[] } = $props();
    
    let columnTasks = $state<any[]>([]);
    let isDragging = $state(false);
    let isAddingTask = $state(false);
    let newTaskTitle = $state('');
    let isMenuOpen = $state(false);

    async function submitTask() {
        await createTask(project.id, newTaskTitle, colStatus);
        isAddingTask = false;
        newTaskTitle = '';
    }

    async function renameColumn() {
        const newName = prompt("Renomear Categoria:\nIsso alterará o cabeçalho. As tarefas continuarão mapeadas ao status novo.", colStatus);
        if (newName && newName.trim() !== '' && newName !== colStatus) {
            if (columns.includes(newName)) {
                alert("Já existe uma categoria com este nome!");
                return;
            }
            let newCols = columns.map(c => c === colStatus ? newName.trim() : c);
            await updateProjectAPI(project.id, { columns_json: JSON.stringify(newCols) });
            isMenuOpen = false;
        }
    }

    async function deleteColumn() {
        if (confirm(`Excluir categoria '${colStatus}'?\nATENÇÃO: As tarefas desta coluna ficarão órfãs na API e sumirão do quadro atual!`)) {
            let newCols = columns.filter(c => c !== colStatus);
            await updateProjectAPI(project.id, { columns_json: JSON.stringify(newCols) });
            isMenuOpen = false;
        }
    }

    $effect(() => {
        if (!isDragging) {
            columnTasks = project.tasks.filter(t => t.status === colStatus);
        }
    });

    function handleDndConsider(e: CustomEvent<any>) {
        isDragging = true;
        columnTasks = e.detail.items;
    }

    function handleDndFinalize(e: CustomEvent<any>) {
        isDragging = false;
        columnTasks = e.detail.items;
        updateProjectTasks(project.id, colStatus, columnTasks);
    }
</script>

<section class="w-80 flex flex-col rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm max-h-full bg-slate-50 dark:bg-[#0c1324] shrink-0 relative">
    <!-- Column Header -->
    <div class="p-4 flex items-center justify-between border-b border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-[#12192b]/50 rounded-t-xl shrink-0 group">
        <h2 class="font-semibold text-slate-800 dark:text-slate-200 text-lg truncate pr-2">{colStatus}</h2>
        <div class="flex items-center gap-2 relative">
            <span class="bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 text-xs font-bold px-2 py-0.5 rounded-full">
                {columnTasks.filter((t: any) => !t.isDndShadowItem).length}
            </span>
            <button onclick={() => isAddingTask = !isAddingTask} class="text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer p-1 rounded hover:bg-blue-50 dark:hover:bg-slate-800" title="Nova Tarefa">
                <Plus class="w-4 h-4" />
            </button>
            <button onclick={() => isMenuOpen = !isMenuOpen} class="text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-800" title="Configurações da Categoria">
                <Settings class="w-4 h-4" />
            </button>

            <!-- Category Settings Popover -->
            {#if isMenuOpen}
                <div class="absolute top-full right-0 mt-1 w-40 bg-white dark:bg-[#12192b] border border-slate-200 dark:border-slate-700 shadow-xl rounded-lg overflow-hidden z-30">
                    <button onclick={renameColumn} class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2 cursor-pointer">
                        <Edit2 class="w-3 h-3"/> Renomear
                    </button>
                    <button onclick={deleteColumn} class="w-full text-left px-4 py-2 text-sm text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/30 flex items-center gap-2 cursor-pointer">
                        <Trash2 class="w-3 h-3"/> Excluir
                    </button>
                </div>
            {/if}
        </div>
    </div>
    
    <!-- Add Task Inline Input -->
    {#if isAddingTask}
        <div class="p-3 pb-0 bg-slate-50 dark:bg-[#0c1324] shrink-0 flex flex-col gap-2 animate-in slide-in-from-top-2">
            <input type="text" bind:value={newTaskTitle} placeholder="Título da nova tarefa..." class="w-full text-sm p-2.5 rounded-lg border border-blue-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 bg-white dark:bg-[#12192b] text-slate-800 dark:text-slate-200 shadow-sm" onkeydown={(e) => { if(e.key === 'Enter') submitTask(); else if(e.key === 'Escape') isAddingTask = false; }} autofocus />
            <div class="flex gap-2">
                <button onclick={submitTask} class="flex-1 bg-slate-800 hover:bg-slate-900 text-white text-[11px] font-bold py-1.5 rounded-md shadow-sm transition-colors cursor-pointer">Salvar</button>
                <button onclick={() => isAddingTask = false} class="flex-1 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-[11px] font-bold py-1.5 rounded-md shadow-sm transition-colors cursor-pointer">Cancelar</button>
            </div>
        </div>
    {/if}

    <!-- Column Cards Dropzone -->
    <div 
        class="p-3 flex-1 overflow-y-auto space-y-3 custom-scrollbar transition-colors min-h-[150px] rounded-b-xl"
        use:dndzone={{items: columnTasks, flipDurationMs: 200, dropTargetStyle: {}, type: 'task'}}
        onconsider={handleDndConsider}
        onfinalize={handleDndFinalize}
    >
        {#each columnTasks as task (task.id)}
            <div animate:flip={{duration: 200}}>
                <KanbanCard {task} {colStatus} />
            </div>
        {/each}
    </div>
</section>
