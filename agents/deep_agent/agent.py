"""The Module 2 deployable research agent, built with Managed Deep Agents (MDA).

Module 1 builds this agent by hand, piece by piece, with `create_deep_agent`.
This project packages the same harness as a Managed Deep Agent: `mda deploy`
builds, hosts, and serves it on LangSmith's Agent Server -- no hand-built
backend, store, checkpointer, or server to run yourself.

Mapping from `create_deep_agent` to `define_deep_agent`, per the migration
guide (https://docs.langchain.com/langsmith/python/managed-deep-agents-migrate):

  - `system_prompt` + the `AGENTS.md` memory file -> `instructions.md`
    (synced to Context Hub on `mda deploy`)
  - `skills=["./skills/"]` -> `skills/<name>/SKILL.md` (same files, synced to
    Context Hub)
  - a hand-built `/memories/` `StoreBackend` route -> `memory.py`'s
    `define_memory(scope="agent")`, mounted at `/memories/agent/`
  - a hand-built `backend=CompositeBackend(FilesystemBackend(virtual_mode=True), ...)`
    -> no backend to declare; without a `sandbox/` declaration the managed
    runtime already gives every run the same thread-scoped virtual filesystem
  - `name` is new and required -- it's also the default deployment name
    (Module 2 §2.6) and the dashboard identifier

`model`, `tools`, `subagents`, and `interrupt_on` carry over unchanged.
"""

import os

from langchain.chat_models import init_chat_model
from managed_deepagents import define_deep_agent

from tools.search import tavily_search

# --- OpenAI, direct (default) ---
model = "openai:gpt-5.6-luna"

# --- OpenAI via the LangSmith Gateway (Module 2 §1.4) ---
# Routes every model call through the Gateway so workspace policies
# (PII / secrets redaction, allow-lists, cost caps) are enforced.
# model = init_chat_model(
#     "openai:gpt-5.6-luna",
#     base_url="https://gateway.smith.langchain.com/openai",
#     use_responses_api=True,
#     api_key=os.environ["LANGSMITH_API_KEY_GATEWAY"],
# )

agent = define_deep_agent(
    name="deep-agent",
    model=model,
    tools=[tavily_search],
    subagents=[{
        "name": "research-agent",
        "description": "Delegate research tasks. Give one topic at a time.",
        "system_prompt": "You are a research assistant. Use tools to gather "
                         "information and cite sources. Limit to 3 search calls.",
        "tools": [tavily_search],
    }],
    interrupt_on={"write_file": True, "edit_file": True},
)
