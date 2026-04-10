with open("core/python_workers/sovereign_matrix.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """    code_map = {
        "IPCA": 433,
        "SELIC": 432,
        "IGPM": 189,
        "INPC": 188
    }"""
    
replacement = """    code_map = {
        "IPCA": 433,
        "SELIC": 432,
        "IGPM": 189,
        "INPC": 188,
        "ANP_OCORRENCIA": 1393,
        "ANP_PRODUCAO": 1393,
        "PETROLEO_SGS": 1393
    }"""

if target in content:
    content = content.replace(target, replacement)
    
    # Also update the error message if indicator doesn't exist
    target_error = 'Supported: IPCA, SELIC, IGPM, INPC"'
    replacement_error = 'Supported: IPCA, SELIC, IGPM, INPC, ANP_OCORRENCIA"'
    if target_error in content:
        content = content.replace(target_error, replacement_error)

    with open("core/python_workers/sovereign_matrix.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCH SUCCESS")
else:
    print("TARGET NOT FOUND IN SOVEREIGN MATRIX")
