# Sovereign Ephemeral Knowledge Engine

## Visão Geral (v1.2.3)

O módulo **Sovereign Ephemeral Knowledge** foi projetado para contornar a maior fraqueza dos RAGs modernos na área de investimentos e geolocalização temporal: o Envenenamento de Viés do Contexto (Context Bias Poisoning). 

Enquanto a **Memória Rígida (O Vault)** indexa informações atemporais e estruturais do usuário (Leis, Regras de Negócios, Scripts), o mundo real flutua. O modelo ingere Notícias Econômicas, Decisões do Copom, Índices Mensais que devem sobreviver na memória da IA apenas enquanto geram repercussão de mercado. Se uma notícia de 3 anos atrás for buscada hoje e emparelhada num prompt, o modelo alucinará tendências passadas.

Para contornar esse problema, criamos a via Efêmera e Transiente com *Garbage Collector* Nativo de Tokens.

---

## 1. Módulo Ephemeral Core (`sqlite-vec`)
Separamos fisicamente as tabelas do `sqlite-vec`. Documentos vitais repousam no `sensus_documents` e `sovereign_chunks`. 
Notícias, links do HackerNews, scrapes gerais em publicações governamentais massivas (acima de 2 mil caracteres que estourariam o Prompt de Prefill), são jogadas no namespace Ephemeral (`ephemeral_knowledge`).

### Estrutura de Metadados Matemáticos (Anticontradição Cronológica)
Todo chunk (vetor) efêmero carrega intrínsecamente carimbos JSON no campo metadata:
- `source`: URL da raspagem (Permite auditoria Reversa)
- `ingested_at`: UTC da Leitura
- `expires_at`: `datetime('now', '+30 days')`

Isso permite que o 'Scribe' faça comparações factuais utilizando a seta do tempo a seu favor.

## 2. A Malha do Extrator Cíbrido (`api_trainer.rs`)
Durante a rotina de Deep Research, quando as `tools` encontram blocos grandes, ocorre uma interrupção. Em vez do texto ser colado linearmente na resposta JSON (que o Scribe formataria brutalmente como Markdown):
1. O texto sofre *Chunking* semântico.
2. Cada bloco pede vetorização remota à instância do Ollama (`nomic-embed-text`).
3. Retorna o array de floats [1024] em `std::mem::transmute<[f32], [u8]>` e repousa no `sqlite-vec`.

## 3. O Ceifeiro Automático / Garbage Collector (`garbage_collector.rs`)
Uma esteira contínua assíncrona baseada em loop `tokio` desperta a cada hora `Sleep(3600)`.
Sua única diretriz O.S: Destruir (`DELETE CASCADE`) da existência memórias semânticas vetoriais cujo timestamp `expires_at` tenha vencido. Mantendo a mente do Matrix enxuta, barata e ágil para análises de janelas móveis de alta velocidade.

---

## The Scribe & Sycophancy Breaker (Epistemic Sabbatine Loop)
Com a retirada forçada dos pesos de tabela (Pandas) nas costas do Mestre Lógico e do Scribe de Finalização, introduziu-se a rotina "Sabatina do Mestre".

Em caso de alucinação detectada, o motor não sofre pane (*hard crash*), ele reescreve a resposta sob ordem destrutiva ('Comendo o toco'):
**Tentativas Permitidas:** 1 (v1.2.4). O Mestre Auditor (`temperature: 0.0`, `num_predict: 512`, `num_ctx: 8192`) inspeciona o output verificando exatidão estrita. Caso reprovar, o relatório é **preservado integralmente** com banners de alerta `> [!WARNING]` embutidos no corpo do artefato, permitindo análise humana e iteração de prompts. **Nenhum conteúdo é destruído.**

> **NOTA ARQUITETURAL (v1.2.4 — Epistemic Guard v2):**
> A verificação de proveniência SHA-256 **não depende mais do LLM**. O Motor Rust re-hasheia os arquivos físicos em `/tmp/sovereign/` em tempo real e compara deterministicamente com os checksums originais gravados durante a extração. Isso elimina o falso positivo estrutural onde SLMs (3-8B) eram incapazes de reproduzir strings hexadecimais de 64 caracteres.

Este pipeline representa o avanço final para a versão Produtiva v1.2.4.

