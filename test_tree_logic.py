import os

def test_build_tree(root_dir):
    def build_tree(current_path: str, name: str = "Root") -> dict:
        node = {"name": name, "type": "dir", "path": current_path, "children": []}
        try:
            with os.scandir(current_path) as it:
                entries = sorted(list(it), key=lambda e: (not e.is_dir(), e.name.lower()))
                
            for entry in entries:
                if entry.name.startswith("."): 
                    continue
                    
                if entry.is_dir():
                    child = build_tree(entry.path, entry.name)
                    if child:
                        node["children"].append(child)
                elif entry.is_file() and entry.name.endswith(".md"):
                    file_node = {
                        "name": entry.name,
                        "type": "file",
                        "path": entry.path,
                        "has_vector": False
                    }
                    node["children"].append(file_node)
        except OSError as e:
            # print(f"Permission denied for {current_path}: {e}")
            pass
            
        return node
    return build_tree(root_dir, os.path.basename(root_dir))

# Testar a pasta do Workspace do user 
path = "/home/jefersonlopes/Developer/local-repositories/sovereign-pair"
tree = test_build_tree(path)
import json
print(json.dumps(tree, indent=2)[:1000]) # Imprime só o top level pra ver se ta vindo algo
