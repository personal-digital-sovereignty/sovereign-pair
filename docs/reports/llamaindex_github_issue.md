# [Bug]: Unspecified Retriever and Index configurations default to OpenAI affecting Air-Gapped and Local-First logic architectures

### Bug Description
When initializing elements referencing `VectorStoreIndex` or `QueryFusionRetriever` without providing explicitly the `llm` or `embed_model` kwargs, the LlamaIndex framework structurally implements defaults adopting OpenAI commercial models (`gpt-3.5-turbo` and `text-embedding-ada-002`). 

Although establishing a simplified development baseline, this methodology inserts unpredicted vulnerabilities to Local-First and Air-Gapped architectures reliant on in-house nodes (e.g. leveraging Ollama limits / vLLM local bindings). The software defaults transmit user prompts out traversing commercial endpoints (`api.openai.com`) whenever a developer skips the binding allocation inside nested retriever objects.

Given an unpurged `OPENAI_API_KEY` exists actively traversing local system variables, this fallback behavior routes traffic silently outside intended domain logic instances without triggering proxy warnings.

### Steps to Reproduce
1. Structurally build a restricted native network processing environment deleting OpenAI credential paths inside system root mappings.
2. Initialize an active instance corresponding to `QueryFusionRetriever` stripping explicit parameter allocations towards the `llm` engine node:
```python
from llama_index.core.retrievers import QueryFusionRetriever

# Isolated architecture logic initialized excluding hardcoded llm definitions
hybrid_retriever = QueryFusionRetriever(
    [vector_retriever, bm25_retriever],
    mode="reciprocal_rank"
)
```
3. Runtime Failure Evaluation: The local setup omits to state generic unallocated dependency error limits (such as `MissingLLMProvider`). The runtime explicitly attempts to interface with OpenAI network endpoints resulting in authentication error:
```text
ValueError: No API key found for OpenAI.
Please set either the OPENAI_API_KEY environment variable or openai.api_key prior to initialization.
```

### Expected Behavior
Framework deployments addressing isolated enterprise compliance restrictions and sovereign internal network data validation should systematically avoid unconfigured fallback commercial instances.

Framework optimization suggestions:
1. Initialize an exclusive structural variable param (e.g. `Settings.strict_mode = True` or `Settings.air_gapped = True`) effectively preventing implicit dependency API assumptions. The module must immediately trigger a severe `MissingProviderError` upon evaluating unassigned variables.
2. Logging Output Evaluation: Process a definitive tracking `WARNING` inside shell operations logging the connection transition: *"Warning: Undefined LLM instance assigned toward QueryFusionRetriever. Reverting network logic variables adopting standard OpenAI defaults. Operations transmit native payload into OpenAI standard commercial external networking APIs."*

### Full Traceback
Execution console evaluation matching the endpoint missing commercial internal variable `OPENAI_API_KEY`:

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
Review instances triggered natively constructing comprehensive bare-metal sovereign components processing internal architectures. Overlooking hardcoded argument limitations transmitted embedded local text references forcing system outbound routes out towards public platforms. Comprehensive environment sanitation procedures blocking network access threw exceptions mapped `401 Unauthorized` intercepting the automated data routing operation limit.

### Environment
- LlamaIndex Version: (Latest)
- Python Version: 3.12
- OS: Linux (Arch)
