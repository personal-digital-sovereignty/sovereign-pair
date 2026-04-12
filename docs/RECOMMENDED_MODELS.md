# Sovereign Engine: Local Models Guide (v1.2.0)

O Sovereign Pair foi arquitetado para operar em topologias híbridas e locais. Porém, para evitar *Out-of-Memory (OOM)*, "swap freezing" do sistema operacional ou baixa velocidade de geração de tokens (Lentidão Severa), os modelos executados localmente (via Ollama) devem ser cirurgicamente escolhidos através da filosofia do "Time dos Sonhos" (A Elite Pipeline).

Acumular dezenas de modelos redundantes no seu SSD apenas fragmenta o Córtex de Orquestração, instiga conflitos na extração JSON e quebra a máquina.

Este documento formaliza as matrizes cognitivas oficiais aprovadas para o Engine v1.2.0+.

---

## 👑 1. A Elite Pipeline (Configuração Sênior / Máxima Mão-de-Obra)
**Público-Alvo:** Bases com Placas de Vídeo Dedicadas (GPUs Nvidia RTX 3060+ / Mac M-Series com 32GB+ RAM) ou Desktops com +32GB RAM DDR5 rápidos.

Neste cenário dominante, escalamos agentes para funções milimétricas com *ZERO sobreposição arquitetural*.

### Os Ocupantes das Cadeiras
*   🧠 **`qwen3:8b` (O Cérebro Operacional / Scribe Master):** Assistente principal ininterrupto. Graças ao nosso Guardrail de *No-Think Bypass*, ele faz "Role-Switch": extrai chaves operacionais e rotas num piscar de olhos (sem ativar o Modo Pensamento consumindo energia) e retoma toda a Hibridez de Pensamento na rodada 25 de Síntese Final de Documentos Markdown. Domina o *Agentic Tool Calling*.
*   ⚖️ **`phi4:14b` (O Engenheiro / Auditor Sênior):** Fica isolado na manga. Só desperta para matemática pesada, codificação densa em Python ou no papel estrito do nosso ***Sycophancy Breaker*** (Auditor do Diabo). Por ser de linhagem Microsoft/Sintética, cruza magistralmente os vieses gerados pelos modelos de linhagem AliBaba, estilhaçando alucinações.
*   📚 **`mistral-nemo:latest` (O Arquivista RAG):** Modelo especializado invocado *apenas* para devorar, mastigar e mesclar PDFs corporativos gigantes ou lidar com hiper-contextos.
*   👁️ **`gemma4:e4b` (Recepção Sensorial):** Seu agente leve de front-desk perfeitamente balanceado, substituindo os ultrapassados e pesados de gerações anteriores, servirá a multimodalidade com elegância estrita e alta qualidade de extração JSON.
*   ⛓️ **`bge-m3:latest` & `nomic-embed-text:latest`:** Os Motores Vetoriais. Transformam as planilhas financeiras e documentos em matemática vetorial de banco de dados (`AnythingLLM` / `Milvus`). Fundamentais.

---

## ⚖️ 2. Perfil Agilidade (O Paradoxo de Hardware Doméstico / 16GB-20GB)
**Hardware Simulado:** Notebooks APU Modernos (ex: Ryzen 7, Gráficos Integrados, sem placa de vídeo pura).

Se jogar múltiplos cérebros simultâneos na APU (ex: Qwen3 e Phi4 ativados no meio de um chat), sua memória desaba e sua UI congela triturada pela paginação de SSD.

### O Corte Vital
*   **[Proibido]** ❌ Modelos `12B` a `14B` (Ex: Phi-4, Gemma3:12b). Devem ser banidos do HD para não asfixiarem a fluidez e as camadas gráficas do Cíbrido OS.

### A Configuração Resiliente (Tier 2 Matrix)
*   **Operacional Absoluto:** `qwen3:8b`. Cairemos apenas no colo desse modelo para o arco inteiro do dia a dia (pensar, extrair JSON e orquestrar ferramentas).
*   **A "Portaria/Recepcionista" Cíbrida:** `gemma4:e4b`. Mantemos este excelente sensor como auxiliar leve de rotina pura.

---

## 🧩 3. Matriz de Guardrails Sub-5B e O Paradoxo do Gatekeeper (Reserva)

O Sovereign Pair V1.2 implementou um motor contínuo para barrar as catástrofes lógicas sintáticas (O Looping Infinito da Nanny de Jason).

### A Defesa: O "Agentic Fallback" Dinâmico
Quando um modelo de porta de entrada (como o `gemma4:e4b`) surta repentinamente soltando um parágrafo textual ao invés do protocolo em Chaves JSON `{...}` necessário pelo *Worker Graph*, a *Thought Nanny* intercepta até a segunda ocorrência. Se persistir, **o Fallback Escalator expulsa o agente travado do loop e pesquisa dinamicamente por qualquer cérebro substituto de porte equivalente (`is_agent = 1`, tamanho `< 5B`) na Matrix do SQLite, reassumindo sem pausar a interface.**

### ⚠️ A Regra do Reserva Estrutural (Nunca apague os pequeninos completamente!)
A tentação da "Régua Limpa" fará você querer desinstalar *todos* os modelos de 3 e 4 bilhões obsoletos do Ollama (como Llama 3.2, Hermes 3 e Phi-4 Mini) para focar apenas no `Gemma4:e4b`.
Se fizer isso, e deixar apenas 1 entidade na classe Sub-5B, **o Fallback não terá ninguém para chamar** caso ocorra um dia ruim gerencial no Gatekeeper.

*   **Recomendação Cíbrida Restrita:** Apesar da limpeza, instale e conceda alvará de estadia permanente no disco ao **`llama3.2:3b`** ou **`nous-hermes3:3b`**!
*   Ele agirá invisível como o colete salva-vidas algorítmico perfeito caso os cérebros oficiais da porta do Sistema (Gemma 4) resvalem numa pedra JSON.

---

## 🌟 4. A Falsa Ilusão: DeepSeek R1 (7B) vs. O Ecosistema Atualizado

### O Expurgar do Destilado Antigo
O modelo outrora cultuado e indispensável `deepseek-r1:7b` converteu-se em entulho redundante se você possuir as IAs da Alibaba. 
Por que? A arquitetura de base utilizada na destilação local de 7B da DeepSeek **é inteiramente oriunda do antigo Qwen 2.5 de 7B**.
Como nossa arquitetura agora rotaciona soberanamente o **`qwen3:8b`**, que já embute em sua genética as camadas híbridas de MODO PENSAMENTO de maneira nativa, superior e nativamente fluente sem os solavancos passados, engatar as peças desmembramentais de um hardware R1/7B custará lentidão severa.

Ao operar arquiteturas Sovereign, opte sempre pelas chaves originais ou pelas arquiteturas R1 exclusivas se (e somente se) contar com suporte à rodagem nativa da infraestrutura fechada na nuvem.

*Comando final base do Workspace V1.2.0 (Resistência Ativa):*
> `ollama run qwen3:8b`
