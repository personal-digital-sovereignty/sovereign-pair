# Engenharia de Segurança e Auditoria Dinâmica (SecOps)

A implantação técnica provê abordagens de DevSecOps contínuas projetadas para prevenir vazamentos de chaves estruturais, além de atenuar impactos derivados da interação de dados nativos na camada de roteamento dos módulos de Large Language Models. A infraestrutura adota a conformidade Zero-Trust em todas as avaliações de pipelines do repositório.

## 1. Analisador de Entradas e Gateway de Segurança (The Sentinel Input Validation)

A injeção indevida de texto malicioso no sistema através dos arquivos locais documentados (.md, .txt) resulta ocasionalmente no desvio das rotinas de extração, acarretando as chamadas *Prompt Injections*. Essa subversão manipula o índice vetorial com o intuito de escapar o framework do agente e forçar alucinações nas respostas.

### 1.1 Filtragem Proativa de Risco Lógico
Para neutralizar ameaças antes da inferência na camada RAG, existe um analisador sintático (arquitetura referenciada globalmente na classe *The Sentinel*).
Esta classe valida os metadados brutos originários do `SQLite Vectors`, identificando formatações sintáticas suspeitas assim que os dados são chamados antes de sua alocação no payload para o LLM. 

Ao encontrar padrões vulneráveis, ela bloqueia de forma silciosa a requisição. Essa resiliência assegura retornos íntegros no fluxo assíncrono perante as integrações do sistema HTTP principal ou Web UI PWA, evitando paralisação.

> [!NOTE] 
> ▫️ **Validador de Tráfego Implementado:** Código compilado localizado na sub-rotina RAG em `/src-rust/core/the_sentinel.rs`

### 1.2 Auditoria Histórica de Dependência Confidencial
Históricos de revisões retêm vulnerabilidades potenciais pelo upload não proposital de dados acoplados *(Hardcoded Credentials em logs de commits velhos)*. Visando reforçar a base do código, foi empregado em fases passadas a ferramenta nativa *git-filter-repo*. 
Esse procedimento executou a reescrita da árvore nativa do repositório, removendo referências esquecidas em metadados de branches para inviabilizar exploração histórica do indexador Git.

---

## 2. CI/CD Pipeline e Validação Restritiva 

Os *workflows* aplicam barreiras rigorosas as ramificações no ambiente. O sistema engatilha validações contínuas bloqueando deploys (`main` API e Front) por quebras técnicas e *warnings* críticos.

### 2.1 Inspeções SAST e Memory Safety (Segurança por Design Rust)
Voltando-se para a predição de códigos vulneráveis, instanciou-se nativamente o scanner analítico e o compilador padrão do ambiente Rust (Cargo Clippy e Cargo Audit) focando nas sub-rotinas da API Axum:
- **Verificação Estrita de Memória:** A alocação local impede corrupções de ponteiros via compilador restritível nativo; o formato inviabiliza vulnerabilidades abertas de injeção direta de subprocessos sem validação rigorosa via Type Checking (RCE).
- **Hard-Blocking no Deployment:** Identificando detecções via *Borrow Checker* na etapa Lint e Test, as aprovações no GitHub Actions são encerradas devolvendo exceção na esteira devolvida do pull-request. **[Localização da Ação: `.github/workflows/rust_clippy.yml`]**

### 2.2 Dependências O.S Mockadas nos Testes Integrativos
Serviços emulados nativamente (*Traits & Mock Objects em Rust*) garantem testabilidade em pipelines sem sobrecarregar instâncias da engine de ML local (Ollama LLM Run Time Process) durantes os testes de *Software Quality Assurance* iterados via `Cargo Test`.
- **Cobertura via Mock:** Impõe falhas induzidas como Timeouts HTTP com bibliotecas de conectividade Reqwest visando depurar o Fallback da Arquitetura Rest API. Avalia estritamente a durabilidade nativa frente a estresse em ambientes de simulação (Simuladores Unitários). **[Base contida via testes declarados em sub-módulos unitários nas sources `src-rust`]**

### 2.3 Execuções UI Automations PWA Rendering
A infraestrutura inclui orquestradores de testes Headless da interface de usuário gerida em Svelte utilizando o Playwright Framework.
- **Teste de Renderização Estrutural Dom:** Avalia limitações e renderizações carregando listas longas ou grafos gerados. O Playwright realiza validações dinâmicas analisando o tempo de framerate no Layout, apontando *Memory Leaks* com antecedência em caso de travamentos ocasionais criados na reatividade dos botões do Sensus Vault.
**[Casos Mapeados na Automação: `tests/e2e/vault_stress_test.spec.ts`]**

> [!NOTE] 
> O executor Bash local (`./run_regression.sh`) automatiza as sub-rotinas do `cargo test` combinadas as avaliações do linter formatador `cargo fmt`, garantindo os padrões controlados e checagem de Memory Safety rigorosa antes do envio ao master branch.
