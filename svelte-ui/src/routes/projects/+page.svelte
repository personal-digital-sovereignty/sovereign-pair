<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { globalState } from '$lib/state.svelte';
    import { Plus, GripVertical, Trash2, Calendar, LayoutTemplate } from 'lucide-svelte';

    type Task = { id: string, title: string, content: string, status: string };
    type Project = { id: string, name: string, tasks: Task[] };

    let projects = $state<Project[]>([]);
    let isLoading = $state(true);
    let draggingTaskId = $state<string | null>(null);

    const API_BASE_URL = 'http://localhost:38001';

    async function fetchProjects() {
        isLoading = true;
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const res = await fetch(`${API_BASE_URL}/v1/projects`, { headers: { 'Authorization': `Bearer ${token}` }});
            if (res.ok) {
                const data = await res.json();
                projects = data || [];
            }
        } catch (e) {
            console.error("Falha ao buscar projetos", e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        // Fallback mockup se a API falhar para demonstração visual rica (Epic 11 Feature Parity)
        projects = [
            { id: '1', name: 'Sovereign Core', tasks: [
                { id: 't1', title: 'Rust Telemetry Engine', content: 'Migrar a abstração em Python para C++...', status: 'Done' },
                { id: 't2', title: 'Svelte Migration', content: 'Reescrever Vue UI em Svelte...', status: 'In Progress' }
            ]},
            { id: '2', name: 'Master Plan', tasks: [
                { id: 't3', title: 'Phase 21: Cíbridos', content: 'Habilitar Múltiplos Agentes Híbridos...', status: 'To Do' }
            ]}
        ];
        fetchProjects();
    });

    // Drag and Drop Logic
    function handleDragStart(e: DragEvent, taskId: string) {
        if (e.dataTransfer) {
            e.dataTransfer.setData('text/plain', taskId);
            draggingTaskId = taskId;
            setTimeout(() => e.target && (e.target as HTMLElement).classList.add('opacity-50'), 0);
        }
    }

    function handleDragEnd(e: DragEvent) {
        draggingTaskId = null;
        if (e.target) (e.target as HTMLElement).classList.remove('opacity-50');
    }

    function handleDragOver(e: DragEvent, status: string, projectId: string) {
        e.preventDefault();
        if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
    }

    async function handleDrop(e: DragEvent, newStatus: string, projectId: string) {
        e.preventDefault();
        const taskId = e.dataTransfer?.getData('text/plain');
        if (!taskId) return;

        let taskToMove: Task | undefined;
        let sourceProjectIndex = -1;
        let taskIndex = -1;

        // Find Task
        projects.forEach((p, pIdx) => {
            const tIdx = p.tasks.findIndex(t => t.id === taskId);
            if (tIdx > -1) {
                taskToMove = p.tasks[tIdx];
                sourceProjectIndex = pIdx;
                taskIndex = tIdx;
            }
        });

        if (taskToMove && sourceProjectIndex > -1) {
            // Remove from source array
            projects[sourceProjectIndex].tasks.splice(taskIndex, 1);
            
            // Update status and push to target array
            taskToMove.status = newStatus;
            const targetProjectIndex = projects.findIndex(p => p.id === projectId);
            
            if (targetProjectIndex > -1) {
                projects[targetProjectIndex].tasks.push(taskToMove);
                projects = [...projects]; // Reatividade
            }
            
            // O ideal seria enviar PUT via API aqui.
        }
    }

</script>

<div class="flex flex-col h-full w-full bg-surface-900 border-l border-surface-700 font-sans">
    
    <header class="flex items-center justify-between p-4 md:p-6 border-b border-surface-700 bg-surface-800/80 shrink-0">
        <div class="flex items-center gap-3">
            <div class="p-2.5 bg-primary-500/10 rounded-xl">
                <LayoutTemplate class="w-6 h-6 text-primary-400" />
            </div>
            <div>
                <h2 class="text-surface-100 font-bold text-lg tracking-tight">Project Board <span class="text-[10px] bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded ml-2 uppercase tracking-widest font-mono">Kanban</span></h2>
                <p class="text-xs text-surface-400 mt-0.5">Gestão Sovereign Híbrida.</p>
            </div>
        </div>
        
        <button class="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-lg flex items-center gap-2 cursor-pointer">
            <Plus class="w-4 h-4" /> NOVO PROJETO
        </button>
    </header>

    <main class="flex-1 overflow-x-auto p-4 md:p-8 flex gap-8 custom-scrollbar items-start">
        
        {#if isLoading && projects.length === 0}
            <div class="w-full flex justify-center py-20 text-surface-500 text-sm animate-pulse">
                Carregando Projetos e Tarefas...
            </div>
        {:else}
            {#each projects as project}
                <div class="flex flex-col gap-4 min-w-[320px] max-w-[320px] bg-surface-800 rounded-2xl border border-surface-700 p-4 shrink-0 shadow-2xl relative overflow-hidden group">
                    <!-- Glow effect Decorator -->
                    <div class="absolute -top-10 -right-10 w-24 h-24 bg-primary-500/20 blur-3xl group-hover:bg-primary-500/30 transition-all z-0 pointer-events-none"></div>

                    <div class="flex items-center justify-between z-10 relative">
                        <h3 class="font-bold text-surface-200 text-sm truncate">{project.name}</h3>
                        <div class="p-1.5 rounded-lg hover:bg-rose-500/20 text-surface-500 hover:text-rose-400 cursor-pointer transition-colors" title="Deletar Projeto">
                            <Trash2 class="w-4 h-4" />
                        </div>
                    </div>

                    <!-- Divider -->
                    <div class="h-px bg-surface-700 w-full z-10"></div>
                    
                    <div class="flex flex-col gap-3 min-h-[150px] z-10 relative">
                        {#each ['To Do', 'In Progress', 'Done'] as colStatus}
                            <div class="flex flex-col gap-2">
                                <h4 class="text-[10px] font-bold tracking-widest uppercase text-surface-500">{colStatus}</h4>
                                <div 
                                    class="min-h-[40px] rounded-xl border-2 border-dashed border-surface-700/50 bg-surface-900/30 p-2 flex flex-col gap-2 transition-all {draggingTaskId ? 'border-primary-500/30 bg-primary-500/5' : ''}"
                                    ondragover={(e) => handleDragOver(e, colStatus, project.id)}
                                    ondrop={(e) => handleDrop(e, colStatus, project.id)}
                                >
                                    {#each project.tasks.filter(t => t.status === colStatus) as task}
                                        <div 
                                            class="bg-surface-800 border border-surface-600 hover:border-primary-500/50 rounded-xl p-3 flex flex-col gap-2 shadow-lg cursor-grab active:cursor-grabbing group/card transition-all"
                                            draggable="true"
                                            ondragstart={(e) => handleDragStart(e, task.id)}
                                            ondragend={handleDragEnd}
                                        >
                                            <div class="flex justify-between items-start gap-2">
                                                <h5 class="text-xs font-bold text-surface-200 leading-tight">{task.title}</h5>
                                                <GripVertical class="w-3.5 h-3.5 text-surface-600 opacity-0 group-hover/card:opacity-100 transition-all shrink-0 cursor-grab" />
                                            </div>
                                            {#if task.content}
                                                <p class="text-[10px] text-surface-400 line-clamp-2 leading-relaxed">{task.content}</p>
                                            {/if}
                                            <div class="flex justify-between items-center mt-1">
                                                <div class="flex items-center gap-1.5 text-[9px] text-surface-500">
                                                    <Calendar class="w-3 h-3" /> Hoje
                                                </div>
                                                <!-- Avatar Mock -->
                                                <div class="w-5 h-5 rounded-full bg-primary-500/20 border border-primary-500/50 flex items-center justify-center text-[8px] font-bold text-primary-400">
                                                    ME
                                                </div>
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        {/each}
                    </div>

                    <button class="w-full py-2 bg-surface-900 hover:bg-surface-900/50 border border-surface-700 hover:border-surface-600 text-surface-400 hover:text-surface-300 rounded-xl text-xs font-medium transition-colors flex items-center justify-center gap-2 mt-2 z-10 cursor-pointer">
                        <Plus class="w-3.5 h-3.5" /> Adicionar Tarefa
                    </button>
                </div>
            {/each}
        {/if}
    </main>
</div>
