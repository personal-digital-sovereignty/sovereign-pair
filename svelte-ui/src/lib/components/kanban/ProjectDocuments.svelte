<script lang="ts">
    import { onMount } from 'svelte';
    import { FileText, Link2, X, AlertCircle } from 'lucide-svelte';
    import { fetchProjectDocuments, linkProjectDocument, unlinkProjectDocument, type Project } from '$lib/projects.svelte';
    import { globalState } from '$lib/state.svelte';

    let { project }: { project: Project } = $props();

    let linkedDocs = $state<any[]>([]);
    let isLinking = $state(false);
    let newDocPath = $state('');
    let isLoading = $state(true);
    let availableFiles = $state<string[]>([]);
    let showDropdown = $state(false);

    async function loadWorkspaceFiles() {
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const activeId = globalState.activeWorkspaceId || 'mesh_roaming';
            const res = await fetch(`http://localhost:38001/v1/workspaces/${activeId}/tree`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const tree = await res.json();
                const paths: string[] = [];
                function extractPaths(node: any) {
                    if (!node.is_dir) paths.push(node.path);
                    if (node.children) node.children.forEach(extractPaths);
                }
                if (Array.isArray(tree)) tree.forEach(extractPaths);
                availableFiles = paths;
            }
        } catch (e) {
            console.error("Erro ao ler cofre", e);
        }
    }

    async function loadDocs() {
        isLoading = true;
        linkedDocs = await fetchProjectDocuments(project.id);
        isLoading = false;
    }

    async function submitLink() {
        if (newDocPath.trim()) {
            await linkProjectDocument(project.id, newDocPath.trim());
            newDocPath = '';
            isLinking = false;
            await loadDocs();
        }
    }

    async function removeLink(filePath: string) {
        await unlinkProjectDocument(project.id, filePath);
        await loadDocs();
    }

    onMount(() => {
        loadDocs();
        loadWorkspaceFiles();
    });

    $effect(() => {
        // Reload if project changes
        if (project.id) {
            loadDocs();
        }
    });
</script>

<div class="bg-white dark:bg-[#0c1324] rounded-xl border border-slate-200/60 dark:border-slate-800/60 p-4 shadow-sm mb-6 flex flex-col gap-3 shrink-0">
    <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
            <Link2 class="w-4 h-4 text-blue-500 dark:text-blue-400" /> 
            Documentos Cíbridos Anexados
        </h3>
        {#if !isLinking}
            <button onclick={() => isLinking = true} class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 bg-blue-50 dark:bg-blue-900/40 hover:bg-blue-100 dark:hover:bg-blue-900/60 px-3 py-1.5 rounded-lg transition-colors cursor-pointer">
                + Vincular Arquivo
            </button>
        {/if}
    </div>

    {#if isLinking}
        <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800/50 p-2 rounded-lg border border-slate-200 dark:border-slate-700">
            <div class="relative flex-1">
                <input 
                    type="text" 
                    bind:value={newDocPath} 
                    placeholder="Buscar arquivo no Vault (nome, caminho)..." 
                    class="w-full text-sm bg-transparent px-2 py-1 outline-none text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500" 
                    onkeydown={(e) => e.key === 'Enter' && submitLink()}
                    onfocus={() => showDropdown = true}
                    onblur={() => setTimeout(() => showDropdown = false, 200)}
                />
                {#if showDropdown && newDocPath.trim() !== ''}
                    <div class="absolute top-full left-0 w-[400px] mt-2 bg-white dark:bg-[#12192b] border border-slate-200 dark:border-slate-700 shadow-xl rounded-lg overflow-hidden z-50 max-h-64 overflow-y-auto custom-scrollbar">
                        {#each availableFiles.filter(f => f.toLowerCase().includes(newDocPath.toLowerCase())) as file}
                            <button 
                                onclick={() => { newDocPath = file; showDropdown = false; setTimeout(submitLink, 50); }} 
                                class="w-full text-left px-4 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-slate-800 border-b border-slate-50 dark:border-slate-800/50 cursor-pointer break-words">
                                {file}
                            </button>
                        {:else}
                            <div class="px-4 py-3 text-xs text-slate-400 dark:text-slate-500 italic">Nenhum documento encontrado com '{newDocPath}'</div>
                        {/each}
                    </div>
                {/if}
            </div>
            <button onclick={submitLink} class="bg-blue-600 dark:bg-blue-500 text-white px-3 py-1.5 rounded shadow-sm text-xs font-bold hover:bg-blue-700 dark:hover:bg-blue-600 transition cursor-pointer">Anexar</button>
            <button onclick={() => isLinking = false} class="bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-1.5 rounded text-xs font-bold hover:bg-slate-300 dark:hover:bg-slate-600 transition cursor-pointer">X</button>
        </div>
    {/if}

    {#if isLoading}
        <div class="text-xs text-slate-400 dark:text-slate-500 animate-pulse py-2">Carregando links espaciais...</div>
    {:else if linkedDocs.length === 0}
        <div class="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500 py-2">
            <AlertCircle class="w-4 h-4 opacity-50" />
            Nenhum documento da Vault foi ancorado a este projeto ainda.
        </div>
    {:else}
        <div class="flex flex-wrap gap-3 mt-1">
            {#each linkedDocs as doc}
                <div class="group relative flex items-center gap-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-100/50 dark:border-blue-800/50 rounded-lg px-3 py-2 pr-8 shadow-[0_1px_2px_rgba(0,0,0,0.02)] transition-colors hover:bg-blue-100/50 dark:hover:bg-blue-900/40 hover:border-blue-200 dark:hover:border-blue-700">
                    <a href="/vault?file={encodeURIComponent(doc.file_path)}&fromProject={project.id}" class="flex items-center gap-2 flex-1 hover:underline text-blue-700 dark:text-blue-400" title="Abrir no Vault: {doc.file_path}">
                        <FileText class="w-4 h-4 shrink-0" />
                        <span class="text-xs font-medium truncate max-w-[200px]">
                            {doc.file_path.split('/').pop()}
                        </span>
                    </a>
                    <button onclick={() => removeLink(doc.file_path)} class="absolute right-2 text-slate-400 dark:text-slate-500 hover:text-rose-500 dark:hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" title="Desvincular">
                        <X class="w-3.5 h-3.5" />
                    </button>
                </div>
            {/each}
        </div>
    {/if}
</div>
