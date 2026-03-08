# [Bug]: Silent fallback to OpenAI in Retrievers and Indexes compromises Air-Gapped/Local-First deployments

### Bug Description
When instantiating components like `VectorStoreIndex` or `QueryFusionRetriever` without explicitly passing the `llm` or `embed_model` kwargs, LlamaIndex silently falls back to OpenAI's models (`gpt-3.5-turbo` and `text-embedding-ada-002`). 

While this default behavior is convenient for quick prototypes, it creates a critical security/privacy flaw for developers building Local-First, Air-Gapped, or Privacy-Strict architectures (e.g., using local Ollama or vLLM instances). If a developer misses injecting the local LLM into a nested retriever, the framework will silently attempt to send the user's private data/vectors to `api.openai.com`.

If an old `OPENAI_API_KEY` happens to exist in the system's environment variables, the data leak occurs completely silently without any warnings.

### Steps to Reproduce
1. Intentionally construct a Local-Only architecture and remove OpenAI keys from the active environment.
2. Instantiate a `QueryFusionRetriever` without explicitly passing the `llm` argument:
```python
from llama_index.core.retrievers import QueryFusionRetriever

# Intending to use local environment, but forgot to pass llm=...
hybrid_retriever = QueryFusionRetriever(
    [vector_retriever, bm25_retriever],
    mode="reciprocal_rank"
)
```
3. Observe the crash: The system does not raise an explicit `MissingLLMProvider` error. Instead, it throws an OpenAI specific error:
```text
ValueError: No API key found for OpenAI.
Please set either the OPENAI_API_KEY environment variable or openai.api_key prior to initialization.
```

### Expected Behavior
For enterprise, legal, or privacy-focused implementations, a framework should not default to a commercial cloud API unconditionally.

Ideally, LlamaIndex should:
1. Provide a global setting like `Settings.strict_mode = True` or `Settings.air_gapped = True` that immediately disables all OpenAI commercial defaults and throws a strict `MissingProviderError` if an LLM is not explicitly provided.
2. At the very least, log a `WARNING` when defaulting to OpenAI in deep instantiations: *"Warning: No LLM provided to QueryFusionRetriever. Falling back to default OpenAI models. Your data will be sent to OpenAI servers."*

### Full Traceback
Here is the exact framework crash output when the environment doesn't have an `OPENAI_API_KEY`:

```text
Traceback (most recent call last):
  ...
  File "/app/src/engine_builder.py", line 116, in build_chat_engine
    hybrid_retriever = QueryFusionRetriever(
                       ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/llama_index/core/retrievers/fusion_retriever.py", line 63, in __init__
    resolve_llm(llm, callback_manager=callback_manager) if llm else Settings.llm
                                                                    ^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/llama_index/core/settings.py", line 36, in llm
    self._llm = resolve_llm("default")
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/llama_index/core/llms/utils.py", line 64, in resolve_llm
    raise ValueError(
ValueError: 
******
Could not load OpenAI model. If you intended to use OpenAI, please check your OPENAI_API_KEY.
Original error:
No API key found for OpenAI.
Please set either the OPENAI_API_KEY environment variable or openai.api_key prior to initialization.
API keys can be found or created at https://platform.openai.com/account/api-keys
******
```

### Context
This was discovered while building a sovereign, 100% local-first RAG architecture. Because of a missing kwarg, the system attempted to leak locally embedded system-knowledge chunks to OpenAI. Luckily, the environment variables were strictly sanitized, which triggered the `401 Unauthorized` exception and exposed the silent fallback behavior.

### Environment
- LlamaIndex Version: (Latest)
- Python Version: 3.12
- OS: Linux (Arch)
