# Épico (v1.3.0): Integração Absoluta de Infraestrutura e Redes Cíbridas

**Status:** Desenhado / Arquitetura Definida para v1.3.0
**Módulo Raiz:** `Sovereign Settings` (Svelte/Rust)
**Objetivo Principal:** Concluir a materialização dos nós de conectividade externa e cold-storage, transformando botões cenográficos e Mocks visuais em túneis TCP e FTS5 autênticos de recuperação física.

---

## 1. Mapeamento de Fricção Atual (Real vs Mock) nas Configurações

### ✅ O que é REAL hoje (v1.2.0)
1. **Sovereign Identity:** A extração do arquivo encriptado `.cybrid` ocorre com fidelidade de base 64 e o JSON salva preferências da porta padrão de inicialização e hiperparâmetros na tabela `global_settings`.
2. **Sovereign Core (AI Engine):** A Matriz de Operações (`modelMatrix`) dita as regras do sistema de forma nativa e reativa a instâncias Ollama caídas ou excluídas (O Watcher Sensus Sync).
3. **Sovereign SecOps API Vault:** Uma verdadeira proteção assimétrica! As chaves API das nuvens corporativas são devidamente injetadas, encapsuladas no backend em formato opaco, lidas e roteadas pelo `culture_matrix.py` aos endpoints verdadeiros.

### 🎭 O que é MOCK cenográfico (Tech Debt)
1. **Sovereign Mesh P2P (Formulário Cego):** Apesar do Svelte ler dinamicamente e corretamente as chaves `ollama_clusters` no Sensus SQLite e listar de forma autêntica... O Botão *"Establish New P2P Tunnel"* não possui *Binding* Svelte (`onclick`). É impossível adicionar uma placa de vídeo da sua rede pelo Hub atual. Se quiser adicionar um nó, hoje é preciso injetar um JSON direto na mão pro SQLite (via DBeaver).
2. **Cloud Sandboxing (Cascão HTML):** As entradas de *OCI Public IP* e *OCI Secret Key Path* no cartão Svelte são puramente marcações HTML (`<input type="text">` estáticos). Não possuem as diretivas sagradas `bind:value` e muito menos um botão de Postagem. Nenhuma instância da Oracle Cloud está sendo amarrada à sua infraestrutura pela Interface no momento atual.
3. **Cold Storage (O Repositório Desconectado):** O painel é maravilhosamente complexo. Ele exibe chaves de bases reais Offline (`Wikipedia ZIM`, `RedPajama 1.2 TB`), e ele de fato *salva* as opções de checkbox marcadas no SQLite com precisão. **Porém**: a Engine Rust RAG (em `core/src/api_trainer.rs`) checa que a flag ligou, e propositalmente barra a indexação dizendo: `// Currently simulating the Cold Storage extraction yield for safety.` O motor não despacha FTS5 no seu Disco Rígido por enquanto.

---

## 2. A Missão do Épico v1.3.0 (Backlog Architecture)

Para que a rede híbrida seja descentralizadamente completa no próximo Release 1.3.0, focaremos na engenharia de dados externa e roteamento.

### Fase 1: Tunneling Dinâmico na Mesh P2P
Tornar a aba P2P livre de scripts manuais.
1. Desenvolver Modal Visual do Svelte em estado aberto para *"Establish New P2P Tunnel"*.
2. Capturar variáveis locais Svelte 5 `$state`: `IP Target`, `Port`, `Security Mesh Key`.
3. Injetar sub-rotina SSH reverso ou Wireguard via Rust `std::process` no endpoint Axum, em vez de apenas registrar um link cru no Banco, testando um "Ping Neural" de Handshake para validar se o Ollama ou LLAMA.CPP remoto está vivo e capaz de injetar Tokens na rede Sovereign.

### Fase 2: OCI Sandboxing (Cloud Controller)
Remover caixas vazias HTML.
1. Implementar modelo de dados (`OciCredentials`) na tabela de Segurança do SQLite e nas propriedades reativas do Svelte.
2. O Axum assumirá uma rota nova `POST /v1/settings/cloud_target`, recebendo o `.pem` Key Path validado em disco. O motor de Rust fará fallback instantâneo `failover` mudando os requests de `localhost:11434` para o roteamento público tunelado da nuvem quando as requisições massivas esmagarem a memória unificada do PC Host local.

### Fase 3: Despertamento do "Cold Storage Logger"
Conectar as marcações de arquivos corporativos com parsers físicos.
1. Em vez do atual `simulate extraction`, a IA Rust precisará carregar dependências e bibliotecas externas. A implementação invocará o framework `kiwix-serve` (Caso bibliotecas ZIM Wikipedia/PubMed) rodando paralelizado (via Docker Engine SDK ou nativo). As conexões de banco de dados irão fazer Query sobre a base aberta descarregando respostas limpas em Markdown prontas pro `Agent Master` da nossa arquitetura inferir.
2. Monitoramento temporal para ignorar o *Cold Storage* caso a inferência peça resolução Ultra-Fast de Chat, mas obrigando que *Deep Research* raspe dados offline integralmente antes do tráfego para a Web-Aberta, reduzindo Hallucination.

---

## 3. Alerta de CI/CD e Esteiras (Svelte AST Mocks Cloaking)
**Nota de Engenharia (Adicionada na finalização da v1.2.0):**
Para evitar que componentes "fictícios" causassem ansiedade arquitetural em tela na versão 1.2.0, optamos por esconder (cloak) essas interfaces (*Cloud Sandboxing*, *Unsloth Monitor*, *Cold Storage*, etc.).

**Atenção para as Ferramentas de Análise Estática:** As esteiras do GitHub Actions / SAST / Vite Compilers **não** encontrarão comentários do tipo HTML padrão `<!-- -->` ao redor desses cartões HTML no código fonte. 

Em vez de comentários HTML, o ocultamento foi feito nativamente via Árvore Sintática do Svelte (AST) utilizando blocos lógicos inalcançáveis:
```svelte
{#if false} <!-- v1.3.0 MOCK HIDDEN -->
    <section class="mock-ui">...</section>
{/if}
```
Isso foi feito propositalmente pois comentários HTML tradicionais quebram a validação dos fechamentos das tags intrínsecas de lógica do próprio Svelte `{#if...} {/each}`, engolindo blocos e engatilhando erros do tipo `Unexpected block closing tag` e `element_invalid_closing_tag`. O uso de `{#if false}` garante que os nós de HTML continuem estritamente válidos perante o `svelte-check`, mantendo as referências CSS escopadas e a checagem de tipos (TypeScript) seguras, enquanto garante absoluta invisibilidade visual ao usuário. O Tech Debt está seguro em *hibernação de código*.

---

## 4. Requirement Gap: Escalonamento Dinâmico de Janela de Contexto (Token Limit)
**Desafio Computacional Identificado visando Cross-Hardware Support:**
Atualmente (v1.2.0), o Sovereign Pair roda confortavelmente alocando até `12.000 tokens` contínuos na janela de contexto de orquestração purista, presumindo instâncias abastadas com **32GB de RAM/VRAM** e alta tolerância térmica. 

Para a **v1.3.0**, o engine deve incorporar um Scanner Dinâmico (Daemon) de hardware durante a inicialização (ou via Heartbeat do `Hardware Telemetry`) para **calcular limites seguros de tokens (Context Window) baseados na totalidade de RAM livre da máquina-hospedeira**.
- Computadores de `8GB`: Limitação agressiva para `4096 tokens`.
- Computadores de `16GB`: Balanceamento em `8192 tokens`.
- Computadores de `24GB+`: Permissão de janelas brutas de `12.000` a `16.000 tokens`.

Esse teto deverá atuar não apenas como "Dica Visual", mas como trava mecânica no motor de Inferência e na limitação dos tensores injetados via Ollama, protegendo usuários com menos condições de sofrerem com OOM (Out-of-Memory) Kills e travamentos de sistema (Kernel Panic / Soft Lock).
