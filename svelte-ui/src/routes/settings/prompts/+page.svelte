<script lang="ts">
    import { API_BASE_URL } from '$lib/env_config';
    import { onMount } from 'svelte';
    import { Lock, Unlock, FileText, X, Loader2, Shield, AlertTriangle, Eye } from 'lucide-svelte';

    interface PromptEntry {
        id: string; slug: string; category: string; title: string;
        prompt_text: string; placeholders: string; is_core: boolean;
        is_active: boolean; version: number; integrity_hash: string | null;
        created_at: string; updated_at: string; created_by: string;
    }

    let prompts = $state<PromptEntry[]>([]);
    let isLoadingPrompts = $state(false);
    let editingPrompt = $state<PromptEntry | null>(null);
    let showPromptModal = $state(false);
    let newPromptSlug = $state('');
    let newPromptTitle = $state('');
    let newPromptCategory = $state('user');
    let newPromptText = $state('');
    let promptValidationError = $state('');
    let isSavingPrompt = $state(false);
    let viewingPrompt = $state<PromptEntry | null>(null);

    onMount(async () => { await loadPrompts(); });

    async function loadPrompts() {
        isLoadingPrompts = true;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/prompts`);
            if (res.ok) prompts = await res.json();
        } catch(e) { console.error('Prompts load failed:', e); }
        finally { isLoadingPrompts = false; }
    }

    function openNewPromptModal() {
        editingPrompt = null;
        newPromptSlug = ''; newPromptTitle = ''; newPromptCategory = 'user'; newPromptText = '';
        promptValidationError = '';
        showPromptModal = true;
    }

    function openEditPromptModal(p: PromptEntry) {
        if (p.is_core) return;
        editingPrompt = p;
        newPromptSlug = p.slug; newPromptTitle = p.title;
        newPromptCategory = p.category; newPromptText = p.prompt_text;
        promptValidationError = '';
        showPromptModal = true;
    }

    async function savePrompt() {
        isSavingPrompt = true;
        promptValidationError = '';
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/prompts`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slug: newPromptSlug, title: newPromptTitle, category: newPromptCategory, prompt_text: newPromptText })
            });
            const data = await res.json();
            if (res.ok) { showPromptModal = false; loadPrompts(); }
            else { promptValidationError = data.reason || data.error || 'Erro desconhecido'; }
        } catch(e) { promptValidationError = 'Falha de conexão com o backend.'; }
        finally { isSavingPrompt = false; }
    }

    async function deletePrompt(slug: string) {
        if (!confirm(`Desativar prompt '${slug}'?`)) return;
        try {
            const res = await fetch(`${API_BASE_URL}/v1/settings/prompts/${encodeURIComponent(slug)}`, { method: 'DELETE' });
            if (res.ok) loadPrompts();
            else { const data = await res.json(); alert(data.error || 'Erro ao desativar prompt.'); }
        } catch(e) {}
    }

    const CAT_COLORS: Record<string, string> = {
        core: 'bg-error-container/20 text-error',
        scribe: 'bg-primary-container/20 text-primary',
        auditor: 'bg-tertiary-container/20 text-on-tertiary-container',
        gate: 'bg-secondary-container/20 text-on-secondary-container',
        extractor: 'bg-secondary-container/20 text-on-secondary-container',
        user: 'bg-surface-variant text-on-surface-variant',
    };
</script>

<div class="p-8 h-full flex flex-col">
    <div class="w-full space-y-10 flex-1">
        <div class="flex justify-between items-end mb-10">
            <div>
                <nav class="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant tracking-wider uppercase mb-2">
                    <span>Settings</span>
                    <span class="material-symbols-outlined text-[14px]">chevron_right</span>
                    <span class="text-primary font-extrabold">Prompts</span>
                </nav>
                <h2 class="text-3xl font-extrabold text-on-surface tracking-tight">Sovereign Prompt Vault</h2>
            </div>
            <div class="flex items-center gap-3">
                <span class="text-[11px] bg-primary-container/20 text-primary px-3 py-1 rounded-full font-mono font-bold">{prompts.length} prompts</span>
                <button onclick={openNewPromptModal}
                    class="px-5 py-2.5 bg-gradient-to-br from-[#001360] to-[#002395] text-white text-xs font-bold uppercase tracking-widest rounded-xl shadow-md shadow-primary/20 hover:shadow-lg active:scale-95 transition-all cursor-pointer flex items-center gap-2">
                    <FileText class="w-4 h-4" /> New Prompt
                </button>
            </div>
        </div>

        <div class="bg-surface-container-lowest p-8 rounded-3xl shadow-sm border border-outline-variant/10 pb-12">
            <div class="flex items-center gap-4 mb-8 pb-6 border-b border-outline-variant/10">
                <div class="p-3 bg-primary-fixed/50 rounded-2xl shadow-inner">
                    <span class="material-symbols-outlined text-primary text-[28px]" style="font-variation-settings: 'FILL' 1;">description</span>
                </div>
                <div>
                    <h3 class="text-xl font-bold text-on-surface">Cognitive Prompts Registry</h3>
                    <p class="text-[11px] font-medium text-on-surface-variant mt-1">Prompts com 🔒 são protegidos por SHA-256 e restaurados automaticamente se adulterados. Prompts do usuário são validados pelo Cognitive Firewall (LLM).</p>
                </div>
            </div>

            <div class="overflow-x-auto rounded-2xl border border-outline-variant/10">
                <table class="w-full text-left text-sm text-on-surface">
                    <thead class="text-[10px] uppercase bg-surface-container-high/50 text-on-surface-variant tracking-widest">
                        <tr>
                            <th class="px-4 py-3.5 font-semibold">ID</th>
                            <th class="px-4 py-3.5 font-semibold">Slug</th>
                            <th class="px-4 py-3.5 font-semibold">Title</th>
                            <th class="px-4 py-3.5 font-semibold">Category</th>
                            <th class="px-3 py-3.5 font-semibold text-center w-14">Lock</th>
                            <th class="px-3 py-3.5 font-semibold text-center w-14">Ver</th>
                            <th class="px-3 py-3.5 font-semibold text-center w-24">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-outline-variant/10">
                        {#if isLoadingPrompts}
                        <tr><td colspan="7" class="p-6 text-center"><Loader2 class="w-5 h-5 animate-spin mx-auto text-primary"/></td></tr>
                        {:else if prompts.length === 0}
                        <tr><td colspan="7" class="p-6 text-center text-on-surface-variant italic text-xs">No prompts found in the vault.</td></tr>
                        {:else}
                            {#each prompts as p (p.slug)}
                            <tr class="hover:bg-surface-container-low/50 transition-colors {!p.is_active ? 'opacity-40' : ''}">
                                <td class="px-4 py-3 font-mono text-[11px] {p.is_core ? 'text-primary' : 'text-on-surface-variant'}">{p.id.substring(0, 7)}</td>
                                <td class="px-4 py-3 font-mono text-xs text-on-surface font-medium">{p.slug}</td>
                                <td class="px-4 py-3 text-xs text-on-surface-variant truncate max-w-[200px]">{p.title}</td>
                                <td class="px-4 py-3">
                                    <span class="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider {CAT_COLORS[p.category] || CAT_COLORS.user}">{p.category}</span>
                                </td>
                                <td class="px-3 py-3 text-center">
                                    {#if p.is_core}<Lock class="w-4 h-4 text-error mx-auto" />{:else}<Unlock class="w-4 h-4 text-tertiary mx-auto" />{/if}
                                </td>
                                <td class="px-3 py-3 text-center text-[11px] text-on-surface-variant font-mono">v{p.version}</td>
                                <td class="px-3 py-3 text-center">
                                    <div class="flex items-center justify-center gap-1.5">
                                        <button onclick={() => viewingPrompt = p} class="text-on-surface-variant/50 hover:text-tertiary transition-colors cursor-pointer p-1 rounded hover:bg-tertiary-container/20" title="View Prompt">
                                            <Eye class="w-3.5 h-3.5" />
                                        </button>
                                        {#if !p.is_core}
                                        <button onclick={() => openEditPromptModal(p)} class="text-on-surface-variant/50 hover:text-primary transition-colors cursor-pointer p-1 rounded hover:bg-primary-container/20" title="Edit">
                                            <FileText class="w-3.5 h-3.5" />
                                        </button>
                                        <button onclick={() => deletePrompt(p.slug)} class="text-on-surface-variant/50 hover:text-error transition-colors cursor-pointer p-1 rounded hover:bg-error-container/20" title="Deactivate">
                                            <X class="w-3.5 h-3.5" />
                                        </button>
                                        {/if}
                                    </div>
                                </td>
                            </tr>
                            {/each}
                        {/if}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- VIEWER MODAL -->
{#if viewingPrompt}
<div class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-12" onclick={() => viewingPrompt = null}>
    <div class="bg-surface w-full max-w-3xl max-h-[85vh] rounded-3xl shadow-2xl flex flex-col border border-outline-variant/20 overflow-hidden animate-in fade-in zoom-in-95 duration-200" onclick={(e) => e.stopPropagation()}>
        <div class="px-8 py-5 border-b border-outline-variant/10 bg-surface-container-lowest flex items-center justify-between shrink-0">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-full {viewingPrompt.is_core ? 'bg-error/10 text-error border-error/20' : 'bg-primary/10 text-primary border-primary/20'} flex items-center justify-center border">
                    {#if viewingPrompt.is_core}<Lock class="w-5 h-5" />{:else}<FileText class="w-5 h-5" />{/if}
                </div>
                <div>
                    <h2 class="text-base font-extrabold text-on-surface tracking-tight">{viewingPrompt.title}</h2>
                    <div class="flex items-center gap-2 mt-0.5">
                        <span class="text-[10px] font-mono text-on-surface-variant/70">{viewingPrompt.slug}</span>
                        <span class="w-1 h-1 rounded-full bg-outline-variant/30"></span>
                        <span class="text-[10px] px-1.5 py-0.5 rounded-full font-bold uppercase tracking-wider {CAT_COLORS[viewingPrompt.category] || CAT_COLORS.user}">{viewingPrompt.category}</span>
                        <span class="w-1 h-1 rounded-full bg-outline-variant/30"></span>
                        <span class="text-[10px] font-mono text-on-surface-variant/70">v{viewingPrompt.version}</span>
                        {#if viewingPrompt.integrity_hash}
                        <span class="w-1 h-1 rounded-full bg-outline-variant/30"></span>
                        <span class="text-[10px] font-mono text-on-surface-variant/50" title={viewingPrompt.integrity_hash}>SHA-256: {viewingPrompt.integrity_hash.substring(0, 12)}…</span>
                        {/if}
                    </div>
                </div>
            </div>
            <button onclick={() => viewingPrompt = null} class="w-8 h-8 rounded-full hover:bg-surface-variant flex items-center justify-center text-on-surface-variant hover:text-error transition-colors cursor-pointer">
                <X class="w-5 h-5" />
            </button>
        </div>
        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <pre class="whitespace-pre-wrap font-mono text-sm text-on-surface leading-relaxed bg-surface-container-high/50 p-6 rounded-2xl border border-outline-variant/10">{viewingPrompt.prompt_text}</pre>
        </div>
        <div class="px-8 py-4 bg-surface-container border-t border-outline-variant/10 flex items-center justify-between shrink-0">
            <p class="text-[10px] font-medium text-on-surface-variant">Created: {new Date(viewingPrompt.created_at).toLocaleString()} · By: {viewingPrompt.created_by}</p>
            <button onclick={() => viewingPrompt = null} class="px-6 py-2 bg-surface-variant text-on-surface-variant font-bold text-xs uppercase tracking-widest rounded-xl transition-all cursor-pointer hover:bg-surface-container-highest active:scale-95">Close</button>
        </div>
    </div>
</div>
{/if}

<!-- PROMPT MODAL -->
{#if showPromptModal}
<div class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-12" onclick={() => showPromptModal = false}>
    <div class="bg-surface w-full max-w-xl rounded-3xl shadow-2xl flex flex-col border border-outline-variant/20 overflow-hidden animate-in fade-in zoom-in-95 duration-200" onclick={(e) => e.stopPropagation()}>
        <div class="px-8 py-5 border-b border-outline-variant/10 bg-surface-container-lowest flex items-center justify-between shrink-0">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
                    <span class="material-symbols-outlined text-xl">edit_note</span>
                </div>
                <h2 class="text-base font-extrabold text-on-surface tracking-tight">{editingPrompt ? 'Editar Prompt' : 'Novo Prompt'}</h2>
            </div>
            <button onclick={() => showPromptModal = false} class="w-8 h-8 rounded-full hover:bg-surface-variant flex items-center justify-center text-on-surface-variant hover:text-error transition-colors cursor-pointer">
                <X class="w-5 h-5" />
            </button>
        </div>

        <div class="p-8 flex flex-col gap-5">
            <div class="flex gap-4">
                <div class="flex-1 flex flex-col gap-1.5">
                    <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Slug</label>
                    <input type="text" bind:value={newPromptSlug} placeholder="meu_analista" disabled={!!editingPrompt}
                        class="w-full bg-surface-container border border-outline-variant/30 rounded-2xl px-4 py-3 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary disabled:opacity-50" />
                </div>
                <div class="flex-1 flex flex-col gap-1.5">
                    <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Category</label>
                    <select bind:value={newPromptCategory}
                        class="w-full bg-surface-container border border-outline-variant/30 rounded-2xl px-4 py-3 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary cursor-pointer">
                        <option value="user">user</option>
                        <option value="scribe">scribe</option>
                        <option value="auditor">auditor</option>
                    </select>
                </div>
            </div>

            <div class="flex flex-col gap-1.5">
                <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Title</label>
                <input type="text" bind:value={newPromptTitle} placeholder="Meu Analista Customizado"
                    class="w-full bg-surface-container border border-outline-variant/30 rounded-2xl px-4 py-3 text-sm text-on-surface outline-none focus:ring-2 focus:ring-primary" />
            </div>

            <div class="flex flex-col gap-1.5">
                <label class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">Prompt Text</label>
                <textarea bind:value={newPromptText} rows="8" placeholder="Você é um analista especializado em..."
                    class="w-full bg-surface-container-high border border-outline-variant/30 rounded-2xl p-4 text-sm font-mono text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary outline-none resize-y custom-scrollbar"></textarea>
            </div>

            {#if promptValidationError}
            <div class="p-3 rounded-xl bg-error-container/20 border border-error/30 flex items-start gap-3 text-error text-[11px] font-semibold">
                <AlertTriangle class="w-4 h-4 mt-0.5 shrink-0" />
                <span>{promptValidationError}</span>
            </div>
            {/if}
        </div>

        <div class="px-8 py-5 bg-surface-container border-t border-outline-variant/10 flex items-center justify-end gap-3">
            <button onclick={() => showPromptModal = false} class="px-6 py-2.5 bg-surface-variant text-on-surface-variant font-bold text-xs uppercase tracking-widest rounded-xl transition-all cursor-pointer hover:bg-surface-container-highest active:scale-95">Cancel</button>
            <button onclick={savePrompt} disabled={isSavingPrompt || !newPromptSlug || !newPromptTitle || !newPromptText}
                class="px-6 py-2.5 bg-primary text-on-primary hover:bg-primary-fixed hover:text-on-primary-fixed font-bold text-xs uppercase tracking-widest rounded-xl shadow-md transition-all flex items-center gap-2 cursor-pointer active:scale-95 disabled:opacity-50 disabled:grayscale">
                {#if isSavingPrompt}<Loader2 class="w-4 h-4 animate-spin" />{:else}<Shield class="w-4 h-4" />{/if}
                {isSavingPrompt ? 'Validating...' : 'Save (LLM Validated)'}
            </button>
        </div>
    </div>
</div>
{/if}

<style>
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
</style>
