# O Manifesto Soberano (Sovereign Pair v0.9.9)

O **Sovereign Pair** evoluiu de um assistente convencional para um **Ecossistema Local-First**. O projeto prioriza a execução de processos na máquina do usuário, reduzindo a dependência de infraestruturas em nuvem de terceiros e garantindo que dados corporativos ou pessoais não precisem ser enviados para fora da sua rede.

Este documento consolida os 5 pilares arquiteturais da versão 0.9.9+, refletindo a transição da antiga arquitetura baseada em Python e LlamaIndex para a nova estrutura unificada.

---

## Pilar I: Filosofia Soberana e Topologia Híbrida

A arquitetura do Sovereing Pair foi pensada para manter o controle total sobre os dados.

1. **Privacidade por Padrão:** O processamento dos modelos de linguagem (LLMs) ocorre primariamente em ambientes isolados, seja na máquina física do usuário ou protegido sob uma VPN privada (WireGuard/Tailscale).
2. **Topologia Híbrida (Daemon / Cliente):** O backend principal em **Rust (`sovereign-core`)** roda em segundo plano (Headless) acoplado ao Banco de Dados. A Interface de Usuário Desktop (**Tauri / Svelte v5**) atua como um cliente leve, comunicando-se de forma assíncrona pela porta `38001`. Essa divisão evita problemas de permissões de sistema e melhora a experiência e estabilidade do usuário no Linux, macOS e Windows.
3. **Rede Isolada (Tailscale 100.x.x.x):** Para proteger o processamento delegado a nós remotos (como uma instância gratuita ARM64 na Oracle Cloud), portas de serviço (como 11434 ou 8000) nunca são expostas na internet pública. Toda a comunicação ocorre de forma invisível nos IPs restritos do túnel Tailscale, prevenindo ataques externos tradicionais.

---

## Pilar II: O Motor Cíbrido (Rust e Python)

A arquitetura moderna foi reescrita para garantir performance e segurança de memória, minimizando os gargalos de antigas bibliotecas.

- **Gateway Universal (Axum/Tokio):** O núcleo da rede processa simultaneamente requisições REST e Server-Sent Events (SSE) de maneira responsiva.
- **SQLite Vector Nativo:** O uso do `ChromaDB` foi descontinuado. Agora, todos os textos processados são armazenados nativamente no SQLite usando a extensão `sqlite-vec`. Isso garante isolamento entre usuários e facilidade de backup com um único arquivo de banco de dados (`sovereign_memory.db`).
- **Nós Multimodais Modulares (Python):** Para integração de visão computacional e transcrição de áudio sem complicar a compilação do Rust, criamos scripts independentes (ex: `faster-whisper`, `paddleocr`). O Rust atua como orquestrador, chamando esses binários locais apenas quando necessário. O resultado retorna em milissegundos e o processo Python é encerrado, liberando recursos e evitando uso contínuo de memória RAM/VRAM.
- **Reranker Local Otimizado:** Usando o `fastembed`, o sistema avalia resultados de busca usando métricas como similaridade de cosseno e BM25 em milissegundos. Assim, o LLM recebe apenas os trechos mais relevantes, evitando consumo desnecessário de contexto e reduzindo custos computacionais (Out of Memory).

---

## Pilar III: RAG Inteligente e Pesquisa Resiliente

As buscas passaram a ser ativas e otimizadas, indo além do simples "scraping" tradicional de páginas web.

- **Automação Auxiliar:** Agentes de verificação (como *The Coder* ou *The Nurse*) validam as informações recebidas dos modelos de linguagem menores antes que a resposta seja entregue na interface do usuário final, reduzindo o risco de alucinações.
- **Processamento de Textos:** Conteúdos longos são quebrados usando `unicode-segmentation` de forma equilibrada, mantendo as ligações semânticas vitais sem poluir a janela de contexto.
- **Resiliência contra Bloqueios:** Se uma pesquisa convencional falha por bloqueio de servidores (como retornos HTTP 403 do Cloudflare), o sistema busca a informação paralelamente em arquivos históricos públicos (como Wayback Machine, Arquivo.pt e Vefsafn). Isso garante a leitura de páginas indexadas diretamente da memória global confiável, contornando proteções comerciais contra robôs.

---

## Pilar IV: Interoperabilidade e Protocolo MCP

A integração do sistema não se limita apenas à sua própria interface web, expandindo-se para o dia a dia do desenvolvedor:

- **Protocolo MCP (Model Context Protocol):** Operando em modo de comunicação inter-processos segura (*Stdio IPC*), o motor pode atuar como servidor passivo para IDEs locais (VS Code, Cursor, Cline). Isso permite que seu editor de código pesquise informações vetorizadas do projeto direto do SQLite sem precisar de APIs na nuvem.
- **Proxy OpenCode Integrado:** Os desenvolvedores que utilizam linha de comando (CLI) podem redirecionar suas requisições tradicionais OpenAI para o proxy rodando na porta local (`http://127.0.0.1:38001/v1/opencode`). Dessa forma, a integração de código flui pelo modelo LLM local do usuário, mantendo a privacidade durante o desenvolvimento de software.

---

## Pilar V: Segurança, Automação e Ajuste Fino

A infraestrutura é mantida por pipelines automatizados no GitHub Actions para impedir a introdução de falhas de segurança durante a evolução do código.

- **Validação Contínua:** Deploys só são autorizados após passarem por verificações preventivas como o varredor de chaves `Gitleaks`, o analisador estático `cargo clippy`, e testes de interface no `Playwright`.
- **Treinamento Contínuo (Unsloth e LoRA):** O banco de dados SQLite exporta dados organizados das suas próprias conversas em formatos simples (`export_unsloth_dataset`). A partir daí, é possível aplicar ajustes finos na nuvem treinando um pequeno modelo base. O resultado (exportado em GGUF) será um modelo especializado no vocabulário e nas convenções da sua empresa, oferecendo resultados superiores em vez de usar modelos corporativos generalistas padrão.

*(Este manifesto atua como a única fonte de arquitetura consolidada a partir da versão 0.9.9, descontinuando documentos antigos da fase inicial de desenvolvimento.)*
