<script lang="ts">
    import { projectState } from '$lib/projects.svelte';
    import { MessageSquare, Send, X, ThumbsUp, ThumbsDown, Copy, RotateCcw } from 'lucide-svelte';

    let { isOpen = $bindable(false) } = $props<{ isOpen?: boolean }>();
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
            
            // Construir o Contexto Dinâmico Soberano para o Hub (Otimizado para LLMs menores)
            const ativos = projectState.projects.filter(p => !p.is_archived);
            const arquivados = projectState.projects.filter(p => p.is_archived);
            
            let systemContext = `INSTRUÇÃO MÁXIMA (SOVEREIGN ORCHESTRATION AI): Você é o assistente global do Hub de Controle. VOCÊ POSSUI ACESSO TOTAL A TODAS AS TAREFAS E PROJETOS. Leia os dados abaixo linha por linha. NUNCA diga que não tem uma informação se ela estiver listada abaixo! Responda de forma executiva.\n\n`;
            systemContext += `RESUMO NUMÉRICO:\n- Total de Projetos: ${projectState.projects.length}\n- Projetos ATIVOS: ${ativos.length}\n- Projetos ARQUIVADOS: ${arquivados.length}\n\n`;
            
            if (ativos.length > 0) {
                systemContext += `LISTA DE PROJETOS ATIVOS:\n` + ativos.map(p => {
                    const created = p.created_at ? p.created_at.split(' ')[0] : 'Desconhecida';
                    const deadline = p.deadline || 'Sem prazo';
                    
                    // Pré-processar a contagem por status para blindar Modelos pequenos (3B/8B) de alucinação matemática
                    const statusCounts: Record<string, number> = {};
                    if (p.tasks) {
                        for (const t of p.tasks) {
                            statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
                        }
                    }
                    const countsStr = Object.entries(statusCounts).map(([k, v]) => `${v} em '${k}'`).join(', ') || '0 tarefas';

                    const tasksSummary = p.tasks && p.tasks.length > 0 
                        ? p.tasks.map(t => `    * [${t.status}] ${t.title} (Criada: ${t.created_at ? t.created_at.split(' ')[0] : '?'})`).join('\n')
                        : '    * Nenhuma tarefa no fluxo';
                    
                    return `\n[PROJETO: ${p.name}]\n- Criado: ${created} | Prazo: ${deadline}\n- Propósito: ${p.purpose || 'N/A'}\n- Resumo Geral: ${countsStr}\n--- TAREFAS DETALHADAS DESTE PROJETO ---\n${tasksSummary}\n----------------------------------------`;
                }).join('\n') + `\n\n`;
            }
            if (arquivados.length > 0) {
                systemContext += `LISTA DE PROJETOS ARQUIVADOS:\n` + arquivados.map(p => `- "${p.name}"`).join('\n') + `\n\n`;
            }
            systemContext += `Sua resposta deve ser estritamente baseada nos dados acima. Não assuma nada que não esteja nesta lista. Responda à pergunta do usuário a seguir:`;
            
            const apiMessages = [
                { role: 'system', content: systemContext },
                ...chatLog.slice(0, -1)
            ];

            const res = await fetch(`${origin}/v1/chat/completions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    model: 'qwen2.5:3b',
                    messages: apiMessages,
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

{#if !isOpen}
    <button onclick={() => isOpen = true} class="fixed bottom-6 right-8 bg-blue-600 text-white p-3.5 rounded-full shadow-lg hover:bg-blue-700 transition z-50 flex items-center justify-center cursor-pointer group hover:scale-110">
        <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.6"/>
        </svg>
        <span class="absolute right-[110%] mr-2 max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ease-in-out font-bold text-sm bg-blue-800 text-blue-50 rounded-lg group-hover:px-3 group-hover:py-1.5 opacity-0 group-hover:opacity-100 shadow-sm">
            Orchestration AI
        </span>
        <span class="absolute -top-1 -right-1 flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
        </span>
    </button>
{:else}
    <div class="fixed top-0 right-0 w-[420px] h-full bg-slate-50/50 backdrop-blur-xl border-l border-slate-200 shadow-2xl flex flex-col z-[999] transform transition-transform duration-300 translate-x-0">
        <div class="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-6 shrink-0 shadow-sm">
            <div class="flex items-center gap-3">
                <div class="bg-emerald-50 border border-emerald-100 p-1.5 rounded-xl">
                    <svg class="w-5 h-5 text-emerald-600" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="4.5" fill="currentColor"/>
                        <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" stroke-opacity="0.6"/>
                    </svg>
                </div>
                <div>
                    <h3 class="font-bold text-slate-800 tracking-wide text-sm">Orchestration AI</h3>
                    <p class="text-slate-500 text-[10px] font-bold uppercase tracking-wider">{activeCount} Projetos Ativos</p>
                </div>
            </div>
            <button onclick={() => isOpen = false} class="p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 rounded-lg cursor-pointer transition">
                <X class="w-5 h-5" />
            </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-5 bg-transparent custom-scrollbar">
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

        <div class="p-4 bg-white border-t border-slate-200 shrink-0">
            <div class="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:ring-2 focus-within:ring-emerald-500/30 focus-within:border-emerald-500 transition-all shadow-sm">
                <textarea 
                    bind:value={message} 
                    onkeydown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder="Orquestre comandos globais..." 
                    class="flex-1 bg-transparent border-none outline-none resize-none max-h-32 text-sm text-slate-700 px-2 py-1 custom-scrollbar" 
                    rows="1"
                ></textarea>
                <button onclick={sendMessage} class="p-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition cursor-pointer shrink-0 shadow-sm">
                    <Send class="w-4 h-4" />
                </button>
            </div>
        </div>
    </div>
    
    <!-- Backdrop Removido para orquestração fluída -->
{/if}
