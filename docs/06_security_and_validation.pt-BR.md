# Engenharia de Segurança e Auditoria Dinâmica (SecOps)

A implantação técnica provê abordagens de DevSecOps contínuas projetadas para prevenir vazamentos de chaves estruturais, além de atenuar impactos derivados da interação de dados nativos na camada de roteamento dos módulos de Large Language Models. A infraestrutura adota a conformidade Zero-Trust em todas as avaliações de pipelines do repositório.

## 1. Analisador de Entradas e Gateway de Segurança (The Sentinel Input Validation)

A injeção indevida de texto malicioso no sistema através dos arquivos locais documentados (.md, .txt) resulta ocasionalmente no desvio das rotinas de extração, acarretando as chamadas *Prompt Injections*. Essa subversão manipula o índice vetorial com o intuito de escapar o framework do agente e forçar alucinações nas respostas.

### 1.1 Filtragem Proativa de Risco Lógico
Para neutralizar ameaças antes da inferência na camada RAG, existe um analisador sintático (arquitetura referenciada globalmente na classe *The Sentinel*).
Esta classe valida os metadados brutos originários do `SQLite Vectors`, identificando formatações sintáticas suspeitas assim que os dados são chamados antes de sua alocação no payload para o LLM. 

Ao encontrar padrões vulneráveis, ela bloqueia de forma silciosa a requisição. Essa resiliência assegura retornos íntegros no fluxo assíncrono perante as integrações do sistema HTTP principal ou Web UI PWA, evitando paralisação.

> [!NOTE] 
> ▫️ **Validador de Tráfego Implementado:** Código localizado na raiz do handler em `/src/core/the_sentinel.py`

### 1.2 Auditoria Histórica de Dependência Confidencial
Históricos de revisões retêm vulnerabilidades potenciais pelo upload não proposital de dados acoplados *(Hardcoded Credentials em logs de commits velhos)*. Visando reforçar a base do código, foi empregado em fases passadas a ferramenta nativa *git-filter-repo*. 
Esse procedimento executou a reescrita da árvore nativa do repositório, removendo referências esquecidas em metadados de branches para inviabilizar exploração histórica do indexador Git.

---

## 2. CI/CD Pipeline e Validação Restritiva 

Os *workflows* aplicam barreiras rigorosas as ramificações no ambiente. O sistema engatilha validações contínuas bloqueando deploys (`main` API e Front) por quebras técnicas e *warnings* críticos.

### 2.1 Inspeções SAST (Static Application Security Testing)
Voltando-se para a predição de códigos vulneráveis, instanciou-se o scanner estático Open-Source Semgrep focando nas sub-rotinas da API RAG Python:
- **Verificação Estática:** Escaneia falhas abertas relacionadas ao uso de `subprocess.run()`, JWT Token Exposures, arquivos locais transitivos abertos, e avalia a correta formatação dos handlers nativos no FastAPI para impossibilitar vetores Remote Code Execution (RCE).
- **Hard-Blocking no Deployment:** Identificando detecções via *Findings Alert*, as aprovações no GitHub Actions são encerradas devolvendo exceção na etapa de pull-request, demandando hotfix corretivo. **[Localização da Ação: `.github/workflows/sast_semgrep.yml`]**

### 2.2 Dependências O.S Mockadas nos Testes Integrativos
Serviços emulados com Python (via *Mock*) garantem testabilidade em pipelines sem sobrecarregar ou intervir nas instâncias da engine de ML local (Ollama LLM Run Time Process) durantes os testes de *Software Quality Assurance* rodados no `pytest`.
- **Cobertura via Mock:** Impõe falhas induzidas como Timeouts HTTP ou exceções intencionais da integração do Axios visando depurar o Fallback da Arquitetura Rest API. Avalia estritamente a durabilidade nativa frente a estresse em ambientes de simulação (Simuladores Unitários). **[Base contida em: `tests/regression/test_ollama_mocks.py`]**

### 2.3 Execuções UI Automations PWA Rendering
A infraestrutura inclui orquestradores de testes Headless da interface de usuário gerida em Vue.js utilizando o Playwright Framework.
- **Teste de Renderização Estrutural Dom:** Avalia limitações e renderizações carregando listas longas ou grafos gerados. O Playwright realiza validações dinâmicas analisando o tempo de framerate no Layout, apontando *Memory Leaks* com antecedência em caso de travamentos ocasionais criados na reatividade dos botões do Sensus Vault.
**[Casos Mapeados na Automação: `tests/e2e/vault_stress_test.spec.ts`]**

> [!NOTE] 
> O executor Bash local (`./run_regression.sh`) automatiza as sub-rotinas do `pytest` combinadas as avaliações no linter formatador `ruff`, garantindo os padrões controlados e checagem semântica rigorosa antes do envio ao versionador do código corporativo originário.
