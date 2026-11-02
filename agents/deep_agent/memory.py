"""Durable, cross-thread memory for the agent, mounted at `/memories/agent/`.

Equivalent to the hand-built `StoreBackend` route (`namespace=("memories",
"shared")`) in the Module 1 notebook's `create_deep_agent` calls -- the
agent's research notes now live under a Context-Hub-backed, agent-scoped
memory layer instead. `instructions.md` is always loaded (the managed
equivalent of "hot" memory); `research_notes.md` under `/memories/agent/` is
read on demand.
"""

from managed_deepagents import define_memory

memory = define_memory(scope="agent")
