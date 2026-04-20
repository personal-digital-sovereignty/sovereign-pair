import { API_BASE_URL } from '$lib/env_config';
// Svelte 5 Native SSE Store for Real-time Rust Telemetry
export const telemetryState = $state({
    connected: false,
    tokensPerSecond: 0.0,
    avgLatencyMs: 0,
    estimatedCost: 0,
    avgCloudCostPer1k: 0.00625,
    activeModel: 'Not Loaded',
    cpuCores: [] as number[],
    ramUsageMB: 0,
    ramTotalGB: 0,
    vramUsageMB: 0,
    vramTotalMB: 0,
    gpuName: 'GPU Compute',
    gpuTemperature: 0,
    ioRxBytes: 0,
    ioTxBytes: 0,
    firewallBlocks: 0,
    trackersBlocked: 0,
    vaultsCount: 0,
    syncedFiles: 0,
    vaultCategories: [] as string[],
    modelsUsage: {} as Record<string, number>,
    historicalModels: [] as any[],
    contentGaps: [] as any[],
    topTopics: [] as any[],
    securityLogs: [] as any[],
    logs: [] as string[]
});

let pollInterval: any;


export function connectTelemetry() {
    if (pollInterval) return;

    telemetryState.connected = true;
    telemetryState.logs.push(`[${new Date().toLocaleTimeString()}] Sensus Telemetry Polling Linked.`);

    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/v1/analytics/telemetry`);
            if (res.ok) {
                const data = await res.json();
                
                telemetryState.connected = true;
                telemetryState.tokensPerSecond = data.avg_tps || 0;
                telemetryState.avgLatencyMs = data.avg_latency_ms || 0;
                telemetryState.estimatedCost = data.estimated_cost || 0;
                telemetryState.avgCloudCostPer1k = data.avg_cloud_cost_per_1k || 0.00625;
                telemetryState.modelsUsage = data.models_usage || {};
                telemetryState.historicalModels = data.historical_models || [];
                telemetryState.contentGaps = data.content_gaps || [];
                telemetryState.topTopics = data.top_topics || [];
                telemetryState.cpuCores = data.hardware?.cpu_cores || [];
                telemetryState.ramUsageMB = data.hardware?.ram || 0;
                telemetryState.ramTotalGB = data.hardware?.ram_total_gb || 24;
                telemetryState.vramTotalMB = data.hardware?.gpu_vram_total_mb || 0;
                telemetryState.gpuName = data.hardware?.gpu_name || 'GPU Compute';
                telemetryState.ioRxBytes = data.hardware?.io_rx || 0;
                telemetryState.ioTxBytes = data.hardware?.io_tx || 0;
                
                // If there are active models, VRAM is engaged.
                if (data.active_models && data.active_models > 0) {
                    telemetryState.vramUsageMB = 0; // GAP-01 FIX: Removed Math.random() mock. Awaiting Vulkan VK_EXT_memory_budget for strict usage.
                    telemetryState.activeModel = 'Native Cibrid API Protocol';
                } else {
                    telemetryState.vramUsageMB = 0;
                    telemetryState.activeModel = 'Idle';
                }

                telemetryState.firewallBlocks = data.security_blocks || 0;
                telemetryState.trackersBlocked = data.trackers_blocked || 0;
                telemetryState.securityLogs = data.security_logs || [];
                telemetryState.vaultsCount = data.cronos?.vaults_count || 0;
                telemetryState.syncedFiles = data.cronos?.synced_files || 0;
                telemetryState.vaultCategories = data.cronos?.vault_categories || [];
            }
        } catch (e) {
            telemetryState.connected = false;
        }
    }, 1500);
}

export function disconnectTelemetry() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
        telemetryState.connected = false;
        telemetryState.logs.push(`[${new Date().toLocaleTimeString()}] Sensus Telemetry Polling Terminated.`);
    }
}
