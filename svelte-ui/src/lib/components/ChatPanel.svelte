<script lang="ts">
    import { MessageSquare, Cpu, Shield, Send, Loader2, Paperclip, ThumbsUp, ThumbsDown, Bot, User, BrainCircuit, Copy, RotateCcw, Settings, Square, ChevronDown } from 'lucide-svelte';
    import { globalState, loadGlobalSession, sendGlobalChatMessage, stopGeneration } from '$lib/state.svelte.js';
    import { settingsState } from '$lib/settings.svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import { onMount, untrack } from 'svelte';

    let message = $state('');

    onMount(() => {
        // Inicializa a sessão uma única vez ao montar caso esteja vasio
        if (globalState.chat.messages.length === 0) {
            loadGlobalSession(globalState.chat.activeSessionId);
        }
    });

    function parseMarkdown(text: string) {
        if (!text) return '';
        
        let processingText = text;
        const thoughtRegex = /<thought>([\s\S]*?)<\/thought>/g;
        let originalThoughts = "";
        
        processingText = processingText.replace(thoughtRegex, (match, inner) => {
            originalThoughts += `<li class="flex items-start gap-2 text-[11px] leading-relaxed"><div class="mt-1.5 w-1.5 h-1.5 rounded-full bg-slate-300 shrink-0"></div><span class="opacity-90">${inner}</span></li>\n`;
            return "";
        });

        const raw = marked.parse(processingText);
        let sanitizedMarkup = DOMPurify.sanitize(raw as string, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'], ADD_ATTR: ['target', 'class'] });

        if (originalThoughts) {
            const safeThoughts = DOMPurify.sanitize(originalThoughts, { ADD_ATTR: ['class'] });
            const thinkingUI = `
                <details class="group mb-5 bg-slate-50 border border-slate-200/60 rounded-xl overflow-hidden shadow-sm transition-all duration-300 ease-in-out open:pb-4 w-full xl:w-11/12 mt-2">
                    <summary class="flex items-center gap-2 px-3 py-2.5 cursor-pointer list-none text-[11px] font-bold tracking-widest uppercase text-slate-500 select-none hover:bg-slate-100 transition-colors">
                        <svg class="w-3.5 h-3.5 text-blue-500 origin-center transition-transform group-open:rotate-90" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                        <svg class="w-3.5 h-3.5 text-blue-500 animate-[spin_3s_linear_infinite] group-open:hidden" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
                        <span class="group-open:hidden text-blue-600 transition-colors">Processo Analítico...</span>
                        <span class="hidden group-open:inline text-slate-400">Desvendar Lógica de Busca</span>
                    </summary>
                    <ul class="flex flex-col gap-2 mt-2 px-4 pb-1 text-slate-600 font-medium">
                        ${safeThoughts}
                    </ul>
                </details>
            `;
            return thinkingUI + sanitizedMarkup;
        }

        return sanitizedMarkup;
    }

    async function triggerFeedback(msgId: number, type: 'up' | 'down') {
        const msg = globalState.chat.messages.find((m: any) => m.id === msgId);
        if (msg) {
           const token = localStorage.getItem('sovereign_token') || '';
           try {
               await fetch('http://localhost:38001/v1/feedback', {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                       'Authorization': `Bearer ${token}`
                   },
                   body: JSON.stringify({
                       text: msg.text,
                       agent: msg.agent,
                       thumbs_up: type === 'up'
                   })
               });
               console.log(`[RLHF] Message ${msgId} synced natively to DB as ${type}`);
               const btnClass = type === 'up' ? 'text-emerald-600 bg-emerald-500/10 border-emerald-500/50' : 'text-rose-600 bg-rose-500/10 border-rose-500/50';
               const el = document.getElementById(`feedback-btn-${msgId}-${type}`);
               if (el) el.className = `p-1.5 rounded-lg transition-all ${btnClass}`;
           } catch(e) {
               console.error("Failed to sync RLHF:", e);
           }
        }
    }

    async function copyToClipboard(text: string) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    }

    function replayMessage(msgId: number) {
        const msg = globalState.chat.messages.find((m: any) => m.id === msgId);
        if (msg) {
            message = msg.text;
        }
    }

    let fileInput: HTMLInputElement;

    function handleFileUpload(e: Event) {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) return;

        if (file.size > 1024 * 1024 * 2) {
            alert("O arquivo excede o limite de 2MB para contexto dinâmico via Chat. Utilize a pasta Vault para documentos massivos.");
            (e.target as HTMLInputElement).value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (re) => {
            const text = re.target?.result as string;
            globalState.chat.inputContext = `[ARQUIVO ANEXADO: ${file.name}]\n\n${text.substring(0, 10000)}`;
        };
        reader.readAsText(file);
        
        (e.target as HTMLInputElement).value = '';
    }

    function handleSend() {
        if (!message) return;
        sendGlobalChatMessage(message);
        message = '';
    }
</script>

<div class="flex flex-col h-full w-full bg-slate-50 dark:bg-[#0c1324] border-l border-slate-200 dark:border-[#424859]/20 font-sans transition-colors">
    
    <!-- Chat Header -->
    <header class="flex items-center justify-between p-4 border-b border-slate-200 dark:border-[#424859]/20 bg-white dark:bg-[#12192b] shrink-0 transition-colors">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg border border-transparent dark:border-[#74b0ff]/20">
                <MessageSquare class="w-5 h-5 text-blue-600 dark:text-[#74b0ff]" />
            </div>
            <div>
                <h2 class="text-slate-800 dark:text-slate-200 font-bold tracking-tight">Cibrid Council <span class="text-[10px] bg-blue-100 dark:bg-blue-500/10 text-blue-700 dark:text-[#74b0ff] border border-transparent dark:border-blue-500/30 px-2 py-0.5 rounded ml-2 uppercase tracking-widest font-mono">Encrypted</span></h2>
                <p class="text-xs text-slate-500 dark:text-slate-400">P2P Mesh Network routing active.</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-slate-500 dark:text-slate-400">
            <div class="flex flex-col items-end">
                <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">{globalState.clusterState.status === 'optimal' ? 'Local Cibrid Core' : 'Sovereign Node'}</span>
                <span class="text-xs flex items-center gap-1.5 font-medium"><div class="w-2 h-2 rounded-full {globalState.clusterState.status === 'optimal' ? 'bg-emerald-500 dark:bg-emerald-400' : 'bg-amber-500 dark:bg-amber-400'} animate-pulse shadow-sm"></div> {globalState.clusterState.status === 'optimal' ? 'Online' : 'Degraded'}</span>
            </div>
            <Cpu class="w-6 h-6 text-slate-400 dark:text-slate-500" />
        </div>
    </header>

    <!-- Message Feed -->
    <main class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-6 custom-scrollbar bg-slate-50 dark:bg-[#080e1d] transition-colors">
        
        {#each globalState.chat.messages as msg}
            {@const thoughtsMatch = msg.text.match(/<thought>([\s\S]*?)(?:<\/thought>|$)/g) || []}
            {@const thoughts = thoughtsMatch.map((t: string) => t.replace(/<\/?thought>/g, '').trim())}
            {@const cleanText = msg.text.replace(/<thought>[\s\S]*?(?:<\/thought>|$)/g, '').trim()}
            <div class="flex flex-col max-w-3xl group {msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}">
                <div class="flex items-center gap-2 mb-1.5 px-1">
                    {#if msg.role === 'assistant'}
                        <div class="relative w-7 h-7 rounded-full flex items-center justify-center shrink-0">
                            <div class="absolute inset-0 rounded-full border border-blue-500 dark:border-[#74b0ff] opacity-20"></div>
                            {#if globalState.chat.isTyping && msg.id === globalState.chat.messages[globalState.chat.messages.length-1].id}
                                <div class="absolute inset-0 rounded-full animate-ping opacity-30 bg-blue-500 dark:bg-[#74b0ff]"></div>
                            {/if}
                            <div class="w-3 h-3 rounded-full bg-blue-500 dark:bg-[#74b0ff]"></div>
                        </div>
                    {:else}
                        <div class="relative w-7 h-7 rounded-full bg-slate-200 dark:bg-[#1d253b] border dark:border-[#424859]/30 flex items-center justify-center shrink-0 p-1.5 text-slate-600 dark:text-slate-400">
                            <svg fill="none" stroke="currentColor" class="w-full h-full" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                    {/if}

                    <span class="text-[10px] uppercase font-bold tracking-widest {msg.role === 'user' ? 'text-slate-500 dark:text-slate-400' : 'text-blue-600 dark:text-[#74b0ff]'}">{msg.agent}</span>
                    <span class="text-[10px] text-slate-400 dark:text-slate-500 font-mono">{msg.time}</span>
                </div>
                
                <!-- LIGHT THEME COLORS FOR BUBBLES -->

                {#if thoughts.length > 0}
                    <details class="w-full mb-3 bg-slate-100/50 dark:bg-[#12192b]/50 rounded-xl border border-slate-200 dark:border-[#424859]/30 overflow-hidden group select-none relative" open={!cleanText}>
                        <summary class="px-4 py-2.5 text-[11px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 cursor-pointer flex items-center gap-2 hover:bg-slate-200/50 dark:hover:bg-[#1d253b] transition-colors">
                            <BrainCircuit class="w-4 h-4 text-blue-500 dark:text-[#74b0ff] {(!cleanText && globalState.chat.isTyping && msg.id === globalState.chat.messages[globalState.chat.messages.length - 1].id) ? 'animate-pulse' : ''}" />
                            Processo Cognitivo ({thoughts.length} {thoughts.length === 1 ? 'fluxo' : 'fluxos'})
                            <ChevronDown class="w-3 h-3 ml-auto opacity-50 group-open:rotate-180 transition-transform" />
                        </summary>
                        <div class="px-4 py-3 text-[11px] font-mono text-slate-600 dark:text-slate-400 border-t border-slate-200 dark:border-[#424859]/30 space-y-2 opacity-90 custom-scrollbar select-text bg-white/50 dark:bg-[#0c1324]/50">
                            {#each thoughts as thought}
                                <div class="flex items-start gap-2">
                                    <span class="text-blue-400 dark:text-[#74b0ff] mt-0.5">·</span>
                                    <span class="leading-relaxed">{@html thought.replace(/\n/g, '<br/>')}</span>
                                </div>
                            {/each}
                            {#if !cleanText && globalState.chat.isTyping && msg.id === globalState.chat.messages[globalState.chat.messages.length - 1].id}
                                <div class="flex items-center gap-2 mt-2 pt-2 text-blue-500 dark:text-[#74b0ff] font-sans tracking-widest uppercase font-bold text-[9px] border-t border-slate-200/50 dark:border-[#424859]/30">
                                    <Loader2 class="w-3 h-3 animate-spin"/> Mapeando Oculto Cíbrido...
                                </div>
                            {/if}
                        </div>
                    </details>
                {/if}

                {#if cleanText || (thoughts.length === 0)}
                    <div class="{msg.role === 'user' ? 'bg-slate-200 dark:bg-slate-700/50 text-slate-800 dark:text-slate-200 border border-transparent dark:border-slate-600/30 rounded-2xl rounded-tr-none' : 'bg-white dark:bg-[#12192b] border border-slate-200 dark:border-[#424859]/30 text-slate-700 dark:text-slate-300 shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] dark:shadow-none rounded-2xl rounded-tl-none'} p-4 text-[15px] leading-relaxed prose dark:prose-invert max-w-full overflow-x-auto custom-scrollbar">
                        {@html parseMarkdown(cleanText || msg.text)}
                    </div>
                {/if}

                <div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 {msg.role === 'user' ? 'mr-1 justify-end' : 'ml-1 justify-start'}">
                    <button onclick={() => copyToClipboard(msg.text)} class="p-1.5 rounded-lg bg-white dark:bg-[#12192b] hover:bg-slate-50 dark:hover:bg-[#1d253b] text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 border border-slate-200 dark:border-slate-800/60 transition-all cursor-pointer" title="Copiar Texto">
                        <Copy class="w-3.5 h-3.5" />
                    </button>

                    {#if msg.role === 'user'}
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-white dark:bg-[#12192b] hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-800/60 transition-all cursor-pointer" title="Replay / Editar Pergunta">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}

                    {#if msg.role === 'assistant'}
                        <button id="feedback-btn-{msg.id}-up" onclick={() => triggerFeedback(msg.id, 'up')} class="p-1.5 rounded-lg bg-white dark:bg-[#12192b] hover:bg-emerald-50 dark:hover:bg-emerald-900/30 text-slate-400 dark:text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 border border-slate-200 dark:border-slate-800/60 transition-all cursor-pointer" title="Boa resposta (Like)">
                            <ThumbsUp class="w-3.5 h-3.5" />
                        </button>
                        <button id="feedback-btn-{msg.id}-down" onclick={() => triggerFeedback(msg.id, 'down')} class="p-1.5 rounded-lg bg-white dark:bg-[#12192b] hover:bg-rose-50 dark:hover:bg-rose-900/30 text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 border border-slate-200 dark:border-slate-800/60 transition-all cursor-pointer" title="Resposta Incorreta (Dislike)">
                            <ThumbsDown class="w-3.5 h-3.5" />
                        </button>
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-white dark:bg-[#12192b] hover:bg-amber-50 dark:hover:bg-amber-900/30 text-slate-400 dark:text-slate-500 hover:text-amber-600 dark:hover:text-amber-400 border border-slate-200 dark:border-slate-800/60 transition-all cursor-pointer" title="Copiar para Input">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}
                </div>
            </div>
        {/each}

    </main>

    <!-- Input Bar -->
    <footer class="p-4 bg-white dark:bg-[#12192b] border-t border-slate-200 dark:border-[#424859]/30 shrink-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.02)] transition-colors">
        {#if globalState.chat.inputContext}
            <div class="mb-3 flex items-center justify-between bg-indigo-50/50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/30 p-2.5 rounded-xl shadow-sm">
                <div class="flex items-center gap-2 overflow-hidden flex-1">
                    <BrainCircuit class="w-4 h-4 text-indigo-500 dark:text-[#74b0ff] shrink-0" />
                    <span class="text-xs text-indigo-700 dark:text-[#74b0ff] font-medium truncate flex-1">Contexto anexado: "{globalState.chat.inputContext}"</span>
                </div>
                <button type="button" aria-label="Limpar Contexto" onclick={() => globalState.chat.inputContext = ''} class="text-indigo-400 dark:text-indigo-500 hover:text-indigo-600 dark:hover:text-[#74b0ff] shrink-0 ml-3 bg-white dark:bg-transparent p-1 rounded-md border border-indigo-100 dark:border-transparent shadow-sm dark:shadow-none transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M18 6L6 18M6 6l12 12" stroke-width="2" stroke-linecap="round"/></svg>
                </button>
            </div>
        {/if}
        <form 
            onsubmit={(e) => { e.preventDefault(); handleSend(); }}
            class="max-w-4xl mx-auto relative flex items-center bg-white dark:bg-[#0c1324] border border-slate-300 dark:border-[#424859]/50 rounded-xl overflow-hidden focus-within:border-blue-500 dark:focus-within:border-[#74b0ff] focus-within:ring-2 focus-within:ring-blue-100 dark:focus-within:ring-[#74b0ff]/20 transition-all shadow-sm dark:shadow-none"
        >
            <input type="file" bind:this={fileInput} onchange={handleFileUpload} class="hidden" />
            
            <button type="button" onclick={() => fileInput.click()} class="absolute left-2 bottom-2 p-2.5 text-slate-400 dark:text-slate-500 hover:text-blue-500 dark:hover:text-[#74b0ff] hover:bg-blue-50 dark:hover:bg-[#1d253b] rounded-lg transition-colors cursor-pointer" title="Anexar Arquivo Rápido de Texto/Código">
                <Paperclip class="w-5 h-5" />
            </button>

            <button type="button" 
                onclick={() => globalState.chat.isDeepResearchEnabled = !globalState.chat.isDeepResearchEnabled}
                class={`absolute left-12 bottom-2 p-2.5 rounded-lg transition-colors cursor-pointer ${globalState.chat.isDeepResearchEnabled ? 'text-indigo-600 dark:text-[#74b0ff] bg-indigo-100 dark:bg-indigo-500/20 shadow-inner dark:shadow-none border border-indigo-200 dark:border-indigo-500/30' : 'text-slate-400 dark:text-slate-500 hover:text-indigo-500 dark:hover:text-[#74b0ff] hover:bg-slate-50 dark:hover:bg-[#1d253b] border border-transparent'}`} 
                title="Ativar Web-Augmented Generation (Deep Research)">
                <Bot class="w-5 h-5" />
            </button>

            <button type="button" 
                onclick={() => globalState.chat.isCognitiveFirewallEnabled = !globalState.chat.isCognitiveFirewallEnabled}
                class={`absolute left-[88px] bottom-2 p-2.5 rounded-lg transition-colors cursor-pointer ${globalState.chat.isCognitiveFirewallEnabled ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-500/20 shadow-inner dark:shadow-none border border-emerald-200 dark:border-emerald-500/30' : 'text-slate-400 dark:text-slate-500 hover:text-emerald-500 dark:hover:text-emerald-400 hover:bg-slate-50 dark:hover:bg-[#1d253b] border border-transparent'}`} 
                title={globalState.chat.isCognitiveFirewallEnabled ? 'Firewall Cognitivo: ON (Modo Estrito)' : 'Firewall Cognitivo: OFF (Modo Quarentena)'}>
                <Shield class="w-5 h-5" />
            </button>

            <button type="button" 
                onclick={() => settingsState.isOpen = true}
                class="absolute left-[128px] bottom-2 p-2.5 text-slate-400 dark:text-slate-500 hover:text-blue-500 dark:hover:text-[#74b0ff] hover:bg-blue-50 dark:hover:bg-[#1d253b] rounded-lg transition-colors cursor-pointer" 
                title="Parâmetros do Modelo">
                <Settings class="w-5 h-5" />
            </button>

            <textarea 
                bind:value={message}
                placeholder="Ask the Global Cybrid Council..." 
                class="flex-1 bg-transparent border-none text-slate-800 dark:text-slate-200 text-sm p-4 pl-[180px] h-14 resize-none outline-none custom-scrollbar placeholder:text-slate-400 dark:placeholder:text-slate-500"
                onkeydown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
            ></textarea>

            {#if globalState.chat.isTyping}
                <button type="button" onclick={stopGeneration} class="absolute right-2 bottom-2 px-3 py-2.5 bg-rose-600 hover:bg-rose-700 dark:bg-rose-500/80 dark:hover:bg-rose-500 text-white rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 group shadow-sm dark:shadow-none" title="Interromper Raciocínio (Stop)">
                    <Square class="w-4 h-4 fill-white text-rose-600 dark:text-transparent" />
                    <span class="text-[10px] font-bold uppercase tracking-widest hidden sm:inline-block">Stop</span>
                </button>
            {:else}
                <button type="submit" disabled={!message.trim()} class="absolute right-2 bottom-2 p-2.5 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500/80 dark:hover:bg-blue-500 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                    <Send class="w-5 h-5" />
                </button>
            {/if}
        </form>
        <div class="text-[10px] text-center text-slate-400 dark:text-slate-500 mt-2 font-mono uppercase tracking-widest">
             End-to-End Local Execution • Context Limited to Graph Density
        </div>
    </footer>

</div>
