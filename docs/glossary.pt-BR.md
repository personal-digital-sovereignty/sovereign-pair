# Sovereign Pair - Glossário Corporativo

Este documento consolida os termos arquiteturais e protocolos técnicos empregados no ecossistema Sovereign Pair. Seu objetivo é balizar engenheiros e operadores no entendimento unificado do sistema, atuando como o alicerce para todos os Manuais do Usuário, Guias de Implantação e Documentações de Arquitetura.

## Terminologia de Arquitetura Base

### Sovereign Pair
A suíte completa de orquestração de Inteligência Artificial composta pela interface local imersiva de interação (Vue3), motores de inferência RAG multimodelo na borda (GPU Local/Metal) e instâncias de automação em nuvem (OCI). O ecossistema promove soberania digital absoluta ao usuário sobre seus dados, abdicando de telemetria ou ingestão de terceiros (Zero-Knowledge).

### Cibrid (Cloud-Hybrid / Nuvem Cíbrida)
Modelo de implantação em que a camada mais pesada de cálculos matriciais ou armazenamento vitalício (LLMs, Ingestão Vetorial e Vault) é estritamente hospedada "On-Premises" na máquina física do usuário (Ex: Workstation com GPU Local), enquanto a interface de coordenação, filas e message-broker operam transparentemente de forma leve em instâncias de nuvem gratuita (Oracle OCI A1 Flex).

### Zero-Trust / Darknet (Malha de Confiança Zero)
Aplica-se ao modelo de rede Tailscale operado no núcleo do sistema. Os motores de Cibrid operacionais (N8N, Redis, APIs e Ollama) nunca expõem portas diretamente de escuta à internet pública (`0.0.0.0` no Ingress/IGW). O fluxo inteiro de dados corre exclusivamente pela VPN interna (ex: endereços `100.x.x.x` da topologia Mesh), garantindo que conexões sem certificados validados e nós não-autorizados sejam intrinsecamente descartados na camada mais baixa da rede.

## Componentes do Motor de Inteligência

### RAG (Retrieval-Augmented Generation)
Arquitetura que recupera documentos locais antes do Llama inferir qualquer frase. Previne alucinações ao forçar o motor semântico (LLM) a ler estritamente os fatos vetoriais extraídos do Vault (Sensus) do usuário.

### BM25 & Híbrido (Hybrid Search)
Método combinatório de ranqueamento que soluciona falhas matemáticas da similiridade cosseno. O Sovereign Pair funde as pontuações probabilísticas de frequências de palavras cruas (Lexical/BM25) com as relações de significado semântico (Vetorial/ChromaDB), resultando numa recuperação extrema de exatidão de datas ou metadados de texto não-textuais (ex: UUIDs).

### Vault (Sensus Vault / God Mode)
A árvore de diretórios literal física do computador local monitorada permanentemente pelo Sovereign Pair. Não requer cópia ou abstração relacional profunda para funcionar: é o repositório orgânico (pastas, `.md`, `.pdf`, planilhas) onde os agentes do sistema habitam, ingerem e refletem. A abstração visual que lê essas árvores na GUI é o Sensus Vault (Dashboard lateral e Graph UI).

## Orquestração (N8N / Core MCP)

### MCP (Model Context Protocol) 
Protocolo estabelecido nativamente (por Anthropic) que o Sovereign Pair herda em suas APIs centrais para que ferramentas de terceiros e LLMs solicitem ações (como LER_VAULT, EXECUTAR_BASH, INGERIR_DADOS) via um padrão universal corporativo. O FastAPI interno hospeda um Servidor MCP que dita os recursos vitais disponíveis no Vault.

### TDD & Zero-Bypass
Mandato organizacional adotado a partir da Release 3.3.0. A suíte inteira de código e a CI/CD devem rodar ininterruptamente sem diretivas tolerantes a falhas fracas como ignore lint (`# noqa`) ou permissões de secrets expostos propositais nos scanners (`.gitleaksignore`). Os artefatos do sistema devem blindar-se puramente por arquitetura de software (Mocks robustos e Re-imports estruturados).

---
> *Nota Interna de Documentação: Novos termos arquiteturais surgidos nas próximas fases devem ser averbados unicamente neste documento de forma alfabética dentro dos grupos correlacionados.*