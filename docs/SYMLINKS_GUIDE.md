# Guia de Links Simbólicos - Sovereign Pair RAG

Este guia explica como usar links simbólicos (symlinks) para integrar seus documentos existentes sem copiá-los.

---

##  O que são Links Simbólicos?

Links simbólicos são "atalhos" que apontam para arquivos ou diretórios em outros locais do sistema. Eles permitem que você acesse seus documentos originais sem duplicá-los.

**Analogia**: Como um atalho na área de trabalho que aponta para um programa instalado em outro lugar.

---

##  Por que usar Symlinks?

### Vantagens

 **Sem Duplicação**: Não ocupa espaço extra no disco
 **Sempre Atualizado**: Mudanças nos arquivos originais são refletidas automaticamente
 **Organização**: Mantém seus arquivos onde já estão
 **Integração com Obsidian**: Use seu vault diretamente
 **Múltiplas Fontes**: Combine documentos de diferentes locais

### Quando Usar

- Você já tem um Obsidian vault organizado
- Seus documentos estão em múltiplas pastas
- Você não quer duplicar arquivos grandes
- Você quer que mudanças sejam refletidas automaticamente

---

##  Como Criar Links Simbólicos

### Sintaxe Básica

```bash
ln -s /caminho/origem /caminho/destino
```

- `/caminho/origem`: Onde seus arquivos realmente estão
- `/caminho/destino`: Onde você quer que apareçam

### Exemplo 1: Obsidian Vault

```bash
# Seu vault está em ~/Documents/ObsidianVault
# Você quer que apareça em data/vault

cd /caminho/para/sovereign-pair
ln -s ~/Documents/ObsidianVault data/vault
```

**Resultado**: `data/vault` agora aponta para seu Obsidian vault!

### Exemplo 2: Pasta de PDFs

```bash
# Você tem PDFs em ~/Documents/PDFs
# Quer indexá-los sem copiar

cd /caminho/para/sovereign-pair
ln -s ~/Documents/PDFs data/raw_docs/pdfs
```

### Exemplo 3: Múltiplas Pastas

```bash
cd /caminho/para/sovereign-pair

# Criar symlinks para diferentes fontes
ln -s ~/Documents/PDFs data/raw_docs/pdfs
ln -s ~/Downloads/Papers data/raw_docs/papers
ln -s ~/Projects/Documentation data/raw_docs/project_docs
```

**Resultado**: Todos os documentos dessas 3 pastas serão indexados!

---

##  Verificando Links Simbólicos

### Ver se é um Symlink

```bash
ls -la data/vault
```

**Saída**:
```
lrwxrwxrwx 1 user user 35 Feb 16 01:00 vault -> /home/user/Documents/ObsidianVault
```

A seta `->` indica que é um symlink e para onde aponta.

### Verificar se o Symlink está Funcionando

```bash
# Ver conteúdo através do symlink
ls data/vault

# Deve mostrar os mesmos arquivos que:
ls ~/Documents/ObsidianVault
```

---

##  Problemas Comuns

### Symlink Quebrado

**Sintoma**: Link existe mas aponta para local inexistente

```bash
ls -la data/vault
# lrwxrwxrwx ... vault -> /caminho/que/nao/existe (em vermelho)
```

**Solução**:
```bash
# Remover symlink quebrado
rm data/vault

# Criar novo com caminho correto
ln -s /caminho/correto data/vault
```

### Permissões

**Sintoma**: Não consegue ler arquivos através do symlink

**Solução**: Verificar permissões do diretório original
```bash
chmod +r ~/Documents/ObsidianVault/*
```

### Caminho Relativo vs Absoluto

** Evite caminhos relativos**:
```bash
ln -s ../../../Documents/Vault data/vault  # Pode quebrar
```

** Use caminhos absolutos**:
```bash
ln -s ~/Documents/Vault data/vault  # Sempre funciona
# ou
ln -s /home/usuario/Documents/Vault data/vault
```

---

##  Integração com Obsidian

### Passo a Passo

1. **Encontre seu Obsidian Vault**
   ```bash
   # Geralmente está em:
   ~/Documents/Obsidian
   # ou
   ~/Documents/ObsidianVault
   ```

2. **Crie o Symlink**
   ```bash
   cd /caminho/para/sovereign-pair
   ln -s ~/Documents/ObsidianVault data/vault
   ```

3. **Configure o .env** (opcional)
   ```env
   # Ou aponte diretamente no .env
   VAULT_PATH=/home/usuario/Documents/ObsidianVault
   FOLLOW_SYMLINKS=true
   ```

4. **Execute a Ingestão**
   ```bash
   cd src
   python ingest.py
   ```

### Vantagens

-  Todas as suas notas do Obsidian ficam disponíveis para o agente
-  Quando você edita no Obsidian, basta re-indexar
-  Não duplica seus arquivos
-  Mantém sua organização existente

---

##  Alternativa: Caminhos Absolutos

Se você não quer usar symlinks, pode configurar caminhos absolutos no `.env`:

```env
# Apontar diretamente para Obsidian vault
VAULT_PATH=/home/usuario/Documents/ObsidianVault

# Múltiplos caminhos de documentos
RAW_DOCS_PATHS=/home/usuario/Documents/PDFs,/home/usuario/Downloads/Papers

# Seguir symlinks se houver
FOLLOW_SYMLINKS=true
```

**Vantagens**:
- Mais simples (não precisa criar symlinks)
- Configuração centralizada no `.env`

**Desvantagens**:
- Menos flexível que symlinks
- Caminho absoluto pode mudar entre sistemas

---

##  Comparação: Symlinks vs Caminhos Absolutos vs Copiar

| Método | Duplicação | Atualização | Flexibilidade | Complexidade |
|--------|------------|-------------|---------------|--------------|
| **Copiar Arquivos** |  Sim |  Manual |  |  Simples |
| **Symlinks** |  Não |  Automática |  |  Médio |
| **Caminhos Absolutos** |  Não |  Automática |  |  Fácil |

---

##  Dicas e Boas Práticas

### 1. Use Nomes Descritivos

```bash
#  Ruim
ln -s ~/docs data/raw_docs/d

#  Bom
ln -s ~/Documents/PDFs data/raw_docs/pdfs
ln -s ~/Downloads/Papers data/raw_docs/research_papers
```

### 2. Documente seus Symlinks

Crie um arquivo `data/SYMLINKS.txt`:
```
vault -> ~/Documents/ObsidianVault
raw_docs/pdfs -> ~/Documents/PDFs
raw_docs/papers -> ~/Downloads/Papers
```

### 3. Verifique Regularmente

```bash
# Script para verificar symlinks
find data -type l -exec ls -la {} \;
```

### 4. Backup de Configuração

Salve seus comandos de criação de symlinks:
```bash
# Criar arquivo setup_symlinks.sh
cat > setup_symlinks.sh << 'EOF'
#!/bin/bash
ln -s ~/Documents/ObsidianVault data/vault
ln -s ~/Documents/PDFs data/raw_docs/pdfs
ln -s ~/Downloads/Papers data/raw_docs/papers
EOF

chmod +x setup_symlinks.sh
```

---

##  Troubleshooting

### Erro: "Vault path não existe"

**Causa**: Symlink quebrado ou caminho incorreto

**Solução**:
```bash
# Verificar symlink
ls -la data/vault

# Se quebrado, recriar
rm data/vault
ln -s /caminho/correto data/vault
```

### Erro: "FOLLOW_SYMLINKS=false"

**Causa**: Configuração desabilitou symlinks

**Solução**: No `.env`:
```env
FOLLOW_SYMLINKS=true
```

### Nenhum Documento Encontrado

**Causa**: Symlink aponta para pasta vazia

**Solução**:
```bash
# Verificar conteúdo
ls -R data/vault

# Verificar origem
ls -R ~/Documents/ObsidianVault
```

---

##  Exemplos Práticos

### Caso 1: Estudante com Múltiplas Fontes

```bash
# Notas de aula (Obsidian)
ln -s ~/Documents/Obsidian/ClassNotes data/vault

# PDFs de livros
ln -s ~/Books/PDFs data/raw_docs/books

# Papers baixados
ln -s ~/Downloads/Research data/raw_docs/papers

# Slides de aula
ln -s ~/Documents/Slides data/raw_docs/slides
```

### Caso 2: Desenvolvedor com Documentação

```bash
# Notas pessoais
ln -s ~/Notes data/vault

# Documentação de projetos
ln -s ~/Projects/project1/docs data/raw_docs/project1
ln -s ~/Projects/project2/docs data/raw_docs/project2

# READMEs e wikis
ln -s ~/Projects/wikis data/raw_docs/wikis
```

### Caso 3: Pesquisador

```bash
# Vault do Obsidian com anotações
ln -s ~/Obsidian/Research data/vault

# Papers organizados por tema
ln -s ~/Research/Papers/ML data/raw_docs/ml_papers
ln -s ~/Research/Papers/NLP data/raw_docs/nlp_papers

# Datasets e documentação
ln -s ~/Research/Datasets/docs data/raw_docs/dataset_docs
```

---

##  Recursos Adicionais

- [Documentação Completa de Configuração](CONFIGURATION.md)
- [README Principal](../README.md)
- [Documentação do Obsidian](https://obsidian.md)

---

**Dica Final**: Comece simples! Crie um symlink para seu Obsidian vault e veja como funciona. Depois adicione mais conforme necessário.

---

**Autor**: Jeferson Lopes
**Assistência**: Google Gemini 3 e Claude Sonnet 4.5 (Anthropic)
**Data**: 2026-02-17
**Versão**: 2.0.0
