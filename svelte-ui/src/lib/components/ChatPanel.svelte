<script lang="ts">
    import { MessageSquare, Cpu, Shield, Send, Loader2, Paperclip, ThumbsUp, ThumbsDown, Bot, User, BrainCircuit, Copy, RotateCcw } from 'lucide-svelte';
    import { globalState } from '$lib/state.svelte.js';
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';
    import { untrack } from 'svelte';

    let message = $state('');
    let messages = $state<any[]>([]);
    let isTyping = $state(false);

    async function loadPastSession(id: number) {
        messages = [];
        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const res = await fetch(`http://localhost:38001/v1/sessions/${id}`, { headers: { 'Authorization': `Bearer ${token}` } });
            if (res.ok) {
                const data = await res.json();
                if (data.messages && data.messages.length > 0) {
                    messages = data.messages.map((m: any) => ({
                        id: m.id,
                        role: m.role,
                        agent: m.role === 'user' ? 'Commander' : 'Sovereign Evaluator',
                        text: m.content,
                        time: new Date(m.created_at).toLocaleTimeString()
                    }));
                }
            }
        } catch(e) { console.error('Error loading session', e); }
    }

    $effect(() => {
        const sid = globalState.chat.activeSessionId;
        untrack(() => {
            if (sid) {
                loadPastSession(sid);
            } else {
                messages = [{ id: Date.now(), role: 'assistant', agent: 'Sovereign Coder', text: 'Sensus Synchronized. Ready for prompt ingestion.', time: new Date().toLocaleTimeString() }];
            }
        });
    });

    function parseMarkdown(text: string) {
        if (!text) return '';
        const raw = marked.parse(text);
        return DOMPurify.sanitize(raw as string, { ADD_TAGS: ['svg', 'path', 'circle', 'line', 'g', 'rect', 'span', 'div'] });
    }

    async function triggerFeedback(msgId: number, type: 'up' | 'down') {
        const msg = messages.find(m => m.id === msgId);
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
               // Retorno visual otimista
               const btnClass = type === 'up' ? 'text-emerald-500 bg-emerald-500/10 border-emerald-500/50' : 'text-rose-500 bg-rose-500/10 border-rose-500/50';
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
        const msg = messages.find(m => m.id === msgId);
        if (msg) {
            message = msg.text;
        }
    }

    async function sendMessage() {
        if (!message.trim() || isTyping) return;
        const currentMsg = message;
        messages = [...messages, { id: Date.now(), role: 'user', agent: 'Commander', text: currentMsg, time: new Date().toLocaleTimeString() }];
        message = '';
        isTyping = true;
        
        let assistantIdx = messages.length;
        const newMsgId = Date.now() + 1;
        messages = [...messages, { id: newMsgId, role: 'assistant', agent: 'Sovereign Evaluator', text: '', time: new Date().toLocaleTimeString() }];

        try {
            const token = localStorage.getItem('sovereign_token') || '';
            const ws_id = globalState.activeWorkspaceId || 'default';
            
            const payload = {
                model: 'gpt-4o',
                messages: [{ role: 'user', content: currentMsg }],
                workspace_id: ws_id,
                session_id: globalState.chat.activeSessionId,
                stream: true
            };

            const response = await fetch('http://localhost:38001/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.body) throw new Error("No readable stream");

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim() === '') continue;
                    if (line.includes('[DONE]')) break;
                    
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            // Capture Native SQLite Session DB ID from the injected SENSUS proxy stream
                            if (data.id && data.id.startsWith('session_')) {
                                const sid = parseInt(data.id.split('_')[1], 10);
                                if (!isNaN(sid) && sid > 0) {
                                    globalState.chat.activeSessionId = sid;
                                }
                            }

                            if (data.choices && data.choices[0].delta && data.choices[0].delta.content) {
                                messages[assistantIdx].text += data.choices[0].delta.content;
                            }
                        } catch(e) { /* ignore JSON chunk errors */ }
                    }
                }
            }
            
            messages = [...messages];
        } catch (error) {
            console.error("Inference Engine Down:", error);
            messages[assistantIdx].text += "\n\n[SYSTEM ERROR] Conexão com o roteador Mesh P2P / OCI foi perdida. Telemetria Inacessível.";
            messages = [...messages];
        } finally {
            isTyping = false;
        }
    }
</script>

<div class="flex flex-col h-full w-full bg-surface-900 border-l border-surface-700 font-sans">
    
    <!-- Chat Header -->
    <header class="flex items-center justify-between p-4 border-b border-surface-700 bg-surface-800/80 shrink-0">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-primary-500/10 rounded-lg">
                <MessageSquare class="w-5 h-5 text-primary-400" />
            </div>
            <div>
                <h2 class="text-surface-100 font-bold tracking-tight">Cibrid Council <span class="text-[10px] bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded ml-2 uppercase tracking-widest font-mono">Encrypted</span></h2>
                <p class="text-xs text-surface-400">P2P Mesh Network routing active.</p>
            </div>
        </div>

        <div class="flex items-center gap-4 text-surface-400">
            <div class="flex flex-col items-end">
                <span class="text-[10px] font-bold uppercase tracking-widest">{globalState.clusterState.status === 'optimal' ? 'Local Cibrid Core' : 'Sovereign Node'}</span>
                <span class="text-xs flex items-center gap-1.5"><div class="w-2 h-2 rounded-full {globalState.clusterState.status === 'optimal' ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse"></div> {globalState.clusterState.status === 'optimal' ? 'Online' : 'Degraded'}</span>
            </div>
            <Cpu class="w-6 h-6 text-surface-500" />
        </div>
    </header>

    <!-- Message Feed -->
    <main class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-6 custom-scrollbar">
        
        {#each messages as msg}
            <div class="flex flex-col max-w-3xl group {msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}">
                <div class="flex items-center gap-2 mb-1.5 px-1">
                    
                    <!-- Sentient Avatar Visual Identity -->
                    {#if msg.role === 'assistant'}
                        <div class="relative w-7 h-7 rounded-full flex items-center justify-center shrink-0">
                            <div class="absolute inset-0 rounded-full border border-primary-500 opacity-20"></div>
                            {#if isTyping && msg.id === messages[messages.length-1].id}
                                <div class="absolute inset-0 rounded-full animate-ping opacity-30 bg-primary-500"></div>
                            {/if}
                            <div class="w-3 h-3 rounded-full bg-primary-500"></div>
                        </div>
                    {:else}
                        <div class="relative w-7 h-7 rounded-full bg-surface-700 flex items-center justify-center shrink-0 p-1.5 text-surface-300">
                            <svg fill="none" stroke="currentColor" class="w-full h-full" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                    {/if}

                    <span class="text-[10px] uppercase font-bold tracking-widest {msg.role === 'user' ? 'text-surface-500' : 'text-primary-400'}">{msg.agent}</span>
                    <span class="text-[10px] text-surface-600 font-mono">{msg.time}</span>
                </div>
                
                <div class="{msg.role === 'user' ? 'bg-surface-700 text-surface-200 rounded-2xl rounded-tr-none' : 'bg-surface-800 border border-surface-700 text-surface-300 rounded-2xl rounded-tl-none'} p-4 shadow-md text-[15px] leading-relaxed prose prose-invert max-w-full overflow-x-auto custom-scrollbar">
                    {@html parseMarkdown(msg.text)}
                </div>

                <!-- Interactions Action Bar (Visible on Hover) -->
                <div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 {msg.role === 'user' ? 'mr-1 justify-end' : 'ml-1 justify-start'}">
                    
                    <!-- Copy Button (Both) -->
                    <button onclick={() => copyToClipboard(msg.text)} class="p-1.5 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-500 hover:text-surface-300 border border-surface-700 transition-all cursor-pointer" title="Copiar Texto">
                        <Copy class="w-3.5 h-3.5" />
                    </button>

                    <!-- Replay / Edit Button (User) -->
                    {#if msg.role === 'user'}
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-surface-800 hover:bg-primary-500/10 text-surface-500 hover:text-primary-400 border border-surface-700 hover:border-primary-500/30 transition-all cursor-pointer" title="Replay / Editar Pergunta">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}

                    <!-- RLHF & Assistant Replay -->
                    {#if msg.role === 'assistant'}
                        <button id="feedback-btn-{msg.id}-up" onclick={() => triggerFeedback(msg.id, 'up')} class="p-1.5 rounded-lg bg-surface-800 hover:bg-emerald-500/10 text-surface-500 hover:text-emerald-400 border border-surface-700 hover:border-emerald-500/30 transition-all cursor-pointer" title="Boa resposta (Like)">
                            <ThumbsUp class="w-3.5 h-3.5" />
                        </button>
                        <button id="feedback-btn-{msg.id}-down" onclick={() => triggerFeedback(msg.id, 'down')} class="p-1.5 rounded-lg bg-surface-800 hover:bg-rose-500/10 text-surface-500 hover:text-rose-400 border border-surface-700 hover:border-rose-500/30 transition-all cursor-pointer" title="Resposta Incorreta (Dislike)">
                            <ThumbsDown class="w-3.5 h-3.5" />
                        </button>
                        <button onclick={() => replayMessage(msg.id)} class="p-1.5 rounded-lg bg-surface-800 hover:bg-amber-500/10 text-surface-500 hover:text-amber-400 border border-surface-700 hover:border-amber-500/30 transition-all cursor-pointer" title="Copiar para Input">
                            <RotateCcw class="w-3.5 h-3.5" />
                        </button>
                    {/if}
                </div>
            </div>
        {/each}

    </main>

    <!-- Input Bar -->
    <footer class="p-4 bg-surface-800/50 border-t border-surface-700 shrink-0">
        <form 
            onsubmit={(e) => { e.preventDefault(); sendMessage(); }}
            class="max-w-4xl mx-auto relative flex items-center bg-surface-900 border border-surface-600 rounded-xl overflow-hidden focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500/50 transition-all shadow-inner"
        >
            <!-- Multimodal Attachment Action (Paperclip) -->
            <button type="button" class="absolute left-2 bottom-2 p-2.5 text-surface-400 hover:text-primary-400 hover:bg-primary-500/10 rounded-lg transition-colors cursor-pointer" title="Anexar Arquivo ou Imagem">
                <Paperclip class="w-5 h-5" />
            </button>

            <textarea 
                bind:value={message}
                placeholder="Ask the Global Cybrid Council..." 
                class="flex-1 bg-transparent border-none text-surface-200 text-sm p-4 pl-14 h-14 resize-none outline-none custom-scrollbar"
                onkeydown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                }}
            ></textarea>

            <button type="submit" disabled={isTyping} class="absolute right-2 bottom-2 p-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                {#if isTyping}
                    <Loader2 class="w-5 h-5 animate-spin" />
                {:else}
                    <Send class="w-5 h-5" />
                {/if}
            </button>
        </form>
        <div class="text-[10px] text-center text-surface-500 mt-2 font-mono uppercase tracking-widest">
             End-to-End Local Execution • Context Limited to Graph Density
        </div>
    </footer>

</div>
