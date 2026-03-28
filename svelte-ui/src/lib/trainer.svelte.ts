export const trainerState = $state({
    // Global Engine Triggers
    internetToRagActive: true,
    strictGrounding: true,
    internalMonologue: false,
    reasoningDepth: 80,
    auditIntensity: 65,

    // Unsloth Lora Constraints
    loraRank: 16,
    batchSize: 4,
    learningRate: 0.0002,

    // RAG Perfection Coordinates
    embeddingAlignmentAlpha: 96,
    contextDepthTopK: 40,

    // Live Training Telemetry / Backend Mock Fallbacks
    isTraining: false,
    vramUsageGb: 0.0,
    vramTotalGb: 24.0,
    epochCurrent: 0,
    epochTotal: 5,
    trainingSpeedTokensSec: 0.0,
    lastCheckpoint: "Idle",

    // Deep Research / RAG Sync Data
    knowledgeGapPercentage: 0.0,
    sourcesScanned: 0,
    sourcesScannedDelta: 0,
    recentlyAcquiredKnowledge: [] as { id: string; title: string; timeAgo: string; type: 'article' | 'description' }[],

    // Unsloth Extended Metrics
    loss: "1.241",
    gradNorm: "0.45",
    learningRateLabel: "2e-4",
    stepTime: "0.82s",
    memoryBw: "1,024 GB/s",
    temperatureC: 64,
    vramHistory: new Array(12).fill(0),
    
    // Distillation Engine
    distillationEpochs: 3,
    distillationBatchSize: 4,
    hasOpenAiKey: true,
    hasAnthropicKey: false,
    datasetSizeCount: 1200000,
    
    // Deep Research Orchestrator
    deepResearchPrompt: "",
    isDeepResearchActive: false,
    deepResearchCrossEncoder: true,
    deepResearchStrictHallucination: true,
    deepResearchGroundingFocus: false,
    deepResearchQueryExpansion: false,
    deepResearchFirewallEnabled: true,
    deepResearchScrapedSources: 0,
    deepResearchModel: "llama3.2:latest"
});

export const AI_MODELS = [
    { id: 'qwen2.5:1.5b', name: 'Qwen 2.5 1.5B', type: 'local', provider: 'ollama', sizeB: 1.5, badge: 'Edge Optimized' },
    { id: 'llama3.2:3b', name: 'Llama 3.2 3B', type: 'local', provider: 'ollama', sizeB: 3, badge: 'Edge Optimized' },
    { id: 'phi3.5', name: 'Phi-3.5 Mini', type: 'local', provider: 'ollama', sizeB: 3.8, badge: 'Edge Optimized' },
    { id: 'llama-3-8b', name: 'Llama 3 8B', type: 'local', provider: 'ollama', sizeB: 8, badge: 'Local Server' },
    { id: 'Dionysus-14B', name: 'Dionysus-14B (Local Edge Pi)', type: 'local', provider: 'sovereign-mesh', sizeB: 14, badge: 'Tier 2 (Advanced)' },
    { id: 'Nexus-70B', name: 'Nexus-70B (Oracle Cloud GPU)', type: 'local', provider: 'sovereign-mesh', sizeB: 70, badge: 'Tier 1 (Elite)' },
    { id: 'GPT-4o', name: 'GPT-4o (OpenAI)', type: 'external', provider: 'openai', sizeB: 1000, badge: 'Tier 1 (Elite)' },
    { id: 'Claude-3.5-Sonnet', name: 'Claude 3.5 Sonnet (Anthropic)', type: 'external', provider: 'anthropic', sizeB: 1000, badge: 'Tier 1 (Elite)' }
];

export async function fetchTrainerStats() {
    try {
        const res = await fetch('http://localhost:38001/v1/engineer/trainer/stats');
        if (res.ok) {
            const data = await res.json();
            trainerState.knowledgeGapPercentage = data.knowledge_gap_percentage || 0;
            trainerState.sourcesScanned = data.sources_scanned || 0;
            trainerState.sourcesScannedDelta = data.sources_scanned_delta || 0;
            if (data.recently_acquired) {
                trainerState.recentlyAcquiredKnowledge = data.recently_acquired;
            }
            
            // Telemetry
            trainerState.isTraining = data.unsloth?.is_training || false;
            if(data.unsloth) {
                trainerState.vramUsageGb = data.unsloth.vram_usage_gb || 0;
                trainerState.vramTotalGb = data.unsloth.vram_total_gb || 24.0;
                trainerState.epochCurrent = data.unsloth.epoch_current || 0;
                trainerState.epochTotal = data.unsloth.epoch_total || 5;
                trainerState.trainingSpeedTokensSec = data.unsloth.tokens_per_sec || 0;
                trainerState.lastCheckpoint = data.unsloth.last_checkpoint || 'Idle';

                trainerState.loss = data.unsloth.loss || "0.000";
                trainerState.gradNorm = data.unsloth.grad_norm || "0.00";
                trainerState.learningRateLabel = data.unsloth.learning_rate || "Idle";
                trainerState.stepTime = data.unsloth.step_time || "Idle";
                trainerState.memoryBw = data.unsloth.memory_bw || "0 GB/s";
                trainerState.temperatureC = data.unsloth.temperature_c || 0;

                // Push rolling VRAM history
                trainerState.vramHistory.push(trainerState.vramUsageGb);
                if (trainerState.vramHistory.length > 12) {
                    trainerState.vramHistory.shift();
                }
            }
        }
    } catch(e) {
        console.error("Failed to fetch Live Trainer Telemetry from Axum:", e);
    }
}

export async function sendUnslothControl(action: 'play' | 'pause' | 'stop') {
    try {
        await fetch('http://localhost:38001/v1/engineer/trainer/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        await fetchTrainerStats(); // Force refresh UI
    } catch(e) {
        console.error("Unsloth RPC failed:", action, e);
    }
}

// JSON Export Aggregator for File I/O
export function exportTrainerConfig() {
    const payload = {
        model: "Llama-3-8B-Instruct-v0.1",
        version: "0.9.7",
        timestamp: new Date().toISOString(),
        config: {
            internet_to_rag: trainerState.internetToRagActive,
            strict_grounding: trainerState.strictGrounding,
            internal_monologue: trainerState.internalMonologue,
            lora_rank: trainerState.loraRank,
            batch_size: trainerState.batchSize,
            learning_rate: trainerState.learningRate,
            embedding_alignment_alpha: trainerState.embeddingAlignmentAlpha / 100, // Normalized
            context_depth_top_k: trainerState.contextDepthTopK
        }
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `sovereign_trainer_config_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Reflection Lab Operations
export function getSelfCorrectRatio() {
    return (100 - trainerState.knowledgeGapPercentage).toFixed(1);
}

export function exportReflectionLogs(liveStreamData: any[] = []) {
    const payload = {
        model: "Llama-3-8B-Instruct-v0.1",
        version: "0.9.7",
        timestamp: new Date().toISOString(),
        reflection_state: {
            think_before_response: trainerState.internalMonologue,
            reasoning_depth: trainerState.reasoningDepth,
            audit_intensity: trainerState.auditIntensity,
            self_correct_ratio: getSelfCorrectRatio()
        },
        logs: liveStreamData
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `reflection_lab_audit_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Distillation Engine Operations
export function getSimilarityScoreBaseline() {
    return Math.max(0.70, (1.0 - (trainerState.knowledgeGapPercentage / 100))).toFixed(2);
}

export function exportDistillationLogs(teacherModel: string, studentModel: string, runLogs: string[]) {
    const payload = {
        session: `distillation_${Date.now()}`,
        teacher_model: teacherModel,
        student_model: studentModel,
        parameters: {
            epochs: trainerState.distillationEpochs,
            batch_size: trainerState.distillationBatchSize
        },
        dataset_size: trainerState.datasetSizeCount,
        final_similarity_score: getSimilarityScoreBaseline(),
        distillation_logs: runLogs
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `distillation_manifest_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
