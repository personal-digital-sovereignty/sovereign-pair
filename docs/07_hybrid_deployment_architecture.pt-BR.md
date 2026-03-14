# Tratado VII: Arquitetura Híbrida de Implantação

## 1. Visão Geral da Topologia de Rede

A infraestrutura busca descentralizar as demandas preservando no host primário o papel de gerir documentos privados. Para compensar limitações físicas sobre o Desktop do desenvolvedor, transações demoradas de inferência de código livre ou geração externa são distribuídas aos provedores da nuvem pública. 

Esse ambiente corporativo se divide na seguinte malha O.S:
1. **Nó Local Central:** Ambientes O.S gerenciados no Hardware Físico Pessoal retendo sob proteção restrita os logs e cofres Markdown (Sensus Vault) e as formatações vectorias do SQLite local.
2. **Nó Auxiliar OCI (Cloud Node):** Utiliza instancição secundária sob Virtual Private Servers (VPS) Oracle OCI atestados via máquinas gratuitas ARM 64-bits (Ampere A1).

---

## 2. Padrões de Roteamento (Distribuição do Motor)

A lógica que organiza e designa responsabilidades dentro dos nós do ambiente multi-agente está dividida conforme o suporte nativo exigido:

| Modulos (Worker) | Responsabilidades Arquiteturais | Implantação Ideal Mínima |
| :--- | :--- | :--- |
| **The Mom / FileWatcher** | Indexação da modificação em pastas estáticas (Linux `notify`). | Máquina Desktop Local |
| **The Dad / Embedded** | Transformação em Chunks vetoriais (`bge-m3` via Python Local). | Máquina Desktop Local |
| **The Nurse / Router** | Avaliação paramétrica categorizando *intents* HTTPS originais. | Máquina Desktop Local |
| **The Doctor / Engine** | Modelação formatada contextual iterando sob o modelo de RAG. | Oracle OCI (VPS externa ou Hardware High-End Local) |
| **The Coder / Logic** | Analisador estrito de documentações refatorais sob o Python OpenCode. | Oracle OCI |

---

## 3. Segurança Estrutural VPN (Tunnel Peer-to-Peer mTLS)

Em caráter definitivo, endpoints da API LLM O.S providenciados pelo *Docker `11434`* ou sub-dependente FastAPI *8000* estarão completamente fechados a instâncias da banda global (Sem *Bind TCP 0.0.0.0* e desprovidos de portas expostas em WAN).

*   **Validação Criptográfica Operativa (WireGuard via Tailscale):** Tráfegos originárias das chamadas na Nuvem perante arquivos vetoriais locais são conduzidos sob conexão criptografada via peer-to-peer atuando diretamente através das interfaces (`100.x.x.x`). A estrutura facilita acesso remoto seguro independente dos roteadores bloqueantes O.S corporativos das companhias locais do usuário.
*   **Mitigação Contraste Passivo:** Varreduras em escaneamento O.S massivo O.S Port Scan externas recairão sob falhas já que os aplicativos isolantes confinam explicitamente na sub-rede VPN, invisibilizando aberturas em portas lógicas do SO da máquina ou Servidor VPS.

---

## 4. Eficiência de Servidor ARM64 e Otimizações de SO

Em infraestrutura Cloud de Baixo Custo (Free Tiers), o provisionamento O.S em ambientes providenciadores de Storage Limitado podem apresentar dificuldades quando atados a arquivos contextuais amplos. Processamentos forçados sob Volumes via Block Storage acarretam perda no *IOPS* e travamentos sob exaustão nas variáveis de memória livre nativa O.S (Ex: Inferencial Llama local no Servidor).

A parametrização técnica `Cloud Init` implementou re-estruturações focadas estritamente na preservação desse tempo de resposta (Timeout Limit Restrictions):

1. **Memória Compacta `zram-tools`:** O SO Linux inicializa um sistema em swap virtual instanciando particionamento alocado sob algoritmo de Super-Compressão `LZ4` na memória livre base do SO. Mitiga o engasgo computacional do disco originário na plataforma sem encarecer servidores e alivia limitações pesantes dos nós da rede.
2. **Execução de LLMs Estendida `OLLAMA_FLASH_ATTENTION=1`:** Inserida expressamente via arquivo de config `SystemD`, esta formatação técnica estática gerencia perante a leitura rápida nativa de modelagem LLM os tokens associados aos "contextos gigantes" (Modelos >32K Tokens/128K Text Strings), melhorando tempos assíncronos das repostas providas a Engine FastAPI nativa de roteamentos paralelos.

---

## 5. Implementação Dinâmica Infrastructure As Code (IaC System/OpenTofu)

Processos dependentes da criação do nó físico em Oracle Nuvem foram completamente automatizados através dos gerenciadores manifestados *Infrastructure as Code* (OpenTofu).

### Pipeline Contínua via Github Actions
O GitHub Operations centraliza e autoriza roteamentos do código orquestrado via workflow `deploy-oci.yml`.
1. A base reativa exige *Merges* atualizados nos manifestos localizados em `./infra/terraform/`.
2. Restritivos secretos sob GitHub Actions Cloud contêm os UUIDs das Tenants Oracle, assim como sua API Authentication (*OCI_PRIVATE_KEY*) limitantes na base secreta do arquivo O.S.
3. Submetidos a instâncias operativas `tofu apply -auto-approve`, os contêineres e configurações base Ubuntu inicializam sob nuvem, reportando nativamente todo seu "Estado Seguro" sob a branch.

## 6. Procedimentos Resilientes (Self-Healing Application Containers)
O desenho base em contêiner obedece à engenharia restrita da recomendação base de sistemas imutáveis (Ex: *12-Factor App*). Diante de oscilações estruturais provindas do OS (Kernel Reboots acidentais, atualizações em massa que reiniciam instâncias VPS primárias base), não requerem inicializações interativas SSH dos usuários corporativos O.S ou engenheiro base local da máquina:

- Suas ferramentas e volumes internos recomeçarão isoladamente, parametrizados sob as configurações restart nativas Docker Engine (`restart: always`).
- Apenas submetem a Engine de RAG final à verificação da NuvemMesh VPN (Interface interna) e realizam o acoplamento autônomo do O.S sob interfaces relativas API FastAPI (Rest Local) atestados assim que O.S Server retoma estabilidade elétrica computacional básica.
