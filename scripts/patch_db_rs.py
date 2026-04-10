import re

with open("core/src/db.rs", "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace everything from `// Garante que a Engine Settings` down to `// Seed Initial Trusted Sources`
# including the `ALTER TABLE` commands.
start_marker = "// Garante que a Engine Settings"
end_marker = "// Seed Initial Trusted Sources"

if start_marker in content and end_marker in content:
    start_idx = content.index(start_marker)
    end_idx = content.index(end_marker)
    
    replacement = """// CARREGAMENTO NATIVO DO SCHEMA MESTRE CIBRIDO (EPIC 4)
    let _ = sqlx::query(include_str!("schemas/001_sensus_init.sql")).execute(&pool).await;

    """
    
    new_content = content[:start_idx] + replacement + content[end_idx:]
    
    with open("core/src/db.rs", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("PATCH SUCESSO: db.rs limpo e isolado com schema.sql")
else:
    print("FALHA: markers nao encontrados.")
