with open("scripts/compile_tool_registry.py", "r", encoding="utf-8") as f:
    content = f.read()

target1 = "Inflação, Selic, IGPM. USE SEMPRE ESTA FERRAMENTA PARA DADOS ECONÔMICOS DE INFLAÇÃO E JUROS"
target2 = "ex: 'IPCA', 'SELIC', 'IGPM', 'INPC'"

if target1 in content and target2 in content:
    content = content.replace(target1, "Inflação, Selic, IGPM, e Petróleo/ANP. USE SEMPRE ESTA FERRAMENTA PARA DADOS ECONÔMICOS, DE INFLAÇÃO, JUROS, OU OCORRÊNCIAS/PRODUÇÃO ANP (Agência Nacional do Petróleo)")
    content = content.replace(target2, "ex: 'IPCA', 'SELIC', 'IGPM', 'INPC', 'ANP_OCORRENCIA'")
    with open("scripts/compile_tool_registry.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("REGISTRY PATCH SUCCESS")
else:
    print("TARGETS NOT FOUND IN REGISTRY SCRIPT")
