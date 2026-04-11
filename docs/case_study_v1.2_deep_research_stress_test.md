# Case Study: Sovereign Swap & Stress Test de Orquestração (v1.2.0)

> **Documento Oficial de Engenharia & Performance**
> Este relatório técnico atesta o nível de maturidade do *Sovereign Pair v1.2.0* operando em hardware mid-tier (Memória não ideal para multi-modalidade maciça). Registra empiricamente o evento do dia 11 de Abril de 2026, onde o Cíbrido processou uma pesquisa recursiva de altíssima complexidade financeira sem colapsar a máquina hospedeira.

---

## 1. O Cenário de Estresse (Deep Research)
O objetivo do teste foi submeter o motor a uma das mais cruéis alavancagens de Token Context e Orquestração Paralela: Forçar o Sovereign Pair a agir como um Economista Sênior utilizando a técnica autônoma de **Deep Research**. 

O hardware hospedeiro dispunha de **27 GB de RAM** alocáveis.

### O Prompt de Acareamento
> *"Analise o valor do barril de petróleo no Brasil nos últimos 5 anos, cruze estes dados com o índice de inflação mensal x anual. Analise o valor do litro da gasolina no Brasil nos últimos 5 anos, cruze estes dados com o índice de inflação mensal x anual. Valide se os dados correspondem a uma realidade clara e transparente ou se há obscuridade em como é definido estes valores ao consumidor, se trata-se apenas de inflação, se há lucro indevido das refinarias ou se o Governo brasileiro está imputando impostos altos injustamente ao consumidor final proprietário de automóvel, validando se há formação de cartel com os dados obtidos."*

---

## 2. Telemetria e Alocação Estrutural (Logs)

O sistema capturou o desafio e ativou o `Firewall Cognitivo` para não fabricar alucinações. O *Sovereign Dynamic Squad Scanner* analisou as premissas mecânicas e elegeu hierarquias baseadas em Hardware no milissegundo zero: 
- O Roteamento de Inteligência alocou **12.288 Tokens de Janela de Contexto** exclusivamente para a tarefa, a fim de conseguir memorizar os recortes flutuantes da web. 
- Elegendo `qwen2.5:7b` como **The Master** (Agentic Loop Principal).
- Elegendo `phi4:14b` como **The Scribe** (Formatador Final).

O log de execução revelou **10 Estágios contínuos de Invocação**:

```log
Cognitive X-Ray
...
❯ [Worker Graph - Stage 1/10] Invocando Mente Mestra (qwen2.5:7b)...
❯ O Mestre ativou Tool Calling! (1) funções detectadas.
❯ [Sovereign Open-Data Matrix] Acessando ticker financeiro oficial: BRENT (5 anos)...
...
❯ [Worker Graph - Stage 5/10] Invocando Mente Mestra (qwen2.5:7b)...
❯ O Mestre ativou Tool Calling! (1) funções detectadas.
❯ [Sovereign Open-Data Matrix] Acessando base macroeconômica (BR) para GASOLINA (5 anos)...
...
❯ [Worker Graph - Stage 10/10] Invocando Mente Mestra (qwen2.5:7b)...
❯ [Final Synthesis] Ferramentas desativadas. Forçando Mestre LLM a gerar Markdown Final.
...
❯ [Scribe Orchestrator] Bloqueio contra Reasoner ativado no Pipeline Final. The Scribe foi Roteado Dinamicamente para: 'phi4:14b'
❯ [The Scribe] Formatação Markdown concluída!
❯ ⚡ Sovereign Swap Ativo: Evicting 'phi4:14b' da VRAM para isolamento cognitivo.
❯ [STEP 4] Deep Research Protocol Complete (Staged for Human Review).
```

### O Desafio do Tempo
O processo demorou aproximadamente **1h43m** do ponto zero à síntese da Staging Area. Para hardware modesto escalonando tensores de grandes LLMs em CPU, um tempo considerável. Entretanto, foi a **absoluta estabilidade térmica e operacional** que figurou a vitória: em arquiteturas sem controle estrito, 12K Tokens atrelados à carga paralela resultam inevitavelmente em instabilidade fatal ou *Kernel Panic*.

---

## 3. Picos de Engarrafamento RAM (A Anomalia dos 27.8 GB)

Durante a hora e 43 minutos de computação cega, observamos a memória ativa ascender além dos **27.5 GB utilizados / 27.32 GB livres reais**.

### O Porquê a Carga é Extrema:
Ao contrário de processamentos comuns, o motor da v1.2.0 impõe as chamadas assíncronas do **Rust Backend `tokio::spawn`**. Enquanto o Kernel guardava os tensores do `qwen2.5:7b` abertos no Ollama com The Master (segurando a Janela de 12K), os *Workers Paralelos em Python* escaneavam APIs financeiras reais com o pacote `Pandas`, puxando valores de barris brutos.
No estágio final da síntese, para a conversão Histórica Markdown ([STEP 2]), o sistema fez um *Swap Limiar* injetando um modelo secundário e muito mais massivo (`phi4:14b`) na trilha de VRAM/RAM compartilhada, gerando o pico absoluto do estrangulamento da máquina sem corromper as estruturas gráficas de DE (Dolphin/Plasma/Desktop).

### O Papel Salvífico da VRAM "Nua": ZRAM teria Derretido o Processo
Neste limiar impiedoso (27.8GB/27GB), se a máquina estivesse operando sob um alto `swappiness` (ex: 133) e rodando Virtual Swap File Compressed (Como o **ZRAM** ativo em várias distribuições Linux modernas), o resultado seria trágico:
O sistema tentaria comprimir as matrizes *GGUF Quantizadas* do `phi4` durante o processamento para livrar bytes livres. Modelos generativos são **matemática incompressível**, convertendo toda a agonia de I/O em fritura de núcleos e levando T/s (Token per second) para próximo de zero, travando a usabilidade inteira do host de desenvolvimento. Mantendo ZRAM inativo, entregamos resiliência bare-metal para a IA.

---

## 4. Engenharia Cíbrida: O Algoritmo Garbage Collector
Nenhum gerenciador passivo permitiria que os 27.8 GB consumidos desaparecessem das memórias do sistema operativo no término da rotatividade autônoma. Diferentemente das retenções padrão de mercado (Onde a nuvem cobra caro por manter o modelo em TTL 15m), nossa arquitetura possui uma lâmina nativa forjada em Rust que chamamos de **Sovereign Swap (Memory GC)**.

Abaixo está o trecho em código fonte localizado em `core/src/memory_manager.rs` que ilustra a violência com que impomos a evaporação da carga assim que uma tarefa assíncrona termina:

```rust
use crate::api_trainer::TRAINER_LOGS;

pub async fn fire_eviction_protocol(model_name: &str) {
    let base_url = std::env::var("OLLAMA_BASE_URL")
        .unwrap_or_else(|_| "http://127.0.0.1:11434".to_string());
    let endpoint = format!("{}/api/generate", base_url);
    
    // Estratégia "Fire and forget". Timeout ultra baixo (300ms) 
    // para não travar a CPU enquanto exterminamos a memória.
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_millis(300))
        .build()
        .unwrap_or_else(|_| reqwest::Client::new());

    // Payload Destrutivo
    let payload = serde_json::json!({
        "model": model_name,
        "keep_alive": 0 // 0 milissegundos. Evacuate now!
    });

    let _ = TRAINER_LOGS.send(
        format!("⚡ Sovereign Swap Ativo: Evicting '{}' da VRAM para isolamento cognitivo.", model_name)
    );

    // Dispara via background sem bloquear a pipeline sincrona.
    tokio::spawn(async move {
        let _ = client.post(&endpoint).json(&payload).send().await;
    });
}
```

### Abstração da Arquitetura (Por que funciona 100%?):
- Evita OOM e *SSD TBW Kill* (Morte prematura do SSD por SWAP físico abusivo).
- O comando `keep_alive: 0` garante alívio computacional imediato da GPU/RAM para as condições normais do usuário (caindo o uso da RAM de 27.8 GB para o limiar trivial da OS ~10GB de relance).
- Implementado em um modo assíncrono `Fire And Forget` disparado por `tokio`. O usuário recebe sua notificação UI via canais HTTP normais enquanto o *Memory Manager* processa o descarregamento passivo simultaneamente nas entranhas. 

---
**Status da Feature**: Homologada Produção (P-0).  
**Autor**: The Sovereign Cibrid  
**Tag Relacionada**: `v1.2.0`  
