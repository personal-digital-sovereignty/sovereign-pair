<script lang="ts">
    import { onMount, tick } from 'svelte';
    import { Search, Folder, FileText, Bot, Settings, X, ChevronRight } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte';
    import { goto } from '$app/navigation'; // Requires SvelteKit

    let isOpen = $state(false);
    let searchQuery = $state('');
    let searchInput: HTMLInputElement;

    // Lógica para Abrir via Atalho (Ctrl+K ou Cmd+K)
    onMount(() => {
        const handleKeydown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                isOpen = !isOpen;
                if (isOpen) {
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

    // Mockados para efeito visual da OmniSearch
    const staticResults = [
        { id: '1', title: 'Dashboard', route: '/dashboard', icon: Folder, type: 'System' },
        { id: '2', title: 'Cibrid Chat', route: '/chat', icon: Bot, type: 'System' },
        { id: '3', title: 'Knowledge Vault Explorer', route: '/vault', icon: FileText, type: 'System' },
        { id: '4', title: 'Kanban Projects Board', route: '/projects', icon: FileText, type: 'System' },
        { id: '5', title: 'Advanced Configs (Mesh & Personas)', route: '/settings', icon: Settings, type: 'System' }
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
    <!-- Backdrop Blur -->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div 
        class="fixed inset-0 bg-surface-900/80 backdrop-blur-md z-[100] flex items-start justify-center pt-[15vh] px-4 animate-in fade-in duration-200"
        onclick={() => isOpen = false}
    >
        <!-- Modal Content -->
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div 
            class="w-full max-w-2xl bg-surface-800 border border-surface-600 rounded-2xl shadow-2xl flex flex-col overflow-hidden ring-1 ring-primary-500/20"
            onclick={(e) => e.stopPropagation()}
        >
            
            <!-- Input Area -->
            <div class="flex items-center px-4 py-4 border-b border-surface-700 gap-3">
                <Search class="w-5 h-5 text-primary-500 shrink-0" />
                <input 
                    bind:this={searchInput}
                    bind:value={searchQuery}
                    class="flex-1 bg-transparent text-lg text-surface-100 placeholder-surface-500 focus:outline-none focus:ring-0"
                    placeholder="Search Sovereign Workspace... (e.g. 'Project', 'Config')"
                    autocomplete="off"
                    spellcheck="false"
                />
                <button 
                    onclick={() => isOpen = false}
                    class="p-1 rounded-lg hover:bg-surface-700 text-surface-400 hover:text-surface-200 transition-colors"
                >
                    <X class="w-5 h-5 text-gray-400" />
                    <span class="sr-only">Close OmniSearch</span>
                </button>
            </div>

            <!-- Results Dropdown -->
            <div class="max-h-[50vh] overflow-y-auto custom-scrollbar p-2">
                {#if filteredResults.length === 0}
                    <div class="p-8 text-center text-surface-500 text-sm">
                        Nenhum resultado encontrado no nó Local ou OCI.
                    </div>
                {:else}
                    <div class="px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-surface-500">
                        Top Actions & Destinations
                    </div>
                    <div class="flex flex-col gap-1 mt-1">
                        {#each filteredResults as res}
                            <button 
                                onclick={() => navigateTo(res.route)}
                                class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-surface-700/50 hover:border-primary-500/30 border border-transparent group transition-all cursor-pointer text-left"
                            >
                                <div class="flex items-center gap-3">
                                    <div class="p-1.5 bg-surface-900 rounded-md border border-surface-600 group-hover:border-primary-500/50 group-hover:bg-primary-500/10 transition-colors text-surface-400 group-hover:text-primary-400">
                                        {#if res.icon}
                                            <res.icon size={16} />
                                        {:else}
                                            <ChevronRight size={16} />
                                        {/if}
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="font-medium text-sm text-surface-200 group-hover:text-white transition-colors">{res.title}</span>
                                        <span class="text-[10px] text-surface-500">{res.type}</span>
                                    </div>
                                </div>
                                <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                                    <ChevronRight class="w-4 h-4 text-primary-500" />
                                </div>
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>
            
            <!-- Footer -->
            <div class="bg-surface-900 px-4 py-2 border-t border-surface-700 flex items-center justify-between text-[10px] text-surface-500 font-mono">
                <div class="flex items-center gap-3">
                    <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 rounded border border-surface-600 bg-surface-800 text-surface-300">Enter</kbd> to select</span>
                    <span class="flex items-center gap-1"><kbd class="px-1.5 py-0.5 rounded border border-surface-600 bg-surface-800 text-surface-300">Esc</kbd> to close</span>
                </div>
                <div>Sovereign Mesh Search (Local)</div>
            </div>

        </div>
    </div>
{/if}
