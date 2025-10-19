# Testes - Guia de Uso

Este diretório contém scripts e dados para testes automatizados do Sovereign Pair RAG.

## Estrutura

```
tests/
├── scripts/           # Scripts de teste
│   ├── prepare_test_env.sh   # Preparação do ambiente
│   ├── run_tests.sh          # Execução dos testes
│   └── cleanup_tests.sh      # Limpeza após testes
├── data/             # Dados de teste (criados automaticamente)
│   ├── vault/        # Documentos de teste
│   ├── raw_docs/     # Documentos adicionais
│   └── symlink_test/ # Estrutura para testes de symlinks
└── results/          # Resultados dos testes (logs)
```

## Como Usar

### 1. Preparar Ambiente de Testes

```bash
cd tests/scripts
./prepare_test_env.sh
```

Este script:
- Cria estrutura de diretórios
- Gera documentos de teste
- Cria symlinks de teste (diretórios, arquivos, circulares, quebrados)
- Prepara casos de teste especiais

### 2. Executar Testes

```bash
./run_tests.sh
```

Este script executa:
- **Testes de Configuração**: Validação de arquivos e variáveis
- **Testes de Estrutura**: Verificação de diretórios e arquivos
- **Testes de Symlinks**: Validação de symlinks (válidos, circulares, quebrados)
- **Testes de Código**: Importação de módulos e validação de implementação
- **Testes de Ingestão**: Dry run de carregamento de documentos

### 3. Verificar Resultados

```bash
# Ver último resultado
cat results/test_results_*.log | tail -50

# Listar todos os resultados
ls -lh results/
```

### 4. Limpar Ambiente (Opcional)

```bash
./cleanup_tests.sh
```

Remove dados de teste e resultados, mantendo apenas os scripts.

## Testes Incluídos

### Categoria 1: Configuração
- ✅ Verificar arquivo `config.py`
- ✅ Verificar `CHUNK_SIZE` definido
- ✅ Verificar `CHUNK_OVERLAP` definido

### Categoria 2: Estrutura de Dados
- ✅ Verificar diretório de dados de teste
- ✅ Verificar documentos de teste criados
- ✅ Verificar symlinks criados

### Categoria 3: Symlinks
- ✅ Symlink de diretório resolve corretamente
- ✅ Symlink de arquivo resolve corretamente
- ✅ Symlink circular detectado
- ✅ Symlink quebrado detectado

### Categoria 4: Código
- ✅ Importar módulo `config`
- ✅ Verificar `SentenceSplitter` em uso
- ✅ Verificar parâmetros de chunking

### Categoria 5: Ingestão (Dry Run)
- ✅ Validar carregamento de documentos
- ✅ Verificar processamento de symlinks
- ✅ Contar documentos carregados

## Dados de Teste

### Documentos Criados

1. **test_doc_01.md**: Documento básico com 3 seções e bloco de código
2. **test_doc_02.md**: Documento secundário para teste múltiplo
3. **test_doc_03_long.md**: Documento longo para testar chunking
4. **test_pdf_placeholder.txt**: Placeholder para simular PDF

### Symlinks de Teste

1. **symlink_dir**: Symlink de diretório válido
2. **symlink_file.txt**: Symlink de arquivo válido
3. **circular_link**: Symlink circular (para teste de detecção)
4. **broken_symlink**: Symlink quebrado (para teste de erro)

## Interpretação de Resultados

### Sucesso Total
```
Total de testes: 15
✅ Testes passados: 15
❌ Testes falhados: 0

✅ TODOS OS TESTES PASSARAM!
```

### Falha Parcial
```
Total de testes: 15
✅ Testes passados: 13
❌ Testes falhados: 2

❌ ALGUNS TESTES FALHARAM
```

Verifique o log completo em `results/test_results_*.log` para detalhes.

## Troubleshooting

### Erro: "Ambiente virtual não encontrado"

```bash
cd ..  # Voltar para raiz do projeto
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Módulo não encontrado"

```bash
source ../.venv/bin/activate
pip install -r ../requirements.txt
```

### Erro: "Permissão negada"

```bash
chmod +x scripts/*.sh
```

## Personalização

### Adicionar Novos Testes

Edite `scripts/run_tests.sh` e adicione:

```bash
run_test "Nome do teste" "comando_a_executar"
```

### Modificar Dados de Teste

Edite `scripts/prepare_test_env.sh` para criar documentos customizados.

## Integração Contínua

Para usar em CI/CD:

```bash
# No seu pipeline
cd tests/scripts
./prepare_test_env.sh
./run_tests.sh
EXIT_CODE=$?

# Publicar resultados
cat ../results/test_results_*.log

exit $EXIT_CODE
```

## Notas Importantes

1. **Não commitar dados de teste**: `data/` e `results/` estão no `.gitignore`
2. **Scripts são portáveis**: Funcionam em qualquer sistema Unix-like
3. **Testes são não-destrutivos**: Não afetam dados de produção
4. **Resultados são timestamped**: Cada execução gera novo log

## Referência

Para mais informações sobre os testes, consulte:
- `docs/TESTES.md`: Documentação completa de testes
- `CHANGELOG.md`: Histórico de mudanças
- `README.md`: Documentação geral do projeto
