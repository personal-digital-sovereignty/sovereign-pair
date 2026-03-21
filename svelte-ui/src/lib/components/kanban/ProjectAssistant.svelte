<script lang="ts">
    import type { Project } from '$lib/projects.svelte';
    import { MessageSquare, X, Send, ThumbsUp, ThumbsDown, Copy, RotateCcw } from 'lucide-svelte';

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
    <!-- Aumentado z-index para 999 para passar por cima do menu Sovereign Admin -->
    <div class="fixed top-0 right-0 w-[420px] h-full bg-slate-50/50 backdrop-blur-xl border-l border-slate-200 shadow-2xl flex flex-col z-[999] transform transition-transform duration-300 translate-x-0">
        <div class="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-6 shrink-0 shadow-sm">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center shadow-sm">
                    <MessageSquare class="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                    <h3 class="font-bold text-slate-800 text-sm">Project Assistant</h3>
                    <p class="text-[10px] text-emerald-600 font-bold uppercase tracking-wider">Lendo: {project.name}</p>
                </div>
            </div>
            <button onclick={() => isOpen = false} class="p-1.5 text-slate-400 hover:bg-rose-100 hover:text-rose-600 rounded-lg cursor-pointer transition">
                <X class="w-5 h-5" />
            </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6 space-y-6 bg-transparent custom-scrollbar">
            {#each chatLog as msg}
                <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
                    <div class="max-w-[85%] rounded-2xl px-4 py-3 text-[13px] leading-relaxed shadow-sm {msg.role === 'user' ? 'bg-slate-800 text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-700 rounded-bl-none'}">
                        {@html msg.content}
                    </div>
                    {#if msg.role === 'assistant'}
                    <div class="flex items-center gap-1 mt-1 ml-1 opacity-0 hover:opacity-100 transition-opacity">
                        <button class="p-1 text-slate-400 hover:text-emerald-600 rounded hover:bg-slate-100 transition"><ThumbsUp class="w-3 h-3"/></button>
                        <button class="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-slate-100 transition"><ThumbsDown class="w-3 h-3"/></button>
                        <button class="p-1 text-slate-400 hover:text-blue-600 rounded hover:bg-slate-100 transition"><Copy class="w-3 h-3"/></button>
                        <button class="p-1 text-slate-400 hover:text-amber-600 rounded hover:bg-slate-100 transition"><RotateCcw class="w-3 h-3"/></button>
                    </div>
                    {/if}
                </div>
            {/each}
        </div>
        
        <div class="p-4 bg-white border-t border-slate-200 shrink-0">
            <div class="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:ring-2 focus-within:ring-emerald-500/30 focus-within:border-emerald-500 transition-all shadow-sm">
                <textarea 
                    bind:value={message} 
                    onkeydown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder="Peça insights sobre o projeto..." 
                    class="flex-1 bg-transparent border-none outline-none resize-none max-h-32 text-sm text-slate-700 px-2 py-1 custom-scrollbar" 
                    rows="1"
                ></textarea>
                <button onclick={sendMessage} class="p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition cursor-pointer shrink-0 shadow-sm">
                    <Send class="w-4 h-4" />
                </button>
            </div>
            <p class="text-[10px] text-slate-400 text-center mt-3 font-medium">
                O Sovereign Pair analisa Propósito, Tarefas e Anexos via RAG local.
            </p>
        </div>
    </div>
    
    <!-- Remover Backdrop para permitir edição do Kanban com a gaveta aberta -->
{/if}
