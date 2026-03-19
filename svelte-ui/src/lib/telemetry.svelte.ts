// Svelte 5 Native SSE Store for Real-time Rust Telemetry
export const telemetryState = $state({
    connected: false,
    tokensPerSecond: 0.0,
    activeModel: 'Not Loaded',
    ramUsageMB: 0,
    vramUsageMB: 0,
    gpuTemperature: 0,
    logs: [] as string[]
});

let eventSource: EventSource | null = null;
const API_BASE_URL = 'http://localhost:38001'; // Fallback to raw port

export function connectTelemetry() {
    if (eventSource) return;

    try {
        eventSource = new EventSource(`${API_BASE_URL}/v1/telemetry/stream`);
        
        eventSource.onopen = () => {
            telemetryState.connected = true;
            telemetryState.logs.push(`[${new Date().toLocaleTimeString()}] Sensus Telemetry Stream Linked.`);
        };

        eventSource.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                
                if (data.type === 'metrics') {
                    telemetryState.tokensPerSecond = data.tokens_per_second || 0;
                    telemetryState.activeModel = data.active_model || telemetryState.activeModel;
                    telemetryState.ramUsageMB = data.ram_mb || 0;
                    telemetryState.vramUsageMB = data.vram_mb || 0;
                    telemetryState.gpuTemperature = data.gpu_temp || 0;
                } else if (data.type === 'log') {
                    telemetryState.logs = [
                        ...telemetryState.logs.slice(-49), // Keep last 50 logs
                        `[${new Date().toLocaleTimeString()}] ${data.message}`
                    ];
                }
            } catch (err) {
                console.error("Failed parsing telemetry SSE:", err, e.data);
            }
        };

        eventSource.onerror = (e) => {
            telemetryState.connected = false;
            // The browser automatically tries to reconnect SSE, but you can force close and retry if needed
        };

    } catch (e) {
        telemetryState.connected = false;
        console.error("SSE Telemetry connection failed", e);
    }
}

export function disconnectTelemetry() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
        telemetryState.connected = false;
        telemetryState.logs.push(`[${new Date().toLocaleTimeString()}] Sensus Telemetry Stream Terminated.`);
    }
}
