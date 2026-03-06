# Tratado III: Configurações, Tuning SRE e Troubleshooting

## 1. Topologia de Variáveis de Ambiente (`.env`)

O projeto ignora os arquivos `.env` passivamente no controle de versão (Git) para garantir a segurança implacável *Zero-Trust*. Todos os parâmetros de alinhamento criptográfico militar e endereçamentos de infraestrutura devem ser declarados via um arquivo `.env` estrito localizado na raiz do projeto.

### 1.1 Configuração de Modelos e Inteligência (Core)
| Variável | Escopo | Valor Padrão (Sugestão) | Observações para Engenheiros SRE |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Rede | `http://localhost:11434` | Se operado remotamente em um *Nó Local Físico* através da malha VPN Tailscale, use o IPv4 privado interno (Ex: `http://100.x.x.x:11434`). Lembre-se de configurar e permitir conexões globais via `OLLAMA_HOST="0.0.0.0"` no PC que possui a placa de vídeo. |
| `LLM_MODEL` | Inferência | `qwen2.5:0.5b` | Define o peso computacional de raciocínio lógico base. O modelo escolhido **deve** ser importado previamente (via cache Docker ou Linux interno) rodando o comando `ollama pull [nome]`. |
| `EMBED_MODEL` | Vetorização Matemática | `bge-m3` | O motor puramente responsável por transmutar texto em um hiper-espaço de 1024 dimensões focado em suporte Multilingual de altíssima fidelidade. **Trade-off Físico de Velocidade:** Se a sua operação demandar ingestão agressivamente rápida em hardware local (Ex: Laptops robustos com Ryzen 7 5800H + 32GB RAM empurrada por ZRAM em ArchLinux), você pode deliberadamente fazer downgrade para a engine `nomic-embed-text` (768 dimensões). Ela é comprovadamente ~3x mais rápida inserindo PDFs no banco, contudo sofre um forte viés para o Idioma Inglês, perdendo o "mapa cognitivo real" em textos nativos em Português. Atenção SRE: O modelo de *Embedding* **nunca** deve ser substituído rodando após a criação inicial do ChromaDB, pois a malha colapsará. |
| `REQUEST_TIMEOUT` | Rede do Servidor | `120.0` | Suba este limite incondicionalmente para generosos `300.0` (5 Minutos) para hardwares que rodam Placas de Vídeo (RTXs/Ryzen) sofrendo em triturações de limite, ou se seu API Orquestrador for uma instância fraca Oracle A1 ARM. |

### 1.2 Customização Parametrizada de Identidade
O Sovereign Pair adapta nativamente o seu *System Prompt* (A Personalidade Atuante Sub-consciente) com base nas configurações da conta. 
| Variável | Injeção no Prompt de Sistema |
|---|---|
| `OWNER_NICKNAME` | Apelido. A Mestre / O Cérebro fará menções e cumprimentos honrosos a você. |
| `SOVEREIGN_NAME` | Nome de batismo da Entidade (Ex: *Sovereign*, *Jarvis*, *Ghost*). Regula a biografia de acordo com o nome que ela acredita possuir. |
| `LANGUAGE` | Regula estritamente a gramática e semântica de saída. Force `Português do Brasil` ou `US English` na marreta aqui para impedir a volatilidade linguística natural de LLMs que às vezes sofrem para "entender" e "responder" no mesmo idioma da requisição técnica N8N ou Front-End. |
| `OCCUPATION` | Formata o jargão profissional. Ex: se você preencher com `Senior SRE DevOps Engineer`, obriga e força psicologicamente o LLM a tratar os assuntos de Docker, Tailscale e Linux com um tom ríspido, técnico e elevado, podando explicações excessivamente "leigas". |

---

## 2. Runbook (Guia de Sobrevivência SRE) para Colapsos do ChromaDB

Quedas de rede bruta entre as placas de rede do Tailscale e a Nuvem Oracle ou Colapsos na densidade do Arquivo de Vetor são corriqueiros. **Jamais** apague os diretórios de Bancos de Dados local manualmente da raiz sem isolar e ler pesadamente os Logs JSON antes para entender.

### 2.1 Corrupção do Estado Incremental (Hashes Divergentes)
*O scan/terminal diz que o arquivo não existe, mas visualizador de Markdown UI Dashboard na tela Web prova que ele está lá.*
- **Incidente:** Ocorre um abalo sísmico entre o Banco Histórico Serializado em Json (`.ingestion_history.json`) e o Indexador relacional Nativo Sqlite do `ChromaDB`. Geralmente causado por *Hard Resets*, Ctrl+C brutais durante processamento massivo, Kernel Panics ou luz piscando durante a mastigação intensa vetorial das pastas locais de 30 Mil arquivos em PDF (`Sensus Vault`).
- **Resolução de Engenharia:** Aniquile e detone o banco *Vector Brain* recriando o nada. Nenhum dado do mundo físico é perdido pelo Sovereign, pois os arquivos cruciais de vida (.md / .pdf) repousam quietos no seu valioso repositório passivo do Vault. O Sistema em Pânico meramente irá reconstruir a Matemática toda para recuperar seus pedaços perdidos e resincronizar os hashes em `< 7s`.

```bash
# SRE Runbook: Expurgação Absoluta do Vector DB.
rm -rf data/chroma_db
rm data/.ingestion_history.json

# Reinicie o container para ele auto-detectar ou detone via script nativo python manual:
python src/ingest.py 
```

---

## 3. O Silenciamento Assassino do LlamaIndex ("Empty Response" Bug)

*A API retorna a famosa String assustadora "Empty Response" em menos de 1.5s na N8N quando tentamos conversar, APESAR de o modelo e a placa de vídeo apontarem online, responsivos e saudáveis.*

- **O Incidente:** Por "Design da Comunidade" enrustido do Repositório Original (e disfarçado como Feature Econômica), os construtores de classe como o `CondensePlusContextChatEngine` (da biblioteca oficial `llama-index` OpenSource Python) simplesmente **abortam e matam a geração pura do LLM** no meio caminho caso o recuperador matemático de vetores retorne exatos `0` *Nodes* e falhe grotescamente em achar correspondências de contexto na pasta para sua busca. Pode ocorrer de duas formas:
   1) O Arquivo e sua Pergunta nada tem em comum para a IA ler o PDF atrelado e ele desiste.
   2) É o Primeiríssimo dia (Day 1 User) de um novo "Inquilino/Tenant" conectando na Engine corporativa RAG N8N Sovereign e seu Banco de Cérebro/Vector, e obviamente, está Limpo e Zerado.
   Para tentar economizar de forma cega no tráfego dos servidores Open-AI de tokens de texto (Custos Cloud), a lib do Llama original trava a Roda (Wheel) e chuta de volta um retorno forjado grotesco escrito String Puro: `"Empty Response"`, ao invés de prosseguir o fluxo encaminhando a pergunta natural ao LLM junto do System Prompt/Engine isolados para te responder cordialmente e conversar como gente fina.
- **A Resolução Corporativa Final (Bypass Soberano):** O Projeto Sovereign Pair é mais brutal. Criou-se um Overrider oficial, explícito como **Sovereign Bypass** ancorado pesadamente na rota Principal (`routes.py`). Se a poderosa e robusta Engine esmurrar um falso `"Empty Response"` gerado artificialmente pela Llama-Index, Nossa API agarra pelo colarinho na hora antes do Stream falhar. Instancia e Intercepta o formato custom do Histórico de Memória Chat antigo da API juntamente do System Prompt completo da Personagem. Ao juntar essas "Duas Bolas Mágicas", despacha diretamente a consulta *Conversacional Local Unificada* por trás do retreiver pesado de vetores, metralhando o *construtor Base-Foundation Bare Metal (`_llm`)* de Categoria Crua em um *Fallback* Gracioso, restaurando e revigorando totalmente o sistema ao retornar IA com vida Pura à tela N8N para Inquilinos Novatos ("Dia 1"). Você jamais lerá um `Empty Output`.
