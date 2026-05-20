<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { API_BASE_URL } from '$lib/env_config';
    import { Terminal, Download, Play, Pause, Trash2, Clock, Bug, Zap } from 'lucide-svelte';

    import { telemetryState } from '$lib/telemetry.svelte';

    interface LogEntry {
        timestamp: string;
        level: string;
        message: string;
    }

    let eventSource: EventSource | null = null;
    let isPaused = $state(false);
    let logsContainer: HTMLElement;
    let autoScroll = $state(true);

    function connectSSE() {
        if (eventSource) return;
        eventSource = new EventSource(`${API_BASE_URL}/v1/system/stream-logs`);
        
        eventSource.onopen = () => {
            console.log("SSE Stream Opened Successfully.");
        };

        eventSource.onmessage = (event) => {
            if (isPaused) return;
            try {
                const log = JSON.parse(event.data);
                telemetryState.systemLogs = [...telemetryState.systemLogs, log];
                
                // Keep only last 1000 logs in memory to avoid DOM bloating
                if (telemetryState.systemLogs.length > 1000) telemetryState.systemLogs = telemetryState.systemLogs.slice(telemetryState.systemLogs.length - 1000);
                
                if (autoScroll && logsContainer) {
                    setTimeout(() => {
                        logsContainer.scrollTop = logsContainer.scrollHeight;
                    }, 50);
                }
            } catch (e) {
                console.error("Failed to parse log event", e);
            }
        };

        eventSource.onerror = () => {
            // Reconnect logic usually handled by browser, but we can visually show it disconnected
            console.warn("SSE Log Stream disconnected. Waiting for browser to reconnect...");
        };
    }

    function disconnectSSE() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }

    onMount(() => {
        connectSSE();
    });

    onDestroy(() => {
        disconnectSSE();
    });

    function togglePause() {
        isPaused = !isPaused;
    }

    function clearLogs() {
        telemetryState.systemLogs = [];
    }

    function downloadLogs() {
        if (telemetryState.systemLogs.length === 0) return;
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `sovereign_core_${timestamp}.log`;
        
        // Formata os logs exatamente como no terminal
        const rawText = telemetryState.systemLogs.map((l: LogEntry) => `[${l.timestamp}] ${l.level.toUpperCase()} - ${l.message}`).join('\n');
        
        const blob = new Blob([rawText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function getLevelColor(level: string) {
        const lower = level.toLowerCase();
        if (lower.includes('error')) return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
        if (lower.includes('warn')) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
        if (lower.includes('info')) return 'text-sky-400 bg-sky-500/10 border-sky-500/20';
        if (lower.includes('debug')) return 'text-purple-400 bg-purple-500/10 border-purple-500/20';
        if (lower.includes('agent')) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
        return 'text-surface-300 bg-surface-500/10 border-surface-500/20';
    }

    function handleScroll(e: Event) {
        const target = e.target as HTMLElement;
        // If user scrolls up, disable autoScroll. If they hit the bottom, re-enable it.
        const isAtBottom = target.scrollHeight - target.scrollTop <= target.clientHeight + 50;
        autoScroll = isAtBottom;
    }
</script>

<div class="flex flex-col h-full bg-surface-900 border border-surface-700/50 rounded-2xl overflow-hidden shadow-2xl">
    
    <!-- Header -->
    <div class="bg-surface-800/80 backdrop-blur-md px-6 py-4 border-b border-surface-700/50 flex justify-between items-center z-10 shrink-0">
        <div class="flex items-center gap-3">
            <div class="p-2.5 bg-primary-500/20 rounded-xl">
                <Terminal class="w-6 h-6 text-primary-400" />
            </div>
            <div>
                <h1 class="text-xl font-bold text-surface-100 font-syncopate tracking-widest flex items-center gap-2">
                    System Logs
                    {#if !isPaused}
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_theme(colors.emerald.500)]"></span>
                    {:else}
                        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                    {/if}
                </h1>
                <p class="text-sm text-surface-400 font-light max-w-xl line-clamp-1">
                    Real-time Native Backend Telemetry (Sovereign Core / Cibrid Router).
                </p>
            </div>
        </div>

        <div class="flex items-center gap-2">
            <button onclick={togglePause} class="btn-icon {isPaused ? 'bg-amber-500/10 text-amber-400' : 'bg-surface-700 text-surface-300'} px-3 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 hover:bg-surface-600 transition-colors" title={isPaused ? "Resume Stream" : "Pause Stream"}>
                {#if isPaused} <Play class="w-4 h-4"/> {:else} <Pause class="w-4 h-4"/> {/if}
                <span class="hidden md:inline">{isPaused ? 'Paused' : 'Streaming'}</span>
            </button>
            <button onclick={clearLogs} class="btn-icon bg-surface-700 text-surface-300 px-3 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 hover:bg-rose-500/20 hover:text-rose-400 transition-colors" title="Clear Buffer">
                <Trash2 class="w-4 h-4" />
                <span class="hidden md:inline">Clear</span>
            </button>
            <div class="w-px h-6 bg-surface-700 mx-1"></div>
            <button onclick={downloadLogs} class="btn-primary bg-primary-500/10 text-primary-400 border border-primary-500/30 px-3 py-2 rounded-xl text-sm font-semibold flex items-center gap-2 hover:bg-primary-500/20 transition-all shadow-[0_0_15px_theme(colors.primary.500/20)]" title="Export Full Session to File for Debugging">
                <Download class="w-4 h-4" />
                <span class="hidden md:inline">Export .log</span>
            </button>
        </div>
    </div>

    <!-- Terminal Output -->
    <div 
        bind:this={logsContainer}
        onscroll={handleScroll}
        class="flex-1 p-4 overflow-y-auto space-y-1 font-mono text-[13px] bg-black/40 scroll-smooth leading-relaxed"
    >
        {#if telemetryState.systemLogs.length === 0}
            <div class="h-full flex flex-col items-center justify-center text-surface-500 gap-4 opacity-50">
                <Bug class="w-16 h-16 stroke-[1.5]" />
                <p>Waiting for Native Rust Backend interactions...</p>
            </div>
        {:else}
            {#each telemetryState.systemLogs as log}
                <div class="flex items-start gap-3 hover:bg-surface-800/30 px-2 py-1 rounded transition-colors group break-words w-full">
                    <div class="flex-shrink-0 text-surface-500 mt-0.5 w-[75px] truncate text-xs flex items-center gap-1.5 opacity-60 group-hover:opacity-100 transition-opacity">
                        <Clock class="w-3 h-3" />
                        {log.timestamp}
                    </div>
                    
                    <div class="flex-shrink-0 w-16 uppercase text-[10px] font-bold tracking-widest text-center border rounded mt-0.5 {getLevelColor(log.level)}">
                        {log.level}
                    </div>
                    
                    <div class="flex-1 text-surface-200">
                        {#if log.message.includes('✨') || log.message.includes('🧠')}
                            <span class="text-indigo-300 font-semibold">{log.message}</span>
                        {:else if log.message.includes('⚠️')}
                            <span class="text-amber-300">{log.message}</span>
                        {:else if log.message.includes('🚨') || log.message.includes('🛑')}
                            <span class="text-rose-400 font-bold">{log.message}</span>
                        {:else}
                            <span class="opacity-90">{log.message}</span>
                        {/if}
                    </div>
                </div>
            {/each}
        {/if}
    </div>

</div>
