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

---

## 🌟 O Salto Geracional: Qwen 2 (7B) vs Qwen 3 (8B)

A adoção do **Qwen 3 (8B)** como motor de linha de frente para tarefas que exigem raciocínio não linear marca um salto geracional massivo no Sovereign Pair. A diferença não se resume a 1 bilhão de parâmetros a mais, mas sim à **arquitetura de "raciocínio híbrido"**.

| Característica | Qwen 2 7B (`qwen2:7b`) | Qwen 3 8B (`qwen3:8b`) |
| :--- | :--- | :--- |
| **Geração** | Meados de 2024 (Geração 2) | Abril de 2025 (Geração 3) |
| **Parâmetros** | ~7.07 Bilhões | ~8.19 Bilhões |
| **Idiomas Suportados** | 29 idiomas | **Mais de 100 idiomas e dialetos** |
| **Modo de Resposta** | Padrão (Causal) | **Híbrido ("Modo Pensamento" + Modo Padrão)** |
| **Uso de Ferramentas / Agente**| Básico | **Avançado e Nativo** (*Agentic Tool Calling*) |
| **Janela de Contexto** | 128.000 tokens | 40K nativo no Ollama (expansível até 131.000 tokens) |

### 🛠️ Por que o Qwen 3 (8B) e não a Geração Anterior?

1. **O "Modo Pensamento" (Resolução de Problemas Complexos):** Qwen 3 8B absorve a capacidade crítica outrora reservada apenas aos titãs (e ao modelo o1 da OpenAI ou R1). Ele é treinado em *chain-of-thought*, pensando passo a passo e corrigindo suas hipóteses antes de emitir a resposta. Adicionar "Pense passo a passo..." no prompt acorda a fera dormente em seus tensores.
2. **Capacidades de Agente (Tool Calling Seguro):** Altíssima aptidão nativa para manusear ferramentas (JSON/Tooling), o que é o cerne do Kernel Sovereign. Ele pausa o output e invoca nossas buscas financeiras ou leituras vetoriais do Pandas de modo quase determinista - sem corromper a malha.
3. **Hardware Custo x Benefício:** Ele custa irrisórios (para o ano de 2025 e diante) 600mb a 800mb adicionais sob Qwen 2, esmagando pesos ineficientes grandes como 14B antigos e oferecendo a "Mente" de um programador e um analista sênior autônomo sem acionar OOM em máquinas com 8GB a 16GB em RAM Unificada. 

Ao configurar a base, o comando de eleição obrigatória para orquestrações complexas locais deve sempre apontar para:
> `ollama run qwen3:8b`

---

## 🤼 Microsoft Phi-4 (14B) vs Alibaba Qwen 3 (8B)

A diferença de peso (8 Bilhões vs. 14 Bilhões de parâmetros) faz a disputa parecer "injusta" à primeira vista. Contudo, em IAs locais, a batalha é entre **escolas de treinamento e arquiteturas diferentes**, colocando no ringue o **"Canivete Suíço Ágil" (Qwen)** contra o **"Especialista de Laboratório" (Phi-4)**. Eles não concorrem diretamente; eles se complementam.

### 🧬 A "Alma" de Cada Modelo

#### 1. Microsoft Phi-4 (14B): *A Força Bruta Sintética*
A filosofia da linha Phi foca em *"qualidade sobre quantidade"*. Alimentado por **dados sintéticos** (lógica gerada por modelos massivos como GPT-4) no nível de "livros didáticos".
* **A Proposta:** O maior rigor analítico local. Dominante em **STEM** (Ciência, Tecnologia, Engenharia e Matemática) e tolerância zero a alucinação estrutural.
* **O Sacrifício:** Língua portuguesa formal e mecânica; exige absurda taxa de VRAM (9 a 11 GB de RAM livres).

#### 2. Alibaba Qwen 3 (8B): *A Agilidade Híbrida e Poliglota*
Treinado com volume colossal de dados do mundo real em 100 idiomas e raciocínio híbrido on-the-fly.
* **A Proposta:** Versatilidade absoluta focada no dia a dia. Especialista nato em Tool Calling (Agentes), JSON, e português empático instantâneo.
* **O Sacrifício:** Profundidade estrita em lógicas obscuras perde para os 14 bilhões do Phi a menos que você exija explicitamente o uso do "Modo Pensamento".

### 🥊 Arena Prática: Qual Escolher?

| A Tarefa / Necessidade | O Vencedor | Por que ganha? |
| :--- | :--- | :--- |
| **Fluência em Português / Copy** | 🏆 **Qwen 3 (8B)** | Compreende ironias, regionalismos e escreve de forma empática sem a frieza acadêmica do Phi-4. |
| **Programação e *Debugging* Pesado** | 🏆 **Phi-4 (14B)** | A densidade de 14B atua como um engenheiro cirúrgico treinado puramente em manuais de código. |
| **Uso de Agentes (n8n, JSON, LangChain)**| 🏆 **Qwen 3 (8B)** | O Qwen 3 é o rei do "Tool Calling". Ele pausa perfeitamente a conversa para injetar ferramentas. |
| **Matemática Fria / Equações** | 🏆 **Phi-4 (14B)** | Rigor sintético intransponível. A taxa de erro e "alucinação criativa" em contas exatas é nula. |
| **Velocidade e Resumo de Documentos** | 🏆 **Qwen 3 (8B)** | Responde num piscar de olhos, lidando majestosamente com arquivos pesados no RAG com baixo custo na máquina. |

### ⚖️ O Veredito de Hardware

#### 🟢 Cenário A: 16 GB de RAM ou GPU robusta
**MANTENHA OS DOIS.** 
* **Qwen 3 (8B) como Assistente Executivo Diário:** Modelo padrão (85% do uso) para RAG rápido, UI, e e-mails instantâneos.
* **Phi-4 (14B) como Consultor Especialista:** Usado pontualmente para debugging profundo, ciência de dados e orquestração lógico-científica pesada.

#### 🔴 Cenário B: 8 GB de RAM (Notebooks e PC Doméstico)
**MANTENHA APENAS O QWEN 3 (8B).**
O Phi-4 de 14B levará seu sistema aos limites da morte via paginação de disco (Swap freezing), gerando 1-2 tokens por segundo travando a UI do Sovereign. Concentre-se exclusivamente no `qwen3:8b` e exija *"Pense passo a passo..."* quando ele esbarrar em obstáculos, garantindo fluidez e integridade mental no kernel.
