# Manutenção e Automação SecOps: CI/CD Pipelines

Este documento detalha o ecossistema de Integração Contínua (CI), Entrega Contínua (CD) e Segurança (DevSecOps) que compõem o repositório do Sovereign Pair orquestradas por fluxos no padrão GitHub Actions. 

O projeto adota uma esteira de nível corporativo (*FOSS Enterprise*), assegurando conformidade de código estritiviva originária de processos limpos onde nenhum payload seja autorizado na "Branch Mestre" (main) ou instâncias Oracle sem atravessar validações semânticas rigorosas, scans mitigativos de vulnerabilidade e estabilidade processual via testes.

---

## 🛡️ 1. Pipeline Primária de Segurança (`devsecops.yml`)
Atua compondo um filtro primário de segregaçao e validação estática de modificações submetidas no repositório com prioridade transacional antes dos processos paralelos do Docker Engine Code Integrations O.S Local Builds O.S Code Component Analysis Testing Node API Integration Definition Flow Models. Garante-se não haver desvios lógicos comprometendo propriedades restritivas do Soberano local O.S API Nodes O.S Mappings Setup Verification Code:
* **Escopo de Inicialização (Triggers):** A cada instrução Git Originária `push` e `pull_request` perante o ramo Mestre.
* **Componentes Limitadores:**
  * **Zizmor & Actionlint:** Responsável por auditoria formativa YML sob as *Actions*. Bloqueia ações *Unpinned* contendo transitoriedade de risco (Hashes variáveis mutáveis de repositórios não autorizados) evitando falhas sistêmicas por dependências inadivertidas.
  * **Gitleaks:** Realiza a rastreabilidade direta do controle de versões caçando artefatos identificados logísticos como UUIDs restritivos AWS, tokens do OCI Cloud Authentication RSA ou variáveis nativamente expostas em código vivo.
  * **Semgrep (Scanner Estático SAST):** Mecanização da Análise de Segurança em Código Fontes O.S Local. Validador processual avaliando códigos sintáticos API Python ou Vue impedindo inserções atreladas à Execuções Locativas Arbitrárias (*RCE*).
  * **Trivy (Composição Mapeamento):** Scanners avaliativos operacionais base para monitoração local do pacote gerencial de linguagens e ferramentas. Localiza exceções de origem (*CVE*) acopladas na ramificação Python Virtual O.S Base (`requirements.txt`).
  * **Ruff:** Verificador relacional base submetendo Python a definições semânticas padronizadas base (PEP-8) evitando loops processuais falhos restritos OS Base Application Format Rules OS Flow Variables Output Component Data Models.

## 🚀 2. Backend Compilacional Cíclico (`docker-api.yml`)
Avaliação e orquestração de entregas sob escopos Back-End nativas OS.
* **Gatilho de Inicialização:** Acionamentos exclusivos restritos sobre modificações em arquivos no diretório `src/api/`, seu respectivo Dockerfile API `Dockerfile.api` e metadados dependência baseados no arquivo Python nativo.
* **Integridade Operacional Base:**
  * **PyTest & PyTest-Mock:** Simula a base paralela originária validativa por Mocks (Sem demandar interface OCI OLLAMA O.S Física Real Component Limits Base Tests Output Framework Integration View Logic Implementation Nodes Flow Output Execution Validations Tests Simulations Automation Validations Architecture API Simulations Data Validations Logic). Garante-se validação de roteadores restritos Python API (Nurse Request Route Code Output Process Simulator).
  * **Ruff Linter:** Validação nativa limpa sintática OS Logic Data Output Mappings Model Applications Automation Rules Output Model Data Base Tests.
  * **Registry Provision:** Compilação das imagens docker final via `ghcr.io` restritas na nuvem após validações aprovar.

## 🎨 3. Arquitetura Frontend Automations (`docker-web.yml`)
Empacota dependências base interface (Sub-Árvore Web-UI VUE/VITE Systems Output Framework Render OS Logic Mappings Implementation Automation API Design View Design Layout UI Validations Code Process Testing Definition Logic Integrations API Validation OS Applications Execution Data Logic System Automation Tests Visual OS Components).
* **Gatilhos Operacionais:** Restrição processada via monitoração do Node PWA Server O.S Components `web-ui/` Client Application Component Executions Output.
* **Validação Transacional:**
  * Avaliação NPM instaladora nativa Node Lock File Version.
  * TypeScript Checking Node Vue-tsc Runtime Compile Verification Simulation Visual Mappings Flow.
  * Otimização Docker Output Final O.S Setup Application Systems Verification.

## ☁️ 4. Instanciação IaaS Oracle Cloud (`deploy-oci.yml`)
Provisionamentos via *Infrastructure as Code*.
* **Gatilho de Acionamento:** Procedimentos manuais (Workflow Dispatch na aba Actions da UI) ou alterações no subdiretório `infra/terraform/`.
