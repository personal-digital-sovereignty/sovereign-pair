# FAQ - Perguntas Frequentes

**Versão**: 3.0.0
**Data**: 2026-02-27

---

##  Índice

1. [Conceitos Básicos](#conceitos-básicos)
2. [Performance](#performance)
3. [Detecção de Mudanças](#detecção-de-mudanças)
4. [ChromaDB](#chromadb)
5. [Histórico](#histórico)
6. [Privacidade e Segurança](#privacidade-e-segurança)
7. [Troubleshooting](#troubleshooting)
8. [Configuração](#configuração)

---

## Conceitos Básicos

### O que é ingestão incremental?

Ingestão incremental é processar apenas arquivos novos ou modificados, ao invés de reprocessar tudo do zero. Economiza tempo e recursos.

### Qual a diferença entre modo full e incremental?

- **Modo Full**: Processa todos os arquivos, recria ChromaDB do zero
- **Modo Incremental**: Processa apenas mudanças (novos, modificados), mantém dados existentes

### Quando devo usar cada modo?

**Modo Full**:
- Primeira execução
- Após mudar modelo de embedding
- Após mudar chunk_size
- Para reconstruir do zero

**Modo Incremental**:
- Execuções normais
- Após adicionar/modificar poucos arquivos
- Para economizar tempo

---

## Performance

### Quanto mais rápido é o modo incremental?

**95%+ mais rápido** quando há poucas mudanças.

**Exemplo real**:
- 100 arquivos, modo full: 2 minutos
- 2 arquivos modificados, modo incremental: 5 segundos
- **Economia: 96%**

### Como a paralelização funciona?

Usa `ThreadPoolExecutor` para calcular hashes de múltiplos arquivos simultaneamente.

**Configuração**:
- Default: 4 workers
- Ajustável em `compute_hashes_parallel(max_workers=N)`

**Ganho**: 3-4x mais rápido em sistemas multi-core

### O que é o cache LRU?

Cache em memória que armazena hashes calculados recentemente.

**Funcionamento**:
- Chave: file_path + mtime
- Se arquivo não mudou (mesmo mtime), usa hash do cache
- Maxsize: 1000 arquivos

**Benefício**: Evita recálculo desnecessário

### Como otimizar para muitos arquivos?

1. **Aumentar workers**:
   ```python
   compute_hashes_parallel(files, max_workers=8)
   ```

2. **Usar SSD**: Disco rápido ajuda muito

3. **Ajustar chunk_size**: Chunks maiores = menos chunks = mais rápido

---

## Detecção de Mudanças

### Como funciona a detecção de modificações?

Usa **hash SHA256 do conteúdo** do arquivo.

**Processo**:
1. Calcula hash atual do arquivo
2. Compara com hash armazenado no histórico
3. Se diferente, arquivo foi modificado

### Por que usar SHA256 e não mtime?

**mtime** (modification time) pode mudar sem o conteúdo mudar:
- Comando `touch arquivo.md`
- Copiar arquivo
- Sincronização de nuvem

**SHA256** garante detecção baseada em **conteúdo real**.

### O que acontece se eu renomear um arquivo?

É tratado como:
- **Deletado**: arquivo antigo
- **Novo**: arquivo com novo nome

Os chunks do arquivo antigo são removidos e novos são criados.

### E se eu mover um arquivo entre diretórios?

Mesmo comportamento de renomear:
- Deletado do diretório antigo
- Novo no diretório novo

**Nota**: Não há detecção de "move" - é sempre delete + add.

---

## ChromaDB

### O que é ChromaDB?

Banco de dados vetorial que armazena embeddings dos chunks de documentos.

**Usado para**:
- Busca semântica
- Recuperação de contexto
- RAG (Retrieval-Augmented Generation)

### Como os chunks são organizados?

Cada chunk tem:
- **ID**: Único (ex: `docs/exemplo.md_chunk_0`)
- **Embedding**: Vetor numérico
- **Metadata**: `{"file_path": "docs/exemplo.md"}`
- **Document**: Texto do chunk

### O que acontece com chunks de arquivos deletados?

São **removidos automaticamente** do ChromaDB.

**Processo**:
1. Detecta arquivo deletado
2. Busca todos os chunks com `file_path` do arquivo
3. Remove chunks do ChromaDB
4. Remove arquivo do histórico

### Posso usar outro banco vetorial?

Sim, mas requer modificação do código. ChromaDB é usado por ser:
- Fácil de usar
- Sem servidor externo
- Persistente em disco
- Integrado com LlamaIndex

---

## Histórico

### O que é o arquivo `.ingestion_history.json`?

Arquivo que rastreia:
- Quais arquivos foram processados
- Hash SHA256 de cada arquivo
- Número de chunks criados
- Timestamp de modificação

**Localização**: `data/.ingestion_history.json`

### Qual a estrutura do histórico?

```json
{
  "version": "1.1",
  "last_updated": "2026-02-27T20:00:00",
  "files": {
    "/path/to/file.md": {
      "content_hash": "abc123...",
      "modified_at": "2026-02-27T19:00:00",
      "chunks": 5
    }
  }
}
```

### O que acontece se eu deletar o histórico?

O sistema detecta ausência de histórico e sugere **modo full**.

**Consequência**: Todos os arquivos serão reprocessados.

### Como migrar de versão antiga?

A migração é **automática**:
- Detecta versão antiga (v1.0 sem `content_hash`)
- Adiciona campo `content_hash` para cada arquivo
- Atualiza versão para v1.1

**Nota**: Primeira execução após migração pode ser lenta (calcula todos os hashes).

---

## Privacidade e Segurança

### O que é enviado para a nuvem quando uso um provedor Cloud (Ex: Anthropic/OpenAI)?

**Seus documentos e o banco de dados ChromaDB NUNCA são enviados para a nuvem.**

A arquitetura RAG (Retrieval-Augmented Generation) do Sovereign Pair garante **Zero-Trust**:

1. **Ingestão Local:** Todos os seus PDFs e arquivos Markdown são indexados e convertidos em vetores matemáticos localmente no seu computador (seja via *bge-m3* no Ollama ou outro provider Embed). Tudo fica salvo na pasta `data/chromadb` do seu disco rígido (ou NVMe).
2. **Busca e Recuperação:** Quando você faz uma pergunta, o sistema procura os trechos de texto (`chunks`) e documentos inteiramente de forma local no seu banco de dados (BM25 + Choma Vector).
3. **Comunicação Ativa com a Nuvem:** O único dado que viaja para os servidores da Anthropic/Google/OpenAI **é a sua pergunta exata** + **os pequenos fragmentos de texto estritamente necessários** que o sistema encontrou nos seus arquivos locais para responder àquela dúvida específica. Todo o resto do seu Cofre (Vault) continua 100% offline e intocável.

É literalmente o equivalente a você pinçar o parágrafo 3 da página 10 de um livro secreto, transcrever isso num Post-it, e enviar esse Post-it por cima do balcão para o Analista ler, emitir a opinião dele sobre o parágrafo, e devolver sua resposta. Ele nunca verá sua biblioteca real de Alexandria inteira.

### Se o RAG local é tão bom, por que eu usaria um Provedor Cloud (Gemini, Claude, GPT-4) ao invés do Ollama 100% offline?

O Sovereign Pair nasceu para ser agnóstico. **Acreditamos que 80% do trabalho diário de busca, indexação e resumo de documentos (RAG) deve ser feito gratuitamente, offline e com privacidade infinita pelo Ollama (como o Llama 3 8B).**

Porém, para os 20% restantes que exigem "Raciocínio de Engenheiro Sênior", os modelos de fronteira (Frontier Models) das Big Techs possuem vantagens arquitetônicas que um computador doméstico simplesmente não consegue rodar. As 5 principais diferenças técnicas reais são:

1. **Orçamento Bilionário de Alinhamento (RLHF):** Após serem treinados, LLMs em nuvem passam meses sendo exaustivamente refinados por Ph.Ds e especialistas de domínio para entender sarcasmo legal, física quântica e arquitetura de software complexa, com orçamentos que ultrapassam dezenas de milhões de dólares *apenas no alinhamento fino*.
2. **"Self-Correction" Numérico Inerente:** Modelos recentes (como a série `o1` ou Gemini pesados) gastam processamento (*Test-Time Compute*) simulando mentalmente milhares de passos antes de lhe responder. Um modelo de 8B no Ollama geralmente lhe entrega a primeira resposta probabilística imediatamente.
3. **Pós-Treinamento em Agenciamento (Tool Use):** Cloud LLMs raramente quebram a sintaxe JSON, perdem o foco da missão ou falham ao recuperar erros complexos de Terminal/Código, pois foram afinados contra milhões de repositórios reais e validadores sistêmicos internos.
4. **Gigante "Mix of Experts" (MoE):** Por trás de uma API do Google ou Anthropic, você não fala com "uma" IA pesando 4GB. Você fala com um comitê de Gênios de dezenas de redes neurais especializadas que pesam trilhões de parâmetros.
5. **Atenção em Contextos Infinitos:** Conseguir achar "uma agulha num palheiro" com 99.9% de precisão dentro de 2 Milhões de Tokens é um desafio matemático massivo (*Ring Attention*), que os *Frontier Models* dominam amplamente hoje.

**Nossa Visão Estratégica:**
Com o Sovereign Pair, a sua CLI permite alternar entre os mundos: Use a força bruta local (Ollama) para tarefas estruturais diárias. No dia em que você precisar planejar uma fusão empresarial baseada num relatório de 40 páginas, você dá "2 cliques" na Web-UI, ativa o Cérebro de Fronteira (Cloud), e a injeção RAG passa a enviar cirurgicamente *apenas os parágrafos cruciais* para esse gigante raciocinar - preservando tanto seu orçamento quanto sua Soberania plena sobre o documento master, que jamais sairá da sua máquina.

---

## Troubleshooting

### "Collection not found" - O que fazer?

**Causa**: ChromaDB não inicializado

**Solução**:
```bash
rm -rf data/chroma_db
python src/ingest.py  # modo full
```

### "Invalid history version" - Como resolver?

**Causa**: Histórico de versão muito antiga ou corrompido

**Solução**:
```bash
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Performance está lenta - Como debugar?

1. **Verificar número de arquivos**:
   ```bash
   find docs vault -type f | wc -l
   ```

2. **Verificar tamanho dos arquivos**:
   ```bash
   du -sh docs vault
   ```

3. **Testar com poucos arquivos**:
   ```bash
   # Mover arquivos temporariamente
   mkdir temp_backup
   mv docs/* temp_backup/
   cp temp_backup/file1.md docs/
   python src/ingest.py
   ```

### Inconsistência entre histórico e ChromaDB - Como resolver?

**Diagnóstico**:
```bash
python tests/validate_state.py
```

**Soluções**:

1. **Divergências menores** (< 5%):
   ```bash
   python src/ingest.py  # modo incremental
   ```

2. **Divergências grandes** (> 10%):
   ```bash
   rm -rf data/chroma_db data/.ingestion_history.json
   python src/ingest.py  # modo full
   ```

### Erro "docx2txt is required" - Como resolver?

**Causa**: Falta a biblioteca necessária para processar arquivos `.docx` (Microsoft Word).

**Solução**:
```bash
pip install docx2txt
# ou
pip install -r requirements.txt
```

### Erro "Permission denied" - O que fazer?

**Causa**: Sem permissão para ler arquivo ou escrever no ChromaDB

**Soluções**:

1. **Verificar permissões**:
   ```bash
   ls -la data/
   ls -la docs/
   ```

2. **Corrigir permissões**:
   ```bash
   chmod -R u+rw data/
   chmod -R u+r docs/
   ```

---

## Configuração

### Quais variáveis de ambiente são necessárias?

**Obrigatórias**:
- `VAULT_DIR`: Diretório principal de documentos
- `RAW_DOCS_DIRS`: Diretórios adicionais (separados por vírgula)
- `CHROMA_DIR`: Diretório do ChromaDB
- `CHROMA_COLLECTION_NAME`: Nome da coleção

**Opcionais**:
- `CHUNK_SIZE`: Tamanho dos chunks (default: 512)
- `CHUNK_OVERLAP`: Sobreposição (default: 50)
- `EMBED_MODEL`: Modelo de embedding (default: BAAI/bge-small-en-v1.5)

### Como processar múltiplos diretórios?

Configure `RAW_DOCS_DIRS` no `.env`:

```bash
RAW_DOCS_DIRS=docs,vault,notes,wiki,knowledge
```

**Nota**: Separar por vírgula, sem espaços.

### Posso mudar o modelo de embedding?

Sim, mas **requer reprocessamento completo**.

**Processo**:
1. Alterar `EMBED_MODEL` no `.env`
2. Deletar ChromaDB e histórico
3. Executar modo full

```bash
# .env
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Terminal
rm -rf data/chroma_db data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Como ajustar o tamanho dos chunks?

Edite `.env`:

```bash
CHUNK_SIZE=1024  # Chunks maiores
CHUNK_OVERLAP=100  # Mais sobreposição
```

**Trade-offs**:
- **Chunks maiores**: Menos chunks, mais rápido, menos granular
- **Chunks menores**: Mais chunks, mais lento, mais granular

**Nota**: Requer reprocessamento completo.

### Posso usar symlinks?

Sim! Configure `FOLLOW_SYMLINKS` no `.env`:

```bash
FOLLOW_SYMLINKS=true
```

**Cuidado**: Evite loops (symlink A → B → A).

---

## Casos de Uso

### Como usar com Obsidian?

1. **Configurar vault**:
   ```bash
   VAULT_DIR=/path/to/obsidian/vault
   ```

2. **Executar**:
   ```bash
   python src/ingest.py
   ```

3. **Workflow**:
   - Editar notas no Obsidian
   - Executar ingestão incremental
   - Apenas notas modificadas são reprocessadas

### Como usar com múltiplos projetos?

Crie `.env` separados:

```bash
# projeto1/.env
VAULT_DIR=data/projeto1
CHROMA_DIR=data/chroma_projeto1

# projeto2/.env
VAULT_DIR=data/projeto2
CHROMA_DIR=data/chroma_projeto2
```

Execute com:
```bash
cd projeto1 && python ../src/ingest.py
cd projeto2 && python ../src/ingest.py
```

### Como automatizar a ingestão?

**Cron (Linux/Mac)**:
```bash
# Executar a cada hora
0 * * * * cd /path/to/project && python src/ingest.py

# Executar diariamente às 2am
0 2 * * * cd /path/to/project && python src/ingest.py
```

**Task Scheduler (Windows)**:
1. Criar tarefa agendada
2. Ação: `python C:\path\to\project\src\ingest.py`
3. Gatilho: Diário/Horário

---

## Recursos Adicionais

- [Guia do Usuário](USER_GUIDE.md)
- [Documentação de API](API.md)
- [Testes End-to-End](../tests/manual_e2e_tests.md)
- [CHANGELOG](../CHANGELOG.md)

---

**Autor**: Jeferson Lopes
**Data**: 2026-02-27
