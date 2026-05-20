<script lang="ts">
    import { Bell, CheckCircle2, AlertTriangle, FileText, Bot, X } from 'lucide-svelte';
    import { globalState, markNotificationsRead } from '$lib/state.svelte.js';
    import { telemetryState } from '$lib/telemetry.svelte';
    import { fly, fade } from 'svelte/transition';
    import { clickOutside } from '$lib/actions/clickOutside';


    let isOpen = $state(false);

    let unreadCount = $derived(globalState.notifications.filter(n => !n.read).length);

    function togglePanel() {
        isOpen = !isOpen;
        if (isOpen && unreadCount > 0) {
            // Mark as read immediately when opening, or have a button for it.
        }
    }

    function removeNotification(id: number) {
        globalState.notifications = globalState.notifications.filter(n => n.id !== id);
    }
</script>

<div class="relative" use:clickOutside={() => isOpen = false}>
    <button 
        onclick={togglePanel}
        class="text-slate-400 hover:text-indigo-500 mr-4 relative transition-colors focus:outline-none"
    >
        <Bell class="w-5 h-5" />
        
        <!-- System Status Dot (Network & Processing) -->
        {#if !unreadCount}
            <span class="absolute top-0 right-0 w-2 h-2 rounded-full border-2 border-white {globalState.chat.isTyping ? 'bg-amber-400 animate-pulse' : (!telemetryState.connected ? 'bg-red-400' : 'bg-emerald-400')}"></span>
        {/if}

        <!-- Unread Badge (Overrides Status Dot when active) -->
        {#if unreadCount > 0}
            <span class="absolute -top-1 -right-1 flex h-3.5 w-3.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full {globalState.chat.isTyping ? 'bg-amber-400' : 'bg-rose-400'} opacity-75"></span>
              <span class="relative inline-flex flex-col flex-1 rounded-full h-3.5 w-3.5 {globalState.chat.isTyping ? 'bg-amber-500' : 'bg-rose-500'} text-[8px] font-bold text-white items-center justify-center border border-white leading-none">{unreadCount}</span>
            </span>
        {/if}
    </button>

    {#if isOpen}
        <div 
            in:fly={{ y: 5, duration: 200 }} 
            out:fade={{ duration: 150 }}
            class="absolute right-0 top-12 w-80 bg-white dark:bg-[#12192b] border border-slate-200 dark:border-slate-800 rounded-xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] z-[9999] overflow-hidden flex flex-col max-h-[400px]"
        >
            <div class="px-4 py-3 bg-slate-50 dark:bg-[#0c1324] border-b border-slate-100 dark:border-slate-800 flex justify-between items-center z-10 sticky top-0">
                <h3 class="text-sm font-bold text-slate-800 dark:text-slate-200">Alertas Cíbridos</h3>
                {#if unreadCount > 0}
                    <button onclick={markNotificationsRead} class="text-[10px] text-indigo-600 font-bold uppercase tracking-widest hover:text-indigo-800 focus:outline-none transition-colors">
                        Marcar Lidas
                    </button>
                {/if}
            </div>
            
            <div class="flex-1 overflow-y-auto custom-scrollbar">
                {#if globalState.notifications.length === 0}
                    <div class="p-8 text-center flex flex-col items-center justify-center text-slate-400 dark:text-slate-500">
                        <CheckCircle2 class="w-8 h-8 text-slate-200 dark:text-slate-700 mb-2" />
                        <span class="text-xs">Nenhum alerta pendente.</span>
                        <span class="text-[10px] uppercase tracking-widest mt-1">Sistemas Normais</span>
                    </div>
                {:else}
                    {#each globalState.notifications as notif}
                        <div class="group relative px-4 py-3 border-b border-slate-50 dark:border-slate-800/50 last:border-0 hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors flex gap-3 {notif.read ? 'opacity-70' : ''}">
                            <div class="mt-1">
                                {#if notif.title.includes('Cognição') || notif.title.includes('Chat')}
                                    <Bot class="w-4 h-4 text-indigo-500" />
                                {:else if notif.title.includes('Segurança') || notif.title.includes('Guardrail')}
                                    <AlertTriangle class="w-4 h-4 text-rose-500" />
                                {:else}
                                    <FileText class="w-4 h-4 text-emerald-500" />
                                {/if}
                            </div>
                            {#if notif.link}
                                <a href={notif.link} onclick={() => isOpen = false} class="flex-1 min-w-0 pr-6 cursor-pointer group/link block focus:outline-none focus:ring-2 focus:ring-indigo-500/20 rounded-md">
                                    <div class="flex items-center justify-between mb-0.5">
                                        <span class="text-xs font-bold text-slate-800 dark:text-slate-200 truncate" class:text-indigo-900={!notif.read} class:dark:text-indigo-400={!notif.read}>{notif.title}</span>
                                        <span class="text-[9px] text-slate-400 dark:text-slate-500 font-mono shrink-0 ml-2">{notif.time}</span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-snug line-clamp-2">{notif.text}</p>
                                    
                                    <div class="mt-1.5 inline-flex items-center gap-1 text-[10px] text-indigo-600 font-semibold group-hover/link:text-indigo-800 transition-colors">
                                        Clique para Abrir &rarr;
                                    </div>
                                </a>
                            {:else}
                                <div class="flex-1 min-w-0 pr-6">
                                    <div class="flex items-center justify-between mb-0.5">
                                        <span class="text-xs font-bold text-slate-800 dark:text-slate-200 truncate" class:text-indigo-900={!notif.read} class:dark:text-indigo-400={!notif.read}>{notif.title}</span>
                                        <span class="text-[9px] text-slate-400 dark:text-slate-500 font-mono shrink-0 ml-2">{notif.time}</span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-snug line-clamp-2">{notif.text}</p>
                                </div>
                            {/if}
                            <button onclick={(e) => { e.stopPropagation(); removeNotification(notif.id); }} class="absolute right-3 top-3 p-1 text-slate-300 hover:text-rose-500 hover:bg-rose-50 rounded opacity-0 group-hover:opacity-100 transition-all focus:outline-none">
                                <X class="w-3.5 h-3.5" />
                            </button>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    {/if}
</div>
