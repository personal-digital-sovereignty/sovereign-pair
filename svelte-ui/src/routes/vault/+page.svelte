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
    let fileCategory = $state<'all' | 'source' | 'artifacts' | 'gaps'>('all');
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
            
            let matchCat = true;
            const isArtifact = f.path.includes('_agents/artifacts');
            const isGap = f.path.includes('/gaps') || f.path_dir === 'gaps/';
            
            if (fileCategory === 'artifacts' && !isArtifact) matchCat = false;
            if (fileCategory === 'gaps' && !isGap) matchCat = false;
            if (fileCategory === 'source' && (isArtifact || isGap)) matchCat = false;

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
            return matchTag && matchSearch && matchCat;
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
            
            // 1. Fetch FileSystem Folders (for the "New File" Modal)
            const resTree = await fetch(`${API_BASE_URL}/v1/workspaces/${ws_id}/tree`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (resTree.ok) {
                const treeNodes = await resTree.json();
                folders = [{path: '', name: 'Raiz do Vault'}];
                extractFolders(treeNodes);
            }

            // 2. Fetch the true Cibrid Sensus Documents from SQLite Engine
            const resDocs = await fetch(`${API_BASE_URL}/v1/vault/documents`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (resDocs.ok) {
                const docRows = await resDocs.json();
                files = docRows.map((doc: any) => {
                    const name = doc.file_path.split('/').pop() || 'Unknown';
                    const path_dir = doc.file_path.substring(0, doc.file_path.length - name.length) || '/';
                    
                    // Extract Obsidian wikilinks locally on frontend from the raw DB content
                    let wikilinks: string[] = [];
                    if (doc.content_raw) {
                        const matches = doc.content_raw.match(/\[\[(.*?)\]\]/g);
                        if (matches) {
                            wikilinks = Array.from(new Set(matches.map((m: string) => m.replace('[[', '').replace(']]', '').split('|')[0]))) as string[];
                        }
                    }

                    return {
                        id: doc.id,
                        name,
                        path: doc.file_path,
                        path_dir,
                        wikilinks,
                        date: doc.last_modified ? new Date(doc.last_modified).toLocaleDateString() : 'Desconhecido',
                        summary: doc.summary,
                        size: doc.content_raw ? `${(doc.content_raw.length / 1024).toFixed(1)} KB` : '0 KB'
                    };
                });
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
    <div class="flex flex-col h-full w-full bg-[#F4F7FA] dark:bg-[#080e1d] transition-colors font-sans">
        
        <header class="mb-6 px-10 pt-10 w-full flex items-center justify-between shrink-0">
            <h1 class="font-extrabold text-2xl text-[#191c1d] dark:text-slate-200 tracking-tight flex items-center gap-3">
                <FileText class="w-6 h-6 text-primary dark:text-[#74b0ff]" />
                Sovereign Knowledge Vault
            </h1>
            
            <div class="flex items-center gap-4">
                <!-- Segmented Control for Categories -->
                <div class="flex items-center gap-1 bg-surface-container-low dark:bg-[#0c1324] p-1 rounded-xl border border-outline-variant/10 dark:border-[#424859]/20 shadow-sm shrink-0">
                    <button aria-label="Show All Files" class="cursor-pointer px-3 py-1.5 text-xs font-bold rounded-lg transition-colors {fileCategory === 'all' ? 'bg-white dark:bg-[#12192b] shadow-sm text-slate-800 dark:text-slate-200' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'}" onclick={() => fileCategory = 'all'}>Tudo</button>
                    <button aria-label="Show Source Files" class="cursor-pointer px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 rounded-lg transition-colors {fileCategory === 'source' ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-[#74b0ff] shadow-sm border border-blue-100 dark:border-blue-500/20' : 'text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-[#74b0ff] hover:bg-blue-50/50 dark:hover:bg-blue-500/10'}" onclick={() => fileCategory = 'source'}><FileText class="w-3.5 h-3.5"/> Sources</button>
                    <button aria-label="Show AI Artifacts" class="cursor-pointer px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 rounded-lg transition-colors {fileCategory === 'artifacts' ? 'bg-purple-50 dark:bg-purple-500/10 text-purple-700 dark:text-purple-400 shadow-sm border border-purple-100 dark:border-purple-500/20' : 'text-slate-500 dark:text-slate-400 hover:text-purple-600 dark:hover:text-purple-400 hover:bg-purple-50/50 dark:hover:bg-purple-500/10'}" onclick={() => fileCategory = 'artifacts'}><Sparkles class="w-3.5 h-3.5"/> AI Artifacts</button>
                    <button aria-label="Show Knowledge Gaps" class="cursor-pointer px-3 py-1.5 text-xs font-bold flex items-center gap-1.5 rounded-lg transition-colors {fileCategory === 'gaps' ? 'bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 shadow-sm border border-amber-100 dark:border-amber-500/20' : 'text-slate-500 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-50/50 dark:hover:bg-amber-500/10'}" onclick={() => fileCategory = 'gaps'}><BrainCircuit class="w-3.5 h-3.5"/> Gaps</button>
                </div>

                <!-- Search Bar -->
                <div class="relative flex items-center bg-surface-container-low dark:bg-[#0c1324] rounded-full px-4 py-2 border border-outline-variant/10 dark:border-[#424859]/20 shadow-sm w-[280px]">
                    <Search class="w-4 h-4 text-on-surface-variant dark:text-slate-400 mr-3 shrink-0" />
                    <input type="text" placeholder="Search Sovereign..." class="bg-transparent border-none text-sm font-medium text-on-surface dark:text-slate-200 w-full focus:outline-none placeholder:text-on-surface-variant/50 dark:placeholder:text-slate-500" bind:value={searchQuery}>
                    {#if searchQuery}
                        <button onclick={() => searchQuery = ''} class="text-on-surface-variant dark:text-slate-400 hover:text-on-surface dark:hover:text-slate-200 transition"><X class="w-4 h-4"/></button>
                    {/if}
                </div>
                
                <!-- Filter Button -->
                <button class="flex items-center gap-2 px-4 py-2 {showAdvancedFilters ? 'bg-surface-container-lowest dark:bg-[#12192b] text-primary dark:text-[#74b0ff] shadow-sm' : 'bg-surface-container-low dark:bg-[#0c1324] text-on-surface-variant dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-[#1d253b]'} rounded-xl border border-outline-variant/10 dark:border-[#424859]/20 font-bold text-xs transition-colors cursor-pointer" onclick={() => showAdvancedFilters = !showAdvancedFilters}>
                    <Filter class="w-4 h-4" /> Filter
                </button>
                
                <!-- New File Action -->
                <button onclick={createNewFile} class="bg-primary dark:bg-indigo-600 hover:bg-primary/90 dark:hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-colors shadow-sm cursor-pointer ml-2">
                    <Plus class="w-4 h-4" /> Novo Arquivo
                </button>
            </div>
        </header>

        <div class="px-10 mb-4">
            {#if showAdvancedFilters}
                <div class="p-3 bg-white/80 dark:bg-[#0c1324]/80 backdrop-blur-md border border-slate-200/60 dark:border-[#424859]/20 rounded-xl flex items-center gap-2 text-xs overflow-x-auto shadow-sm">
                    <span class="font-bold text-slate-500 dark:text-slate-400 mr-2 tracking-wide uppercase">Comandos CMD:</span>
                    <button class="px-2.5 py-1.5 bg-white dark:bg-[#12192b] font-mono font-medium border border-slate-200 dark:border-[#424859]/30 rounded-md shadow-sm hover:bg-blue-50 dark:hover:bg-blue-500/10 flex items-center hover:text-blue-600 dark:hover:text-[#74b0ff] dark:text-slate-200 hover:border-blue-200 dark:hover:border-blue-500/30 transition-colors cursor-pointer" onclick={() => appendFilterCmd('tag:')}>tag:</button>
                    <button class="px-2.5 py-1.5 bg-white dark:bg-[#12192b] font-mono font-medium border border-slate-200 dark:border-[#424859]/30 rounded-md shadow-sm hover:bg-blue-50 dark:hover:bg-blue-500/10 hover:text-blue-600 dark:hover:text-[#74b0ff] dark:text-slate-200 hover:border-blue-200 dark:hover:border-blue-500/30 transition-colors cursor-pointer" onclick={() => appendFilterCmd('path:')}>path:</button>
                    <button class="px-2.5 py-1.5 bg-white dark:bg-[#12192b] font-mono font-medium border border-slate-200 dark:border-[#424859]/30 rounded-md shadow-sm hover:bg-blue-50 dark:hover:bg-blue-500/10 hover:text-blue-600 dark:hover:text-[#74b0ff] dark:text-slate-200 hover:border-blue-200 dark:hover:border-blue-500/30 transition-colors cursor-pointer" onclick={() => appendFilterCmd('status:')}>status:</button>
                    <button class="px-2.5 py-1.5 bg-white dark:bg-[#12192b] font-mono font-medium border border-slate-200 dark:border-[#424859]/30 rounded-md shadow-sm hover:bg-blue-50 dark:hover:bg-blue-500/10 hover:text-blue-600 dark:hover:text-[#74b0ff] dark:text-slate-200 hover:border-blue-200 dark:hover:border-blue-500/30 transition-colors cursor-pointer" onclick={() => appendFilterCmd('name:')}>name:</button>
                    <div class="ml-auto text-slate-400 dark:text-slate-500 italic">Ex: "tag:linux path:projects/linux"</div>
                </div>
            {/if}
        </div>

        <div class="flex-1 flex gap-4 overflow-hidden px-10 pb-6 w-full relative">
            <!-- Main Table Area -->
            <div class="flex-1 bg-white/90 dark:bg-[#0c1324]/90 backdrop-blur-md rounded-xl flex flex-col overflow-hidden shadow-sm border border-slate-200/60 dark:border-[#424859]/20">

            <div class="flex-1 overflow-auto border border-slate-100 dark:border-[#424859]/10 rounded-lg shadow-inner bg-white dark:bg-[#0c1324] custom-scrollbar">
                <table class="w-full text-left text-sm whitespace-nowrap">
                    <thead class="sticky top-0 bg-slate-50/95 dark:bg-[#12192b]/95 backdrop-blur z-10 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-[#424859]/20">
                        <tr>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none" onclick={() => handleSort('name')}>File Name {sortColumn === 'name' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none" onclick={() => handleSort('path_dir')}>Path {sortColumn === 'path_dir' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none" onclick={() => handleSort('wikilinks')}>Category (Wikilink) {sortColumn === 'wikilinks' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none" onclick={() => handleSort('modified')}>Date {sortColumn === 'modified' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors select-none" onclick={() => handleSort('status')}>Status {sortColumn === 'status' ? (sortAscending ? '↑' : '↓') : ''}</th>
                            <th class="px-4 py-3 w-16">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-[#424859]/20 text-slate-700 dark:text-slate-300">
                        {#each filteredFiles as file}
                            <tr class="hover:bg-slate-50 dark:hover:bg-[#12192b] cursor-pointer transition-colors group" onclick={() => openFile(file.path, file.name)}>
                                <td class="px-4 py-2.5 font-medium flex items-center gap-3">
                                    {#if file.path.includes('_agents/artifacts')}
                                        <div class="p-1.5 bg-purple-100 dark:bg-purple-500/10 rounded-lg shrink-0 shadow-inner"><Sparkles class="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" /></div>
                                    {:else if file.path.includes('/gaps') || file.path_dir === 'gaps/'}
                                        <div class="p-1.5 bg-amber-100 dark:bg-amber-500/10 rounded-lg shrink-0 shadow-inner"><BrainCircuit class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" /></div>
                                    {:else}
                                        <FileText class="w-4 h-4 text-blue-500 dark:text-[#74b0ff] shrink-0" /> 
                                    {/if}
                                    <div class="flex flex-col">
                                        <span class="truncate max-w-[200px]" title={file.name}>{file.name}</span>
                                        {#if file.path.includes('_agents/artifacts')}
                                            <span class="text-[9px] font-bold uppercase tracking-widest text-purple-600 dark:text-purple-400 mt-0.5">Deep Research</span>
                                        {:else if file.path.includes('/gaps') || file.path_dir === 'gaps/'}
                                            <span class="text-[9px] font-bold uppercase tracking-widest text-amber-600 dark:text-amber-400 mt-0.5">Knowledge Gap</span>
                                        {/if}
                                    </div>
                                </td>
                                <td class="px-4 py-2.5 text-slate-400 dark:text-slate-500 text-xs font-mono">{file.path_dir}</td>
                                <td class="px-4 py-2.5 flex items-center gap-1.5 flex-wrap">
                                    {#each file.wikilinks as tag}
                                        <!-- svelte-ignore a11y_click_events_have_key_events -->
                                        <!-- svelte-ignore a11y_no_static_element_interactions -->
                                        <span class="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 text-indigo-700 dark:text-[#74b0ff] rounded-md text-[10px] font-bold uppercase tracking-widest cursor-pointer hover:bg-indigo-100 dark:hover:bg-indigo-500/20 hover:scale-105 transition-transform" onclick={(e) => { e.stopPropagation(); activeFilterTag = activeFilterTag === tag ? null : tag; }}>{tag}</span>
                                    {/each}
                                    {#if file.wikilinks.length === 0}
                                        <span class="text-slate-300 dark:text-slate-600 italic text-[11px]">--</span>
                                    {/if}
                                </td>
                                <td class="px-4 py-2.5 text-slate-500 dark:text-slate-400 text-xs">{file.date}</td>
                                <td class="px-4 py-2.5"><span class="px-2 py-1 bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 rounded-md text-[10px] font-bold uppercase tracking-wider">Synced</span></td>
                                <td class="px-4 py-2.5">
                                    <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onclick={(e) => renameFile(e, file)} class="p-1 text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-[#74b0ff] rounded transition-colors" title="Renomear"><Edit2 class="w-4 h-4"/></button>
                                        <button onclick={(e) => deleteFile(e, file)} class="p-1 text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 rounded transition-colors" title="Deletar"><Trash2 class="w-4 h-4"/></button>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                        {#if filteredFiles.length === 0 && !isLoading}
                            <tr><td colspan="6" class="px-4 py-8 text-center text-slate-400 dark:text-slate-500 italic">{files.length > 0 ? 'Nenhum arquivo encontrado para esta categoria.' : 'No files found in Vault.'}</td></tr>
                        {/if}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Right Sidebar (Insights) -->
        <div class="w-80 flex flex-col gap-4 shrink-0">
            <div class="bg-white/90 dark:bg-[#0c1324]/90 backdrop-blur-md rounded-xl border border-slate-200 dark:border-[#424859]/20 p-6 flex flex-col gap-6 shadow-sm">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-teal-50 dark:bg-teal-500/10 flex items-center justify-center">
                        <BrainCircuit class="w-5 h-5 text-teal-600 dark:text-teal-400" />
                    </div>
                    <h3 class="text-xl font-semibold text-slate-800 dark:text-slate-200">AI Core</h3>
                </div>
                <div class="h-px w-full bg-slate-200 dark:bg-[#424859]/20"></div>
                <div class="flex flex-col gap-5">
                    <div>
                        <p class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">Total Files</p>
                        <p class="text-2xl font-bold text-slate-800 dark:text-slate-200">{files.length}</p>
                    </div>
                    <div>
                        <p class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-1">Index Status</p>
                        <p class="text-xl font-semibold text-emerald-600 dark:text-emerald-400">Fully Vectored</p>
                    </div>
                </div>
            </div>

            <!-- Global Wikilinks Index -->
            <div class="bg-white/90 dark:bg-[#0c1324]/90 backdrop-blur-md rounded-xl border border-slate-200 dark:border-[#424859]/20 p-6 flex flex-col gap-6 shadow-sm">
                <div class="flex flex-col gap-2">
                    <h3 class="text-[11px] font-bold tracking-widest uppercase text-slate-400 dark:text-slate-500 flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full bg-indigo-500 dark:bg-[#74b0ff] shadow-[0_0_8px_rgba(99,102,241,0.6)] dark:shadow-[0_0_8px_rgba(116,176,255,0.6)]"></div>
                        Global Wikilinks Index
                    </h3>
                    <p class="text-[10px] text-slate-400 dark:text-slate-500 leading-relaxed tracking-wider font-mono mt-1">
                        {files.length} Docs Indexed
                    </p>
                </div>
                <div class="h-px w-full bg-slate-200 dark:bg-[#424859]/20"></div>
                <div class="flex flex-wrap gap-2">
                    {#each allTags as tag}
                        <button 
                            onclick={() => activeFilterTag = activeFilterTag === tag ? null : tag}
                            class="px-2.5 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors cursor-pointer border shadow-sm {activeFilterTag === tag ? 'bg-indigo-500 dark:bg-[#74b0ff] text-white dark:text-[#0c1324] border-indigo-500 dark:border-[#74b0ff]' : 'bg-slate-50 dark:bg-[#12192b] text-slate-600 dark:text-slate-400 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 hover:text-indigo-700 dark:hover:text-[#74b0ff] border-slate-200 dark:border-[#424859]/20 hover:border-indigo-200 dark:hover:border-indigo-500/30'}"
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
    <div class="flex-1 bg-white dark:bg-[#0c1324] rounded-2xl shadow-sm border border-slate-200 dark:border-[#424859]/20 flex flex-col overflow-hidden h-full">
        <!-- Toolbar & Tabs -->
        <div class="p-2 border-b border-slate-100 dark:border-[#424859]/20 flex items-center justify-between bg-slate-50/50 dark:bg-[#12192b]/50 shrink-0">
            <div class="flex items-center gap-4 flex-1 overflow-hidden">
                <button onclick={() => viewState = 'explorer'} class="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg text-slate-500 dark:text-slate-400 transition-colors cursor-pointer" title="Back to Explorer">
                    <ChevronLeft class="w-5 h-5" />
                </button>
                {#if fromProject}
                    <a href="/projects" class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 text-blue-700 dark:text-[#74b0ff] rounded-lg text-xs font-bold transition-colors shadow-sm ml-1">
                        <Rocket class="w-3 h-3" /> Voltar ao Projeto
                    </a>
                {/if}
                
                <div class="flex items-center gap-2 overflow-x-auto custom-scrollbar flex-1 px-2 pb-1 pt-1">
                    {#each tabs as tab}
                        <!-- svelte-ignore a11y_click_events_have_key_events -->
                        <!-- svelte-ignore a11y_no_static_element_interactions -->
                        <div 
                            class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors cursor-pointer shrink-0 border {globalState.vault.activeDocumentId === tab.id ? 'bg-white dark:bg-[#1d253b] border-slate-300 dark:border-[#424859]/50 text-blue-600 dark:text-[#74b0ff] shadow-sm' : 'bg-transparent border-transparent text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}"
                            onclick={() => globalState.vault.activeDocumentId = tab.id}
                        >
                            <FileText class="w-4 h-4 {globalState.vault.activeDocumentId === tab.id ? 'text-blue-500 dark:text-[#74b0ff]' : 'opacity-60'}" />
                            <span class="max-w-[150px] truncate font-medium">{tab.name}</span>
                            <button onclick={(e) => closeTab(e, tab.id)} class="p-0.5 rounded-full hover:bg-slate-200 dark:hover:bg-rose-500/10 text-slate-400 dark:text-slate-500 hover:text-rose-500 dark:hover:text-rose-400 transition-colors">
                                <X class="w-3 h-3" />
                            </button>
                        </div>
                    {/each}
                    {#if tabs.length === 0}
                        <span class="text-sm text-slate-400 dark:text-slate-500 italic">No files opened.</span>
                    {/if}
                </div>
            </div>
        </div>
        
        <!-- Main Viewer Area -->
        <div class="flex-1 flex overflow-hidden">
            <!-- Left: Editor -->
            <div class="flex-1 flex flex-col bg-slate-50 dark:bg-[#080e1d] relative border-r border-slate-200 dark:border-[#424859]/20">
                <div class="flex-1 bg-white dark:bg-[#0c1324] flex flex-col overflow-hidden relative">
                    {#if globalState.vault.activeDocumentId}
                        {#key globalState.vault.activeDocumentId}
                            {@const activeTab = tabs.find(t => t.id === globalState.vault.activeDocumentId)}
                            <div class="absolute inset-0 overflow-y-auto">
                                {#if activeTab?.type === 'image'}
                                    <div class="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50/50 dark:bg-transparent min-h-full">
                                        <div class="bg-white dark:bg-[#12192b] p-4 rounded-xl shadow-sm border border-slate-200 dark:border-[#424859]/20">
                                            <img src="{API_BASE_URL}/v1/vault/media?path={encodeURIComponent(globalState.vault.activeDocumentId)}" alt={activeTab.name} class="max-w-full max-h-[60vh] rounded-lg object-contain" />
                                        </div>
                                    </div>
                                {:else if activeTab?.type === 'pdf'}
                                    <div class="flex-1 flex w-full h-full bg-slate-50 dark:bg-slate-800 relative">
                                        <iframe src="{API_BASE_URL}/v1/vault/media?path={encodeURIComponent(globalState.vault.activeDocumentId)}" class="w-full h-[85vh] border-none" title={activeTab.name}></iframe>
                                    </div>
                                {:else}
                                    <BlockEditor documentId={globalState.vault.activeDocumentId} />
                                {/if}
                            </div>
                        {/key}
                    {:else}
                         <div class="flex-1 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-4 bg-slate-50 dark:bg-[#0c1324]">
                             <FileText class="w-16 h-16 opacity-20" />
                             <p class="font-medium text-slate-500 dark:text-slate-400">Select a document from the tabs above or return to Explorer.</p>
                         </div>
                    {/if}
                </div>
            </div>

            <!-- Right: Chat -->
            <aside class="w-[450px] bg-white dark:bg-[#0c1324] flex flex-col h-full overflow-hidden shrink-0 z-10 hidden xl:flex border-l border-slate-200 dark:border-[#424859]/20">
                 <ChatPanel />
            </aside>
        </div>
    </div>
{/if}

{#if showCreateModal}
    <div class="fixed inset-0 bg-slate-900/40 dark:bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div class="bg-white dark:bg-[#12192b] rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col border border-slate-200 dark:border-[#424859]/20">
            <div class="px-6 py-4 border-b border-slate-100 dark:border-[#424859]/20 flex items-center justify-between bg-slate-50/50 dark:bg-[#0c1324] transition-colors">
                <h3 class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2"><Plus class="w-4 h-4 text-blue-500 dark:text-[#74b0ff]"/> Criar Novo Arquivo</h3>
                <button onclick={() => showCreateModal = false} class="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 dark:text-slate-500 rounded transition-colors cursor-pointer"><X class="w-4 h-4"/></button>
            </div>
            <div class="p-6 flex flex-col gap-5">
                <div>
                    <label for="new_file_name_input" class="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Nome e Extensão</label>
                    <input id="new_file_name_input" type="text" bind:value={newFileName} placeholder="ex: manifesto_arquitetura.md" class="w-full px-4 py-2 border border-slate-200 dark:border-[#424859]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-500/50 focus:border-blue-500 dark:focus:border-blue-500/50 transition-shadow bg-white dark:bg-[#1d253b] text-slate-800 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500">
                </div>
                <div>
                    <label for="new_file_folder_select" class="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Pasta de Destino (Vault Index)</label>
                    <select id="new_file_folder_select" bind:value={newFileFolder} class="w-full px-4 py-2 border border-slate-200 dark:border-[#424859]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-500/50 focus:border-blue-500 dark:focus:border-blue-500/50 transition-shadow bg-white dark:bg-[#1d253b] text-sm text-slate-700 dark:text-slate-200 cursor-pointer">
                        {#each folders as folder}
                            <option value={folder.path}>{folder.name}</option>
                        {/each}
                    </select>
                </div>
                <button onclick={confirmCreateFile} disabled={!newFileName.trim()} class="mt-2 w-full py-2.5 bg-blue-600 dark:bg-indigo-600 hover:bg-blue-700 dark:hover:bg-indigo-500 text-white font-bold rounded-lg transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
                    Criar Arquivo
                </button>
            </div>
        </div>
    </div>
{/if}
