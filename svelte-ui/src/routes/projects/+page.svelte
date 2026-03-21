<script lang="ts">
    import { onMount } from 'svelte';
    import { Plus, ArrowLeft, Archive, FolderKanban, BarChart2, Edit2 } from 'lucide-svelte';
    import { projectState, fetchProjects, createProject, updateProjectAPI } from '$lib/projects.svelte';
    import KanbanBoard from '$lib/components/kanban/KanbanBoard.svelte';
    import ProjectDocuments from '$lib/components/kanban/ProjectDocuments.svelte';
    import HubTelemetry from '$lib/components/kanban/HubTelemetry.svelte';
    import ProjectTelemetry from '$lib/components/kanban/ProjectTelemetry.svelte';
    import ProjectAssistant from '$lib/components/kanban/ProjectAssistant.svelte';
    import HubAssistant from '$lib/components/kanban/HubAssistant.svelte';

    let isAddingProject = $state(false);
    let newProjectName = $state('');
    let activeProjectId = $state<string | null>(null);
    let activeTab = $state<'active' | 'archived'>('active');

    let isEditingSettings = $state(false);
    let editName = $state('');
    let editPurpose = $state('');

    let filteredProjects = $derived(
        projectState.projects.filter(p => activeTab === 'active' ? !p.is_archived : p.is_archived)
    );

    let activeProject = $derived(
        projectState.projects.find(p => p.id === activeProjectId)
    );

    async function submitProject() {
        await createProject(newProjectName);
        isAddingProject = false;
        newProjectName = '';
    }

    async function toggleArchive(proj: import('$lib/projects.svelte').Project) {
        await updateProjectAPI(proj.id, { is_archived: !proj.is_archived });
    }

    function startEditing() {
        if (activeProject) {
            editName = activeProject.name;
            editPurpose = activeProject.purpose || '';
            isEditingSettings = true;
        }
    }

    async function saveSettings() {
        if (activeProject && editName.trim()) {
            await updateProjectAPI(activeProject.id, { 
                name: editName.trim(), 
                purpose: editPurpose.trim() 
            });
            // Optionally refresh or trust local reactivity
            isEditingSettings = false;
        }
    }

    $effect(() => {
        if (!activeProjectId) isEditingSettings = false;
    });

    onMount(() => {
        fetchProjects();
    });
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] font-sans">
    
    {#if activeProject}
        <!-- ================= PROJECT DETAIL VIEW (KANBAN) ================= -->
        <header class="min-h-[140px] px-8 py-5 flex items-start justify-between bg-transparent shrink-0 border-b border-slate-200/60">
            <div class="flex items-start gap-6 w-full max-w-3xl">
                <button onclick={() => activeProjectId = null} class="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-full transition-colors cursor-pointer mt-1">
                    <ArrowLeft class="w-5 h-5" />
                </button>
                <div class="flex flex-col w-full">
                    {#if isEditingSettings}
                        <input type="text" bind:value={editName} onkeydown={(e) => e.key === 'Enter' && saveSettings()} class="font-bold text-slate-800 text-2xl tracking-wide bg-white border border-blue-300 rounded px-3 py-1 outline-none shadow-sm focus:ring-2 focus:ring-blue-500 w-full mb-2" placeholder="Nome do Projeto..."/>
                        <textarea bind:value={editPurpose} class="text-sm text-slate-600 bg-white border border-blue-300 rounded px-3 py-2 outline-none shadow-sm focus:ring-2 focus:ring-blue-500 resize-none custom-scrollbar w-full" rows="2" placeholder="Descreva qual o propósito ou métrica de sucesso deste projeto..."></textarea>
                        <div class="flex gap-2 mt-3">
                            <button onclick={saveSettings} class="bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold px-4 py-1.5 rounded shadow-sm transition cursor-pointer">Salvar Alterações</button>
                            <button onclick={() => isEditingSettings = false} class="bg-slate-200 hover:bg-slate-300 text-slate-600 text-xs font-bold px-4 py-1.5 rounded shadow-sm transition cursor-pointer">Cancelar</button>
                        </div>
                    {:else}
                        <div 
                            role="button"
                            tabindex="0"
                            onkeydown={(e) => e.key === 'Enter' && startEditing()}
                            onclick={startEditing} 
                            class="group flex flex-col items-start cursor-text hover:bg-white hover:shadow-sm px-3 py-1.5 rounded-xl transition -ml-3 w-fit border border-transparent hover:border-blue-100" 
                            title="Editar Título/Propósito">
                            <h1 class="font-bold text-slate-800 text-3xl tracking-wide flex items-center gap-3">
                                {activeProject.name}
                                <Edit2 class="w-4 h-4 text-slate-300 group-hover:text-blue-500 opacity-0 group-hover:opacity-100 transition" />
                            </h1>
                            <p class="text-sm font-medium text-slate-500 mt-1 w-full max-w-xl group-hover:text-slate-600">
                                {activeProject.purpose || '💡 Clique aqui para definir o propósito raiz deste projeto...'}
                            </p>
                        </div>
                    {/if}
                    <div class="mt-4 w-full pr-8">
                        <ProjectTelemetry project={activeProject} />
                    </div>
                </div>
            </div>
            <div class="flex flex-col items-end gap-3 mt-1">
                <button onclick={() => toggleArchive(activeProject!)} class="text-sm font-bold px-4 py-2 rounded-lg {activeProject.is_archived ? 'bg-emerald-100 text-emerald-700 hover:opacity-80' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'} transition cursor-pointer flex items-center gap-2">
                    <Archive class="w-4 h-4" />
                    {activeProject.is_archived ? 'Desarquivar Projeto' : 'Arquivar Projeto'}
                </button>
                <span class="text-[11px] text-slate-400 font-bold uppercase tracking-wider">
                    {activeProject.tasks.length} {activeProject.tasks.length === 1 ? 'Tarefa' : 'Tarefas'} no Fluxo
                </span>
            </div>
        </header>

        <main class="flex-1 overflow-x-auto overflow-y-hidden px-8 pt-6 pb-8 custom-scrollbar relative flex flex-col">
            <ProjectDocuments project={activeProject} />
            <div class="flex-1 overflow-y-hidden min-h-0">
                <KanbanBoard project={activeProject} />
            </div>
        </main>
        
    {:else}
        <!-- ================= PROJECTS OVERVIEW HUB ================= -->
        <header class="h-32 px-10 flex flex-col justify-center bg-transparent shrink-0 space-y-4 border-b border-slate-200/50">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="font-bold text-slate-800 text-3xl tracking-wide flex items-center gap-3">
                        <FolderKanban class="w-8 h-8 text-blue-600"/>
                        Hub de Orquestração
                    </h1>
                    <p class="text-sm text-slate-500 mt-1 font-medium">Gerencie e orquestre todas as suas iniciativas Cíbridas num só local.</p>
                </div>
                
                {#if isAddingProject}
                    <div class="flex items-center gap-2 bg-white p-1.5 rounded-xl border border-slate-200 shadow-sm">
                        <input type="text" bind:value={newProjectName} class="px-3 py-1.5 text-sm font-bold bg-transparent focus:outline-none min-w-[200px]" placeholder="Nome do Novo Projeto..." onkeydown={(e) => e.key === 'Enter' && submitProject()} />
                        <button onclick={submitProject} class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition">Lançar</button>
                        <button onclick={() => {isAddingProject = false; newProjectName = '';}} class="bg-slate-100 hover:bg-slate-200 text-slate-500 px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition">X</button>
                    </div>
                {:else}
                    <button onclick={() => isAddingProject = true} class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold flex items-center transition-colors shadow-md cursor-pointer">
                        <Plus class="w-5 h-5 mr-2" />
                        Novo Projeto
                    </button>
                {/if}
            </div>
            
            <!-- Tabs -->
            <div class="flex gap-6 pb-0.5 mt-2">
                <button onclick={() => activeTab = 'active'} class="text-sm font-bold pb-2 border-b-2 {activeTab === 'active' ? 'border-blue-600 text-blue-700' : 'border-transparent text-slate-400 hover:text-slate-800'} transition cursor-pointer">
                    Projetos Ativos ({projectState.projects.filter(p => !p.is_archived).length})
                </button>
                <button onclick={() => activeTab = 'archived'} class="text-sm font-bold pb-2 border-b-2 {activeTab === 'archived' ? 'border-amber-500 text-amber-700' : 'border-transparent text-slate-400 hover:text-slate-800'} transition cursor-pointer">
                    Gaveta de Arquivos ({projectState.projects.filter(p => p.is_archived).length})
                </button>
            </div>
        </header>

        <main class="flex-1 overflow-y-auto px-10 pt-6 pb-8 custom-scrollbar">
            <HubTelemetry />
            
            <div class="flex gap-8 items-start">
                <div class="flex-1">
                    {#if projectState.isLoading}
                        <div class="w-full flex justify-center py-20 text-slate-500 text-sm font-bold animate-pulse uppercase tracking-wider">
                            Lendo Matrizes de Dados...
                        </div>
                    {:else if filteredProjects.length === 0}
                <div class="flex flex-col items-center justify-center py-32 text-slate-400">
                    <FolderKanban class="w-16 h-16 mb-4 opacity-30 text-slate-400" />
                    <p class="font-medium">Nenhum projeto encontrado nesta visão.</p>
                </div>
            {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {#each filteredProjects as project (project.id)}
                        <!-- Project Card Overview -->
                        <div onclick={() => activeProjectId = project.id} class="bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-xl hover:border-blue-300 hover:-translate-y-1 transition-all cursor-pointer group flex flex-col h-48">
                            <div class="flex justify-between items-start mb-2 gap-4">
                                <h3 class="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition truncate flex-1">{project.name}</h3>
                                <div role="button" tabindex="0" onkeydown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); toggleArchive(project); } }} class="p-1.5 bg-slate-50 hover:bg-rose-50 rounded border border-slate-100 text-slate-400 group-hover:text-rose-500 transition cursor-pointer" onclick={(e) => { e.stopPropagation(); toggleArchive(project); }} title="Mover para gaveta">
                                    <Archive class="w-3.5 h-3.5" />
                                </div>
                            </div>
                            
                            <p class="text-xs text-slate-500 flex-1 line-clamp-3 leading-relaxed mt-1 font-medium">
                                {project.purpose || 'Nenhum propósito definido ainda. Entre no Quadro para editar as propriedades.'}
                            </p>
                            
                            <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-bold">
                                <div class="flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded">
                                    <BarChart2 class="w-3.5 h-3.5 text-blue-500" />
                                    <span>{project.tasks.length} {project.tasks.length === 1 ? 'Tarefa' : 'Tarefas'}</span>
                                </div>
                                
                                <span class="px-2 py-1 bg-slate-100 text-slate-600 rounded-[4px] font-bold uppercase tracking-wider text-[10px]">
                                    {project.traction_status || 'Ideação'}
                                </span>
                            </div>
                        </div>
                    {/each}
                </div>
                    {/if}
                </div>
                
                <div class="w-[380px] shrink-0 sticky top-0">
                    <HubAssistant />
                </div>
            </div>
        </main>
    {/if}

    {#if activeProject && !activeProject.is_archived}
        <ProjectAssistant project={activeProject} />
    {/if}
</div>
