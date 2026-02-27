import json
import uvicorn
from src.api.main import app

def export_openapi():
    schema = app.openapi()
    with open("docs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print("OpenAPI schema exported to docs/openapi.json")

if __name__ == "__main__":
    export_openapi()
