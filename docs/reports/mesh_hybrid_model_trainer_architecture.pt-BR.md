# Relatório Arquitetural: Model Trainer de Rede Mesh e Destilação de Conhecimento Híbrida

**Data:** Março de 2026
**Assunto:** Sovereign Pair - Treinamento Local Distribuído e Inferência de Mesh
**Classificação:** Documentação de Arquitetura Pública

---

## 1. Sumário Executivo
A arquitetura do **Sovereign Pair** foi desenhada fundamentalmente para solucionar as restrições físicas da execução local de IA (VRAM limitada e Baixo Computador em dispositivos de usuários finais). Para alcançar a verdadeira "Soberania Digital" sem sacrificar inteligência, a aplicação emprega um **Model Trainer Híbrido em Mesh**.

Esta arquitetura permite que um agente local leve (ex: Laptop Mac/Windows rodando a Interface de Usuário) orquestre operações complexas — como Destilação de Conhecimento e Fine-Tuning LoRA — despachando transparentemente as cargas pesadas para nós mais potentes dentro da rede Mesh privada do usuário (ex: um servidor robusto Oracle Cloud ou uma estação de trabalho local com GPUs dedicadas).

## 2. Mesh Global de Nós (O Cluster Soberano)
O Sovereign Core (`api_settings.rs` e `api_mesh.rs`) mantém um índice ativo de todos os nós Ollama disponíveis para o usuário. Cada nó registra sua `URI` única, perfil computacional físico e modelos instalados (`/api/tags`).

Quando o usuário acessa o painel do **Model Trainer** em seu dispositivo local, a engine consulta de forma nativa o **Nó de Trabalho (Worker Node)** ativo.
- Se o Nó Ativo configurado for `http://10.0.0.5:11434` (Um servidor remoto na Oracle Cloud), o Model Trainer mira dinamicamente esta instância remota.
- A Stream de telemetria visual (**Unsloth Monitor**) da interface recebe os Server-Sent Events (SSE) envelopados e redirecionados diretamente do status de sincronização de tensores do servidor remoto (`/api/create`), renderizando as métricas em tempo real localmente, como se o hardware estivesse fisicamente dentro do laptop do usuário.

## 3. Destilação de Conhecimento: Do 70B/GPT-4 ao 3B Local
A Destilação de Conhecimento (Knowledge Distillation) dentro do Sovereign Pair não é apenas simbólica; ela é construída sobre uma pipeline orquestrada de extração de dados e subsequente injeção de modelo.

### Cenários de Destilação Multicamadas

**Cenário A: Professor Terceirizado (GPT-4o) ➡️ Aluno Local (Llama 3.2 3B)**
O usuário pode alavancar inteligência proprietária para forjar soberania localizada de código aberto.
1. O usuário especifica **Professor:** `gpt-4o` e **Aluno:** `llama3.2:3b`.
2. O Rust Sovereign Core consulta de forma segura a API da OpenAI (utilizando as chaves de API auto-criptografadas por KMS no Vault do usuário).
3. A engine extrai respostas de raciocínio lógico estrutural, formatando um "Gold Dataset" de alta qualidade que é salvo diretamente no banco de memória P2P local (`sovereign_memory.db`).
4. Esse dataset é então consumido via injetores para alimentar a instância do Ollama local em processos de ajuste de parâmetros, solidificando o conhecimento externo offline de forma perpétua.

**Cenário B: Professor Soberano Remoto (Llama 3 70B) ➡️ Aluno Local (Qwen 1.5B)**
Para ambientes Zero-Trust, APIs externas são completamente contornadas.
1. Um modelo Llama 3 70B superpotente roda em um Nó Mesh acoplado (ex: Servidor no trabalho ou Nuvem Dedicada).
2. O Model Trainer orquestra requisições de geração pelo túnel VPN/Mesh, extraindo deduções lógicas do professor 70B offline.
3. Os datasets derivados são trazidos pela rede até o nó do dispositivo local e utilizados para treinar o modelo menor de 1.5B ou 3B (o aluno) localmente.
4. O usuário conquista altíssima capacidade de raciocínio offline e hiper-especializada em seu laptop sem jamais depender da internet, e o servidor na nuvem pode ser desligado após ceder seus talentos.

## 4. Design de Engenharia Resiliente
Para garantir total estabilidade durante horas de operações pesadas:
- **Pool de Tarefas Assíncronas**: O ambiente assíncrono do Rust (`tokio::spawn`) dispara os Requests HTTP de longo termo para as APIs externas/Ollama sem bloquear a thread principal, mantendo a responsividade Cíbrida da interface de usuário em 60 frames.
- **Canais de Transmissão (Broadcast)**: O canal robusto do Rust `tokio::sync::broadcast` garante que o stream de telemetria da interface viaje limpo sobrevivendo à latência imposta pela rede externa durante processos de fine-tuning.
- **Abstração Soberana**: O módulo frontend (`SettingsModal.svelte`) lê localmente ou remotamente sem distinção lógica. Para o sistema, não há diferença visual/de uso entre lidar com a GPU do computador ou o datacenter gigantesco a duas cidades de distância.

## 5. Conclusão da Arquitetura Cíbrida
O Model Trainer do Sovereign Pair é muito mais que uma tela simplória de treinamento. Ele age como um verdadeiro Sistema Operacional Distribuído em Rede. Ele prevê um futuro próximo onde dispositivos hiper-leves lidam apenas com orquestração pesada e renderização de dados, enquanto toda queima de silício pesado é enviada inteligentemente para os porões onde as GPUs habitam.
