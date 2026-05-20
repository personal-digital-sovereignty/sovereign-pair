<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { globalState } from '$lib/state.svelte';
    import { Plus, ArrowLeft, Archive, FolderKanban, BarChart2, Edit2, Search, X } from 'lucide-svelte';
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
    let isProjectAssistantOpen = $state(false);
    let isHubAssistantOpen = $state(false);

    let isEditingSettings = $state(false);
    let editName = $state('');
    let editPurpose = $state('');
    let searchQuery = $state('');

    let filteredProjects = $derived(
        projectState.projects.filter(p => {
            const matchesTab = activeTab === 'active' ? !p.is_archived : p.is_archived;
            const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || (p.purpose || '').toLowerCase().includes(searchQuery.toLowerCase());
            return matchesTab && matchesSearch;
        })
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

    $effect(() => {
        if (activeProjectId) {
            isHubAssistantOpen = false;
        } else {
            isProjectAssistantOpen = false;
        }
    });

    onMount(() => {
        fetchProjects();
    });
</script>

<div class="flex flex-col h-full w-full bg-[#F4F7FA] dark:bg-[#12192b] font-sans transition-colors duration-200">
    
    {#if activeProject}
        <!-- ================= PROJECT DETAIL VIEW (KANBAN) ================= -->
        <header class="min-h-[140px] px-8 py-5 flex items-start justify-between bg-transparent shrink-0 border-b border-slate-200/60 dark:border-slate-800/60 transition-colors">
            <div class="flex items-start gap-6 w-full max-w-3xl">
                <button onclick={() => activeProjectId = null} class="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors cursor-pointer mt-1">
                    <ArrowLeft class="w-5 h-5" />
                </button>
                <div class="flex flex-col w-full">
                    {#if isEditingSettings}
                        <input type="text" bind:value={editName} onkeydown={(e) => e.key === 'Enter' && saveSettings()} class="font-bold text-slate-800 dark:text-slate-200 text-2xl tracking-wide bg-white dark:bg-[#0c1324] border border-blue-300 dark:border-slate-700 rounded px-3 py-1 outline-none shadow-sm focus:ring-2 focus:ring-blue-500 w-full mb-2" placeholder="Nome do Projeto..."/>
                        <textarea bind:value={editPurpose} class="text-sm text-slate-600 dark:text-slate-300 bg-white dark:bg-[#0c1324] border border-blue-300 dark:border-slate-700 rounded px-3 py-2 outline-none shadow-sm focus:ring-2 focus:ring-blue-500 resize-none custom-scrollbar w-full" rows="2" placeholder="Descreva qual o propósito ou métrica de sucesso deste projeto..."></textarea>
                        <div class="flex gap-2 mt-3">
                            <button onclick={saveSettings} class="bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-bold px-4 py-1.5 rounded shadow-sm transition cursor-pointer">Salvar Alterações</button>
                            <button onclick={() => isEditingSettings = false} class="bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-bold px-4 py-1.5 rounded shadow-sm transition cursor-pointer">Cancelar</button>
                        </div>
                    {:else}
                        <div 
                            role="button"
                            tabindex="0"
                            onkeydown={(e) => e.key === 'Enter' && startEditing()}
                            onclick={startEditing} 
                            class="group flex flex-col items-start cursor-text hover:bg-white dark:hover:bg-[#0c1324] hover:shadow-sm px-3 py-1.5 rounded-xl transition -ml-3 w-fit border border-transparent hover:border-blue-100 dark:hover:border-slate-800" 
                            title="Editar Título/Propósito">
                            <h1 class="font-bold text-slate-800 dark:text-slate-200 text-3xl tracking-wide flex items-center gap-3">
                                {activeProject.name}
                                <Edit2 class="w-4 h-4 text-slate-300 dark:text-slate-500 group-hover:text-blue-500 opacity-0 group-hover:opacity-100 transition" />
                            </h1>
                            <p class="text-sm font-medium text-slate-500 dark:text-slate-400 mt-1 w-full max-w-xl group-hover:text-slate-600 dark:group-hover:text-slate-300">
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
                <button onclick={() => toggleArchive(activeProject!)} class="text-sm font-bold px-4 py-2 rounded-lg {activeProject.is_archived ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 hover:opacity-80' : 'bg-slate-200 text-slate-700 hover:bg-slate-300 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700'} transition cursor-pointer flex items-center gap-2">
                    <Archive class="w-4 h-4" />
                    {activeProject.is_archived ? 'Desarquivar Projeto' : 'Arquivar Projeto'}
                </button>
                <span class="text-[11px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider">
                    {activeProject.tasks.length} {activeProject.tasks.length === 1 ? 'Tarefa' : 'Tarefas'} no Fluxo
                </span>
            </div>
        </header>

        <div class="flex-1 flex overflow-hidden relative min-h-0">
            <main class="flex-1 overflow-auto px-8 pt-6 relative flex flex-col min-w-0 custom-scrollbar">
                <div class="w-max min-w-full h-full flex flex-col pb-4 pr-4">
                    <div class="min-w-[900px] shrink-0">
                        <ProjectDocuments project={activeProject} />
                    </div>
                    <div class="flex-1 min-h-0 mt-4">
                        <KanbanBoard project={activeProject} />
                    </div>
                </div>
            </main>
            {#if !activeProject.is_archived}
                <ProjectAssistant project={activeProject} bind:isOpen={isProjectAssistantOpen} />
            {/if}
        </div>
    {:else}
        <!-- ================= PROJECTS OVERVIEW HUB ================= -->
        <header class="mb-6 px-10 pt-10 w-full flex items-center justify-between shrink-0">
            <div class="flex items-center gap-4">
                <h1 class="font-extrabold text-2xl text-[#191c1d] dark:text-white tracking-tight flex items-center gap-3">
                    <FolderKanban class="w-6 h-6 text-primary" />
                    Hub de Orquestração
                </h1>
            </div>

            <div class="flex items-center gap-4">
                <!-- Search Bar -->
                <div class="relative flex items-center bg-surface-container-low dark:bg-[#0c1324] rounded-full px-4 py-2 border border-outline-variant/10 dark:border-slate-800 shadow-sm w-[300px]">
                    <Search class="w-4 h-4 text-on-surface-variant dark:text-slate-400 mr-3" />
                    <input type="text" bind:value={searchQuery} placeholder="Buscar projetos..." class="bg-transparent border-none text-sm font-medium text-on-surface dark:text-slate-200 w-full focus:outline-none placeholder:text-on-surface-variant/50 dark:placeholder:text-slate-500" />
                    {#if searchQuery}
                        <button onclick={() => searchQuery = ''} class="text-on-surface-variant dark:text-slate-400 hover:text-on-surface dark:hover:text-slate-200 transition"><X class="w-4 h-4"/></button>
                    {/if}
                </div>
                
                <!-- Pill Menu -->
                <div class="flex items-center gap-1 bg-surface-container-low dark:bg-[#0c1324] p-1.5 rounded-xl border border-outline-variant/10 dark:border-slate-800">
                    <button onclick={() => activeTab = 'active'} class="px-4 py-2 {activeTab === 'active' ? 'bg-white dark:bg-slate-800 text-primary dark:text-blue-400 shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800/50'} font-bold text-xs rounded-lg transition-colors cursor-pointer">
                        Projetos Ativos ({projectState.projects.filter(p => !p.is_archived).length})
                    </button>
                    <button onclick={() => activeTab = 'archived'} class="px-4 py-2 {activeTab === 'archived' ? 'bg-white dark:bg-slate-800 text-primary dark:text-blue-400 shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800/50'} font-bold text-xs rounded-lg transition-colors cursor-pointer">
                        Gaveta ({projectState.projects.filter(p => p.is_archived).length})
                    </button>
                </div>

                <!-- Add Project Action -->
                {#if isAddingProject}
                    <div class="flex items-center gap-2 bg-white dark:bg-[#0c1324] p-1.5 rounded-xl border border-primary/20 dark:border-blue-900/50 shadow-sm ml-2">
                        <input type="text" bind:value={newProjectName} class="px-3 py-1.5 text-sm font-bold bg-transparent focus:outline-none min-w-[150px] text-slate-800 dark:text-slate-200" placeholder="Nome..." onkeydown={(e) => e.key === 'Enter' && submitProject()} />
                        <button onclick={submitProject} class="bg-primary hover:bg-primary/90 text-white px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition">Lançar</button>
                        <button onclick={() => {isAddingProject = false; newProjectName = '';}} class="px-2 py-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition"><X class="w-4 h-4"/></button>
                    </div>
                {:else}
                    <button onclick={() => isAddingProject = true} class="bg-primary text-white p-2.5 rounded-xl hover:bg-primary/90 transition shadow-sm cursor-pointer ml-2">
                        <Plus class="w-5 h-5" />
                    </button>
                {/if}
            </div>
        </header>

        <div class="flex-1 flex overflow-hidden relative min-h-0">
            <main class="flex-1 overflow-auto px-8 pt-6 relative flex flex-col min-w-0 custom-scrollbar">
                <div class="w-max min-w-full h-full flex flex-col pb-4 pr-4">
                    <div class="min-w-[960px] shrink-0">
                        <HubTelemetry />
                    </div>
                    
                    {#if projectState.isLoading}
                        <div class="w-full flex justify-center py-20 text-slate-500 dark:text-slate-400 text-sm font-bold animate-pulse uppercase tracking-wider">
                            Lendo Matrizes de Dados...
                        </div>
                    {:else if filteredProjects.length === 0}
                        <div class="flex flex-col items-center justify-center py-32 text-slate-400 dark:text-slate-500">
                            <FolderKanban class="w-16 h-16 mb-4 opacity-30 text-slate-400 dark:text-slate-500" />
                            <p class="font-medium">Nenhum projeto encontrado nesta visão.</p>
                        </div>
                    {:else}
                        <div class="flex-1 min-h-0 pt-2 mt-4">
                            <div class="flex gap-6 w-max h-full px-2 pb-6">
                                {#each filteredProjects as project (project.id)}
                                <!-- Project Card Overview -->
                                <div role="button" tabindex="0" onkeydown={(e) => { if (e.key === 'Enter') activeProjectId = project.id; }} onclick={() => activeProjectId = project.id} class="w-[320px] shrink-0 bg-white/80 dark:bg-[#0c1324]/80 backdrop-blur-sm border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-[0_2px_8px_rgba(0,0,0,0.04)] dark:shadow-none hover:shadow-xl hover:border-blue-300 dark:hover:border-blue-500/50 hover:-translate-y-1 transition-all cursor-pointer group flex flex-col h-48 text-left">
                            <div class="flex justify-between items-start mb-2 gap-4">
                                <h3 class="font-bold text-lg text-slate-800 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition truncate flex-1">{project.name}</h3>
                                <div role="button" tabindex="0" onkeydown={(e) => { if (e.key === 'Enter') { e.stopPropagation(); toggleArchive(project); } }} class="p-1.5 bg-slate-50 dark:bg-slate-800/80 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded border border-slate-100 dark:border-slate-700 text-slate-400 dark:text-slate-500 group-hover:text-rose-500 dark:group-hover:text-rose-400 transition cursor-pointer" onclick={(e) => { e.stopPropagation(); toggleArchive(project); }} title="Mover para gaveta">
                                    <Archive class="w-3.5 h-3.5" />
                                </div>
                            </div>
                            
                            <p class="text-xs text-slate-500 dark:text-slate-400 flex-1 line-clamp-3 leading-relaxed mt-1 font-medium">
                                {project.purpose || 'Nenhum propósito definido ainda. Entre no Quadro para editar as propriedades.'}
                            </p>
                            
                            <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-bold">
                                <div class="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800/60 px-2 py-1 rounded">
                                    <BarChart2 class="w-3.5 h-3.5 text-blue-500 dark:text-blue-400" />
                                    <span>{project.tasks.length} {project.tasks.length === 1 ? 'Tarefa' : 'Tarefas'}</span>
                                </div>
                                
                                <span class="px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-[4px] font-bold uppercase tracking-wider text-[10px]">
                                    {project.traction_status || 'Ideação'}
                                </span>
                                </div>
                            </div>
                            {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </main>
            <HubAssistant bind:isOpen={isHubAssistantOpen} />
        </div>
    {/if}
</div>
