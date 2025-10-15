# Guia de Formatos de Arquivo Suportados

Este guia documenta os formatos de arquivo suportados pelo sistema de ingestão do Sovereign Pair RAG.

---

## Suporte a Links Simbólicos (Symlinks)

O sistema suporta **links simbólicos** tanto para **arquivos** quanto para **diretórios**, permitindo organização flexível sem duplicar dados.

### Symlinks de Diretórios

Você pode criar symlinks para diretórios inteiros, e o sistema processará **recursivamente** todo o conteúdo:

```bash
# Linkar Obsidian vault
ln -sf /path/to/obsidian-vault data/vault/my-vault

# Linkar diretório de documentos
ln -sf ~/Documents/Projects/docs data/raw_docs/project-docs

# Linkar múltiplos diretórios
ln -sf ~/Dropbox/Notes data/vault/dropbox
ln -sf ~/Google\ Drive/Docs data/raw_docs/gdrive
```

**Comportamento**:
- ✅ Todo o conteúdo do diretório linkado é indexado recursivamente
- ✅ Subdiretórios dentro do symlink são processados
- ✅ Respeita `ALLOWED_EXTENSIONS` configurado
- ✅ Evita loops infinitos (symlinks circulares)

**Exemplo de log**:
```
🔗 Seguindo symlink de diretório: my-vault -> /home/user/obsidian-vault
   ✓ 45 documento(s) de 'my-vault/'
```

### Symlinks de Arquivos

Você também pode criar symlinks para arquivos individuais:

```bash
# Linkar arquivo específico
ln -sf ~/important-doc.pdf data/raw_docs/doc.pdf

# Linkar múltiplos arquivos
ln -sf ~/thesis.pdf data/raw_docs/
ln -sf ~/notes.md data/vault/
```

**Comportamento**:
- ✅ Arquivo linkado é processado normalmente
- ✅ Respeita extensões permitidas

### Configuração: FOLLOW_SYMLINKS

Controle se symlinks devem ser seguidos via `.env`:

```env
# Seguir symlinks (padrão: true)
FOLLOW_SYMLINKS=true

# Ignorar symlinks
FOLLOW_SYMLINKS=false
```

**Com `FOLLOW_SYMLINKS=false`**:
- Symlinks são ignorados
- Apenas arquivos e diretórios reais são processados
- Log: `⚠️  Ignorando symlink 'nome' (FOLLOW_SYMLINKS=false)`

### Detecção de Problemas

O sistema detecta e reporta problemas com symlinks:

**Symlink Quebrado**:
```
❌ Symlink quebrado 'old-vault': data/vault/old-vault -> /path/nonexistent
```

**Symlink Circular**:
```
⚠️  Symlink circular detectado, ignorando: loop
```

### Casos de Uso

#### Obsidian Vault

```bash
# Não copiar vault, apenas linkar
ln -sf ~/Obsidian/MyVault data/vault/obsidian

# Resultado: todas as notas .md são indexadas
```

#### Múltiplas Fontes de Documentos

```bash
# Linkar diferentes fontes
ln -sf ~/Dropbox/Work data/raw_docs/work
ln -sf ~/Google\ Drive/Personal data/raw_docs/personal
ln -sf ~/Documents/Research data/raw_docs/research

# Todas são indexadas juntas
```

#### Documentos Compartilhados

```bash
# Linkar diretório compartilhado na rede
ln -sf /mnt/nas/shared-docs data/raw_docs/shared

# Documentos acessíveis sem duplicação
```

---

## Formatos Suportados Nativamente

O sistema utiliza o `SimpleDirectoryReader` do LlamaIndex, que suporta nativamente os seguintes formatos:

| Formato | Extensão | Descrição | Suporte |
|---------|----------|-----------|---------|
| **Markdown** | `.md` | Arquivos de texto formatado (ideal para Obsidian) | ✅ Nativo + Chunking inteligente |
| **PDF** | `.pdf` | Documentos PDF | ✅ Nativo |
| **Texto** | `.txt` | Arquivos de texto simples | ✅ Nativo |
| **Word (novo)** | `.docx` | Microsoft Word (formato moderno) | ✅ Nativo |
| **CSV** | `.csv` | Planilhas em formato CSV | ✅ Nativo |
| **JSON** | `.json` | Dados estruturados em JSON | ✅ Nativo |
| **HTML** | `.html` | Páginas web | ✅ Nativo |

---

## Chunking Inteligente para Markdown

Arquivos `.md` recebem tratamento especial com o **MarkdownNodeParser**:

### Funcionalidades

- ✅ **Respeita cabeçalhos**: Divide por `##`, `###`, etc.
- ✅ **Preserva blocos de código**: Mantém ` ``` ` intactos
- ✅ **Contexto semântico**: Mantém hierarquia de notas
- ✅ **Ideal para Obsidian**: Estrutura de vault preservada

### Exemplo

```markdown
## Capítulo 1: Introdução

Este é o conteúdo do capítulo 1.

### Seção 1.1

Conteúdo da seção 1.1.

```python
def exemplo():
    return "código preservado"
```

## Capítulo 2: Desenvolvimento

Conteúdo do capítulo 2.
```

**Resultado**: 3 blocos semânticos criados:
1. "Capítulo 1: Introdução" (com conteúdo)
2. "Seção 1.1" (com código preservado)
3. "Capítulo 2: Desenvolvimento"

---

## Formatos NÃO Suportados Nativamente

### Microsoft Word Antigo (.doc)

**Status**: ❌ Não suportado nativamente

**Solução**: Converter para `.docx`

#### Usando LibreOffice (Linux/macOS)

```bash
# Converter um arquivo
libreoffice --headless --convert-to docx arquivo.doc

# Converter múltiplos arquivos
for file in *.doc; do
    libreoffice --headless --convert-to docx "$file"
done
```

#### Usando Microsoft Word

1. Abrir o arquivo `.doc`
2. Arquivo → Salvar Como
3. Escolher formato `.docx`

---

### OpenDocument Text (.odt)

**Status**: ❌ Não suportado nativamente

**Solução**: Converter para `.docx`

#### Usando LibreOffice

```bash
# Converter um arquivo
libreoffice --headless --convert-to docx arquivo.odt

# Converter múltiplos arquivos
for file in *.odt; do
    libreoffice --headless --convert-to docx "$file"
done
```

#### Usando Google Docs

1. Upload do arquivo `.odt` para Google Drive
2. Abrir com Google Docs
3. Arquivo → Download → Microsoft Word (.docx)

---

## Configuração de Extensões

### Arquivo `.env`

```env
# Extensões permitidas (separadas por vírgula)
ALLOWED_EXTENSIONS=.md,.pdf,.txt,.docx
```

### Extensões Padrão

Se não configurado, o sistema usa:
```
.md, .pdf, .txt, .docx, .csv, .json, .html
```

### Personalizando

Para adicionar ou remover formatos:

```env
# Apenas Markdown e PDF
ALLOWED_EXTENSIONS=.md,.pdf

# Todos os formatos suportados
ALLOWED_EXTENSIONS=.md,.pdf,.txt,.docx,.csv,.json,.html

# Adicionar formatos customizados (se tiver readers instalados)
ALLOWED_EXTENSIONS=.md,.pdf,.txt,.docx,.epub
```

---

## Script de Conversão em Lote

Para facilitar a conversão de múltiplos arquivos:

### convert_docs.sh

```bash
#!/bin/bash

# Script para converter .doc e .odt para .docx

echo "Convertendo arquivos .doc para .docx..."
for file in **/*.doc; do
    if [ -f "$file" ]; then
        echo "  Convertendo: $file"
        libreoffice --headless --convert-to docx "$file" --outdir "$(dirname "$file")"
    fi
done

echo ""
echo "Convertendo arquivos .odt para .docx..."
for file in **/*.odt; do
    if [ -f "$file" ]; then
        echo "  Convertendo: $file"
        libreoffice --headless --convert-to docx "$file" --outdir "$(dirname "$file")"
    fi
done

echo ""
echo "✅ Conversão concluída!"
```

**Uso**:
```bash
chmod +x convert_docs.sh
./convert_docs.sh
```

---

## Verificando Formatos nos Seus Documentos

### Listar extensões presentes

```bash
# No diretório de documentos
find data/vault data/raw_docs -type f | sed 's/.*\.//' | sort | uniq -c
```

**Saída exemplo**:
```
  45 md
  12 pdf
   8 txt
   3 docx
   2 doc    # ⚠️ Precisa conversão
   1 odt    # ⚠️ Precisa conversão
```

### Encontrar arquivos que precisam conversão

```bash
# Encontrar .doc
find data/vault data/raw_docs -name "*.doc"

# Encontrar .odt
find data/vault data/raw_docs -name "*.odt"
```

---

## Troubleshooting

### Erro: "Nenhum documento encontrado"

**Causa**: Extensões não permitidas ou arquivos em formato não suportado

**Solução**:
1. Verificar `ALLOWED_EXTENSIONS` no `.env`
2. Converter arquivos `.doc`/`.odt` para `.docx`
3. Verificar se há arquivos nos diretórios

### Erro ao processar PDF

**Causa**: PDF pode estar corrompido ou protegido

**Solução**:
1. Abrir PDF em visualizador para verificar
2. Se protegido, remover proteção
3. Recriar PDF se corrompido

### LibreOffice não instalado

**Linux (Ubuntu/Debian)**:
```bash
sudo apt install libreoffice
```

**macOS**:
```bash
brew install --cask libreoffice
```

---

## Estatísticas de Processamento

Durante a ingestão, o sistema mostra:

```
📋 Etapa 2/4: Processando documentos com chunking inteligente
======================================================================
   📝 Arquivos Markdown: 45
   📄 Outros formatos: 15

   🧩 Processando Markdown com MarkdownNodeParser...
      (Respeita cabeçalhos ## e blocos de código ```)
      ✓ 234 blocos semânticos criados

   📦 Processando 15 documentos não-Markdown...
      ✓ 87 blocos criados

   📊 Total de blocos (nodes): 321
   📏 Tamanho médio: 512 caracteres
```

---

## Recomendações

### Para Usuários Obsidian

- ✅ Use `.md` para todas as notas
- ✅ Aproveite o chunking inteligente
- ✅ Mantenha estrutura de cabeçalhos

### Para Documentação Técnica

- ✅ `.md` para documentação versionada
- ✅ `.pdf` para manuais e especificações
- ✅ `.docx` para documentos colaborativos

### Para Pesquisa Acadêmica

- ✅ `.pdf` para papers e artigos
- ✅ `.md` para anotações e resumos
- ✅ `.txt` para transcrições

---

## Recursos Adicionais

- [Documentação LlamaIndex - SimpleDirectoryReader](https://docs.llamaindex.ai/)
- [Guia de Links Simbólicos](SYMLINKS_GUIDE.md)
- [Configuração Completa](CONFIGURATION.md)
- [README Principal](../README.md)

---

**Dica**: Mantenha seus documentos em formatos suportados nativamente para melhor performance e qualidade de indexação!
