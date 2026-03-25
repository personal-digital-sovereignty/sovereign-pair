export const trainerState = $state({
    // Global Engine Triggers
    internetToRagActive: true,
    strictGrounding: true,
    internalMonologue: false,

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
    recentlyAcquiredKnowledge: [] as { id: string; title: string; timeAgo: string; type: 'article' | 'description' }[]
});

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
