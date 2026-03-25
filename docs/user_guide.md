# Guia Oficial do Usuário: Sovereign Pair

Bem-vindo ao **Sovereign Pair**, o seu ecossistema pessoal de Inteligência Artificial Privada e Geração Aumentada Cíbrida (RAG). Este guia foi cuidadosamente desenhado para conduzi-lo através de todas as telas e painéis da nossa interface de Controle (Hub). 

Imagine o Sovereign Pair não apenas como um chatbot, mas como um sistema nervoso descentralizado que vive no seu computador, processa seus documentos locais, e interage com o mundo de forma autônoma e absolutamente segura.

Abaixo, detalhamos cada uma das seções que você encontrará no menu principal da sua interface. Tudo o que você ler aqui reflete sistemas mecânicos reais do seu software.

---

## 0. Settings (Configurações Globais)
A engrenagem base de tudo. O **Settings** é o alicerce criptografado do seu aplicativo.
- **O que você encontra aqui:** O gerenciamento das chaves de API (OpenAI, Anthropic, Gemini, Groq) e parâmetros core da sua instância.
- **Para que serve:** Sempre que precisar alternar provedores corporativos nas destilações do motor, ou inserir o seu Token Mestre para sincronizar novos repositórios/workspaces. Tudo aqui é guardado e trancado apenas na memória do seu SQLite interno de forma offline, sem servidores fofoqueiros.

## 1. Home (O Centro de Comando)
A página **Home** é o seu *Dashboard* (painel de controle). Aqui você tem uma visão panorâmica e em tempo real da saúde da sua malha cíbrida.
- **O que você encontra aqui:** Gráficos de velocidade de resposta (Tokens por segundo), quantidade de documentos que o sistema já absorveu, temperatura do sistema e o tráfego da rede P2P (ponto a ponto).
- **Para que serve:** Sempre que você ligar o sistema, olhe para cá para confirmar se as "engrenagens" de memória e o hardware do seu PC estão operantes e balanceados.

## 2. Chat (A Interface de Conversa)
O **Chat** é a sua sala privada de diálogo com a Inteligência Artificial. Diferente de sistemas genéricos na nuvem, tudo o que você escreve aqui é criptografado e não sai da sua máquina a não ser que você autorize.
- **O que você encontra aqui:** Um campo limpo para enviar mensagens, anexar arquivos rapidamente, e visualizar as respostas analíticas da IA, que ativamente consulta o seu *Vault* (Cofre) de memórias em tempo real.
- **Para que serve:** Tirar dúvidas difíceis, pedir a criação de códigos ou debater grandes ideias criativas de forma instantânea.

## 3. Vault (Seu Cofre de Conhecimento)
O **Vault** (Cofre) é a manifestação física do espaço de HD que você concedeu à IA. É onde vivem os "Workspaces" (Suas pastas de conhecimento).
- **Explorador de Arquivos:** Você pode navegar organizadamente por pastas e documentos Markdown (`.md`), PDFs e Imagens sincronizadas. 
- **O Visualizador Frontal:** Ao clicar em um arquivo, ele se abre em abas limpas para leitura rápida, sem interromper sua pesquisa.
- **Sinalização Inteligente de Artefatos da IA:** Nossa UI classifica as pastas visualmente para você não se perder.
  - **✨ Deep Research Artifact:** Arquivos demarcados com insígnias lilás brilhantes. São relatórios ultra-completos e condensados gerados de forma 100% autônoma pela IA após uma pesquisa profunda na internet (Eles ficam salvos em `_agents/artifacts/`).
  - **🧠 Knowledge Gap:** Arquivos demarcados com a cor laranja. São relatórios de "Buracos no Sistema", criados quando a IA nota que o cofre carece de dados importantes sobre algum tema vital (Eles ficam salvos em `gaps/`).

## 4. Projects (A Prancheta de Projetos)
A aba de **Projects** foi desenhada para amarrar a IA nas amarras organizacionais do seu dia a dia (Estilo Trello/Kanban).
- **O que você encontra aqui:** Quadros de tarefas separadas em "A Fazer", "Em Progresso" e "Concluído". 
- **Para que serve:** Vincular documentos específicos de um projeto e criar um roteiro onde a IA saiba exatamente o contexto específico daquela tarefa antes de escrever uma linha de código.

---

## 5. System Modules (O Motor Cíbrido)
Aqui é onde a mágica absoluta, a ciência de dados e a engenharia profunda acontecem. O *System Modules* expõe os "órgãos internos" da IA para que você tenha controle laboratorial.

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
O módulo onde você sintoniza os hiper-parâmetros dos Modelos de Base para deixá-los "no ponto" ideal.
- **Perfection Controls:** Controles vetoriais reais em sliders magnéticos (`Alpha`, `Top-K Context Depth`, `Batch Sizes do Computador` e níveis táticos de `LoRA Rank`). 
- **Painel Unsloth Matrix Monitor:** Você vislumbrará todo o poder de fogo computacional no monitor retangular: O ressoar estrondoso do uso da VRAM consumida pela sua Placa de Vídeo e o avanço milissegundo a milissegundo pelo console nativo logando taxas matemáticas (`Loss Curve`, `Grad Norm` e os `Tokens Processing`). Tudo administrado por 3 robustos botões de *Playback* (Start, Stop, Pause).
- **Export Configuration:** O extrator em um clique das matrizes JSON. Clique e guarde em backup toda a personalização que gerou bons resultados.

#### C. Reflection Lab (O Monólogo Interno)
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
