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
        const groups: Record<string, typeof sessions> = { 'Chats Recentes': [] };
        for (const s of sessions) {
            const folder = s.folder_name || 'Chats Recentes';
            if (!groups[folder]) groups[folder] = [];
            groups[folder].push(s);
        }
        return Object.keys(groups).map(k => ({ folder: k, items: groups[k] }));
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

<div class="flex flex-col h-full w-full bg-surface-900 border-r border-surface-700 text-surface-200">
    <div class="px-4 py-4 shrink-0 flex items-center justify-between border-b border-surface-700">
        <h3 class="text-xs uppercase font-bold tracking-widest text-surface-400 flex items-center gap-2">
            <MessageSquare class="w-3.5 h-3.5"/> Histórico
        </h3>
        <button onclick={createNewSession} class="p-1.5 rounded-lg bg-primary-600 hover:bg-primary-500 text-white transition-colors cursor-pointer" title="Nova Sessão">
            <Plus class="w-3.5 h-3.5" />
        </button>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar p-3 flex flex-col gap-4">
        {#if isLoading}
            <div class="text-xs text-center text-surface-500 py-4 animate-pulse">Carregando Sensus...</div>
        {:else if sessions.length === 0}
             <div class="text-xs text-center text-surface-500 py-4">Nenhuma sessão local.</div>
        {:else}
            {#each groupedSessions as group}
                {#if group.items.length > 0}
                    <div class="flex flex-col gap-1">
                        <div 
                            class="px-2 py-1.5 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-surface-500 hover:text-surface-300 hover:bg-surface-800/50 rounded-lg cursor-pointer transition-all select-none"
                            onclick={() => toggleFolder(group.folder)}
                            onkeydown={(e) => { if (e.key === 'Enter') toggleFolder(group.folder) }}
                            role="button"
                            tabindex="0"
                        >
                            <div class="w-3.5 h-3.5 flex items-center justify-center">
                                {#if collapsedFolders[group.folder]}
                                    <ChevronRight class="w-3 h-3 text-surface-400" />
                                {:else}
                                    <ChevronDown class="w-3 h-3 text-surface-400" />
                                {/if}
                            </div>
                            {#if group.folder !== 'Chats Recentes'} <FolderIcon class="w-3 h-3 text-primary-500"/> {:else} <Hash class="w-3 h-3 text-surface-600"/> {/if}
                            <span class="truncate">{group.folder}</span>
                            <span class="ml-auto bg-surface-800 text-surface-500 px-1.5 py-0.5 rounded text-[8px]">{group.items.length}</span>
                        </div>
                        
                        {#if !collapsedFolders[group.folder]}
                            {#each group.items as s}
                                {#if editingSessionId === s.id}
                                    <!-- Formulário de Edição (Rename e Mover Pasta) -->
                                    <div class="w-full flex flex-col gap-2 p-3 bg-surface-800 border border-primary-500/50 rounded-xl shadow-lg ring-1 ring-primary-500/20 z-10 relative mt-1 mb-1">
                                        <label class="text-[9px] uppercase font-bold tracking-widest text-primary-500">Título do Chat</label>
                                        <input bind:value={editTitle} class="bg-surface-900 border border-surface-600 rounded-lg px-2 py-1.5 text-xs text-surface-200 focus:outline-none focus:border-primary-500 w-full" placeholder="Nome do Chat" />
                                        
                                        <label class="text-[9px] uppercase font-bold tracking-widest text-primary-500 mt-1">Mover para Projeto/Pasta</label>
                                        <input bind:value={editFolder} class="bg-surface-900 border border-surface-600 rounded-lg px-2 py-1.5 text-xs text-surface-200 focus:outline-none focus:border-primary-500 w-full" placeholder="(Vazio = Chats Recentes)" />

                                        <div class="flex items-center gap-2 mt-2 self-end">
                                            <button onclick={cancelEdit} class="p-1.5 rounded-lg bg-surface-700 hover:bg-surface-600 text-surface-300 transition-colors cursor-pointer" title="Cancelar">
                                                <X class="w-3.5 h-3.5" />
                                            </button>
                                            <button onclick={(e) => saveEdit(e, s.id)} class="p-1.5 rounded-lg bg-primary-600 hover:bg-primary-500 text-white transition-colors cursor-pointer" title="Salvar Organização">
                                                <Check class="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>
                                {:else}
                                    <button 
                                        onclick={() => selectSession(s.id, s.title)}
                                        class="w-full relative group text-left px-3 py-2.5 rounded-xl transition-all border flex flex-col gap-1 items-start {globalState.chat.activeSessionId === s.id ? 'bg-primary-500/10 border-primary-500/30 text-surface-100' : 'bg-transparent border-transparent text-surface-400 hover:bg-surface-800 hover:border-surface-700'}"
                                    >
                                        <span class="text-sm font-medium leading-snug truncate w-full pr-[4.5rem]">{s.title}</span>
                                        <span class="text-[9px] font-mono text-surface-600">{new Date(s.updated_at).toLocaleDateString()}</span>
                                        
                                        <div class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 flex items-center gap-0.5 transition-all">
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-primary-500/20 text-surface-600 hover:text-primary-400 cursor-pointer transition-all"
                                                role="button" tabindex="0"
                                                onclick={(e) => startEdit(e, s.id, s.title, s.folder_name)}
                                                onkeydown={(e) => { if (e.key === 'Enter') startEdit(e, s.id, s.title, s.folder_name) }}
                                                title="Editar (Mover Pastas / Renomear)"
                                            >
                                                <Edit2 class="w-3.5 h-3.5" />
                                            </div>
                                            <div 
                                                class="p-1.5 rounded-md hover:bg-rose-500/20 text-surface-600 hover:text-rose-400 cursor-pointer transition-all"
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
