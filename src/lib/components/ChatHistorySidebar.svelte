<script lang="ts">
    import { MessageSquare, Plus, Folder as FolderIcon, Trash2, Hash, Edit2, Check, X, ChevronDown, ChevronRight } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte.js';
    import { onMount } from 'svelte';

    let sessions = $state<{id: number, title: string, folder_name: string | null, updated_at: string}[]>([]);
    let isLoading = $state(true);

    async function fetchSessions() {
        isLoading = true;
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const res = await fetch('http://localhost:38001/v1/sessions', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                sessions = await res.json();
                const uniqueFolders = new Set(sessions.map((s: any) => s.folder_name || 'Chats Recentes'));
                const newCollapsed: Record<string, boolean> = {};
                for (const folder of uniqueFolders) {
                    newCollapsed[folder] = folder !== 'Chats Recentes';
                }
                collapsedFolders = newCollapsed;
            }
        } catch (e) {
            console.error("Failed fetching chat sessions", e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        fetchSessions();
    });

    function createNewSession() {
        globalState.chat.activeSessionId = null;
        globalState.chat.activeSessionTitle = 'Nova Sessão';
    }

    function selectSession(id: number, title: string) {
        globalState.chat.activeSessionId = id;
        globalState.chat.activeSessionTitle = title;
    }

    async function deleteSession(e: Event, id: number) {
        e.stopPropagation();
        if (!confirm('Deseja deletar esta sessão de chat para sempre?')) return;
        
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            await fetch(`http://localhost:38001/v1/sessions/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (globalState.chat.activeSessionId === id) {
                createNewSession();
            }
            await fetchSessions();
        } catch(err) {
            console.error("Deleção falhou", err);
        }
    }

    let groupedSessions = $derived.by((): { folder: string, items: typeof sessions }[] => {
        const groups: Record<string, typeof sessions> = {};
        for (const s of sessions) {
            const folder = s.folder_name || 'Chats Recentes';
            if (!groups[folder]) groups[folder] = [];
            groups[folder].push(s);
        }
        const keys = Object.keys(groups);
        const standardFolders = keys.filter(k => k !== 'Chats Recentes').sort((a,b) => a.localeCompare(b));
        let result = standardFolders.map(k => ({ folder: k, items: groups[k] }));
        if (groups['Chats Recentes']) {
            result.push({ folder: 'Chats Recentes', items: groups['Chats Recentes'] });
        }
        return result;
    });

    // ------------------ Módulo de Pastas Acordeão ------------------
    let collapsedFolders = $state<Record<string, boolean>>({});

    function toggleFolder(folder: string) {
        collapsedFolders[folder] = !collapsedFolders[folder];
    }

    // ------------------ Módulo de Edição Inline (Pencil) ------------------
    let editingSessionId = $state<number | null>(null);
    let editTitle = $state('');
    let editFolder = $state('');

    function startEdit(e: Event, id: number, currentTitle: string, currentFolder: string | null) {
        e.stopPropagation();
        editingSessionId = id;
        editTitle = currentTitle || '';
        editFolder = currentFolder || '';
    }

    function cancelEdit(e: Event) {
        e.stopPropagation();
        editingSessionId = null;
    }

    async function saveEdit(e: Event, id: number) {
        e.stopPropagation();
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            await fetch(`http://localhost:38001/v1/sessions/${id}`, {
                method: 'PUT',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: editTitle,
                    folder_name: editFolder.trim() === '' ? null : editFolder.trim()
                })
            });
            editingSessionId = null;
            if (globalState.chat.activeSessionId === id) {
                globalState.chat.activeSessionTitle = editTitle;
            }
            await fetchSessions();
        } catch(err) {
            console.error("Failed to update session", err);
        }
    }
</script>

<div class="flex flex-col h-full w-full bg-slate-50 border-r border-slate-200 text-slate-700">
    <div class="px-4 py-4 shrink-0 flex items-center justify-between border-b border-slate-200 bg-white">
        <h3 class="text-[11px] uppercase font-bold tracking-widest text-slate-500 flex items-center gap-2">
            <MessageSquare class="w-4 h-4 text-blue-500"/> Histórico
        </h3>
        <button onclick={createNewSession} class="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors cursor-pointer shadow-sm" title="Nova Sessão">
            <Plus class="w-4 h-4" />
        </button>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar p-3 flex flex-col gap-4">
        {#if isLoading}
            <div class="text-xs text-center text-slate-400 py-4 animate-pulse">Carregando Sensus...</div>
        {:else if sessions.length === 0}
             <div class="text-xs text-center text-slate-400 py-4">Nenhuma sessão local.</div>
        {:else}
            {#each groupedSessions as group}
                {#if group.items.length > 0}
                    <div class="flex flex-col gap-1">
                        <div 
                            class="px-2 py-1.5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-slate-700 hover:bg-slate-200/50 rounded-lg cursor-pointer transition-all select-none"
                            onclick={() => toggleFolder(group.folder)}
                            onkeydown={(e) => { if (e.key === 'Enter') toggleFolder(group.folder) }}
                            role="button"
                            tabindex="0"
                        >
                            <div class="w-3.5 h-3.5 flex items-center justify-center">
                                {#if collapsedFolders[group.folder]}
                                    <ChevronRight class="w-3 h-3 text-slate-400" />
                                {:else}
                                    <ChevronDown class="w-3 h-3 text-slate-400" />
                                {/if}
                            </div>
                            {#if group.folder !== 'Chats Recentes'} <FolderIcon class="w-3 h-3 text-blue-500"/> {:else} <Hash class="w-3 h-3 text-slate-400"/> {/if}
                            <span class="truncate">{group.folder}</span>
                            <span class="ml-auto bg-white border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded text-[8px] font-semibold shadow-sm">{group.items.length}</span>
                        </div>
                        
                        {#if !collapsedFolders[group.folder]}
                            {#each group.items as s}
                                {#if editingSessionId === s.id}
                                    <!-- Formulário de Edição (Rename e Mover Pasta) -->
                                    <div class="w-full flex flex-col gap-2 p-3 bg-white border border-blue-200 rounded-xl shadow-md z-10 relative mt-1 mb-1">
                                        <label class="text-[9px] uppercase font-bold tracking-widest text-blue-600">Título do Chat</label>
                                        <input bind:value={editTitle} class="bg-slate-50 border border-slate-300 rounded-lg px-2 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-full" placeholder="Nome do Chat" />
                                        
                                        <label class="text-[9px] uppercase font-bold tracking-widest text-blue-600 mt-1">Mover para Projeto/Pasta</label>
                                        <input bind:value={editFolder} class="bg-slate-50 border border-slate-300 rounded-lg px-2 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-full" placeholder="(Vazio = Chats Recentes)" />

                                        <div class="flex items-center gap-2 mt-2 self-end">
                                            <button onclick={cancelEdit} class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 transition-colors cursor-pointer" title="Cancelar">
                                                <X class="w-3.5 h-3.5" />
                                            </button>
                                            <button onclick={(e) => saveEdit(e, s.id)} class="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors cursor-pointer" title="Salvar Organização">
                                                <Check class="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>
                                {:else}
                                    <button 
                                        onclick={() => selectSession(s.id, s.title)}
                                        class="w-full relative group text-left px-3 py-2.5 rounded-xl transition-all border flex flex-col gap-1 items-start {globalState.chat.activeSessionId === s.id ? 'bg-blue-50 border-blue-200 text-blue-900 shadow-sm' : 'bg-transparent border-transparent text-slate-600 hover:bg-white hover:border-slate-200 hover:shadow-sm'}"
                                    >
                                        <span class="text-[13px] font-semibold leading-snug truncate w-full pr-[4.5rem]">{s.title || 'Sessão Sem Título'}</span>
                                        <span class="text-[9px] font-medium text-slate-400 uppercase tracking-widest">{new Date(s.updated_at).toLocaleDateString()}</span>
                                        
                                        <div class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 flex items-center gap-0.5 transition-all">
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-blue-100 text-slate-400 hover:text-blue-600 cursor-pointer transition-all"
                                                role="button" tabindex="0"
                                                onclick={(e) => startEdit(e, s.id, s.title, s.folder_name)}
                                                onkeydown={(e) => { if (e.key === 'Enter') startEdit(e, s.id, s.title, s.folder_name) }}
                                                title="Editar (Mover Pastas / Renomear)"
                                            >
                                                <Edit2 class="w-3.5 h-3.5" />
                                            </div>
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-rose-100 text-slate-400 hover:text-rose-600 cursor-pointer transition-all"
                                                role="button" tabindex="0"
                                                onclick={(e) => deleteSession(e, s.id)}
                                                onkeydown={(e) => { if (e.key === 'Enter') deleteSession(e, s.id) }}
                                                title="Deletar permanentemente"
                                            >
                                                <Trash2 class="w-3.5 h-3.5" />
                                            </div>
                                        </div>
                                    </button>
                                {/if}
                            {/each}
                        {/if}
                    </div>
                {/if}
            {/each}
        {/if}
    </div>
</div>
