<script lang="ts">
    import { MessageSquare, Cpu, Shield, Send } from 'lucide-svelte';

    let message = $state('');
    let messages = $state([
        { role: 'assistant', agent: 'Sovereign Coder', text: 'Sensus Synchronized. Ready for prompt ingestion.', time: new Date().toLocaleTimeString() }
    ]);

    function sendMessage() {
        if (!message.trim()) return;
        messages = [...messages, { role: 'user', agent: 'Commander', text: message, time: new Date().toLocaleTimeString() }];
        message = '';
        
        // Simular Resposta
        setTimeout(() => {
            messages = [...messages, { role: 'assistant', agent: 'Sovereign Oracle', text: 'Acknowledged. Telemetry stream is stable.', time: new Date().toLocaleTimeString() }];
        }, 1000);
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
                <span class="text-[10px] font-bold uppercase tracking-widest">Oracle Node</span>
                <span class="text-xs flex items-center gap-1.5"><div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div> Online</span>
            </div>
            <Cpu class="w-6 h-6 text-surface-500" />
        </div>
    </header>

    <!-- Message Feed -->
    <main class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col gap-6 custom-scrollbar">
        
        {#each messages as msg}
            <div class="flex flex-col max-w-2xl {msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'}">
                <div class="flex items-center gap-2 mb-1.5 px-1">
                    {#if msg.role === 'assistant'}
                        <Shield class="w-3 h-3 text-primary-500" />
                    {/if}
                    <span class="text-[10px] uppercase font-bold tracking-widest {msg.role === 'user' ? 'text-surface-500' : 'text-primary-400'}">{msg.agent}</span>
                    <span class="text-[10px] text-surface-600 font-mono">{msg.time}</span>
                </div>
                
                <div class="{msg.role === 'user' ? 'bg-surface-700 text-surface-200 rounded-2xl rounded-tr-none' : 'bg-surface-800 border border-surface-700 text-surface-300 rounded-2xl rounded-tl-none'} p-4 shadow-md text-sm leading-relaxed prose prose-invert overflow-hidden">
                    {msg.text}
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
            <textarea 
                bind:value={message}
                placeholder="Ask the Global Cybrid Council..." 
                class="flex-1 bg-transparent border-none text-surface-200 text-sm p-4 h-14 resize-none outline-none custom-scrollbar"
                onkeydown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                }}
            ></textarea>

            <button type="submit" class="absolute right-2 bottom-2 p-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                <Send class="w-5 h-5" />
            </button>
        </form>
        <div class="text-[10px] text-center text-surface-500 mt-2 font-mono uppercase tracking-widest">
             End-to-End Local Execution • Context Limited to Graph Density
        </div>
    </footer>

</div>
