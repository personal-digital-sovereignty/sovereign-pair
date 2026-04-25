# 🏛️ Sovereign Pair — Engineering Blueprint
## O Livro Aberto da Engenharia Cíbrida

Este documento serve como o manifesto técnico definitivo do Sovereign Pair. Ele detalha "cada parafuso" de nossa engenharia, desde a orquestração de threads em Rust até o pipeline de inferência agêntica.

---

## 1. Visão Geral da Arquitetura (The Cybrid Nexus)

O Sovereign Pair opera sob um modelo **Cíbrido (Cibernético + Híbrido)**. Ele combina a segurança e performance de um núcleo escrito em **Rust** com a flexibilidade do ecossistema de dados e IA em **Python**.

### 1.1 Diagrama de Fluxo Mestre
```mermaid
graph TD
    User((Usuário)) <--> Svelte[Frontend SvelteKit]
    Svelte <--> Axum[Backend Axum / Rust]
    
    subgraph "Sovereign Core (Rust)"
        Axum --> Router[Model Router]
        Router --> Ollama[Local Ollama]
        Router --> Cloud[Cloud Providers: Qwen/Nvidia/OpenRouter]
        
        Axum --> Sensus[Sensus Sync Engine]
        Sensus <--> SQLite[(Sovereign Memory DB)]
        Sensus <--> Markdown[/Markdown Vault/]
        
        Axum --> AgentLoop[Reflexive Agent Loop]
    end
    
    subgraph "Python Workers (The Squad)"
        AgentLoop --> Nurse[The Nurse: Data Scraper]
        AgentLoop --> Doctor[The Doctor: Financial Analyst]
        AgentLoop --> Accountant[The Accountant: Math Engine]
    end
    
    subgraph "Cloud Mesh"
        Axum <--> OCIMesh[Oracle Cloud Mesh Tunnel]
        OCIMesh <--> OCINode[Oracle aarch64 Node]
    end
```

---

## 2. Componentes de Engenharia

### 2.1 [Sensus Sync Engine](sensus_sync_engine.md)
O **Sensus** é o nosso sistema de persistência dual. Ele garante que o estado do sistema (tarefas, notas, logs) esteja sempre disponível tanto em um banco de dados relacional (SQLite para performance) quanto em arquivos Markdown legíveis por humanos (Vault para soberania e portabilidade).

### 2.2 [Reflexive Agent Loop](agentic_workflows.md)
Diferente de chatbots comuns, o Sovereign Pair utiliza um loop reflexivo baseado em "Pensamentos" e "Ações" (ReWOO, Reflexion, etc).

### 2.3 [Observabilidade & FinOps](observability_llmops.md)
Monitoramento de métricas TTFT/TPS e gestão de custos de inferência via Semantic Caching.

### 2.4 Epistemic Guard (Segurança)
Blindagem de nível de kernel para LLMs:
*   **KMS**: Chaves de API nunca são salvas em texto puro.
*   **Prompt Sanitization**: Proteção contra injeção de prompt e exfiltração de dados sensíveis.
*   **OOM Guard**: Telemetria de hardware em tempo real (VRAM/RAM) que ajusta a janela de contexto dinamicamente para evitar crashes.

---

## 3. Topologia de Rede (OCI Mesh)
Não expomos portas. O túnel SSH reverso cria uma ponte segura entre o hardware local e a nuvem Oracle.

```mermaid
sequenceDiagram
    participant Local as Master Node (Local)
    participant SSH as SSH Tunnel
    participant OCI as Oracle Cloud Node
    
    Local->>SSH: Estabelece Túnel Seguro (Porta 41434)
    SSH->>OCI: Mapeia para localhost:11434 (Ollama)
    Local->>OCI: Envia inferência via localhost:41434
    OCI-->>Local: Retorna tokens via túnel
```

---

## 4. Guia de Manutenção de "Parafusos"
(Em construção: Detalhamento de cada módulo do `core/src`)
