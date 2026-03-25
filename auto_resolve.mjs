import fs from 'fs';

const AXUM_API = "http://localhost:38001";
const OLLAMA_API = "http://localhost:11434/api/generate";
const MODEL = "llama3.2:latest";

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function resolveGaps() {
    console.log("🕵️  [Autómaton] Iniciando varredura por Knowledge Gaps pendentes no Axum...");
    
    let gaps = [];
    try {
        const res = await fetch(`${AXUM_API}/v1/rag-engine/gaps`);
        if (!res.ok) throw new Error("Falha ao buscar gaps");
        const allGaps = await res.json();
        gaps = allGaps.filter(g => !g.status || g.status === 'pending');
    } catch(e) {
        console.error("❌ Erro de comunicação com o Axum:", e.message);
        return;
    }

    if (gaps.length === 0) {
        console.log("✅ [Autómaton] Rumo à Perfeição. Nenhum Gap pendente para resolver no momento.");
        return;
    }

    console.log(`🚨 [Autómaton] Foram detectados ${gaps.length} Gaps. Acionando Mente Sintética Local (${MODEL}) para forjar as resoluções...\n`);

    for (let i = 0; i < gaps.length; i++) {
        const gap = gaps[i];
        console.log(`[${i+1}/${gaps.length}] 🧠 Resolvendo Gap de Frequência ${gap.frequency}: "${gap.query}"`);
        
        let ai_context = "";
        try {
            const prompt = `Você é um curador de conhecimento sênior corporativo no Sovereign Pair. Um usuário tentou e falhou repetidamente com a seguinte query: '${gap.query}'. Escreva estrita e unicamente um parágrafo técnico denso em português (Brasil) respondendo ou provendo um guia/resposta absoluta para sanar esta busca. Sem saudações. Direto ao ponto.`;
            
            const ask = await fetch(OLLAMA_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL,
                    prompt: prompt,
                    stream: false
                })
            });
            const askJson = await ask.json();
            ai_context = askJson.response.trim();
        } catch(e) {
            console.error("  ❌ Falha de Inferência com Ollama:", e.message);
            continue;
        }

        console.log(`  ✅ IA Respondeu (${ai_context.length} bytes). Injetando Dados Cíbridos na Matrix...`);
        
        const safeGapId = "Gap_" + gap.id.substring(0, 8);
        const fileName = `${safeGapId}.md`;
        const mdPayload = `# Knowledge Resolution: ${safeGapId}\n\n**Unresolved User Query:**\n${gap.query}\n\n**Operator Context Injection:**\n(Auto-Resolvido por Autómaton)\n${ai_context}`;
        
        try {
            // 1. Escreve diretamente no O.S (Vault Master Markdown Root)
            await fetch(`${AXUM_API}/v1/vault/document/${encodeURIComponent(fileName)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workspace_id: 1, content: mdPayload })
            });

            // 2. Registra o Dual-Truth Soft Delete na Memória SQLite
            const putRes = await fetch(`${AXUM_API}/v1/rag-engine/gaps/${gap.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resolution_content: ai_context })
            });
            const textResponse = await putRes.text();
            
            console.log(`  🛡️ Dual-Truth Gravado Sucesso. Void '${safeGapId}' neutralizado. Axum: ${textResponse}\n`);
        } catch(e) {
            console.error("  ❌ Falha na injeção HTTP:", e.message);
        }
        
        // Cooldown para não fritar o processador e dar respiro de DB I/O
        await sleep(1500); 
    }
    
    console.log("🎉 [Autómaton] Operação Finalizada! Todos os Gaps detectados foram varridos do mapa cognitivo.");
}

resolveGaps();
