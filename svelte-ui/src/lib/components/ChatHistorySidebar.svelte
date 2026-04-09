<script lang="ts">
import { API_BASE_URL } from '$lib/env_config';

    import { MessageSquare, Plus, Folder as FolderIcon, Trash2, Hash, Edit2, Check, X, ChevronDown, ChevronRight } from 'lucide-svelte';
    import { globalState, loadGlobalSession, stopGeneration } from '$lib/state.svelte.js';
    import { onMount } from 'svelte';

    let sessions = $state<{id: number, title: string, folder_name: string | null, updated_at: string}[]>([]);
    let isLoading = $state(true);

    async function fetchSessions() {
        isLoading = true;
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const res = await fetch(`${API_BASE_URL}/v1/sessions`, {
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
        if (globalState.chat.isTyping) stopGeneration();
        globalState.chat.activeSessionId = null;
        globalState.chat.activeSessionTitle = 'Nova Sessão';
        loadGlobalSession(null);
    }

    function selectSession(id: number, title: string) {
        if (globalState.chat.isTyping) stopGeneration();
        globalState.chat.activeSessionId = id;
        globalState.chat.activeSessionTitle = title;
        loadGlobalSession(id);
    }

    async function deleteSession(e: Event, id: number) {
        e.stopPropagation();
        if (!confirm('Deseja deletar esta sessão de chat para sempre?')) return;
        
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            await fetch(`${API_BASE_URL}/v1/sessions/${id}`, {
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
            await fetch(`${API_BASE_URL}/v1/sessions/${id}`, {
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

<div class="flex flex-col h-full w-full bg-slate-50 dark:bg-[#0c1324] border-r border-slate-200 dark:border-[#424859]/20 text-slate-700 dark:text-slate-300 transition-colors">
    <div class="px-4 py-4 shrink-0 flex items-center justify-between border-b border-slate-200 dark:border-[#424859]/20 bg-white dark:bg-[#12192b] transition-colors">
        <h3 class="text-[11px] uppercase font-bold tracking-widest text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <MessageSquare class="w-4 h-4 text-blue-500 dark:text-[#74b0ff]"/> Histórico
        </h3>
        <button onclick={createNewSession} class="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 dark:bg-blue-500/20 dark:hover:bg-blue-500/30 text-white dark:text-[#74b0ff] transition-colors cursor-pointer shadow-sm" title="Nova Sessão">
            <Plus class="w-4 h-4" />
        </button>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar p-3 flex flex-col gap-4">
        {#if isLoading}
            <div class="text-xs text-center text-slate-400 dark:text-slate-500 py-4 animate-pulse">Carregando Sensus...</div>
        {:else if sessions.length === 0}
             <div class="text-xs text-center text-slate-400 dark:text-slate-500 py-4">Nenhuma sessão local.</div>
        {:else}
            {#each groupedSessions as group}
                {#if group.items.length > 0}
                    <div class="flex flex-col gap-1">
                        <div 
                            class="px-2 py-1.5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/50 dark:hover:bg-[#1d253b] rounded-lg cursor-pointer transition-all select-none"
                            onclick={() => toggleFolder(group.folder)}
                            onkeydown={(e) => { if (e.key === 'Enter') toggleFolder(group.folder) }}
                            role="button"
                            tabindex="0"
                        >
                            <div class="w-3.5 h-3.5 flex items-center justify-center">
                                {#if collapsedFolders[group.folder]}
                                    <ChevronRight class="w-3 h-3 text-slate-400 dark:text-slate-500" />
                                {:else}
                                    <ChevronDown class="w-3 h-3 text-slate-400 dark:text-slate-500" />
                                {/if}
                            </div>
                            {#if group.folder !== 'Chats Recentes'} <FolderIcon class="w-3 h-3 text-blue-500 dark:text-[#74b0ff]"/> {:else} <Hash class="w-3 h-3 text-slate-400 dark:text-slate-500"/> {/if}
                            <span class="truncate">{group.folder}</span>
                            <span class="ml-auto bg-white dark:bg-[#1d253b] border border-slate-200 dark:border-[#424859]/30 text-slate-500 dark:text-slate-400 px-1.5 py-0.5 rounded text-[8px] font-semibold shadow-sm">{group.items.length}</span>
                        </div>
                        
                        {#if !collapsedFolders[group.folder]}
                            {#each group.items as s}
                                {#if editingSessionId === s.id}
                                    <!-- Formulário de Edição (Rename e Mover Pasta) -->
                                    <div class="w-full flex flex-col gap-2 p-3 bg-white dark:bg-[#12192b] border border-blue-200 dark:border-blue-500/30 rounded-xl shadow-md z-10 relative mt-1 mb-1">
                                        <label for="edit_title_{s.id}" class="text-[9px] uppercase font-bold tracking-widest text-blue-600 dark:text-[#74b0ff]">Título do Chat</label>
                                        <input id="edit_title_{s.id}" bind:value={editTitle} class="bg-slate-50 dark:bg-slate-800/50 border border-slate-300 dark:border-[#424859]/50 rounded-lg px-2 py-1.5 text-xs text-slate-700 dark:text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:focus:border-[#74b0ff] dark:focus:ring-[#74b0ff] w-full" placeholder="Nome do Chat" />
                                        
                                        <label for="edit_folder_{s.id}" class="text-[9px] uppercase font-bold tracking-widest text-blue-600 dark:text-[#74b0ff] mt-1">Mover para Projeto/Pasta</label>
                                        <input id="edit_folder_{s.id}" bind:value={editFolder} class="bg-slate-50 dark:bg-slate-800/50 border border-slate-300 dark:border-[#424859]/50 rounded-lg px-2 py-1.5 text-xs text-slate-700 dark:text-slate-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:focus:border-[#74b0ff] dark:focus:ring-[#74b0ff] w-full" placeholder="(Vazio = Chats Recentes)" />

                                        <div class="flex items-center gap-2 mt-2 self-end">
                                            <button onclick={cancelEdit} class="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors cursor-pointer" title="Cancelar">
                                                <X class="w-3.5 h-3.5" />
                                            </button>
                                            <button onclick={(e) => saveEdit(e, s.id)} class="p-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 dark:bg-blue-500/20 dark:hover:bg-blue-500/30 text-white dark:text-[#74b0ff] transition-colors cursor-pointer" title="Salvar Organização">
                                                <Check class="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>
                                {:else}
                                    <button 
                                        onclick={() => selectSession(s.id, s.title)}
                                        class="w-full relative group text-left px-3 py-2.5 rounded-xl transition-all border flex flex-col gap-1 items-start {globalState.chat.activeSessionId === s.id ? 'bg-blue-50 dark:bg-[#74b0ff]/10 border-blue-200 dark:border-[#74b0ff]/30 text-blue-900 dark:text-[#74b0ff] shadow-sm' : 'bg-transparent border-transparent text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-[#1d253b] hover:border-slate-200 dark:hover:border-[#424859]/30 hover:shadow-sm'}"
                                    >
                                        <span class="text-[13px] font-semibold leading-snug truncate w-full pr-[4.5rem]">{s.title || 'Sessão Sem Título'}</span>
                                        <span class="text-[9px] font-medium text-slate-400 dark:text-slate-500 uppercase tracking-widest">{new Date(s.updated_at).toLocaleDateString()}</span>
                                        
                                        <div class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 flex items-center gap-0.5 transition-all">
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-blue-100 dark:hover:bg-[#74b0ff]/10 text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-[#74b0ff] cursor-pointer transition-all"
                                                role="button" tabindex="0"
                                                onclick={(e) => startEdit(e, s.id, s.title, s.folder_name)}
                                                onkeydown={(e) => { if (e.key === 'Enter') startEdit(e, s.id, s.title, s.folder_name) }}
                                                title="Editar (Mover Pastas / Renomear)"
                                            >
                                                <Edit2 class="w-3.5 h-3.5" />
                                            </div>
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-rose-100 dark:hover:bg-rose-500/10 text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 cursor-pointer transition-all"
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
