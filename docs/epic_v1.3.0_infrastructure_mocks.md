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
