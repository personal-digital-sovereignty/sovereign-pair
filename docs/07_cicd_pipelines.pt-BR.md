# Sovereign Pair - CI/CD & DevSecOps Pipelines

Este documento detalha o ecossistema de Integração Contínua (CI), Entrega Contínua (CD) e Segurança (DevSecOps) que compõem o repositório do Sovereign Pair no GitHub Actions. 

O projeto adota uma esteira **FOSS Enterprise**, garantindo que nenhum código suba para produção (ou para os nós da Oracle) sem passar por um rigoroso crivo de formatação, vulnerabilidades e estabilidade.

---

## 🛡️ 1. FOSS Enterprise DevSecOps (`devsecops.yml`)
Esta é a pipeline de segurança primária (Central Gateway). Ela atua interceptando as modificações lançadas no repositório antes ou durante processos de build para garantir resiliência e a não-exposição de dados da Soberania do usuário.
* **Gatilho (Triggers):** A cada `push` e `pull_request` em qualquer lugar do repositório.
* **Etapas de Validação:**
  * **Zizmor & Actionlint:** Audita todos os aquivos `.yml` do GitHub Actions em busca de *Cache Poisoning*, *Shell Injection* ou *Unpinned Actions* (ações com hashes vulneráveis).
  * **Gitleaks:** Escaneia ativamente os commits empurrados bloqueando caso detecte vazamento de chaves AWS, JWT, GitHub Tokens ou chaves RSA privadas.
  * **Semgrep (SAST):** Análise Estática de Segurança do Código (*Static Application Security Testing*). Valida código Python (API) e TypeScript (Vue) caçando injeções SQL, XSS, e brechas de injeção de parâmetros nas chamadas do LLM.
  * **Trivy (SCA):** Rastreia vulnerabilidades em bibliotecas de terceiros (*Software Composition Analysis*), por exemplo: exploits expostos dentro do `requirements.txt` do Python.
  * **Ruff:** O guardião rígido do Clean Code backend. Enforça boas práticas da `PEP-8` e impede declarações mal-formadas (como strings-F quebradas e variáveis ociosas).

## 🚀 2. Backend API CI/CD (`docker-api.yml`)
A malha de compilação da alma do sistema (FastAPI).
* **Gatilho:** Modificações nos diretórios `src/api/`, `Dockerfile.api` e `requirements.txt`.
* **Etapas de Validação:**
  * **PyTest & PyTest-Mock:** Roda as dezenas de testes assíncronos que validam o *The Nurse*, o RAG de ingestão paralela e parsing dos YAML frontmatter.
  * **Ruff Linter:** Validação final do código Python do core do ecossistema.
  * **Build & Push ghcr.io:** Se os testes derem verde, constrói a imagem leve do *sovereign-pair-api* e envia (push) para o GitHub Container Registry hospedado na nuvem.

## 🎨 3. Web UI CI/CD (`docker-web.yml`)
Malha de distribuição do Frontend (Vue 3 + Vite).
* **Gatilho:** Modificações dentro da pasta sub-árvore `web-ui/` ou no seu respectivo `Dockerfile.web`.
* **Etapas de Validação:**
  * **Node/npm CI:** Valida árvore de dependências exatas criadas em lockfile e compila os sub-módulos do Vue.
  * **TypeScript Checkout:** Faz a checagem rigorosa de tipagem estática do Vite (`vue-tsc`).
  * **Build & Push ghcr.io:** Se compilado com sucesso e não houver vazamentos de payload no frontend, joga a versão otimizada da Interface na imagem Ngnix final no repositório GitHub.

## ☁️ 4. Deploy Sovereign Cibrid Cloud (`deploy-oci.yml`)
O Coração da transição para a Oracle Cloud (Automação de Infraestrutura).
* **Gatilho:** Manual (via botão *Workflow Dispatch* -> `apply` / `destroy`) ou edições na pasta `infra/terraform/`.
* **Etapas de Ação:**
  * **OpenTofu Init / Validate:** Abre o motor Open Source reativo para aplicar infra como código, lendo as receitas das chaves do Oracle em Segredo (GitHub Secrets).
  * **Orquestração da Nuvem:** Dispara via API as regras configurando uma arquitetura *Zero-Trust Network* (Tailscale Mesh), requisitando a instância A1 e injetando instaleção *cloud-init* do Docker e do RAG instantaneamente. Executa o *Apply* ou, sob demanda, o *Destroy* da máquina toda.

## 📦 5. Sensus Vault Plugin Release (`release-sensusvault.yml`)
Cria os pacotes (artefatos) auto-instaláveis para a poderosa integração com o Sensus Vault PKM.
* **Gatilho:** A cada subida de tags de versão formatadas como `sensusvault-v*`.
* **Etapas de Ação:**
  * Usa repositórios NPM do NodeJS purificados.
  * Constrói e condensa (minify) o `main.js`, `styles.css` e o `manifest.json`.
  * Compacta em formato *ZIP* e dispara ativamente um *Release* contendo os binários limpos lá na home page de Releases do GitHub para download do usuário final.

## 🖥️ 6. CLI Release (`release-cli.yml`)
Pipeline de publicação automática das engrenagens CLI (Single-Binaries) se aplicável.
* **Gatilho:** Manualmente engatilhado no painel ou por versão de cli releases.
* **Ação:** Cria executáveis purificados para permitir o uso retroativo da ferramenta local sem dependência contínua dos containers em ambientes de Edge local isolados.
