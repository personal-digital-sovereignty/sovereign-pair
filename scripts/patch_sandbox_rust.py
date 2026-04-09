import re

with open("core/src/sandbox.rs", "r", encoding="utf-8") as f:
    content = f.read()

target = r"""    let output = Command::new\(&python_bin\)\s*\n\s*\.arg\(&script_path\)\s*\n\s*\.current_dir\(&temp_dir\)\s*\n\s*\.output\(\);"""

replacement = """    // AST Jail Injection (Epic 9)
    let jail_script = env::current_dir().unwrap_or_else(|_| PathBuf::from(".")).join("core/python_workers/ast_jail.py");
    
    let output = if jail_script.exists() {
        Command::new(&python_bin)
            .arg(&jail_script)
            .arg(&script_path)
            .current_dir(&temp_dir)
            .output()
    } else {
        // Fallback or panic
        Command::new(&python_bin)
            .arg(&script_path)
            .current_dir(&temp_dir)
            .output()
    };"""

new_content = re.sub(target, replacement, content)

if content != new_content:
    with open("core/src/sandbox.rs", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SANDBOX PATCH SUCCESS")
else:
    print("TARGET NOT FOUND IN SANDBOX.RS")
