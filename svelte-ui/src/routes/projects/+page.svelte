<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { globalState } from '$lib/state.svelte';
    import { Plus, GripVertical, Trash2, Calendar, Settings, CheckCircle, ArrowRight, Folder } from 'lucide-svelte';

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
                if (data && Array.isArray(data) && data.length > 0) {
                    projects = data;
                }
            }
        } catch (e) {
            console.error("Falha ao buscar projetos", e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        // Fallback mockup
        projects = [
            { id: '1', name: 'Sovereign Core', tasks: [
                { id: 't1', title: 'Implement neural network core', content: 'Develop and integrate...', status: 'To Do' },
                { id: 't2', title: 'Refine RAG query optimizer', content: 'Optimize retrieval-augmented...', status: 'In Progress' },
                { id: 't3', title: 'Deploy initial agent swarm', content: 'Successfully deployed...', status: 'Done' }
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

        projects.forEach((p, pIdx) => {
            const tIdx = p.tasks.findIndex(t => t.id === taskId);
            if (tIdx > -1) {
                taskToMove = p.tasks[tIdx];
                sourceProjectIndex = pIdx;
                taskIndex = tIdx;
            }
        });

        if (taskToMove && sourceProjectIndex > -1) {
            projects[sourceProjectIndex].tasks.splice(taskIndex, 1);
            taskToMove.status = newStatus;
            const targetProjectIndex = projects.findIndex(p => p.id === projectId);
            
            if (targetProjectIndex > -1) {
                projects[targetProjectIndex].tasks.push(taskToMove);
                projects = [...projects]; 
            }
        }
    }
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] font-sans">
    
    <!-- Top Header -->
    <header class="h-20 px-8 flex items-center justify-between bg-transparent shrink-0">
        <h1 class="font-bold text-slate-800 text-3xl tracking-wide">Project Kanban Workspace</h1>
        <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors shadow-sm cursor-pointer">
            <Plus class="w-4 h-4 mr-2" />
            New Project
        </button>
    </header>

    <main class="flex-1 overflow-x-auto overflow-y-hidden px-8 pb-8 custom-scrollbar">
        {#if isLoading && projects.length === 0}
            <div class="w-full flex justify-center py-20 text-slate-500 text-sm animate-pulse">
                Carregando Projetos e Tarefas...
            </div>
        {:else}
            <!-- Render a horizontal board for each project (if multiple, they stack vertically or horizontally) -->
            <div class="flex flex-col gap-12 h-full">
                {#each projects as project}
                    <div class="flex flex-col h-full shrink-0">
                        {#if projects.length > 1}
                            <div class="flex items-center justify-between mb-4 px-2">
                                <h2 class="text-xl font-bold text-slate-700 flex items-center gap-2">
                                    <Folder class="w-5 h-5 text-blue-500" />
                                    {project.name}
                                </h2>
                                <button class="text-rose-400 hover:text-rose-600 p-2 cursor-pointer"><Trash2 class="w-4 h-4"/></button>
                            </div>
                        {/if}
                        
                        <div class="flex h-full gap-6 items-start min-w-max pb-4">
                            {#each ['To Do', 'In Progress', 'Done'] as colStatus}
                                <!-- Column -->
                                <section class="w-80 flex flex-col rounded-xl border border-slate-200 shadow-sm max-h-full bg-slate-50 shrink-0">
                                    <!-- Column Header -->
                                    <div class="p-4 flex items-center justify-between border-b border-slate-200/60 bg-white/50 rounded-t-xl shrink-0">
                                        <h2 class="font-semibold text-slate-800 text-lg">{colStatus}</h2>
                                        <div class="flex items-center gap-2">
                                            <span class="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded-full">
                                                {project.tasks.filter(t => t.status === colStatus).length}
                                            </span>
                                            <button class="text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"><Settings class="w-4 h-4" /></button>
                                        </div>
                                    </div>
                                    
                                    <!-- Column Cards Dropzone -->
                                    <div 
                                        class="p-3 flex-1 overflow-y-auto space-y-3 custom-scrollbar {draggingTaskId ? 'bg-blue-50/50' : ''} transition-colors min-h-[150px] rounded-b-xl"
                                        ondragover={(e) => handleDragOver(e, colStatus, project.id)}
                                        ondrop={(e) => handleDrop(e, colStatus, project.id)}
                                    >
                                        {#each project.tasks.filter(t => t.status === colStatus) as task}
                                            <!-- Task Card -->
                                            <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
                                            <article 
                                                class="bg-white p-4 rounded-lg shadow-md border border-slate-100 hover:shadow-lg transition-all cursor-grab active:cursor-grabbing group"
                                                draggable="true"
                                                ondragstart={(e) => handleDragStart(e, task.id)}
                                                ondragend={handleDragEnd}
                                            >
                                                <div class="flex items-start justify-between gap-3 mb-3">
                                                    <h3 class="font-semibold text-slate-800 text-sm leading-tight pr-4">{task.title}</h3>
                                                    <GripVertical class="w-4 h-4 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                                                </div>
                                                {#if task.content}
                                                    <p class="text-slate-500 text-xs mb-4 leading-relaxed line-clamp-3">{task.content}</p>
                                                {/if}
                                                <div class="flex items-center justify-between mt-auto pt-2 border-t border-slate-50">
                                                    <div class="text-xs text-slate-500 font-medium flex items-center gap-1">
                                                        <Calendar class="w-3 h-3" /> Hoje
                                                    </div>
                                                    {#if colStatus === 'Done'}
                                                        <div class="flex items-center gap-1">
                                                            <span class="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-1 rounded border border-green-200">Completed</span>
                                                            <CheckCircle class="text-emerald-600 w-3 h-3" />
                                                        </div>
                                                    {:else if colStatus === 'In Progress'}
                                                        <div class="flex items-center gap-1">
                                                            <span class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-1 rounded border border-blue-200">Active</span>
                                                            <ArrowRight class="text-blue-500 w-3 h-3" />
                                                        </div>
                                                    {:else}
                                                        <div class="flex items-center gap-1">
                                                            <span class="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-1 rounded border border-slate-200">Pending</span>
                                                        </div>
                                                    {/if}
                                                </div>
                                            </article>
                                        {/each}
                                    </div>
                                    
                                    <!-- Add Task Button -->
                                    <div class="p-3 border-t border-slate-200/60 bg-white/50 rounded-b-xl shrink-0 flex justify-center">
                                        <button class="bg-blue-600 hover:bg-blue-700 text-white py-1.5 rounded-md text-sm font-medium flex items-center justify-center transition-colors shadow-sm px-6 w-full cursor-pointer">
                                            <Plus class="w-4 h-4 mr-2" /> Add Task
                                        </button>
                                    </div>
                                </section>
                            {/each}
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </main>

    <!-- BEGIN: System Status Widget (Absolute bottom right) -->
    <div class="fixed bottom-6 right-8 bg-white/90 backdrop-blur-sm border border-slate-200 p-4 rounded-xl shadow-lg flex items-center gap-4 z-20 pointer-events-none">
        <div class="w-24 h-12 bg-slate-50 border border-slate-100 rounded flex items-end overflow-hidden relative">
            <div class="absolute inset-0 flex flex-col justify-between py-1 px-1 opacity-30">
                <div class="w-full border-b border-slate-400 border-dashed"></div>
                <div class="w-full border-b border-slate-400 border-dashed"></div>
                <div class="w-full border-b border-slate-400 border-dashed"></div>
            </div>
            <svg class="w-full h-full text-blue-500 fill-blue-100/50 relative z-10" preserveAspectRatio="none" viewBox="0 0 100 40">
                <path d="M0 40 L0 30 L10 25 L20 28 L30 15 L40 20 L50 10 L60 15 L70 5 L80 12 L90 8 L100 2 L100 40 Z" stroke="currentColor" stroke-width="1.5"></path>
            </svg>
        </div>
        <div class="text-xs font-medium space-y-1">
            <div class="flex justify-between gap-4">
                <span class="text-slate-500">System Status:</span>
                <span class="text-emerald-600 font-semibold">Online</span>
            </div>
            <div class="flex justify-between gap-4">
                <span class="text-slate-500">Nodes Connected:</span>
                <span class="text-slate-800">42</span>
            </div>
        </div>
    </div>
</div>
