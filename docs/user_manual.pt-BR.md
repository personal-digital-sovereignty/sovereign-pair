# Sovereign Pair - Manual do Usuário e Operações Frontend

**Versão da Interface:** 3.3.0
**Acesso Padrão (Local):** `https://localhost`
**Acesso Cloud (Tailscale):** `https://sovereign-rag-cloud.[SUA_TAILNET].ts.net`

Este documento é estruturado para Analistas, Engenheiros e Usuários Finais do Sovereign Pair RAG, detalhando a exploração, gestão de sessão e operação na Interface Web (PWA) de alto desempenho acionada por `Vue3`.

---

## 1. Topologia da Interface Web

A interface Sovereign Pair foi arquitetada sob os princípios de foco extremo e densidade de informação limpa (*Dark/Light Mode* nativo). O layout divide-se em componentes espaciais estritos:

### 1.1 Barra de Atividades (Activity Bar)
Localizada na extremidade esquerda da tela (Colapsável/Invisível em resoluções menores). Serve como leme de navegação principal entre módulos isolados do sistema.
- **Ícone Chat:** Retorna à Central de Sessões e Diálogos Cíbridos.
- **Ícone Vault (Sensus):** Expande o explorador de Sistema de Arquivos em Tempo Real.
- **Ícone Settings:** Abre os painéis de customização (Temperatura de LLM, Troca de Modelos, Tokens).

### 1.2 Painel de Sessões (Session List)
Vizinho à Activity Bar. Exibe o registro persistente de todos os diálogos estabelecidos com o Back-End Postgres. As sessões são arquivadas cronologicamente. 
- Engaja a mecânica de roteamento silencioso para preservar o contexto local sem trafegar *overheads* desnecessários.

---

## 2. Acesso à Inteligência (Módulo de Chat)

O módulo de Chat é a via de Injeção Primária de *Prompts*.
A comunicação flui via *Server-Sent Events (SSE)*, proporcionando emissão predatória de tokens sem *timeouts* em respostas analíticas densas.

### 2.1 Uso de Metadados e Contextualização
Diferente de sistemas chat isolados, nossa engenharia implementa o conceito de RAG. Sempre que o usuário clica em um arquivo pelo Sensus Vault e preenche o Chat, o ID daquele documento passa a nortear o contexto.
- Quando a malha semântica for acionada, ela cruzará o seu prompt textualmente com as informações estritas vetorizadas na base correspondente ao contexto aberto.

### 2.2 Seletores de Modelo e Temperatura
Nos Painéis Superiores (Dropdowns Ocultos), o usuário pode alternar a carga cognitiva instantaneamente:
- **Modelo:** Alternância entre endpoints Ollama Locais (`llama3.2`) ou chamadas corporativas na API da OpenAI, sem perda do fio conversacional da sessão.
- **Temperatura:** Deslizante dinâmico. Altere para `0.0` em extração seca de código, ou eleve para `0.7` em análises arquiteturais que exijam abstração.

---

## 3. Gestão de Arquivos (Sensus Vault Director)

O Sovereign Pair transcende aplicações Web Tradicionais ao dispor de um Gestor de Arquivos Sistêmico injetado diretamente na Interface via SSR.

### 3.1 Operações de CRUD de Pastas
O `Vault` exibe a sua árvore corporativa de documentos espelhando o disco do Host Servidor lógico isolado em `data/vault`.
1. **Navegação Recursiva:** Diretórios são expandidos linearmente, respeitando ordens alfabéticas e alocações lógicas.
2. **Criação Rápida:** Ícones de "Nova Pasta" e "Novo Arquivo" no topo da árvore materializam instâncias diretamente no disco via despachos da API.
3. **Restrições de Segurança (Path Traversal):** Qualquer tentativa de criar arquivos injetando strings relativas (`../`) será interceptada pela barreira Zero-Trust do `sovereign-api`, prevenindo escalonamento de privilégios.

### 3.2 Visualizador Markdown Incorporado
Arquivos `.md` selecionados no Sensus Vault são hidratados em um renderizador central robusto. Esse painel compilará as marcações lógicas, blocos de código com *Syntax Highlighting*, e formatação fluente para leitura imersiva lado a lado com a aba do Chat Ativo.

---

## 4. O Sistema de Injeção de Conhecimento (Ingestão)

### 4.1 Pipeline Híbrido Incremental
Toda atualização de arquivos em lote precisa ser processada e registrada na mente Vetorial do RAG (ChromaDB) para que a IA possa raciocinar sobre eles.
- O Processo é executado nativamente pela CLI do Host (via `python src/ingest.py`). 
- **O Modo Incremental** rastreia os Hashes SHA256 de todo o cofre de documentos do Host. Ele identifica inteligentemente quais parágrafos sofreram modificações e vetoriza estritamente os trechos delta, injetando agilidade brutal (economia computacional > 90%).

### 4.2 Arquivos Suportados nativamente:
- Textos Puros e Estruturados (`.md`, `.txt`, `.csv`, `.json`).
- Paginação Densa (`.pdf`, `.docx`, `.html`).
O Ingestador aplica regras corporativas de particionamento (Chunking) onde sentenças longas são mantidas íntegras nas dobras matemáticas (Overlap) para que respostas sistêmicas nunca retornem cortadas sem contexto aos usuários do Frontend.

---

## 5. Orientações de Identidade Cíbrida (Zero-Trust Mobile)
Sempre que acessar o sistema corporativo fora das premissas via Celular ou Redes Públicas, assegure-se que a chave Métrica HTTPS reflete estritamente o Domínio Tailscale autenticado do nó correspondente, e a aba lateral do App relata `Status: Conectado e Blindado` provado via tokens JWT emitidos no Edge.

- O Aplicativo Web implementará estratégias agressivas no Service Worker para manter os artefatos funcionais inclusive durante transições de áreas sem cobertura (3G/4G). A reconexão empilhará silenciosamente a telemetria pendente. 

---
**Glossário Técnico Referenciado:** Vide `docs/glossary.pt-BR.md`.
