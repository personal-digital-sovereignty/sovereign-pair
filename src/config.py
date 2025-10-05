from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Configuração do LLM para futuro chat e definição de request para o prompt
llm = Ollama(model="llama3.1", request_timeout=120.0)

# Configuração do modelo que irá indexar os arquivos e transformar em vetores no chromadb
embed_model = OllamaEmbedding(model_name="nomic-embed-text")