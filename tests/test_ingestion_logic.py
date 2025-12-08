
import unittest
import yaml
from unittest.mock import MagicMock
import sys
import os

# Adicionar src ao path para importar ingest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mockar imports que não estão disponíveis no ambiente de teste ou não são o foco
sys.modules['chromadb'] = MagicMock()
sys.modules['llama_index'] = MagicMock()
sys.modules['llama_index.core'] = MagicMock()
sys.modules['llama_index.vector_stores.chroma'] = MagicMock()
sys.modules['config'] = MagicMock()
sys.modules['history'] = MagicMock()
sys.modules['diff'] = MagicMock()
sys.modules['interactive'] = MagicMock()
sys.modules['hash_utils'] = MagicMock()
sys.modules['cleanup'] = MagicMock()

from ingest import preprocess_document

class MockDocument:
    def __init__(self, text):
        self.text = text
        self.metadata = {}

class TestIngestionLogic(unittest.TestCase):
    
    def test_yaml_extraction_simple(self):
        """Testa se YAML simples é extraído e removido do texto."""
        text = """---
title: Teste
date: 2026-02-17
---
Conteúdo real."""
        doc = MockDocument(text)
        preprocess_document(doc)
        
        self.assertEqual(doc.metadata.get('title'), 'Teste')
        self.assertEqual(str(doc.metadata.get('date')), '2026-02-17') # Date pode ser parsed como obj
        self.assertEqual(doc.text.strip(), 'Conteúdo real.')

    def test_yaml_list_metadata_flattening(self):
        """Testa se listas no YAML são convertidas para string (correção do bug)."""
        text = """---
tags: [tag1, tag2, tag3]
categories:
  - cat1
  - cat2
---
Conteúdo."""
        doc = MockDocument(text)
        preprocess_document(doc)
        
        # O BUG ATUAL: isso provavelmente vai falhar ou passar dependendo da minha implementação.
        # Mas para o ChromaDB, deve ser string.
        # Vamos verificar o que o preprocess_document faz. Atualmente ele NÃO trata isso.
        # O teste deve falhar ou mostrar que é lista, confirmando o problema.
        
        tags = doc.metadata.get('tags')
        
        # A correção esperada é que seja uma string "tag1, tag2, tag3"
        # Se for lista, o teste de unidade em si passa, mas a integração com Chroma falha.
        # Vou afirmar que DEVE ser string para forçar a correção.
        self.assertIsInstance(tags, str, f"Tags deveria ser string, mas é {type(tags)}")
        self.assertEqual(tags, "tag1, tag2, tag3")

    def test_dataview_removal(self):
        """Testa remoção de blocos dataview."""
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
        
        self.assertNotIn("list from", doc.text, "Bloco dataview deve ser removido")
        self.assertNotIn("dv.list", doc.text, "Bloco dataviewjs deve ser removido")
        self.assertTrue("Texto antes." in doc.text)
        self.assertTrue("Texto depois." in doc.text)

    def test_noise_removal(self):
        """Testa remoção de ruído de navegação V2."""
        text = """Conteúdo útil.

---
**Navegação:** [[Blog]] 🏠 | Old Blog
* [Share](#)
* [Facebook](url)
"""
        doc = MockDocument(text)
        preprocess_document(doc)
        
        self.assertNotIn("**Navegação:**", doc.text)
        self.assertNotIn("[Share]", doc.text)
        self.assertNotIn("[Facebook]", doc.text)
        self.assertTrue("Conteúdo útil." in doc.text)

if __name__ == '__main__':
    unittest.main()
