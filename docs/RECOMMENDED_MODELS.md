# Sovereign Engine: Local Models Guide (v1.0.1)

O Sovereign Pair foi arquitetado para operar em topologias híbridas e locais. Porém, para evitar *Out-of-Memory (OOM)*, "swap freezing" do sistema operacional ou baixa velocidade de geração de tokens (Lentidão Severa), os modelos executados localmente (via Ollama) devem ser milimetricamente escolhidos de acordo com o seu hardware.

Este documento traz a recomendação das matrizes cognitivas oficiais aprovadas para o Engine v1.0.0+.

---

## 🚀 Tier 1: Perfil Sênior (Hardware de Alta Performance)
**Público-Alvo:** Workstations com Placas de Vídeo Dedicadas (GPUs Nvidia RTX 3060+ / Mac M-Series com 32GB+ RAM unificada) ou Desktops com +32GB RAM DDR5 rápidos.

Neste cenário de hardware generoso, o sistema pode alocar simultaneamente Modelos Roteadores Rápidos e Orquestradores Pesados ("Mistura de Especialistas" - MoE).

### Os Modelos (Trindade Oficial)
*   `phi4:14b` **(Agente Crítico e Auditor)**: Essencial para revisões de segurança e lógicas. Implacável na matemática.
*   `qwen2.5-coder:14b` **(Interpretador de Código)**: SOTA local para geração e execução de DataFrames e lógica complexa de programação no Terminal.
*   `deepseek-r1:8b` ou `r1:7b` **(Orquestrador Cognitivo)**: Usado antes do RAG (*WAG Optimizer*) para gerar blocos de raciocínio lógico `<think>` antes de buscar ativamente na web.
*   `llama3.1:8b` **(Master Scribe)**: Focado em orquestrar as ferramentas e gerar o relatório corporativo Markdown perfeitamente finalizado.
*   **Porteiros Rápidos:** `gemma3:4b` ou `llama3.2:3b`. Aprovam ferramentas JSON em milissegundos servindo como a "porta de entrada" do Kanban e Hub.

---

## ⚖️ Tier 2: Perfil Agilidade (Notebooks e Hardware Doméstico)
**Hardware Simulado:** Notebooks APU Modernos (ex: **Ryzen 7 5500U, i7 de 10ª+ Geração, 16GB a 20GB de RAM, Gráficos Integrados**).

### Diagnóstico do Ambiente (20GB RAM)
Um processador Ryzen 7 5500U utiliza gráficos integrados (Radeon Vega). A RAM do sistema (20GB) é totalmente compartilhada entre o CPU e a Placa de Vídeo. 
Se você carregar um modelo de **14B** (que ocupa ~9GB na RAM) junto a outro modelo roteador **3B** (~2 GB), sobrarão menos de 8GB para o Windows/Linux, O IDE (VSCode/Cursor), o backend do Sovereign e centenas de abas do navegador. 
Se a RAM engasgar, o sistema começará a fazer "Paging/Swap" no SSD, tornando a geração de texto brutalmente lenta (~2 a 4 tokens por segundo) e a máquina congelará.

### Solução e Corte de Pesos Morte
Para este perfil, nós **bloqueamos terminantemente o download de modelos 14B**. A estratégia deve focar em modelos de 8B super-destilados que entregam a mesma qualidade consumindo metade da memória.

### Os Modelos Seguros (Tier 2 Matrix)
*   **[Removido]** ❌ `phi4:14b` e `qwen2.5-coder:14b` — *Motivo: Heavy-lifting fatal para 20GB compartilhados.*
*   `deepseek-r1:7b` **(WAG Reasoner & Orquestrador)**: Use o modelo de 7B no lugar do 14B. O Deepseek 7B destilado da Qwen possui capacidades analíticas que humilham antigos modelos de 30B, custando apenas **4.7 GB de RAM**. 
*   `qwen2.5-coder:7b` **(Codificador e Lógico)**: Custando míseros 4.7 GB, atende perfeitamente ao *Sandbox Python* no lugar do colossal 14B.
*   `llama3.2:3b` **(Agente de Retaguarda Kanban/Hub)**: Pesando gloriosos **2.0 GB**, será o roteador de base. Não crasheia a máquina quando rola paralelamente com os motores pesados de 7B.
*   `phi4-mini:3.8b` **(O Auditor Matemático Menor)**: O substituto do gigante 14b quando precisarmos fazer cruza estrita de matemática sem explodir a memória. Pesa apenas 2.5 GB.

**Resumo da Ópera (Para Ryzen 7 5500U - 20GB):**
O seu ecossistema perfeito de máxima eficiência se construirá na intersecção do `DeepSeek-r1 7B` com o `Llama3.2:3b`. Deletando arquivos de 14B e finetunings de 9B, você resgata gigabytes vitais de banda de memória SSD para fazer a sua infraestrutura Multi-Agente voar nativamente!
