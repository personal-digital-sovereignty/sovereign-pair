<script lang="ts">
    import { projectState } from '$lib/projects.svelte';
    import { MessageSquare, Send, Sparkles } from 'lucide-svelte';

    let message = $state('');
    let isTyping = $state(false);
    
    // Tentar manter mensagem de inicialização reativa às contagens de projetos
    let activeCount = $derived(projectState.projects.filter(p => !p.is_archived).length);
    
    let chatLog = $state<{role: string, content: string}[]>([
        { role: 'assistant', content: `Bem-vindo ao Hub Master! Como posso te ajudar na orquestração hoje? (Ex: *'Criar um projeto para o Q4'*, *'Resumir tarefas travadas'*).` }
    ]);

    async function sendMessage() {
        if (!message.trim()) return;
        const currentMessage = message;
        chatLog = [...chatLog, { role: 'user', content: currentMessage }];
        message = '';
        isTyping = true;
        
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
                    stream: true
                })
            });

            isTyping = false;
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
            isTyping = false;
            chatLog[assistantIndex].content = "**Erro fatal ao contatar o Sovereign Hub API.** Servidor offline?";
        }
    }
</script>

<div class="w-full bg-white border border-slate-200/80 shadow-sm rounded-2xl overflow-hidden flex flex-col h-[500px]
">
    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-4 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
            <div class="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
                <Sparkles class="w-5 h-5 text-white" />
            </div>
            <div>
                <h3 class="font-bold text-white tracking-wide text-sm">Orchestration AI</h3>
                <p class="text-blue-100 text-[10px] font-bold uppercase tracking-wider">Sovereign Pair Logic</p>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span class="text-[10px] text-white font-bold tracking-wider uppercase opacity-90">Online</span>
        </div>
    </div>

    <div class="flex-1 overflow-y-auto p-5 space-y-5 bg-slate-50/30 custom-scrollbar">
        {#each chatLog as msg}
            <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
                <div class="max-w-[85%] rounded-2xl px-4 py-3 text-[13px] leading-relaxed {msg.role === 'user' ? 'bg-blue-600 text-white shadow-md rounded-br-none' : 'bg-white border border-slate-200 text-slate-700 shadow-sm rounded-bl-none'}">
                    {@html msg.content}
                </div>
            </div>
        {/each}
        {#if isTyping}
            <div class="flex flex-col items-start">
                <div class="bg-white border border-slate-200 shadow-sm rounded-2xl rounded-bl-none px-4 py-3.5">
                    <div class="flex gap-1.5">
                        <div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"></div>
                        <div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.15s"></div>
                        <div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" style="animation-delay: 0.3s"></div>
                    </div>
                </div>
            </div>
        {/if}
    </div>

    <div class="p-4 bg-white border-t border-slate-100 shrink-0">
        <div class="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:ring-2 focus-within:ring-blue-500/50 focus-within:border-blue-500 transition-all shadow-sm">
            <textarea 
                bind:value={message} 
                onkeydown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                placeholder="Orquestre comandos e insights..." 
                class="flex-1 bg-transparent border-none outline-none resize-none max-h-24 text-sm text-slate-700 px-3 py-1.5 custom-scrollbar font-medium" 
                rows="1"
            ></textarea>
            <button onclick={sendMessage} class="p-2.5 mb-0.5 mr-0.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition cursor-pointer shrink-0 shadow-sm">
                <Send class="w-4 h-4" />
            </button>
        </div>
    </div>
</div>
