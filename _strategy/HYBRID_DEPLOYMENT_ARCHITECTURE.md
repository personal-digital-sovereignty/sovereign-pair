# Arquitetura de Implantação Híbrida (Local e Nuvem)

## 1. Visão Geral da Topologia de Rede
A arquitetura principal do projeto prioriza o processamento local para garantir a estabilidade e privacidade dos dados manipulados (Soberania Prática). Contudo, na finalidade da otimização de recursos sob o hardware base do desenvolvedor, cargas computacionais de inferência não relacionadas sensivelmente a fragmentos críticos de código podem ser transferidas ou distribuídas a nós auxiliares em provedores públicos, caracterizando a implementação em Malha.

O escopo segmenta-se computacionalmente em dois módulos:
1. **Host Executivo (Nó Local)**: Ambiente isolado onde residem estritamente o cofre (Vault) de arquivos em Markdown, o banco de persistência relacional unificado e indexadores de Vetores Lógicos (SQLite). O tratamento de LLM nativo e operações confidenciais acontecem in-loco (Offline Inference).
2. **Nó de Computação Distribuída (Oracle Cloud OCI)**: Uma instância separada instalada no ecossistema IaaS da Oracle Cloud, cuja atribuição foca no processamento complementar em Nuvem (como alocar e iterar queries longas no modelo `Qwen2.5-Coder` via VS Code IDE na integração OpenCode).

---

## 2. Orquestração e Deploy de Componentes

O sistema de processamento abstrato define o roteamento baseado no papel processual de cada engine na infraestrutura. A disposição de processabilidade pode ocorrer na seguinte matriz recomendada:

| Engine | Atribuição Principal | Local Operacional (Recomendado) |
| :--- | :--- | :--- |
| **The Mom** | Indexação monitorada assíncrona do file system do O.S. (Via Rust Notify). | Ambiente Local |
| **The Dad** | Serializador de chunks textuais e processamento intensivo de matrizes Embedded vetoriais (ex: `bge-m3`). | Ambiente Local |
| **The Nurse** | Roteador e classificador analítico de prioridade/requisição inicial (Low Latency Models). | Ambiente Local |
| **The Doctor** | Modelo mestre focado nas reestruturações das matrizes finais baseadas no RAG Engine (Reflexão Complexa). | Servidor Virtual OCI (ou Local via instâncias de alto rendimento) |
| **The Coder** | Análise e inferência interativa focada estritamente na emissão de abstração sintática e refatoração de projetos de código puro. | Servidor Virtual OCI |

---

## 3. Topologia de Conectividade Extrema (VPN mTLS Peer-to-Peer)

As sessões em instâncias de Nuvem não ativam permissões de portas diretas a web pública IPv4/IPv6, especialmente restritivas às portas inerentes de escuta da LLM API (`11434`), minimizando a superfície exposta para injeções automatizadas ou ameaças massivas do tipo *Scanning* (por ex., via buscadores de roteadores).

*   **Autenticação Via WireGuard (Tailscale)**: A arquitetura prevê que Instâncias na Cloud permaneçam circunscritas localmente dentro do túnel privado da máquina base (Mesh Desktop). Operando através de chaves ativas do WireGuard, a transação entre as tabelas vetoriais locais e o endpoint inferencial da Nuvem flui estritamente sob criptografia forte ponta a ponta na sua subrede invisível roteada pela operadora `100.x.x.x`.
*   **Contenção de Vulnerabilidades Passivas**: O Bind TCP das instâncias vitais na Nuvem, como os contêineres Docker e Ollama, estão condicionados intrinsecamente à interface de rede isolada gerenciada pelo cliente Tailscale nativo. Port-scans independentes encontrarão recusas forçadas de conexão.

---

## 4. Otimização Analítica (Performance Paged em Processadores ARM)

As especificidades do provimento nas topologias ARM de Cloud gratuitas (ou de entrada empresarial) frequentemente inviabilizam alocações completas baseadas em I/O Swap Disk tradicional (Devido à severa penalização em IOPS da estrutura Block Volume que travam processos intensivos de GPU/CPU Unificada dos grandes modelos).

As contra-medidas parametrizadas ao Cloud-Init do Host garantem que as predições sigam um curso responsivo nos cenários de stress local:

1. **Memória Virtual Comprimida (zram-tools)**: Antes do deploy das massas Docker, implementa-se no sistema operacional uma configuração persistente particionando as margens seguras (ex: 33% da RAM Base ou max. 8GB) configurada na compressão algoritmo LZ4. Sem tocar no disco virtual do serviço de OCI, modelos operantes liberam buffer massivamente reduzindo timeouts do banco neural nos gargalos pesados.
2. **Flash Attention na Engine (Directives SystemD)**: Injeções controladas nativamente no unit file da Daemon (Ollama) validam concorrência nativa de fila em LLMs de janela extensiva (ex: `128K context`). Variáveis parametrizáveis de ambiente como `OLLAMA_FLASH_ATTENTION=1` reduzem restritamente alocamentos ociosos no trânsito O.S / App Layer e previnem asfixia RAM no Qwen.

---

## 5. Práticas de Infraestrutura como Código Automática (IaC)

A implantação virtual em Servidores Terceirizados é desonerada do desenvolvedor através do fluxo de provisionamento Infrastructure as Code baseada primariamente via ferramentas HashiCorp/OpenTofu.

### CI/CD Automotivo via Actions
Um manifesto GitHub YAML parametrizado via `.github/workflows/deploy-oci.yml` provê a auditoria de estado e alocação.
1. O gatilho operacional submete pushes validados ao caminho do diretório `infra/terraform/`.
2. Acessos são decodificados via ambiente encriptado no próprio GitHub (Envs/Secrets), alimentando os pre-requisitos de Token OCI (`OCI_PRIVATE_KEY` e ID) e `TAILSCALE_AUTH_KEY`.
3. Aplicações modulares em infra executam `tofu apply -auto-approve` garantindo paralelidade e integridade final entre Nuvem/Repositório de Terraform State.

### Operação Cloud-Init
Arquivos físicos descritivos acionados pela VM provedora durante milissegundos críticos após boot processam de maneira sequencial (Garantido em non-interactive shells):
*   Restauração e padronização total da biblioteca gerencial APT Base (Removendo mirrors instáveis).
*   Download nativo do Mesh Layer (Tailscale Tunneling Client) com ativação deferida.
*   Instalação da Docker Engine local O.S e restabelecimento das rotinas LLM base Systemctl.
*   Processos dissociados (`nohup background jobs`) rodam execuções que persistem o pull serializado gigabital para popular os nós dos modelos Llama/Qwen durante os primeiros minutos de uptime isolado da VPS, preservando conectividade ssh.

---

## 6. Integridade de Container e Self-Healing Operacional 

Projetado em conformidade estrutural à metodologias 12-Factor App, eventuais reinícios não interativos de servidor (exs: Upgrades críticos Ubuntu OCI, Kernel patches do SO ou paralisações de hardware em Power-Cuts no host Edge Development) requerem nula atuação do Developer ou usuário administrador para a restauração lógica final da malha.

### Orquestração em Nível Processual (Docker)
Os módulos base contam com restrições arquiteturais aplicadas à diretiva robusta do Docker (`restart: always`), abrigando em invólucros estanques independentes as premissas de re-run automático de seus núcleos e processos filho:
- O balanceador e gateway reverso (`caddy`).
- Sincronização e transações de rede RESTful e Async (`api` e `n8n`).
- Interwebs GUI renderizado com Ngnix (`web`) e bancos legados se aplicáveis (`postgres`).

### Relê de Retomada a Frio do State Local
1. Subida da daemon base Docker no Host FileSystem.
2. Comutação sistêmica interligando sub-nets com contêineres às chaves de Tunelamento nativas.
3. Volumes da malha efetuam o Bind Mount in-loco (Restauro temporal dos Sqlite Vectors de forma stateful).
4. Libera-se os *Health Checks* garantindo que a conexão HTTP e SSL operem antes de injetar requests nas instâncias dos Agentes. Sem scripts de *bootstrap* auxiliares ou chaves SSH pendentes.
