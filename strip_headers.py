import os
import glob
import re

routes_dir = "svelte-ui/src/routes/engineer"
pages = glob.glob(f"{routes_dir}/**/+page.svelte", recursive=True)

for path in pages:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Regex para pegar o bloco de cabeçalho
    # Assumindo que tem <!-- Header Section --> até flex-1 ou algo similar
    pattern = r"(\s+<!-- Header Section -->.*?</header>)(?=\r?\n)"
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)
    
    # Ajustando o mb-10 que existia e a div .p-8 se der
    # Como não sabemos exatamente, a remoção da <header> já funciona se o Flex layout
    # assumir o espaço livre restante.
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Removed header from {path}")
