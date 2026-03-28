<script lang="ts">
    import { MessageSquare, Cpu, Shield, Send, Loader2, Paperclip, ThumbsUp, ThumbsDown, Bot, User, BrainCircuit, Copy, RotateCcw, Settings, Square } from 'lucide-svelte';
    import { globalState, loadGlobalSession, sendGlobalChatMessage, stopGeneration } from '$lib/state.svelte.js';
    import { settingsState } from '$lib/settings.svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import { untrack } from 'svelte';

    let message = $state('');

    $effect(() => {
        const sid = globalState.chat.activeSessionId;
        untrack(() => {
            loadGlobalSession(sid);
        });
    });

    function parseMarkdown(text: string) {
        if (!text) return '';
        const raw = marked.parse(text);
        return DOMPurify.sanitize(raw as string, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'] });
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

<div class="flex flex-col h-full w-full bg-slate-50 border-l border-slate-200 font-sans">
    
    <!-- Chat Header -->
    <header class="flex items-center justify-between p-4 border-b border-slate-200 bg-white shrink-0">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-blue-50 rounded-lg">
                <MessageSquare class="w-5 h-5 text-blue-600" />
            </div>
            <div>
                <h2 class="text-slate-800 font-bold tracking-tight">Cibrid Council <span class="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded ml-2 uppercase tracking-widest font-mono">Encrypted</span></h2>
                <p class="text-xs text-slate-500">P2P Mesh Network routing active.</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-slate-500">
            <div class="flex flex-col items-end">
                <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">{globalState.clusterState.status === 'optimal' ? 'Local Cibrid Core' : 'Sovereign Node'}</span>
                <span class="text-xs flex items-center gap-1.5 font-medium"><div class="w-2 h-2 rounded-full {globalState.clusterState.status === 'optimal' ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse"></div> {globalState.clusterState.status === 'optimal' ? 'Online' : 'Degraded'}</span>
            </div>
            <Cpu class="w-6 h-6 text-slate-400" />
        </div>
    </header>

    <!-- Message Feed -->
    <main class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-6 custom-scrollbar bg-slate-50">
        
        {#each globalState.chat.messages as msg}
            <div class="flex flex-col max-w-3xl group {msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}">
                <div class="flex items-center gap-2 mb-1.5 px-1">
                    {#if msg.role === 'assistant'}
                        <div class="relative w-7 h-7 rounded-full flex items-center justify-center shrink-0">
                            <div class="absolute inset-0 rounded-full border border-blue-500 opacity-20"></div>
                            {#if globalState.chat.isTyping && msg.id === globalState.chat.messages[globalState.chat.messages.length-1].id}
                                <div class="absolute inset-0 rounded-full animate-ping opacity-30 bg-blue-500"></div>
                            {/if}
                            <div class="w-3 h-3 rounded-full bg-blue-500"></div>
                        </div>
                    {:else}
                        <div class="relative w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 p-1.5 text-slate-600">
                            <svg fill="none" stroke="currentColor" class="w-full h-full" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                    {/if}

                    <span class="text-[10px] uppercase font-bold tracking-widest {msg.role === 'user' ? 'text-slate-500' : 'text-blue-600'}">{msg.agent}</span>
                    <span class="text-[10px] text-slate-400 font-mono">{msg.time}</span>
                </div>
                
                <!-- LIGHT THEME COLORS FOR BUBBLES -->
                <div class="{msg.role === 'user' ? 'bg-slate-200 text-slate-800 rounded-2xl rounded-tr-none' : 'bg-white border border-slate-200 text-slate-700 shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] rounded-2xl rounded-tl-none'} p-4 text-[15px] leading-relaxed prose max-w-full overflow-x-auto custom-scrollbar">
                    {@html parseMarkdown(msg.text)}
                </div>

                <div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 {msg.role === 'user' ? 'mr-1 justify-end' : 'ml-1 justify-start'}">
                    <button onclick={() => copyToClipboard(msg.text)} class="p-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-400 hover:text-slate-600 border border-slate-200 transition-all cursor-pointer" title="Copiar Texto">
                        <Copy class="w-3.5 h-3.5" />
                    </button>

                    {#if msg.role === 'user'}
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-white hover:bg-blue-50 hover:text-blue-600 text-slate-400 border border-slate-200 hover:border-blue-200 transition-all cursor-pointer" title="Replay / Editar Pergunta">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}

                    {#if msg.role === 'assistant'}
                        <button id="feedback-btn-{msg.id}-up" onclick={() => triggerFeedback(msg.id, 'up')} class="p-1.5 rounded-lg bg-white hover:bg-emerald-50 text-slate-400 hover:text-emerald-600 border border-slate-200 hover:border-emerald-200 transition-all cursor-pointer" title="Boa resposta (Like)">
                            <ThumbsUp class="w-3.5 h-3.5" />
                        </button>
                        <button id="feedback-btn-{msg.id}-down" onclick={() => triggerFeedback(msg.id, 'down')} class="p-1.5 rounded-lg bg-white hover:bg-rose-50 text-slate-400 hover:text-rose-600 border border-slate-200 hover:border-rose-200 transition-all cursor-pointer" title="Resposta Incorreta (Dislike)">
                            <ThumbsDown class="w-3.5 h-3.5" />
                        </button>
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-white hover:bg-amber-50 text-slate-400 hover:text-amber-600 border border-slate-200 hover:border-amber-200 transition-all cursor-pointer" title="Copiar para Input">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}
                </div>
            </div>
        {/each}

    </main>

    <!-- Input Bar -->
    <footer class="p-4 bg-white border-t border-slate-200 shrink-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.02)]">
        {#if globalState.chat.inputContext}
            <div class="mb-3 flex items-center justify-between bg-indigo-50/50 border border-indigo-100 p-2.5 rounded-xl shadow-sm">
                <div class="flex items-center gap-2 overflow-hidden flex-1">
                    <BrainCircuit class="w-4 h-4 text-indigo-500 shrink-0" />
                    <span class="text-xs text-indigo-700 font-medium truncate flex-1">Contexto anexado: "{globalState.chat.inputContext}"</span>
                </div>
                <button type="button" aria-label="Limpar Contexto" onclick={() => globalState.chat.inputContext = ''} class="text-indigo-400 hover:text-indigo-600 shrink-0 ml-3 bg-white p-1 rounded-md border border-indigo-100 shadow-sm transition-colors cursor-pointer">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M18 6L6 18M6 6l12 12" stroke-width="2" stroke-linecap="round"/></svg>
                </button>
            </div>
        {/if}
        <form 
            onsubmit={(e) => { e.preventDefault(); handleSend(); }}
            class="max-w-4xl mx-auto relative flex items-center bg-white border border-slate-300 rounded-xl overflow-hidden focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all shadow-sm"
        >
            <input type="file" bind:this={fileInput} onchange={handleFileUpload} class="hidden" />
            
            <button type="button" onclick={() => fileInput.click()} class="absolute left-2 bottom-2 p-2.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer" title="Anexar Arquivo Rápido de Texto/Código">
                <Paperclip class="w-5 h-5" />
            </button>

            <button type="button" 
                onclick={() => globalState.chat.isDeepResearchEnabled = !globalState.chat.isDeepResearchEnabled}
                class={`absolute left-12 bottom-2 p-2.5 rounded-lg transition-colors cursor-pointer ${globalState.chat.isDeepResearchEnabled ? 'text-indigo-600 bg-indigo-100 shadow-inner border border-indigo-200' : 'text-slate-400 hover:text-indigo-500 hover:bg-slate-50 border border-transparent'}`} 
                title="Ativar Web-Augmented Generation (Deep Research)">
                <Bot class="w-5 h-5" />
            </button>

            <button type="button" 
                onclick={() => settingsState.isOpen = true}
                class="absolute left-[88px] bottom-2 p-2.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer" 
                title="Parâmetros do Modelo">
                <Settings class="w-5 h-5" />
            </button>

            <textarea 
                bind:value={message}
                placeholder="Ask the Global Cybrid Council..." 
                class="flex-1 bg-transparent border-none text-slate-800 text-sm p-4 pl-[140px] h-14 resize-none outline-none custom-scrollbar placeholder:text-slate-400"
                onkeydown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
            ></textarea>

            {#if globalState.chat.isTyping}
                <button type="button" onclick={stopGeneration} class="absolute right-2 bottom-2 px-3 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 group shadow-sm" title="Interromper Raciocínio (Stop)">
                    <Square class="w-4 h-4 fill-white text-rose-600" />
                    <span class="text-[10px] font-bold uppercase tracking-widest hidden sm:inline-block">Stop</span>
                </button>
            {:else}
                <button type="submit" disabled={!message.trim()} class="absolute right-2 bottom-2 p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                    <Send class="w-5 h-5" />
                </button>
            {/if}
        </form>
        <div class="text-[10px] text-center text-slate-400 mt-2 font-mono uppercase tracking-widest">
             End-to-End Local Execution • Context Limited to Graph Density
        </div>
    </footer>

</div>
