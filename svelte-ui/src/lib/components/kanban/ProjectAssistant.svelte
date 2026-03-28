<script lang="ts">
    import type { Project } from '$lib/projects.svelte';
    import { MessageSquare, X, Send, ThumbsUp, ThumbsDown, Copy, RotateCcw, Paperclip, Loader2 } from 'lucide-svelte';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';

    function parseMarkdown(text: string) {
        if (!text) return '';
        
        let processingText = text;
        const thoughtRegex = /<thought>([\s\S]*?)<\/thought>/g;
        let originalThoughts = "";
        
        processingText = processingText.replace(thoughtRegex, (match, inner) => {
            originalThoughts += `<li class="flex items-start gap-2 text-[10px] leading-relaxed"><div class="mt-1 w-1.5 h-1.5 rounded-full bg-slate-300 shrink-0"></div><span class="opacity-90">${inner}</span></li>\n`;
            return "";
        });

        const raw = marked.parse(processingText);
        let sanitizedMarkup = DOMPurify.sanitize(raw as string, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'], ADD_ATTR: ['target', 'class'] });

        if (originalThoughts) {
            const safeThoughts = DOMPurify.sanitize(originalThoughts, { ADD_ATTR: ['class'] });
            const thinkingUI = `
                <details class="group mb-5 bg-slate-50 border border-slate-200/60 rounded-xl overflow-hidden shadow-sm transition-all duration-300 ease-in-out open:pb-4 w-full mt-2">
                    <summary class="flex items-center gap-2 px-3 py-2 cursor-pointer list-none text-[10px] font-bold tracking-widest uppercase text-slate-500 select-none hover:bg-slate-100 transition-colors">
                        <svg class="w-3.5 h-3.5 text-blue-500 origin-center transition-transform group-open:rotate-90" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                        <svg class="w-3.5 h-3.5 text-blue-500 animate-[spin_3s_linear_infinite] group-open:hidden" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
                        <span class="group-open:hidden text-blue-600 transition-colors">Processo Analítico...</span>
                        <span class="hidden group-open:inline text-slate-400">Ocultar Estratégia</span>
                    </summary>
                    <ul class="flex flex-col gap-1.5 mt-2 px-3 pb-1 text-slate-600 font-medium">
                        ${safeThoughts}
                    </ul>
                </details>
            `;
            return thinkingUI + sanitizedMarkup;
        }

        return sanitizedMarkup;
    }

    let { project, isOpen = $bindable(false) }: { project: Project; isOpen?: boolean } = $props();
    let message = $state('');
    let chatLog = $state<{role: string, content: string}[]>([]);
    
    $effect(() => {
        if (project) {
            chatLog = [{ role: 'assistant', content: `Olá! Sou seu Sovereign Pair. Estou vendo o projeto **${project.name}** com suas ${project.tasks?.length || 0} tarefas. Como posso ajudar a acelerar essa entrega hoje?` }];
        }
    });

    async function sendMessage() {
        if (!message.trim()) return;
        const currentMessage = message;
        chatLog = [...chatLog, { role: 'user', content: currentMessage }];
        message = '';
        
        chatLog = [...chatLog, { role: 'assistant', content: '' }];
        const assistantIndex = chatLog.length - 1;
        
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const origin = window.location.origin.includes('5173') ? 'http://127.0.0.1:38001' : window.location.origin;
            const res = await fetch(`${origin}/v1/chat/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    model: 'qwen2.5:3b',
                    messages: chatLog.slice(0, -1),
                    project_id: project.id,
                    stream: true
                })
            });

            if (res.body) {
                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    const chunkStr = decoder.decode(value);
                    for (let line of chunkStr.split("\n\n")) {
                        line = line.trim();
                        if (line.startsWith("data: ")) {
                            const dataStr = line.replace("data: ", "");
                            if (dataStr === '[DONE]') continue;
                            try {
                                const obj = JSON.parse(dataStr);
                                const word = obj.choices?.[0]?.delta?.content || "";
                                chatLog[assistantIndex].content += word;
                                chatLog = [...chatLog]; // trigger reactivity
                            } catch(e) {}
                        }
                    }
                }
            }
        } catch (e) {
            console.error(e);
            chatLog[assistantIndex].content = "**Erro fatal ao contatar a API.** Servidor desligado?";
        }
    }
</script>

{#if !isOpen}
    <button onclick={() => isOpen = true} class="fixed bottom-6 right-8 bg-emerald-600 text-white p-3.5 rounded-full shadow-lg hover:bg-emerald-700 transition z-50 flex items-center justify-center cursor-pointer group hover:scale-110">
        <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.6"/>
        </svg>
        <span class="absolute right-[110%] mr-2 max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ease-in-out font-bold text-sm bg-emerald-800 text-emerald-50 rounded-lg group-hover:px-3 group-hover:py-1.5 opacity-0 group-hover:opacity-100 shadow-sm">
            Falar com Sovereign AI
        </span>
        <span class="absolute -top-1 -right-1 flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
    </button>
{:else}
    <aside class="w-[450px] bg-slate-50 flex flex-col h-full overflow-hidden shrink-0 border-l border-slate-200 font-sans z-10">
        <!-- Chat Header -->
        <header class="flex items-center justify-between p-4 border-b border-slate-200 bg-white shrink-0">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-50 rounded-lg">
                    <MessageSquare class="w-5 h-5 text-blue-600" />
                </div>
                <div>
                    <h2 class="text-slate-800 font-bold tracking-tight">Project Assistant <span class="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded ml-2 uppercase tracking-widest font-mono">Local Agent</span></h2>
                    <p class="text-xs text-slate-500 whitespace-nowrap overflow-hidden text-ellipsis max-w-[150px]">Lendo: {project.name}</p>
                </div>
            </div>
            <div class="flex items-center gap-2 text-slate-500">
                <div class="flex flex-col items-end mr-1 hidden sm:flex">
                    <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Sovereign Core</span>
                    <span class="text-xs flex items-center gap-1.5 font-medium"><div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div> Online</span>
                </div>
                <button onclick={() => isOpen = false} class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer">
                    <X class="w-5 h-5" />
                </button>
            </div>
        </header>

        <!-- Message Feed -->
        <main class="flex-1 overflow-y-auto p-4 md:p-6 flex flex-col gap-6 custom-scrollbar bg-slate-50">
            {#each chatLog as msg}
                <div class="flex flex-col max-w-3xl group {msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}">
                    <div class="flex items-center gap-2 mb-1.5 px-1">
                        {#if msg.role === 'assistant'}
                            <div class="relative w-7 h-7 rounded-full flex items-center justify-center shrink-0">
                                <div class="absolute inset-0 rounded-full border border-blue-500 opacity-20"></div>
                                <!-- Animação isTyping aqui se houvesse a variavel isTyping. Neste caso não implementada no escopo original, omitindo. -->
                                <div class="w-3 h-3 rounded-full bg-blue-500"></div>
                            </div>
                        {:else}
                            <div class="relative w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 p-1.5 text-slate-600">
                                <svg fill="none" stroke="currentColor" class="w-full h-full" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                            </div>
                        {/if}
                        <span class="text-[10px] uppercase font-bold tracking-widest {msg.role === 'user' ? 'text-slate-500' : 'text-blue-600'}">{msg.role === 'user' ? 'Commander' : 'Project AI'}</span>
                    </div>
                    
                    <div class="{msg.role === 'user' ? 'bg-slate-200 text-slate-800 rounded-2xl rounded-tr-none' : 'bg-white border border-slate-200 text-slate-700 shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] rounded-2xl rounded-tl-none'} p-4 text-[14px] leading-relaxed prose max-w-full overflow-x-auto custom-scrollbar">
                        {@html parseMarkdown(msg.content)}
                    </div>

                    <div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 {msg.role === 'user' ? 'mr-1 justify-end' : 'ml-1 justify-start'}">
                        <button class="p-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-400 hover:text-slate-600 border border-slate-200 transition-all cursor-pointer"><Copy class="w-3.5 h-3.5" /></button>
                        {#if msg.role === 'user'}
                            <button class="p-1.5 rounded-lg bg-white hover:bg-blue-50 hover:text-blue-600 text-slate-400 border border-slate-200 hover:border-blue-200 transition-all cursor-pointer"><RotateCcw class="w-3.5 h-3.5" /></button>
                        {/if}
                        {#if msg.role === 'assistant'}
                            <button class="p-1.5 rounded-lg bg-white hover:bg-emerald-50 text-slate-400 hover:text-emerald-600 border border-slate-200 hover:border-emerald-200 transition-all cursor-pointer"><ThumbsUp class="w-3.5 h-3.5" /></button>
                            <button class="p-1.5 rounded-lg bg-white hover:bg-rose-50 text-slate-400 hover:text-rose-600 border border-slate-200 hover:border-rose-200 transition-all cursor-pointer"><ThumbsDown class="w-3.5 h-3.5" /></button>
                        {/if}
                    </div>
                </div>
            {/each}
        </main>

        <!-- Input Bar -->
        <footer class="p-4 bg-white border-t border-slate-200 shrink-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.02)]">
            <form 
                onsubmit={(e) => { e.preventDefault(); sendMessage(); }}
                class="max-w-4xl mx-auto relative flex items-center bg-white border border-slate-300 rounded-xl overflow-hidden focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all shadow-sm"
            >
                <button type="button" class="absolute left-2 bottom-2 p-2.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer" title="Anexar Arquivo ou Imagem">
                    <Paperclip class="w-5 h-5" />
                </button>
                <textarea 
                    bind:value={message}
                    placeholder="Peça insights sobre o projeto..." 
                    class="flex-1 bg-transparent border-none text-slate-800 text-sm p-4 pl-14 h-14 resize-none outline-none custom-scrollbar placeholder:text-slate-400"
                    onkeydown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                        }
                    }}
                ></textarea>
                <button type="submit" class="absolute right-2 bottom-2 p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors cursor-pointer">
                    <Send class="w-5 h-5" />
                </button>
            </form>
            <div class="text-[10px] text-center text-slate-400 mt-2 font-mono uppercase tracking-widest">
                Sovereign Pair analisa Propósito, Tarefas e Anexos via RAG local.
            </div>
        </footer>
    </aside>
{/if}
