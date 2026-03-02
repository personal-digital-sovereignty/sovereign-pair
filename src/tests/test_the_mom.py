import pytest
import os
import uuid
from src.core.the_mom import MarkdownParser

@pytest.fixture
def sample_markdown():
    return """---
title: Projeto Sovereign
type: architecture
tags: [ai, local-first]
---

# Sensus Vault Planning

Este é um documento de teste para validar a "Mãe", nosso parser O(1).
Tudo aqui deve ser capturado no regex sem acionar a LLM!

## Lista de Afazeres
- [ ] Construir a Mãe (The Mom)
- [x] Terminar a Fase 15 do Docker
- [ ] Testar os links bidirecionais

## Conexões
Acho interessante olhar o documento principal do [[Synesis Core]] e também o de [[Interface Vision]].

## Tags aleatórias
Isto é um teste de #tag_parsing e vamos ver se o #SovereignPair capta.

"""

def test_markdown_parser_extracts_frontmatter(sample_markdown):
    doc = MarkdownParser.parse_content(sample_markdown, "dummy_path.md", "tenant-1")
    
    assert doc.frontmatter is not None
    assert doc.frontmatter.get("title") == "Projeto Sovereign"
    assert doc.frontmatter.get("type") == "architecture"
    assert "local-first" in doc.frontmatter.get("tags", [])

def test_markdown_parser_extracts_todos(sample_markdown):
    doc = MarkdownParser.parse_content(sample_markdown, "dummy_path.md", "tenant-1")
    
    todos = doc.extracted_todos
    assert len(todos) == 3
    assert "[ ] Construir a Mãe (The Mom)" in todos
    assert "[x] Terminar a Fase 15 do Docker" in todos
    assert "[ ] Testar os links bidirecionais" in todos

def test_markdown_parser_extracts_links(sample_markdown):
    doc = MarkdownParser.parse_content(sample_markdown, "dummy_path.md", "tenant-1")
    
    links = doc.extracted_links
    assert len(links) == 2
    assert "Synesis Core" in links
    assert "Interface Vision" in links

def test_markdown_parser_extracts_tags(sample_markdown):
    doc = MarkdownParser.parse_content(sample_markdown, "dummy_path.md", "tenant-1")
    
    tags = doc.extracted_tags
    assert len(tags) == 2
    assert "tag_parsing" in tags
    assert "SovereignPair" in tags

def test_markdown_parser_no_false_positives_inside_yaml():
    md = """---
description: This is a test #not_a_tag
todos:
  - "[ ] not_a_real_todo"
target: "[[not_a_link]]"
---
# Content
- [x] Real task
"""
    doc = MarkdownParser.parse_content(md, "dummy_path.md", "tenant-1")
    
    assert len(doc.extracted_tags) == 0
    assert len(doc.extracted_links) == 0
    assert len(doc.extracted_todos) == 1
    assert doc.extracted_todos[0] == "[x] Real task"
