<script lang="ts">
    import { Plus } from 'lucide-svelte';
    import KanbanColumn from './KanbanColumn.svelte';
    import { updateProjectAPI, type Project } from '$lib/projects.svelte';

    let { project }: { project: Project } = $props();

    let columns = $derived(
        project.columns_json ? JSON.parse(project.columns_json) : ['To Do', 'In Progress', 'Done']
    );

    async function addColumn() {
        const newColName = prompt("Nome da Nova Categoria:");
        if (newColName && newColName.trim() !== '') {
            // Prevent duplicates blindly
            if (!columns.includes(newColName.trim())) {
                let newCols = [...columns, newColName.trim()];
                await updateProjectAPI(project.id, { columns_json: JSON.stringify(newCols) });
            } else {
                alert("Categoria já existe!");
            }
        }
    }
</script>

<div class="flex flex-col h-full shrink-0">
    <div class="flex h-full gap-6 items-start min-w-max pb-4 pr-10">
        {#each columns as colStatus}
            <KanbanColumn {colStatus} {project} {columns} />
        {/each}

        <button onclick={addColumn} class="w-80 h-16 flex items-center justify-center gap-2 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl text-slate-500 dark:text-slate-400 font-bold hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-400 dark:hover:border-slate-600 hover:text-slate-600 dark:hover:text-slate-300 transition shrink-0 cursor-pointer">
            <Plus class="w-5 h-5" />
            Nova Categoria
        </button>
    </div>
</div>
