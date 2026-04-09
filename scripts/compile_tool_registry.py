import os
import ast
import json
import re

def parse_docstring(docstring):
    lines = docstring.strip().split('\n')
    desc_lines = []
    params = {}
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        param_match = re.match(r':param\s+(\w+):\s*(.*)', line)
        if param_match:
            params[param_match.group(1)] = param_match.group(2)
        elif line.startswith('@agent_tool'):
            continue
        elif not line.startswith(':'):
            desc_lines.append(line)
            
    return " ".join(desc_lines), params

def main():
    workers_dir = "core/python_workers"
    output_file = "core/python_workers/registry.json"
    
    # Static Rust Tools (Native)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "dispatch_sub_researcher",
                "description": "Ferramenta para buscar fatos e dados na internet em tempo real. Deve receber múltiplas consultas curtas e atômicas (Google Dorks) de uma vez.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_queries": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Array OBRIGATÓRIO contendo as buscas. Cada string (Dork) deve ser curta, contendo APENAS as palavras-chave vitais. Se a diretriz for complexa cruzando vários tópicos, quebre-a em buscas atômicas."
                        }
                    },
                    "required": ["search_queries"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dispatch_visual_artist",
                "description": "Ferramenta para desenhar ilustrações, criar quadros ou arte visual (Text-to-Image) quando o usuário pedir para 'desenhar', 'criar imagem' ou gerar arte.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "O prompt cinematográfico MÁXIMAMENTE DETALHADO EM INGLÊS descrevendo a cena visual desejada para o Stable Diffusion."
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_api_directory",
                "description": "Busca no banco de dados do Sovereign API Gateway por APIs livres, públicas e abertas para consumo (JSON) baseadas num tópico ou palavra-chave (ex: 'crypto', 'weather', 'finance'). Use para evitar o Web Scraper genérico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "O tema da API em Inglês. Exemplo: 'currency', 'news'."
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_json_endpoint",
                "description": "Dispara uma requisição HTTP GET real para a base da API e retorna os dados brutos (JSON) para que você sintetize a resposta sem precisar de Scraping HTML sujo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "A URL EXATA para chamar, obrigatoriamente montada baseada na Base URL descoberta via directory."
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python_code",
                "description": "Ferramenta para executar código Python seguro localmente. Ideal para matemática complexa, cruzamento de dados de inflação/preços, cálculos precisos, e extração manipulada de arrays. Você DEVE imprimir os resultados finais EXPLICITAMENTE (via print()) para conseguir ler a resposta e utiliza-la para redigir seu relatório.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "O script Python completo a ser executado."
                        }
                    },
                    "required": ["code"]
                }
            }
        }
    ]
    
    # Inject Sovereign Matrix natively since we are keeping its file structure as is
    tools.append({
        "type": "function",
        "function": {
            "name": "fetch_financial_ticker",
            "description": "Acessa a Sovereign Open-Data Matrix (yfinance) para baixar diretamente dados históricos fechados de Ações, Petróleo, Ouro ou Câmbio. USE SEMPRE ESTA FERRAMENTA PARA COMMODITIES, AÇÕES OU PREÇO DO DÓLAR EM VEZ DO SCRAPER WEB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "O símbolo financeiro. Exemplo: 'BRENT' (Petróleo Brent), 'WTI' (Petróleo Texas), 'DOLAR' (Dólar/BRL), 'PETROBRAS' (Ações)."
                    },
                    "years": {
                        "type": "string",
                        "description": "A quantidade de anos de histórico necessários. Exemplo: '5'."
                    }
                },
                "required": ["symbol", "years"]
            }
        }
    })
    
    tools.append({
        "type": "function",
        "function": {
            "name": "fetch_macroeconomy",
            "description": "Acessa a Sovereign Open-Data Matrix (Banco Central API) para baixar taxas macroeconômicas oficiais de um país, como Inflação, Selic, IGPM. USE SEMPRE ESTA FERRAMENTA PARA DADOS ECONÔMICOS DE INFLAÇÃO E JUROS EM VEZ DO SCRAPER WEB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "indicator": {
                        "type": "string",
                        "description": "O indicador (ex: 'IPCA', 'SELIC', 'IGPM', 'INPC')."
                    },
                    "country": {
                        "type": "string",
                        "description": "O código do país (ex: 'BR'). Atualmente focado em 'BR'."
                    },
                    "years": {
                        "type": "string",
                        "description": "A quantidade de anos de histórico necessários. Exemplo: '5'."
                    }
                },
                "required": ["indicator", "country", "years"]
            }
        }
    })

    # Scan python files for reflexive nodes
    if os.path.exists(workers_dir):
        for fname in os.listdir(workers_dir):
            if fname.endswith(".py") and fname != "sovereign_matrix.py":
                fpath = os.path.join(workers_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            if docstring and '@agent_tool' in docstring:
                                desc, params_desc = parse_docstring(docstring)
                                
                                props = {}
                                req = []
                                for arg in node.args.args:
                                    arg_name = arg.arg
                                    if arg_name == 'self': continue
                                    props[arg_name] = {
                                        "type": "string",
                                        "description": params_desc.get(arg_name, f"O parâmetro {arg_name}.")
                                    }
                                    req.append(arg_name)
                                    
                                tool_node = {
                                    "type": "function",
                                    "function": {
                                        "name": fname[:-3], # tool name is strictly the file name for Universal Dispatcher
                                        "description": desc,
                                        "parameters": {
                                            "type": "object",
                                            "properties": props,
                                            "required": req
                                        }
                                    }
                                }
                                tools.append(tool_node)
                                print(f"[\033[32m+\033[0m] Reflexive Regexed Tool: {fname[:-3]}")
                except Exception as e:
                    print(f"Erro ao parsear {fname}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=4, ensure_ascii=False)
        
    print(f"[\033[34m*\033[0m] Registry compilado com {len(tools)} schemas dinâmicos em '{output_file}'.")

if __name__ == "__main__":
    main()
