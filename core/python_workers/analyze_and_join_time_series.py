#!/usr/bin/env python3
import sys
import json
import re
import datetime

try:
    import pandas as pd
except ImportError:
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pandas"])
        import pandas as pd
    except:
        print(json.dumps({"error": "Failed to install required pandas package"}))
        sys.exit(1)

def parse_markdown_blocks(raw_blocks):
    """
    Parses multiple raw strings formatted as:
    [CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO MACRO INDICADOR IPCA]
    2024-01-01 | 0.42
    2024-02-01 | 0.83
    """
    datasets = {}
    
    # regex for getting table headers
    header_regex = re.compile(r'\[CONTEXT: DADOS HISTÓRICOS BRUTOS REFERENTES AO.*?([A-Z0-9_\-\.\=\ ]+)\]')
    # regex for generic date string and numbers  "2024-01 | USD 75.3 | BRL 350.2" or "2024-01-10 | 0.5"
    row_regex = re.compile(r'^(\d{4}-\d{2}(?:-\d{2})?)\s*\|\s*(.*)$')
    
    for block in raw_blocks:
        current_ds_name = "UNKNOWN"
        lines = block.split('\n')
        
        # Encontrar o nome do dataset no header
        for line in lines:
            h_match = header_regex.search(line)
            if h_match:
                current_ds_name = h_match.group(1).strip()
                break
                
        # Se for UNKNOWN tenta inferir por heurística simples
        if current_ds_name == "UNKNOWN":
            if "PETROLEO" in block.upper() or "BRENT" in block.upper(): current_ds_name = "BRENT"
            elif "IPCA" in block.upper(): current_ds_name = "IPCA"
            elif "GASOLINA" in block.upper(): current_ds_name = "GASOLINA"
            else: current_ds_name = f"DATASET_{len(datasets)}"

        if current_ds_name in datasets:
            current_ds_name = f"{current_ds_name}_{len(datasets)}"
            
        data = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('['):
                continue
                
            r_match = row_regex.search(line)
            if r_match:
                date_str = r_match.group(1)
                vals_raw = r_match.group(2)
                
                # Extract first floating point found:
                # "USD 70.3 | BRL 300.5" -> get 70.3 as primary
                # We can try to extract all numbers, but let's take the first one or specifically map it.
                numbers = re.findall(r'-?\d+\.\d+|-?\d+', vals_raw)
                if numbers:
                    if 'USD' in vals_raw and 'BRL' in vals_raw and len(numbers) >= 2:
                        # Extract both explicit values directly from string
                        usd_val = float(numbers[0])
                        brl_val = float(numbers[1])
                        
                        # Only provide Cambio if USD is non-zero to avoid division by zero
                        if usd_val > 0.0:
                            cambio = round(brl_val / usd_val, 2)
                            data.append({'Date': date_str, f"{current_ds_name}_USD": usd_val, f"{current_ds_name}_BRL": brl_val, "Taxa_Cambio": cambio})
                        else:
                            data.append({'Date': date_str, f"{current_ds_name}_USD": usd_val, f"{current_ds_name}_BRL": brl_val})
                    else:
                        # Single asset fallback
                        val = float(numbers[-1]) if 'BRL' in vals_raw else float(numbers[0])
                        data.append({'Date': date_str, current_ds_name: val})
                    
        if data:
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            df.set_index('Date', inplace=True)
            # Resample to monthly end ('ME' or 'M') to normalize Daily vs Monthly
            df = df.resample('ME').mean()
            datasets[current_ds_name] = df
            
    return datasets

def join_and_extract(raw_data_blocks):
    datasets_dict = parse_markdown_blocks(raw_data_blocks)
    
    if len(datasets_dict) == 0:
        return json.dumps({"error": "No temporal datasets found to join."})
        
    dfs = list(datasets_dict.values())
    
    if len(dfs) == 1:
        # Nothing to join
        final_df = dfs[0]
        matrix_str = final_df.to_markdown()
        output = f"> [!TIP]\n> **Matrix Engine**: Apenas um dataset identificado. Dados formatados nativamente.\n\n{matrix_str}"
        return json.dumps({"status": "success", "markdown": output})
        
    from functools import reduce
    # Outer join all datasets by Date
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), dfs)
    
    # Sort chronological
    merged_df.sort_index(inplace=True)
    
    # Create the pearson correlation 
    corr_matrix = merged_df.corr(method='pearson').round(3)
    
    # -----------------------------
    # EPISTEMIC RULES
    # -----------------------------
    # 1. Forward Fill (ffill) safely allows last known prices/indicators to flow down to missing edges.
    merged_df.ffill(inplace=True)
    
    # Pre-calculate Annual Averages before changing index to strings
    try:
        annual_df = merged_df.resample('YE').mean()
        annual_df.index = annual_df.index.strftime('%Y')
        annual_md = annual_df.round(2).to_markdown()
    except Exception:
        annual_md = "N/A"
    
    # 2. Format the index to YYYY-MM
    merged_df.index = merged_df.index.strftime('%Y-%m')
    
    # 3. Any remaining NaNs (usually at start) become "N/A - PENDENTE"
    merged_df.fillna("N/A - PENDENTE", inplace=True)
    
    # Prepare Markdown Output
    table_md = merged_df.round(2).to_markdown()
    corr_md = corr_matrix.to_markdown()
    
    alert_box = (
        "> [!NOTE]\n"
        "> **Sovereign Symbiotic Pipeline**: Múltiplas séries temporais detectadas e fundidas nativamente pelo Backend.\n"
        "> Preenchimento automático `ffill()` aplicado para alinhar assimetrias de extração (Diário vs Mensal).\n\n"
        "### Matriz de Correlação de Pearson ($r$)\n"
        f"{corr_md}\n\n"
        "### Médias Anuais Consolidadas\n"
        f"{annual_md}\n\n"
        "### Time-Series Consolidada\n"
        f"{table_md}"
    )
    
    return json.dumps({"status": "success", "markdown": alert_box})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Pode estar mandando por Stdin JSON (Ex: Tool call arguments)
        try:
            input_data = sys.stdin.read()
            payload = json.loads(input_data)
            blocks = payload.get("raw_data_blocks", [])
            print(join_and_extract(blocks))
        except Exception as e:
            print(json.dumps({"error": f"Invalid input format: {e}"}))
    else:
        # Modos CLI de teste
        mode = sys.argv[1].lower()
        print(json.dumps({"error": f"Modo nao suportado via argumentos. Use stdin json com raw_data_blocks."}))
