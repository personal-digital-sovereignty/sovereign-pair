@dosu Thanks for confirming and providing the related issues. 

However, the fact that this is a **known behavior** (reported across #19403, #17379, #18349, and now escalating in parallel in **#20917**) makes it significantly worse from an Enterprise and InfoSec perspective. 

Suggesting users to "just configure `Settings` globally" is a documentation workaround, not an engineering fix. In complex modular RAG systems, a developer might instantiate a specific retriever, evaluator, or agent dynamically, entirely bypassing the global `Settings`. The consequence of a single missed `llm=` argument shouldn't be "silently sending sensitive local data to a 3rd party commercial API".

**Proposal for maintainers**:
If removing the commercial OpenAI fallback from `resolve_llm` is considered an undesirable "breaking change" for beginners, please explicitly offer an environment variable or global flag to enforce an **Air-Gapped / Sovereign** behavior. For example:

```python
import os
os.environ["LLAMAINDEX_STRICT_LOCAL"] = "1"
# OR
Settings.strict_mode = True
```

When enabled, `resolve_llm` MUST immediately raise a `MissingProviderError` if it attempts to instantiate OpenAI classes or contact `api.openai.com` without explicit user injection. 

This is a baseline privacy guardrail to prevent silent data exfiltration in Healthcare, Defense, and Sovereign deployments.

Would the core team be open to reviewing a PR that implements a systemic `strict_mode` flag?
