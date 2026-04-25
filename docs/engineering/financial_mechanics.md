# Índices Cambiais: DOLAR (BRL=X) vs DOLAR_PTAX (SGS 10813)

> **Documento de Referência Interna — Sovereign Research Engine**
> Classificação: Epistêmico / Fundamentos Financeiros
> Aplicável: Symbiotic Pipeline, Scribe System Prompt, Análises Macroeconômicas

---

## 1. Por que existem dois "dólares"?

O mercado cambial brasileiro opera em camadas. O que chamamos informalmente de "cotação do dólar" é, na verdade, um **ecossistema de preços** com naturezas fundamentalmente diferentes:

| Índice | Fonte | Nome Oficial | Natureza |
|---|---|---|---|
| **BRL=X** | Yahoo Finance (Interbank Spot) | Dólar Spot Interbancário | **Expectativa** — inclui prêmio de risco, forward premium, especulação de traders |
| **PTAX** | BCB SGS 10813 | Taxa PTAX Venda Média Ponderada | **Fato consumado** — média ponderada de transações REAIS reportadas por dealers autorizados |

---

## 2. O que cada um representa EXATAMENTE

### BRL=X (Yahoo Finance / Interbank Spot)

- **O que é:** Taxa de câmbio spot do mercado interbancário, atualizada em tempo real durante o pregão
- **Quem define:** Oferta e demanda entre bancos, corretoras, fundos de investimento
- **Inclui:**
  - Prêmio de risco-país (CDS Brasil)
  - Expectativas de juros futuros (diferencial Fed vs Selic)
  - Fluxos de hedge de exportadores/importadores
  - Especulação pura de traders
- **Quando usar:** Análise de **tendência de mercado**, volatilidade, correlação com ativos internacionais, movimentos de bolsa (PETR4, VALE3)
- **Analogia:** É o "termômetro" — mede temperatura, mas também reage à ansiedade do paciente

### PTAX (BCB SGS 10813)

- **O que é:** Média ponderada por volume das transações cambiais efetivamente liquidadas, calculada pelo Banco Central em 4 janelas diárias (abertura, 10h, 11h, 12h)
- **Quem define:** Banco Central, com base nos fechamentos REAIS reportados por dealers
- **Inclui:**
  - **Apenas transações concretizadas** — dinheiro que efetivamente trocou de mãos
  - Sem prêmio de risco especulativo
  - Sem expectativa futura
- **Quando usar:**
  - **Cálculos fiscais** (impostos sobre importação de combustíveis)
  - **PPI da Petrobras** (Preço de Paridade de Importação usa PTAX)
  - **Liquidação de contratos** de câmbio e dívida externa
  - **Deflação de séries** de comércio exterior pelo IBGE
  - **Qualquer análise que impacte o bolso do consumidor final**
- **Analogia:** É o "exame de sangue" — mostra o que realmente está no organismo, não o que o paciente sente

---

## 3. A Regra de Ouro

> **"Dá-se por real o fechamento pago, não a promessa."**

Quando a análise é sobre **impacto ao consumidor** (gasolina, inflação, custo de vida), o PTAX é o índice correto porque:

1. A Petrobras calcula o PPI usando PTAX, não BRL=X
2. A Receita Federal cobra ICMS e PIS/COFINS de importação usando PTAX
3. O IBGE deflaciona séries de custo de vida usando câmbio oficial (PTAX)

O BRL=X pode estar 2-5% acima do PTAX em momentos de estresse — essa diferença é o **prêmio de risco**, que é dinheiro que o especulador cobra mas que não entra na composição real do preço do combustível.

---

## 4. Quando manter ambas as colunas

A coexistência de DOLAR_PTAX e DOLAR_SPOT (BRL=X) na mesma tabela é **desejável** quando:

1. **A divergência entre ambos revela o prêmio de risco futuro** — se DOLAR_SPOT > PTAX consistentemente, o mercado está precificando instabilidade
2. **Permite calcular o "custo da especulação"** — quanto do preço final do combustível é inflado por expectativas de risco vs custo real
3. **Audita a formulação de preços da Petrobras** — se o preço na bomba segue PTAX (correto) ou BRL=X (sobrepreço)

### Cálculo Didático

```
BRENT em BRL (institucional) = BRENT_USD × PTAX_Venda
BRENT em BRL (mercado)       = BRENT_USD × BRL=X

Diferença = prêmio de risco embutido no câmbio
```

Se a diferença for consistentemente >3%, sugere que ou:
- O mercado está em modo de pânico (risco ≠ realidade)
- Ou o governo está usando o PTAX para "segurar" artificialmente o câmbio oficial

---

## 5. Prompt de Referência para o LLM (Scribe / Mestre)

O prompt abaixo pode ser injetado no system prompt do Scribe para que ele entenda a nuance ao redigir análises:

```
[REFERÊNCIA CAMBIAL SOBERANA]
O dataset contém dois índices de câmbio com naturezas DISTINTAS:

• DOLAR_PTAX (BCB SGS 10813): Taxa oficial de LIQUIDAÇÃO — média ponderada de
  transações REAIS reportadas ao Banco Central. Este é o câmbio que governa
  impostos, PPI da Petrobras, e preço final ao consumidor. USAR COMO BASE
  para qualquer análise de impacto ao bolso do cidadão.

• DOLAR_CAMBIO (BRL=X Yahoo): Taxa SPOT interbancária — inclui prêmio de risco,
  forward premium e especulação. USAR para análise de tendência de mercado,
  correlação com ativos e volatilidade.

REGRA: Quando a análise envolver "quanto o consumidor paga", referencie PTAX.
       Quando envolver "para onde o mercado está indo", referencie BRL=X.
       A DIVERGÊNCIA entre ambos é um indicador valioso: revela o prêmio de risco
       (custo da incerteza) que o mercado cobra mas que não entra na fórmula
       oficial de precificação.
```

---

## 6. Implicações para o Symbiotic Pipeline

### Decisão Arquitetural (v1.2.4)

O `analyze_and_join_time_series.py` deve:

1. **Manter DOLAR_PTAX quando existir** — é o índice primário para análises de consumidor
2. **Manter DOLAR_CAMBIO (BRL=X) quando existir** — é complementar para análise de mercado
3. **NÃO fazer dedup automático** entre PTAX e CAMBIO — são índices diferentes com aplicações diferentes
4. **Calcular BRENT_BRL usando PTAX** quando ambos existem (institucional > especulativo)
5. Se apenas um estiver disponível, usar o que tiver e indicar a limitação

### Taxa_Cambio (derivada do BRENT)

A coluna `Taxa_Cambio` gerada automaticamente pela divisão `BRL ÷ USD` dentro do ticker BRENT do Yahoo é uma **terceira medida** — é o câmbio implícito no preço do commodity naquele momento. Geralmente está entre PTAX e BRL=X. Pode ser descartada quando PTAX estiver presente, pois é derivada e não oficial.

---

## Referências

- **BCB SGS 10813:** [https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados](https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados)
- **Metodologia PTAX:** [https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes](https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes)
- **PPI Petrobras:** Fórmula usa PTAX D-1 para conversão BRL do Brent ICE
- **Incidente-raiz:** Análise do artefato `bf95d800` (15/04/2026) onde a tabela continha apenas BRENT e DOLAR sem diferenciação PTAX vs Spot
