# 🧬 Mecânicas de RAG & Pesquisa Soberana

Este documento detalha o funcionamento interno do motor de Retrieval-Augmented Generation (RAG) e os fluxos de Deep Research.

---

## 1. Ephemeral Knowledge RAG (Pesquisa Web)

O sistema não armazena permanentemente todo o lixo da internet. Ele utiliza o conceito de **Conhecimento Efêmero**.

- **Workflow**:
    1. O sistema dispara scrapers (Nurse) para coletar dados recentes.
    2. Os dados são injetados em uma tabela SQLite temporária (`ephemeral_knowledge`).
    3. O **Cross-Encoder Reranker** filtra o ruído e seleciona apenas os chunks relevantes.
    4. Após a inferência, o conhecimento efêmero é purgado ou arquivado de acordo com a política de retenção.

---

## 2. Deep Research Engine

O motor de pesquisa profunda opera em ciclos de reflexão e auditoria.

- **Scribe (Analista)**: Escreve o relatório baseado nos fatos brutos.
- **Auditor (Sycophancy Breaker)**: Verifica se o Scribe inventou dados ou ignorou contradições.
- **Grounding Engine**: Trava a IA para responder estritamente com base nos documentos fornecidos, ignorando sua memória estática de treinamento.

---

## 3. Apêndice: Case Study - Deep Research Stress Test (v1.2.10)

Durante os testes de stress da v1.2.10, validamos a eficácia do sistema contra alucinações.

- **Cenário**: Análise financeira complexa envolvendo tickers brasileiros e câmbio PTAX.
- **Resultado**: O sistema produziu relatórios bitwise idênticos (SHA-256) em execuções repetidas com modelos de 8B e 14B, provando que o determinismo foi alcançado através da injeção rigorosa de contexto e auditoria adversária.
