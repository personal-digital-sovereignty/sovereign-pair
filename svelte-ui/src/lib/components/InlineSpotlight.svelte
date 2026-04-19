<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { Search, Folder, FileText, Bot, Settings, X, ChevronRight } from 'lucide-svelte';
    import { goto } from '$app/navigation';

    let isOpen = $state(false);
    let searchQuery = $state('');
    let searchInput: HTMLInputElement;

    onMount(() => {
        const handleKeydown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                isOpen = !isOpen;
                if (isOpen) {
                    searchQuery = '';
                    tick().then(() => searchInput?.focus());
                }
            }
            if (e.key === 'Escape' && isOpen) {
                isOpen = false;
            }
        };
        window.addEventListener('keydown', handleKeydown);
        return () => window.removeEventListener('keydown', handleKeydown);
    });

    const staticResults = [
        { id: '1', title: 'Dashboard',                    route: '/dashboard', icon: Folder,      type: 'Sistema' },
        { id: '2', title: 'Cibrid Chat',                  route: '/chat',      icon: Bot,          type: 'Sistema' },
        { id: '3', title: 'Knowledge Vault Explorer',     route: '/vault',     icon: FileText,     type: 'Sistema' },
        { id: '4', title: 'Kanban Projects Board',        route: '/projects',  icon: FileText,     type: 'Sistema' },
        { id: '5', title: 'Configurações (Mesh & Personas)', route: '/settings', icon: Settings,  type: 'Sistema' },
    ];

    let filteredResults = $derived.by(() => {
        if (!searchQuery) return staticResults;
        return staticResults.filter(r => r.title.toLowerCase().includes(searchQuery.toLowerCase()));
    });

    function navigateTo(route: string) {
        isOpen = false;
        searchQuery = '';
        goto(route);
    }
</script>

{#if isOpen}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="spotlight-backdrop" onclick={() => isOpen = false}>

        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div class="spotlight-panel" onclick={(e) => e.stopPropagation()}>

            <!-- Search Input -->
            <div class="spotlight-input-row">
                <Search size={18} class="spotlight-search-icon" />
                <input
                    bind:this={searchInput}
                    bind:value={searchQuery}
                    class="spotlight-input"
                    placeholder="Buscar em Sovereign... (ex: 'Chat', 'Config')"
                    autocomplete="off"
                    spellcheck="false"
                />
                <button class="spotlight-close-btn" onclick={() => isOpen = false} title="Fechar (Esc)">
                    <X size={16} />
                </button>
            </div>

            <!-- Results -->
            <div class="spotlight-results">
                {#if filteredResults.length === 0}
                    <div class="spotlight-empty">Nenhum resultado encontrado.</div>
                {:else}
                    <div class="spotlight-results-label">Destinos Rápidos</div>
                    {#each filteredResults as res}
                        <button class="spotlight-result-item" onclick={() => navigateTo(res.route)}>
                            <div class="spotlight-result-icon">
                                {#if res.icon}
                                    <res.icon size={15} />
                                {:else}
                                    <ChevronRight size={15} />
                                {/if}
                            </div>
                            <div class="spotlight-result-text">
                                <span class="spotlight-result-title">{res.title}</span>
                                <span class="spotlight-result-type">{res.type}</span>
                            </div>
                            <ChevronRight size={14} class="spotlight-result-arrow" />
                        </button>
                    {/each}
                {/if}
            </div>

            <!-- Footer -->
            <div class="spotlight-footer">
                <div class="spotlight-footer-hints">
                    <span><kbd>Enter</kbd> selecionar</span>
                    <span><kbd>Esc</kbd> fechar</span>
                    <span><kbd>⌘K</kbd> toggle</span>
                </div>
                <span class="spotlight-footer-brand">Sovereign Mesh Search</span>
            </div>
        </div>
    </div>
{/if}

<style>
    /* ── Backdrop ── */
    .spotlight-backdrop {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 14vh;
        padding-inline: 1rem;
        background: rgba(0, 0, 0, 0.60);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        animation: spotlight-fade-in 0.15s ease;
    }

    @keyframes spotlight-fade-in {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    /* ── Panel ── */
    .spotlight-panel {
        width: 100%;
        max-width: 640px;
        background: rgba(15, 15, 25, 0.92);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 18px;
        box-shadow:
            0 32px 80px rgba(0, 0, 0, 0.70),
            0 0 0 1px rgba(139, 92, 246, 0.10),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        overflow: hidden;
        animation: spotlight-slide-in 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        pointer-events: all;
    }

    @keyframes spotlight-slide-in {
        from { transform: translateY(-12px) scale(0.97); opacity: 0; }
        to   { transform: translateY(0) scale(1); opacity: 1; }
    }

    /* ── Input Row ── */
    .spotlight-input-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }

    :global(.spotlight-search-icon) {
        color: #8b5cf6;
        flex-shrink: 0;
    }

    .spotlight-input {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        font-size: 1.05rem;
        color: #f1f5f9;
        font-family: inherit;
    }

    .spotlight-input::placeholder {
        color: rgba(148, 163, 184, 0.50);
    }

    .spotlight-close-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.35rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 8px;
        color: #94a3b8;
        cursor: pointer;
        transition: background 0.15s, color 0.15s;
        line-height: 0;
    }

    .spotlight-close-btn:hover {
        background: rgba(139, 92, 246, 0.20);
        color: #c4b5fd;
        border-color: rgba(139, 92, 246, 0.40);
    }

    /* ── Results ── */
    .spotlight-results {
        max-height: 52vh;
        overflow-y: auto;
        padding: 0.5rem;
        scrollbar-width: thin;
        scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
    }

    .spotlight-empty {
        text-align: center;
        padding: 2.5rem 1rem;
        color: rgba(148, 163, 184, 0.5);
        font-size: 0.875rem;
    }

    .spotlight-results-label {
        padding: 0.35rem 0.75rem 0.5rem;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(148, 163, 184, 0.5);
    }

    .spotlight-result-item {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0.75rem;
        border-radius: 10px;
        border: 1px solid transparent;
        background: transparent;
        cursor: pointer;
        text-align: left;
        transition: background 0.12s, border-color 0.12s;
        color: inherit;
    }

    .spotlight-result-item:hover {
        background: rgba(139, 92, 246, 0.12);
        border-color: rgba(139, 92, 246, 0.25);
    }

    .spotlight-result-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 8px;
        color: #8b5cf6;
        flex-shrink: 0;
        transition: background 0.12s, border-color 0.12s;
    }

    .spotlight-result-item:hover .spotlight-result-icon {
        background: rgba(139, 92, 246, 0.18);
        border-color: rgba(139, 92, 246, 0.40);
    }

    .spotlight-result-text {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .spotlight-result-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: #e2e8f0;
    }

    .spotlight-result-type {
        font-size: 0.65rem;
        color: rgba(148, 163, 184, 0.5);
    }

    :global(.spotlight-result-arrow) {
        color: rgba(139, 92, 246, 0.4);
        opacity: 0;
        transition: opacity 0.12s;
        flex-shrink: 0;
    }

    .spotlight-result-item:hover :global(.spotlight-result-arrow) {
        opacity: 1;
        color: #8b5cf6;
    }

    /* ── Footer ── */
    .spotlight-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 1.25rem;
        border-top: 1px solid rgba(255, 255, 255, 0.07);
        background: rgba(0, 0, 0, 0.25);
    }

    .spotlight-footer-hints {
        display: flex;
        gap: 1rem;
        font-size: 0.65rem;
        color: rgba(148, 163, 184, 0.5);
        font-family: monospace;
    }

    .spotlight-footer-hints kbd {
        display: inline-block;
        padding: 0.15rem 0.4rem;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 4px;
        font-size: 0.65rem;
        color: #cbd5e1;
        font-family: monospace;
        margin-right: 0.2rem;
    }

    .spotlight-footer-brand {
        font-size: 0.65rem;
        color: rgba(139, 92, 246, 0.5);
        font-family: monospace;
    }
</style>
