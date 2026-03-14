from src.api.database import SessionLocal
from src.api.models import SensusDocumentModel

def get_graph():
    db = SessionLocal()
    tenant_id = "Jeferson"
    docs = db.query(SensusDocumentModel).filter(SensusDocumentModel.tenant_id.in_(["default", tenant_id])).all()
    
    print(f"Total docs found for graph: {len(docs)}")
    nodes = []
    links = []
    
    import os
    path_to_id = {}
    basename_to_id = {}
    folder_nodes = set()
    
    for doc in docs:
        node_id = doc.id
        path_to_id[doc.file_path] = node_id
        basename = os.path.basename(doc.file_path)
        basename_without_ext = os.path.splitext(basename)[0]
        
        basename_to_id[basename] = node_id
        basename_to_id[basename_without_ext] = node_id
        
        nodes.append({
            "id": node_id,
            "name": basename,
            "path": doc.file_path,
            "val": 1.5,
            "type": "file",
            "tags": doc.extracted_tags or []
        })
        
        dirname = os.path.basename(os.path.dirname(doc.file_path))
        if dirname and dirname != "data" and dirname != "RAW_DOCS_DIR":
            folder_id = f"folder_{dirname}"
            if folder_id not in folder_nodes:
                folder_nodes.add(folder_id)
                nodes.append({
                    "id": folder_id,
                    "name": dirname,
                    "val": 3,
                    "type": "folder",
                    "tags": []
                })
            links.append({
                "source": node_id,
                "target": folder_id,
                "type": "hierarchy"
            })

    for doc in docs:
        if not doc.extracted_links:
            continue
            
        source_id = doc.id
        for raw_link in doc.extracted_links:
            link_target = raw_link.replace("[[", "").replace("]]", "").strip()
            
            target_id = path_to_id.get(link_target) or basename_to_id.get(link_target)
            
            if target_id and target_id != source_id:
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "reference"
                })
    print(f"Nodes: {len(nodes)}, Links: {len(links)}")
    db.close()
    
if __name__ == "__main__":
    get_graph()
