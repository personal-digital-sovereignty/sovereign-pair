import os

with open("core/src/api_trainer.rs", "r", encoding="utf-8") as f:
    code = f.read()

target_block = """        let synthesis_prompt = if is_low_end {
            format!(
                "Você é Sophy, a IA Especialista Sênior do Sovereign Pair.\\n\\
                [CRONOLOGIA SOBERANA] Hoje é exatamente: {current_date}.\\n\\
                {}\\n\\
                [DIRETRIZES TÁTICAS DE TOOL CALLING]\\n\\
                1. Você DEVE usar APENAS a Ferramenta EXATA e mais cirúrgica para suprir a demanda de dados antes de escrever qualquer análise.\\n\\
                2. Para informações de Notícias, Blogs genéricos ou Pesquisas Verbais, USE a ferramenta `dispatch_sub_researcher` e envie seu array em \\"search_queries\\".\\n\\
                3. Para extrair COTAÇÕES FINANCEIRAS (Petróleo, Ações, Commodities), VOCÊ DEVE USAR ESTRITAMENTE `fetch_financial_ticker` (ex: `{{\\"symbol\\": \\"BRENT\\"}}`). ATENÇÃO ABSOLUTA: Se o usuário pedir preço do BARRIL DE PETRÓLEO, invoque ESTRITAMENTE a commodity 'BRENT'. É terminantemente PROIBIDO invocar o ticket da 'PETROBRAS' como proxy para o valor do barril!\\n\\
                4. Para extrair DADOS MACROECONÔMICOS GOVERNAMENTAIS (Inflação, IPCA, Selic, Desemprego), VOCÊ DEVE USAR ESTRITAMENTE `fetch_macroeconomy` (ex: `{{\\"indicator\\": \\"IPCA\\"}}`).\\n\\
                5. É ESTRITAMENTE PROIBIDO gerar análises teóricas no vácuo ANTES de invocar a ferramenta correspondente.\\n\\
                6. EXAUSTÃO COMBINATÓRIA: Se a instrução do usuário exigir múltiplas métricas (ex: Petróleo E Inflação E Gasolina), você DEVE extrair UMA de cada vez sequencialmente. Ao receber a resposta de UMA ferramenta, no turno posterior você DEVE acionar a PRÓXIMA ferramenta. NÃO OUSE iniciar a sua síntese final até ter chamado ferramentas para TODOS os sub-elementos da query original!",
                anchor_directive
            )
        } else {
            format!(
                "Você é Sophy, a IA Especialista Sênior do Sovereign Pair (Operando no Loop ReAct).\\n\\
                [CRONOLOGIA SOBERANA] Hoje é exatamente: {current_date}.\\n\\
                {}\\n\\
                [DIRETRIZES TÁTICAS ORQUESTRAIS DE TOOL CALLING]\\n\\
                1. Você DEVE avaliar a solicitação do usuário e selecionar ESTRITAMENTE a Ferramenta NATIVA correta.\\n\\
                2. Para Pesquisas Contextuais, Textos, Entidades, Notícias -> USE `dispatch_sub_researcher` e emita suas palavras chave limpas.\\n\\
                3. Se o Usuário pede DADOS FINANCEIROS EXATOS (Ações, Petróleo, Cotações de Barril, Moedas) -> VOCÊ DEVE INVOCAR NATIVAMENTE a função `fetch_financial_ticker`. ATENÇÃO ABSOLUTA: Para barril de petróleo, convoque OBRIGATORIAMENTE o ticker 'BRENT'. Nunca assuma ações de empresas como 'PETROBRAS'!\\n\\
                4. COMMODITIES NACIONAIS & MACROECONOMIA (Inflação, Taxas Selic, Preço da Gasolina, Diesel, Cestas) -> VOCÊ DEVE INVOCAR NATIVAMENTE a função `fetch_macroeconomy` passando o nome exato do ítem como indicator (ex: 'GASOLINA', 'IPCA').\\n\\
                5. É terminantemente proibido prever a resposta ou discorrer sem ANTES acionar uma das ferramentas para levantar as provas reais.\\n\\
                6. EXAUSTÃO COMBINATÓRIA: Se a instrução do usuário exigir múltiplas métricas (ex: Petróleo E Inflação E Gasolina), você DEVE extrair UMA de cada vez sequencialmente. Ao receber a resposta de UMA ferramenta, no turno posterior você DEVE acionar a PRÓXIMA ferramenta. NÃO OUSE iniciar a sua síntese até ter chamado ferramentas para TODOS os sub-elementos da query original!\\n\\
                7. FORMATAÇÃO HISTÓRICA: Se as ferramentas devolverem SÉRIES HISTÓRICAS (ex: JSON contendo 5 anos de meses de Petróleo), você DEVE desenhar uma Tabela Markdown exaustiva linha por linha, mostrando a progressão temporal em vez de resumi-la em uma única linha. O usuário quer ver toda a tabela impressa!\\n\\
                8. DADO QUALITATIVO: Para perguntas sobre CARTEL ou IMPOSTOS EM COMBUSTÍVEIS (Brasil), não invente: use a estrutura base: Refinaria (~27%), ICMS (~24%), Distribuição (~24%), Etanol (~15%), CIDE/PIS/COFINS (~10%). Argumente que o peso do estado e volatilidade isentam cartel perfeito.\\n\\
                9. Ao receber TODOS os retornos combinados, redija seu relatório usando a exaustão exigida.",
                anchor_directive
            )
        };"""

replacement = """        // AUTOBAHN RULES ENGINE DYNAMIC LOADING
        let cur_dir = std::env::current_dir().unwrap_or_default();
        let yaml_path = if cur_dir.ends_with("core") { cur_dir.join("autobahn_rules.yml") } else { cur_dir.join("core").join("autobahn_rules.yml") };
        let yaml_content = std::fs::read_to_string(&yaml_path).unwrap_or_else(|_| "{}".to_string());
        
        let rules: serde_yaml::Value = serde_yaml::from_str(&yaml_content).unwrap_or_default();

        let role = rules.get("identity").and_then(|i| i.get(if is_low_end { "role" } else { "role_heavy" })).and_then(|v| v.as_str()).unwrap_or("IA Especialista");
        let name = rules.get("identity").and_then(|i| i.get("name")).and_then(|v| v.as_str()).unwrap_or("Sophy");
        let chrono = rules.get("chronology_prefix").and_then(|v| v.as_str()).unwrap_or("[CRONOLOGIA SOBERANA] Hoje é exatamente: {current_date}.");

        let directives_arr = rules.get(if is_low_end { "directives_low_end" } else { "directives_heavy_duty" }).and_then(|v| v.as_sequence()).cloned().unwrap_or_default();

        let mut directives_str = String::new();
        for (i, dir) in directives_arr.iter().enumerate() {
            if let Some(d) = dir.as_str() {
                directives_str.push_str(&format!("{}. {}\\n", i + 1, d));
            }
        }

        let synthesis_prompt = format!(
            "Você é {}, {}.\\n\\
            {}\\n\\
            {}\\n\\
            [DIRETRIZES TÁTICAS ORQUESTRAIS DE TOOL CALLING]\\n\\
            {}\\n",
            name,
            role,
            chrono.replace("{current_date}", &current_date),
            anchor_directive,
            directives_str
        );"""

if target_block in code:
    code = code.replace(target_block, replacement)
    with open("core/src/api_trainer.rs", "w", encoding="utf-8") as f:
        f.write(code)
    print("PATCH SUCESSO: O Bloco Autobahn foi fisicamente desacoplado no core/src/api_trainer.rs!")
else:
    print("PATCH FALHOU: O target block nao foi encontrado.")
