<script lang="ts">
    import BlockEditor from '$lib/components/BlockEditor.svelte';
    import ChatPanel from '$lib/components/ChatPanel.svelte';
    import { globalState } from '$lib/state.svelte.js';
    import { untrack, onMount } from 'svelte';
    import { ChevronLeft, ChevronRight, X, Search, FileText, Filter, BrainCircuit, Sparkles, Plus, Trash2, Edit2, Rocket } from 'lucide-svelte';
    import { page } from '$app/stores';

    let viewState = $state<'explorer' | 'editor'>('explorer');
    let fromProject = $derived($page.url.searchParams.get('fromProject'));
    let fileParam = $derived($page.url.searchParams.get('file'));

    $effect(() => {
        if (fileParam && !tabs.find(t => t.id === fileParam)) {
            openFile(fileParam, fileParam.split('/').pop() || 'Arquivo');
            // Remove o params logico da url sem recarregar a pagina para nao ficar abrindo sempre se o cara fechar a aba
            const url = new URL(window.location.href);
            url.searchParams.delete('file');
            window.history.replaceState({}, '', url);
        }
    });

    type Tab = { id: string; name: string; type?: string };
    let tabs = $state<Tab[]>([]);
    
    let files = $state<any[]>([]);
    let isLoading = $state(true);
    let activeFilterTag = $state<string | null>(null);
    let searchQuery = $state('');
    let sortColumn = $state<string | null>('name');
    let sortAscending = $state(true);
    let showAdvancedFilters = $state(false);

    function appendFilterCmd(cmd: string) {
        if (!searchQuery.includes(cmd)) {
            searchQuery = (searchQuery + ' ' + cmd).trim() + ' ';
        }
    }

    function handleSort(column: string) {
        if (sortColumn === column) {
            sortAscending = !sortAscending;
        } else {
            sortColumn = column;
            sortAscending = true;
        }
    }

    let allTags = $derived(Array.from(new Set(files.flatMap(f => f.wikilinks || []))).slice(0, 20));
    let filteredFiles = $derived((() => {
        let result = files.filter(f => {
            const matchTag = activeFilterTag ? f.wikilinks?.includes(activeFilterTag) : true;
            let matchSearch = true;

            if (searchQuery) {
                const terms = searchQuery.toLowerCase().split(/\s+/).filter(t => t.length > 0);
                for (const term of terms) {
                    if (term.startsWith('path:')) {
                        const val = term.substring(5);
                        if (!f.path.toLowerCase().includes(val)) matchSearch = false;
                    } else if (term.startsWith('tag:') || term.startsWith('category:')) {
                        const val = term.substring(term.indexOf(':') + 1);
                        if (!(f.wikilinks && f.wikilinks.some((w: string) => w.toLowerCase().includes(val)))) matchSearch = false;
                    } else if (term.startsWith('status:')) {
                        const val = term.substring(7);
                        if (!"synced".includes(val)) matchSearch = false;
                    } else if (term.startsWith('name:')) {
                        const val = term.substring(5);
                        if (!f.name.toLowerCase().includes(val)) matchSearch = false;
                    } else {
                        // General query search in filename or tags
                        if (!(f.name.toLowerCase().includes(term) || (f.wikilinks && f.wikilinks.some((w: string) => w.toLowerCase().includes(term))))) {
                            matchSearch = false;
                        }
                    }
                }
            }
            return matchTag && matchSearch;
        });

        const col = sortColumn;
        if (col) {
            result.sort((a, b) => {
                let valA = a[col as keyof typeof a] || '';
                let valB = b[col as keyof typeof b] || '';

                if (col === 'wikilinks') {
                    valA = a.wikilinks?.join(', ') || '';
                    valB = b.wikilinks?.join(', ') || '';
                } else if (col === 'modified') {
                    valA = a.modified || 0;
                    valB = b.modified || 0;
                }
                
                if (typeof valA === 'string' && typeof valB === 'string') {
                    return sortAscending ? valA.localeCompare(valB) : valB.localeCompare(valA);
                }

                if (valA < valB) return sortAscending ? -1 : 1;
                if (valA > valB) return sortAscending ? 1 : -1;
                return 0;
            });
        }
        return result;
    })());

    const API_BASE_URL = 'http://localhost:38001';

    function flatten(nodes: any[], prefix = ''): any[] {
        let arr: any[] = [];
        for (const n of nodes) {
            if (n.is_dir) {
                arr = arr.concat(flatten(n.children || [], `${prefix}${n.name}/`));
            } else {
                arr.push({ ...n, path_dir: prefix || 'Root', wikilinks: n.wikilinks || [], date: 'Hoje', size: '2 KB' });
            }
        }
        return arr;
    }

    let folders = $state<{path: string, name: string}[]>([{path: '', name: 'Raiz do Vault'}]);
    
    function extractFolders(nodes: any[]) {
        for (const n of nodes) {
            if (n.is_dir) {
                if (n.id !== 'root') {
                    folders.push({ path: n.id, name: `📁 ${n.id}` });
                }
                extractFolders(n.children || []);
            }
        }
    }

    async function fetchFiles() {
        isLoading = true;
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            const res = await fetch(`${API_BASE_URL}/v1/workspaces/${ws_id}/tree`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (res.ok) {
                const treeNodes = await res.json();
                files = flatten(treeNodes);
                folders = [{path: '', name: 'Raiz do Vault'}];
                extractFolders(treeNodes);
            }
        } catch(e) { console.error(e); } finally { isLoading = false; }
    }

    let showCreateModal = $state(false);
    let newFileName = $state('');
    let newFileFolder = $state('');

    function createNewFile() {
        newFileName = '';
        newFileFolder = '';
        showCreateModal = true;
    }

    async function confirmCreateFile() {
        if (!newFileName.trim()) return;
        const name = newFileName.trim();
        const req = { workspace_id: Number(globalState.activeWorkspaceId), type: "file", name, path: newFileFolder };
        try {
            await fetch(`${API_BASE_URL}/v1/vault/fs/create`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }, body: JSON.stringify(req) });
            showCreateModal = false;
            fetchFiles();
        } catch(e) { console.error(e); }
    }

    async function renameFile(e: Event, file: any) {
        e.stopPropagation();
        const new_name = prompt("Novo nome:", file.name);
        if (!new_name || new_name === file.name) return;
        const req = { workspace_id: Number(globalState.activeWorkspaceId), path: file.path, new_name };
        try {
            await fetch(`${API_BASE_URL}/v1/vault/fs/rename`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }, body: JSON.stringify(req) });
            fetchFiles();
        } catch(e) { console.error(e); }
    }

    async function deleteFile(e: Event, file: any) {
        e.stopPropagation();
        if (!confirm(`Remover definitivamente ${file.name}?`)) return;
        const req = { workspace_id: Number(globalState.activeWorkspaceId), path: file.path };
        try {
            await fetch(`${API_BASE_URL}/v1/vault/fs/delete`, { method: 'DELETE', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('sovereign_token') || ''}` }, body: JSON.stringify(req) });
            fetchFiles();
        } catch(e) { console.error(e); }
    }

    $effect(() => {
        const ws_id = globalState.activeWorkspaceId;
        untrack(() => {
            if (ws_id && ws_id !== 'mesh_roaming') {
                fetchFiles();
            }
        });
    });

    function openFile(path: string, name: string) {
        if (!tabs.find(t => t.id === path)) {
            const isImage = /\.(png|jpe?g|gif|webp|svg|bmp)$/i.test(path);
            const isPdf = /\.pdf$/i.test(path);
            let type = 'markdown';
            if (isImage) type = 'image';
            if (isPdf) type = 'pdf';
            tabs = [...tabs, { id: path, name, type }];
        }
        globalState.vault.activeDocumentId = path;
        viewState = 'editor';
    }

    function closeTab(e: Event, id: string) {
        e.stopPropagation();
        tabs = tabs.filter(t => t.id !== id);
        if (globalState.vault.activeDocumentId === id) {
            globalState.vault.activeDocumentId = tabs.length > 0 ? tabs[tabs.length - 1].id : '';
        }
    }
</script>

{#if viewState === 'explorer'}
    <!-- EXPLORER VIEW (Blueprint 2) -->
    <div class="flex flex-col h-full w-full bg-[#F4F7FA] font-sans">
        
        <header class="mb-6 px-10 pt-10 w-full flex items-center justify-between shrink-0">
            <h1 class="font-extrabold text-2xl text-[#191c1d] tracking-tight flex items-center gap-3">
                <FileText class="w-6 h-6 text-primary" />
                Sovereign Knowledge Vault
            </h1>
            
            <div class="flex items-center gap-4">
                <!-- Search Bar -->
                <div class="relative flex items-center bg-surface-container-low rounded-full px-4 py-2 border border-outline-variant/10 shadow-sm w-[400px]">
                    <Search class="w-4 h-4 text-on-surface-variant mr-3" />
                    <input type="text" placeholder="Search Sovereign Network (Names & Cmds)..." class="bg-transparent border-none text-sm font-medium text-on-surface w-full focus:outline-none placeholder:text-on-surface-variant/50" bind:value={searchQuery}>
                    {#if searchQuery}
                        <button onclick={() => searchQuery = ''} class="text-on-surface-variant hover:text-on-surface transition"><X class="w-4 h-4"/></button>
                    {/if}
                </div>
                
                <!-- Filter Button -->
                <button class="flex items-center gap-2 px-4 py-2 {showAdvancedFilters ? 'bg-surface-container-lowest text-primary shadow-sm' : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high'} rounded-xl border border-outline-variant/10 font-bold text-xs transition-colors cursor-pointer" onclick={() => showAdvancedFilters = !showAdvancedFilters}>
                    <Filter class="w-4 h-4" /> Filter
                </button>
                
                <!-- New File Action -->
                <button onclick={createNewFile} class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-colors shadow-sm cursor-pointer ml-2">
                    <Plus class="w-4 h-4" /> Novo Arquivo
                </button>
            </div>
        </header>

        <div class="px-10 mb-4">
            {#if showAdvancedFilters}
                <div class="p-3 bg-white/80 backdrop-blur-md border border-slate-200/60 rounded-xl flex items-center gap-2 text-xs overflow-x-auto shadow-sm">
                    <span class="font-bold text-slate-500 mr-2 tracking-wide uppercase">Comandos CMD:</span>
                    <button class="px-2.5 py-1.5 bg-white font-mono font-medium border border-slate-200 rounded-md shadow-sm hover:bg-blue-50 flex items-center hover:text-blue-600 hover:border-blue-200 transition-colors cursor-pointer" onclick={() => appendFilterCmd('tag:')}>tag:</button>
                    <button class="px-2.5 py-1.5 bg-white font-mono font-medium border border-slate-200 rounded-md shadow-sm hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors cursor-pointer" onclick={() => appendFilterCmd('path:')}>path:</button>
                    <button class="px-2.5 py-1.5 bg-white font-mono font-medium border border-slate-200 rounded-md shadow-sm hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors cursor-pointer" onclick={() => appendFilterCmd('status:')}>status:</button>
                    <button class="px-2.5 py-1.5 bg-white font-mono font-medium border border-slate-200 rounded-md shadow-sm hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors cursor-pointer" onclick={() => appendFilterCmd('name:')}>name:</button>
                    <div class="ml-auto text-slate-400 italic">Ex: "tag:linux path:projects/linux"</div>
                </div>
            {/if}
        </div>

        <div class="flex-1 flex gap-4 overflow-hidden px-10 pb-6 w-full relative">
            <!-- Main Table Area -->
            <div class="flex-1 bg-white/90 backdrop-blur-md rounded-xl flex flex-col overflow-hidden shadow-sm border border-slate-200/60">

            <div class="flex-1 overflow-auto border border-slate-100 rounded-lg shadow-inner bg-white custom-scrollbar">
                <table class="w-full text-left text-sm whitespace-nowrap">
                    <thead class="sticky top-0 bg-slate-50/95 backdrop-blur z-10 text-slate-600 font-semibold border-b border-slate-200">
                        <tr>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none" onclick={() => handleSort('name')}>File Name {sortColumn === 'name' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none" onclick={() => handleSort('path_dir')}>Path {sortColumn === 'path_dir' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none" onclick={() => handleSort('wikilinks')}>Category (Wikilink) {sortColumn === 'wikilinks' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none" onclick={() => handleSort('modified')}>Date {sortColumn === 'modified' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 transition-colors select-none" onclick={() => handleSort('status')}>Status {sortColumn === 'status' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 w-16">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 text-slate-700">
                        {#each filteredFiles as file}
                            <tr class="hover:bg-slate-50 cursor-pointer transition-colors group" onclick={() => openFile(file.path, file.name)}>
                                <td class="px-4 py-2.5 font-medium flex items-center gap-2">
                                    <FileText class="w-4 h-4 text-blue-500 shrink-0" /> 
                                    <span class="truncate max-w-[200px]" title={file.name}>{file.name}</span>
                                </td>
                                <td class="px-4 py-2.5 text-slate-400 text-xs font-mono">{file.path_dir}</td>
                                <td class="px-4 py-2.5 flex items-center gap-1.5 flex-wrap">
                                    {#each file.wikilinks as tag}
                                        <!-- svelte-ignore a11y_click_events_have_key_events -->
                                        <!-- svelte-ignore a11y_no_static_element_interactions -->
                                        <span class="px-2 py-0.5 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-md text-[10px] font-bold uppercase tracking-widest cursor-pointer hover:bg-indigo-100 hover:scale-105 transition-transform" onclick={(e) => { e.stopPropagation(); activeFilterTag = activeFilterTag === tag ? null : tag; }}>{tag}</span>
                                    {/each}
                                    {#if file.wikilinks.length === 0}
                                        <span class="text-slate-300 italic text-[11px]">--</span>
                                    {/if}
                                </td>
                                <td class="px-4 py-2.5 text-slate-500 text-xs">{file.date}</td>
                                <td class="px-4 py-2.5"><span class="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-md text-[10px] font-bold uppercase tracking-wider">Synced</span></td>
                                <td class="px-4 py-2.5">
                                    <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onclick={(e) => renameFile(e, file)} class="p-1 text-slate-400 hover:text-blue-600 rounded transition-colors" title="Renomear"><Edit2 class="w-4 h-4"/></button>
                                        <button onclick={(e) => deleteFile(e, file)} class="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors" title="Deletar"><Trash2 class="w-4 h-4"/></button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                        {#if filteredFiles.length === 0 && !isLoading}
                            <tr><td colspan="6" class="px-4 py-8 text-center text-slate-400 italic">{files.length > 0 ? 'Nenhum arquivo encontrado para esta categoria.' : 'No files found in Vault.'}</td></tr>
                        {/if}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Right Sidebar (Insights) -->
        <div class="w-80 flex flex-col gap-4 shrink-0">
            <div class="bg-white/90 backdrop-blur-md rounded-xl border border-slate-200 p-6 flex flex-col gap-6 shadow-sm">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-teal-50 flex items-center justify-center">
                        <BrainCircuit class="w-5 h-5 text-teal-600" />
                    </div>
                    <h3 class="text-xl font-semibold text-slate-800">AI Core</h3>
                </div>
                <div class="h-px w-full bg-slate-200"></div>
                <div class="flex flex-col gap-5">
                    <div>
                        <p class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Total Files</p>
                        <p class="text-2xl font-bold text-slate-800">{files.length}</p>
                    </div>
                    <div>
                        <p class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Index Status</p>
                        <p class="text-xl font-semibold text-emerald-600">Fully Vectored</p>
                    </div>
                </div>
            </div>

            <!-- Global Wikilinks Index -->
            <div class="bg-white/90 backdrop-blur-md rounded-xl border border-slate-200 p-6 flex flex-col gap-6 shadow-sm">
                <div class="flex flex-col gap-2">
                    <h3 class="text-[11px] font-bold tracking-widest uppercase text-slate-400 flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></div>
                        Global Wikilinks Index
                    </h3>
                    <p class="text-[10px] text-slate-400 leading-relaxed tracking-wider font-mono mt-1">
                        {files.length} Docs Indexed
                    </p>
                </div>
                <div class="h-px w-full bg-slate-200"></div>
                <div class="flex flex-wrap gap-2">
                    {#each allTags as tag}
                        <button 
                            onclick={() => activeFilterTag = activeFilterTag === tag ? null : tag}
                            class="px-2.5 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer border shadow-sm {activeFilterTag === tag ? 'bg-indigo-500 text-white border-indigo-500' : 'bg-slate-50 text-slate-600 hover:bg-indigo-50 hover:text-indigo-700 border-slate-200 hover:border-indigo-200'}"
                        >
                            {tag}
                        </button>
                    {/each}
                    {#if allTags.length === 0}
                        <span class="text-xs text-slate-400 italic">Nenhuma Theodora tag encontrada.</span>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
{:else}
    <!-- EDITOR VIEW (Blueprint 1) with Tabs -->
    <div class="flex-1 bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-full">
        <!-- Toolbar & Tabs -->
        <div class="p-2 border-b border-slate-100 flex items-center justify-between bg-slate-50/50 shrink-0">
            <div class="flex items-center gap-4 flex-1 overflow-hidden">
                <button onclick={() => viewState = 'explorer'} class="p-2 hover:bg-slate-200 rounded-lg text-slate-500 transition-colors cursor-pointer" title="Back to Explorer">
                    <ChevronLeft class="w-5 h-5" />
                </button>
                {#if fromProject}
                    <a href="/projects" class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-bold transition-colors shadow-sm ml-1">
                        <Rocket class="w-3 h-3" /> Voltar ao Projeto
                    </a>
                {/if}
                
                <div class="flex items-center gap-2 overflow-x-auto custom-scrollbar flex-1 px-2 pb-1 pt-1">
                    {#each tabs as tab}
                        <!-- svelte-ignore a11y_click_events_have_key_events -->
                        <!-- svelte-ignore a11y_no_static_element_interactions -->
                        <div 
                            class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors cursor-pointer shrink-0 border {globalState.vault.activeDocumentId === tab.id ? 'bg-white border-slate-300 text-blue-600 shadow-sm' : 'bg-transparent border-transparent text-slate-500 hover:bg-slate-100'}"
                            onclick={() => globalState.vault.activeDocumentId = tab.id}
                        >
                            <FileText class="w-4 h-4 {globalState.vault.activeDocumentId === tab.id ? 'text-blue-500' : 'opacity-60'}" />
                            <span class="max-w-[150px] truncate font-medium">{tab.name}</span>
                            <button onclick={(e) => closeTab(e, tab.id)} class="p-0.5 rounded-full hover:bg-slate-200 text-slate-400 hover:text-rose-500 transition-colors">
                                <X class="w-3 h-3" />
                            </button>
                        </div>
                    {/each}
                    {#if tabs.length === 0}
                        <span class="text-sm text-slate-400 italic">No files opened.</span>
                    {/if}
                </div>
            </div>
        </div>
        
        <!-- Main Viewer Area -->
        <div class="flex-1 flex overflow-hidden">
            <!-- Left: Editor -->
            <div class="flex-1 flex flex-col bg-slate-50 relative border-r border-slate-200">
                <div class="flex-1 bg-white flex flex-col overflow-hidden relative">
                    {#if globalState.vault.activeDocumentId}
                        {#key globalState.vault.activeDocumentId}
                            {@const activeTab = tabs.find(t => t.id === globalState.vault.activeDocumentId)}
                            <div class="absolute inset-0 overflow-y-auto">
                                {#if activeTab?.type === 'image'}
                                    <div class="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50/50 min-h-full">
                                        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
                                            <img src="{API_BASE_URL}/v1/vault/media?path={encodeURIComponent(globalState.vault.activeDocumentId)}" alt={activeTab.name} class="max-w-full max-h-[60vh] rounded-lg object-contain" />
                                        </div>
                                    </div>
                                {:else if activeTab?.type === 'pdf'}
                                    <div class="flex-1 flex w-full h-full bg-slate-50 relative">
                                        <iframe src="{API_BASE_URL}/v1/vault/media?path={encodeURIComponent(globalState.vault.activeDocumentId)}" class="w-full h-[85vh] border-none" title={activeTab.name}></iframe>
                                    </div>
                                {:else}
                                    <BlockEditor documentId={globalState.vault.activeDocumentId} />
                                {/if}
                            </div>
                        {/key}
                    {:else}
                         <div class="flex-1 flex flex-col items-center justify-center text-slate-400 gap-4 bg-slate-50">
                             <FileText class="w-16 h-16 opacity-20" />
                             <p class="font-medium text-slate-500">Select a document from the tabs above or return to Explorer.</p>
                         </div>
                    {/if}
                </div>
            </div>

            <!-- Right: Chat -->
            <aside class="w-[450px] bg-white flex flex-col h-full overflow-hidden shrink-0 z-10 hidden xl:flex">
                 <ChatPanel />
            </aside>
        </div>
    </div>
{/if}

{#if showCreateModal}
    <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col">
            <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <h3 class="font-bold text-slate-800 flex items-center gap-2"><Plus class="w-4 h-4 text-blue-500"/> Criar Novo Arquivo</h3>
                <button onclick={() => showCreateModal = false} class="p-1 hover:bg-slate-200 text-slate-400 rounded transition-colors cursor-pointer"><X class="w-4 h-4"/></button>
            </div>
            <div class="p-6 flex flex-col gap-5">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Nome e Extensão</label>
                    <input type="text" bind:value={newFileName} placeholder="ex: manifesto_arquitetura.md" class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Pasta de Destino (Vault Index)</label>
                    <select bind:value={newFileFolder} class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white text-sm text-slate-700">
                        {#each folders as folder}
                            <option value={folder.path}>{folder.name}</option>
                        {/each}
                    </select>
                </div>
                <button onclick={confirmCreateFile} disabled={!newFileName.trim()} class="mt-2 w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
                    Criar Arquivo
                </button>
            </div>
        </div>
    </div>
{/if}
