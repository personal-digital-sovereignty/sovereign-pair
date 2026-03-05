import pytest
import sys
import os

# Adicionar src ao path para importar ingest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_dependencies(mocker):
    """Substitui dependências externas usando pytest-mock."""
    # O LlamaIndex importa schemas que iteram sobre objetos mockados. 
    # Usar unittest.mock.MagicMock lida com operações mágicas (__iter__, etc) corretamente.
    mock_modules = {
        'chromadb': MagicMock(),
        'llama_index': MagicMock(),
        'llama_index.core': MagicMock(),
        'llama_index.core.schema': MagicMock(),
        'llama_index.core.node_parser': MagicMock(),
        'llama_index.vector_stores.chroma': MagicMock(),
        'config': MagicMock(),
        'history': MagicMock(),
        'diff': MagicMock(),
        'interactive': MagicMock(),
        'hash_utils': MagicMock(),
        'cleanup': MagicMock(),
    }
    
    mocker.patch.dict(sys.modules, mock_modules)

class MockDocument:
    def __init__(self, text):
        self.text = text
        self.metadata = {}

def test_yaml_extraction_simple():
    """Testa se YAML simples é extraído e removido do texto."""
    from ingest import preprocess_document
    text = """---
title: Teste
date: 2026-02-17
---
Conteúdo real."""
    doc = MockDocument(text)
    preprocess_document(doc)
    
    assert doc.metadata.get('title') == 'Teste'
    assert str(doc.metadata.get('date')) == '2026-02-17'
    assert doc.text.strip() == 'Conteúdo real.'

def test_yaml_list_metadata_flattening():
    """Testa se listas no YAML são convertidas para string."""
    from ingest import preprocess_document
    text = """---
tags: [tag1, tag2, tag3]
categories:
  - cat1
  - cat2
---
Conteúdo."""
    doc = MockDocument(text)
    preprocess_document(doc)
    
    tags = doc.metadata.get('tags')
    assert isinstance(tags, str), f"Tags deveria ser string, mas é {type(tags)}"
    assert tags == "tag1, tag2, tag3"
    
    categories = doc.metadata.get('categories')
    assert categories == "cat1, cat2"

def test_yaml_nested_metadata_flattening():
    """Testa conversão segura de dicts para json-string."""
    from ingest import preprocess_document
    import json
    text = """---
author:
  name: "User"
  email: "user@example.com"
---
Test."""
    doc = MockDocument(text)
    preprocess_document(doc)
    author = doc.metadata.get('author')
    assert isinstance(author, str)
    assert json.loads(author) == {"name": "User", "email": "user@example.com"}

def test_dataview_removal():
    """Testa remoção de blocos dataview e js."""
    from ingest import preprocess_document
    text = """Texto antes.
```dataview
list from "folder"
```
Texto depois.
```dataviewjs
dv.list(dv.pages())
```
Fim."""
    doc = MockDocument(text)
    preprocess_document(doc)
    
    assert "list from" not in doc.text
    assert "dv.list" not in doc.text
    assert "Texto antes." in doc.text
    assert "Texto depois." in doc.text

def test_noise_removal():
    """Testa remoção de ruído de navegação V2."""
    from ingest import preprocess_document
    text = """Conteúdo útil.

---
**Navegação:** [[Blog]] 🏠 | Old Blog
* [Share](#)
* [Facebook](url)
"""
    doc = MockDocument(text)
    preprocess_document(doc)
    
    assert "**Navegação:**" not in doc.text
    assert "[Share]" not in doc.text
    assert "[Facebook]" not in doc.text
    assert "Conteúdo útil." in doc.text
