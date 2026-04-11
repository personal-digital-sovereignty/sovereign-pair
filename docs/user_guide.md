# Guia Oficial do Usuário: Sovereign Pair

Bem-vindo ao **Sovereign Pair**, o seu ecossistema pessoal de Inteligência Artificial Privada e Geração Aumentada Cíbrida (RAG). Este guia foi cuidadosamente desenhado para conduzi-lo através de todas as telas e painéis da nossa interface de Controle (Hub). 

Imagine o Sovereign Pair não apenas como um chatbot, mas como um sistema nervoso descentralizado que vive no seu computador, processa seus documentos locais, e interage com o mundo de forma autônoma e absolutamente segura.

Abaixo, detalhamos cada uma das seções que você encontrará no menu principal da sua interface. Tudo o que você ler aqui reflete sistemas mecânicos reais do seu software.

---

## 0. Settings (Identidade & Infraestrutura)
A sala das máquinas. O **Settings** não é um painel genérico de chaves de API, mas sim o alicerce operacional da sua inteligência descentralizada. Dividido em 4 pilares:
- **Sovereign Identity (Cortex Continuity):** Onde você pode *Exportar* ou *Importar* um arquivo encriptado `.cybrid`. Ele salva todo o seu estado mental (pastas, preferências, chaves) te permitindo restaurar a IA inteira em outra máquina num clique.
- **Sovereign Mesh P2P:** Mostra onde seus cérebros físicos estão operando. Pode ser o `ryzen-local-alpha` do seu quarto, ou uma placa remota. É aqui que você abre novos túneis P2P descentralizados.
- **Cloud Sandboxing (OCI):** A configuração de contingência da Oracle Cloud. Usado apenas quando seu maquinário local ficar indisponível.
- **Sovereign Core (AI Engine):** O controle de tráfego do sistema nervoso neural, subdividido em dois planos de atuação:
  - **A Matriz Autônoma (Model Operations Matrix):** O painel do motor Assíncrono (Background). Aqui você configura papéis específicos (Mente Mestra, Scribe, Coder, Agent) via *checkboxes*. O sistema escolhe dinamicamente o maior modelo habilitado (`ORDER BY size DESC`). Toda vez que uma rotina massiva (Deep Research ou Projetos Complexos) for acordada, ela assumirá esta hierarquia isoladamente para operar ferramentas, caçar na web e sintetizar artefatos. *Nota Especial de Contingência Gratuita:* Se um modelo for desinstalado (`ollama rm`), ele não é perdido da Matriz: ele ganha um rótulo especial vermelho **[OFFLINE]** e é omitido dinamicamente das rotas mecânicas, blindando a arquitetura contra quebras. Baixá-lo novamente retorna suas características Cíbridas ativas na hora.
  - **O Seletor de Chat (Engine Settings Modal):** O painel Síncrono (Zero-Shot). No ícone de engrenagem principal, o campo "Model Name" diz ao sistema quem deve responder a perguntas do dia a dia no Chat. Independente da "Matriz" rodando no fundo, o modelo escolhido aqui será o que conversará e analisará arquivos isolados que você enviar diretamente. Você escolhe a Temperatura, limita o Top-K de criatividade e gerencia o fluxo livre do Cíbrido em instantes imediatos.

## 1. Home (O Centro de Comando)
A página **Home** é o seu *Dashboard* (painel de controle). Aqui você tem uma visão panorâmica e em tempo real da saúde da sua malha cíbrida.
- **O que você encontra aqui:** Gráficos de velocidade de resposta (Tokens por segundo), quantidade de documentos que o sistema já absorveu, temperatura do sistema e o tráfego da rede P2P (ponto a ponto).
- **Para que serve:** Sempre que você ligar o sistema, olhe para cá para confirmar se as "engrenagens" de memória e o hardware do seu PC estão operantes e balanceados.

## 2. Chat (A Interface de Conversa)
O **Chat** é a sua sala privada de diálogo com a Inteligência Artificial. Diferente de sistemas genéricos na nuvem, tudo o que você escreve aqui é criptografado e não sai da sua máquina a não ser que você autorize.
- **Deep Research Mode:** O botão de hiper-foco investigativo. Em vez de uma simples e passiva resposta em texto, o modelo ativa uma rotina de pesquisa contínua e autônoma na Web, entregando para você dossiês implacáveis após escavar a camada superficial dos links.
- **Análise Nativa de PDFs:** Arraste e solte arquivos complexos ou massivos (PDFs corporativos, contratos densos, manuais) diretamente na janela de conversa. O Motor RAG fará a trituração matemática vetorial sem enviar um único byte para fora.
- **Histórico Isolado em Árvore de Diretórios:** Esqueça a fila caótica de chats em nuvem. A retenção das suas requisições possui estrutura de *file-system* real. Você pode instanciar Diretórios Lógicos (*Folders*) de contexto e isolar a janela de memória do LLM em blocos por projeto de código, níveis de segurança ou depuração bruta, organizando as threads de forma cirúrgica e unicamente na sua máquina.

## 3. Vault (Seu Cofre de Conhecimento)
O **Vault** (Cofre) é a manifestação física do espaço de HD que você concedeu à IA. É onde vivem os "Workspaces" (Suas pastas de conhecimento).
- **Categorização em Nível Cerebral (Wikilinks):** Toda vez que você ou a IA referenciou um conceito interno ativando as chaves duplas (`[[conceito]]`), o Vault lê e constrói uma Categoria Lógica inteira baseada nesses nós de ligação da internet neural.
- **Busca Cirúrgica com Filtros Nativos:** Uma barra de busca com o poder limpo de um shell Linux nativo integrado ao painel transparente do Svelte. Acione comandos precisos na busca, como `tag:linux`, `path:/projects/code`, `status:synced` ou `name:relatorio.md` para filtrar em nanossegundos sua vastidão intelectual.
- **Editor Markdown e Motor de Tabelas Complexas:** Escreva ou visualize os relatórios das IAs através do poderoso renderizador da UI, que constrói tabelas matemáticas, grids organizacionais e *code-highlights* com estética laboratorial polida.
- **Gestão Viva de Interface e Documentos:** Com botões ágeis no próprio explorador, crie documentos interativos (`Novo Arquivo`), renomeie instantaneamente com cliques contínuos ou mande arquivos mortos para a exclusão física através do botão vermelho (*Trash2*).
- **Chat Exclusivo Centrado no Contexto:** Um sistema impecável — quando você clica em um documento no Explorador do Vault, ele é aberto na Área de Leitura. Imediatamente, o painel Direito do Chat lateral restringe total e *estritamente* seus conhecimentos de leitura ao Escopo Analítico do que estava aberto. Se você perguntou, a resposta é blindada usando o seu arquivo.
- **Isolamento de Sessão e Imersão Literária:** O Vault opera com "Amnésia de Contexto" proposital. Ao abrir esta área ou seus documentos, seu chat nace inteiramente limpo e isolado de conversas prévias trazidas de outros lugares do menu. Esse rigor impede o vazamento de ideias entre contextos diferentes. Adicionalmente, caso precise do máximo de atenção na leitura/escrita, clique no **ícone de Ocultar Painel** no canto superior direito para colapsar o Chat Cíbrido e expandir a tela de documentos, similar à liberdade da tela de Projetos.
- **Sinalização Inteligente de Artefatos da IA:** Nossa UI classifica as pastas visualmente para você não se perder na poeira.
  - **✨ Deep Research Artifact:** Arquivos demarcados com bolhas lilás brilhantes. Relatórios destilados e gerados pela IA autônoma em jornadas pela internet (Salvos em `_agents/artifacts/`).
  - **🧠 Knowledge Gap:** Arquivos demarcados com insígnias âmbar/laranja. Diários alertando de "Buracos Lógicos Verificados no Modelo" a serem preenchidos com mais material intelectual (Salvos em `gaps/`).

## 4. Projects (A Prancheta de Projetos)
A aba de **Projects** foi forjada para domar o caos. Esqueça sistemas de gerenciamento passivos; aqui, as demandas do seu dia a dia evoluem e são amarradas sob os olhos da Inteligência Artificial.
- **Listagem e Visão Geral:** Ao entrar, você obtém uma visão tática macro de todos os seus "Projetos". É um sistema de gestão vivo: você pode criar novos escopos, editar as premissas estruturais, ou "engavetar" (Arquivar) temporariamente projetos antigos ou concluídos para focar apenas nas prioridades vitais correntes.
- **Direto ao Ponto (Dentro do Projeto):** Ao selecionar um item, a interface silencia o resto do computador e cria uma bolha. Você passa a dominar um sofisticado **Quadro Kanban** (A Fazer, Em Progresso, Concluído). Cada *Task* aceita descritivos detalhados, tags e o peso de se trabalhar com extrema rigidez de cronogramas — definindo datas de entrega ("Com Prazos") ou atuando em modo focado exploratório ("Sem Prazos").
- **O Vínculo Cinético com o Vault (O Verdadeiro Poder):** Você pode ancorar arquivos físicos ou pastas gigantes do seu *Vault* ligando-os visceralmente a uma tarefa específica ou à raiz do projeto. Toda a interface reconhece o que está linkado.
- **A IA Acelerando a Vida (Sem Ctrl+C/Ctrl+V):** Com a tarefa ancorada a um arquivo do Vault, o Chat lateral não te fará perder tempo. Se você abriu seu Kanban e ordenou ao Chat: *"Analise a documentação linkada e resolva esta tarefa"*, a IA atravessará dinamicamente os vínculos salvos no Kanban, fará a leitura matemática exata do código/documento em pauta baseando-se no prazo e cenário da sua tarefa, e te devolverá a resolução já no balanço ideal. A interação atinge um nível impiedoso de organização profissional sem que você tenha movido o cursor.

---

## 5. System Modules (O Motor Cíbrido)
Aqui é onde a mágica absoluta, a ciência de dados e a engenharia profunda acontecem. O *System Modules* expõe os "órgãos internos" da IA para que você tenha controle laboratorial.

> **⚠️ Arquitetura Estrita de Isolamento (Sub-Tenants Contextuais):**
> Antes de dissecarmos os laboratórios abaixo, grave essa regra: **todo e qualquer Chat com a IA espalhado pelo sistema vive confinado num *Sub-Tenant* (Locatário de Contexto) isolado e criptografado.** Isso evita severamente a contaminação cruzada e as temidas "Alucinações". Uma pergunta técnica realizada no módulo *Model Trainer* jamais invocará ou se confundirá com os desabafos organizacionais que você conversou com o Chat no módulo de *Projects*. Toda janela de diálogo é blindada, fazendo a Inteligência Artificial ser super-especialista no escopo de tela onde você a chamou, apagando alucinações cognitivas indesejadas pela raiz.

### 5.1 Cognitive Graph (O Cérebro em Mapeamento)
Uma representação visual e viva do seu conhecimento. Enquanto o Vault guarda as pastas friamente, o *Cognitive Graph* desenha os neurônios e brilha as *Sinapses* luminosas (ligações dinâmicas) constatando as correlações lógicas entre os documentos e as rotinas diárias gravadas nele.

### 5.2 RAG Engine (O Motor de Busca Semântica)
O **RAG** (Retrieval-Augmented Generation) é o tubo de resfriamento intelectual. É aqui que você refina a capacidade do sistema ler os PDFs e Pastas do Vault.
- **Routing Rules:** Painel para determinar se uma pergunta básica usará um modelo levíssimo em processamento, e se uma pergunta complexa de programação acordará o modelo superior.
- **Remote Models:** O painel para inserir as provedoras terceirizadas de modelos proprietários para balanceamento (quando sua placa de vídeo pedir trégua).
- **Quality & Gaps:** O Scanner de buracos! Este painel gera insights e aponta falhas contínuas de raciocínio. Quando uma falha intelectual é consertada e seu texto "Gap Restore" salvo, o sistema roteia a correção mecanicamente para o `Vault/gaps/` enriquecendo o motor. 

### 5.3 Model Trainer (A Forja da Inteligência)
Provavelmente a seção mais fascinante de todo o projeto. Onde você molda os preceitos de caráter e memória técnica dos modelos. Não há ilusão gráfica, todos os inputs aqui desviam a injeção do Rust Engine. É subdividido em 4 laboratórios:

#### A. RAG Pipeline & Deep Research Orchestrator
A usina de expedições massivas em busca de verdade documental.
- **Research Directive:** O quadrante no qual você pede ao modelo para ir ao mundo: *"Levante a documentação histórica inteira do Java e sumarize a viabilidade da versão 21..."* 
- **Research Modifiers (Toggles Ativos):**  
  - **Cross-Encoder Re-rank:** Força a IA a ser preciosista. Se encontrar 100 páginas, lerá profundamente em re-ordenação vetorial avançada para selecionar apenas as cruciais, rejeitando entulho.
  - **Strict Hallucination:** O bloqueador de ruídos e mentiras matemáticas.
  - **Grounding Focus:** O "Modo Isolamento Absoluto". Ao ativar este card de vidro (Grounding Engine Active), você aprisiona a IA. Ela será estritamente submissa aos arquivos que VOCÊ colocou no Vault. Literalmente cega ao resto da internet.
- **Execution Flow Graph (Telemetria Viva):** Ao estourar o gatilho *Launch Deep Research*, você verá na tela lateral em `Real-time` o triturar impiedoso dos Scrapers (Raspadores HTML), injetando *Tokens* recém formados de volta na pasta de artefatos da sua máquina.

#### B. Fine-Tuning Engine & Unsloth Monitor

> **⚠️ Alerta de Cenografia Estrutural (Mocks vs Realidade na v1.2.0):** 
> Transparência técnica é o pilar cíbrido. A atual aba de *Fine-Tuning Engine* é uma obra-prima de design hibrido: partes dela ditam verdade absoluta, enquanto a computação de Loss Gradient está simulada aguardando o Orquestrador Python (v1.3.0).
> 
> **✅ O Que Funciona (Ambiente Real):**
> 1. **Telemetria Deep Research (RAG):** Os marcadores de *Knowledge Gap Percentage*, *Sources Scanned* e *Recently Acquired Knowledge* não são falsos. Eles buscam ativamente o seu tráfego de leitura do SQLite e contam as injeções em disco.
> 2. **Perfection Controls (Controles Reais):** Seus ajustes de `Strict Grounding`, `Embedding Alignment Alpha` e `Top-K` alteram o vetor das buscas e a forma com a qual RAG injeta tokens nos prompts. O JSON montado vai até o motor Rust ileso.
> 3. **Export Configurations:** O backup em `.json` extrai com fidelidade todo o payload modificado por você.
> 
> **🎭 O Que é Mock (Simulação para Interface):**
> 1. **Treinamento de Redes Neurais (O Engano Seguro):** O motor *Ollama* nativo utilizado no momento recusa o retreino de tensores (Fine-tuning puro). Ao clicar em "Start Fine-Tuning", a interface Svelte e a API Rust conspiram num bypass inteligente: A *Engine* clona instantaneamente (`/api/create`) os Modelfiles, sem alterar "os cérebros" do IA via Python VRAM, retornando `Sucesso` falso.
> 2. **Unsloth Matrix Monitor:** É uma *Casca Audiovisual* impressionante. As linhas subindo de *VRAM Usage*, a queda matemática da *Loss Curve* e o contador de *Epochs* são scripts Assíncronos controlados via tempo. Não se assuste se sua GPU nem aquecer! 

O módulo onde você sintoniza os hiper-parâmetros dos Modelos de Base para deixá-los "no ponto" ideal.
- **Perfection Controls:** Controles vetoriais em sliders magnéticos (`Alpha`, `Top-K Context Depth`, `Batch Sizes do Computador` e níveis táticos de `LoRA Rank`). 
- **Painel Unsloth Matrix Monitor:** Espaço onde você vislumbrará todo o poder de fogo computacional no monitor retangular: O ressoar estrondoso do uso da VRAM consumida pela sua Placa de Vídeo e o avanço pelo console nativo logando taxas matemáticas. O play control aciona as janelas.
- **Export Configuration:** O extrator em um clique das matrizes JSON. Clique e guarde em backup toda a personalização que gerou bons resultados.

#### C. Reflection Lab (O Monólogo Interno)
> **⚠️ Em Desenvolvimento (v1.3.0 Mock):** Assim como o Unsloth Monitor, o laboratório de Reflexão está cenograficamente construído nesta versão para pavimentação da telemetria de métricas do sistema. O "Live Stream" gera auditorias randômicas temporárias em loop, simulando o que a próxima arquitetura de *SSE IPC* e Raciocínio Latente injetará em breve.
É onde as consciências ocultas são transparentes no seu controle. Se a IA errava e não se justificava, agora ela passa semanas dissecando cadeias invisíveis para entregar o estado da arte.
- **Internal Monologue:** A Chave Metacognitiva Mestra. Transforma o output do Cíbrido de uma geração imediata de texto numa escalada estruturada de "Pensar Primeiro".
- **Reasoning Depth & Self-Correct Ratio:** Sliders de Intensidade. Quantos "passos" de duvidar ela terá de respeitar antes de imprimir um retorno? O marcador reativo *Self-Correct* expõe o quanto do raciocínio base precisou se re-alinhar baseando-se no teto das falhas matemáticas lidas pelo scanner de Knowledge Gaps do RAG.
- **Live Stream e O Dataset JSON Editor:** O local tátil para injetar "Simulações Lógicas Ruidosas" de metadados em cadeia, testá-las nativamente (`Validate Schema`), e fixar correntes de dedução de falhas (Apply To Training) ensinando-a a sempre pensar devagar para assuntos complexos.

#### D. Knowledge Distillation
O Alquimista Numérico. Onde o "Professor (Cloud ou Massive Local LLM)" transfere o raciocínio intelectual abstrato para "O Estudante" (Modelos extremamente menores de 8B ou 14B rodáveis num laptop leve).
- **Professor X Student Paradigm:** Seletores lógicos condicionados a *Flags*. Se você buscar destilar pedindo conhecimento da OpenAI, emblemas cinzas de alerta pipocarão te alertando sobre limites éticos da núvem. Se escolher um motor interno Sovereign Local Puro, o escudo Verde-Impetuoso piscará garantindo o *Sigilo Isolado e Custo Zero* vitalício.
- **Similarity Matrix Streamer:** O mostrador animado monitorando a aproximação e maturação sináptica entre Aluno x Mestre (Crescendo percentualmente como `0.85 -> 0.90 -> 0.94%`), atestando a robustez com o Log visual passando sob sua visada durante os descarregamentos de épocas do treinamento em `Background`.

### 5.4 Analytics
Módulo de reportagem retroativa para contabilização estatística pesada do uso local ao decorrer dos meses.

---

### O Fator Soberano
O Sovereign Pair foi moldado com a intenção impiedosa de exterminar o comodismo opaco de Big-Techs, resgatando as rédeas vitais das suas mãos. Nada nesta UI é um *Dashboard de Vaidade*. Deslizar um botão implica invocar motores Rust blindados no fundo do seu HD. O controle absoluto não está apenas garantido, ele é o protocolo fundamental em operação.
