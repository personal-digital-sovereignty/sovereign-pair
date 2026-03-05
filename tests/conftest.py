import sys
import os

# Força o diretório raiz do Sovereign-Pair ao PYTHONPATH antes dos testes
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)
