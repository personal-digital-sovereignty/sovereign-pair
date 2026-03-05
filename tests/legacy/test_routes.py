import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.api.main import app
for route in app.routes:
    print(getattr(route, "path", route.name))
