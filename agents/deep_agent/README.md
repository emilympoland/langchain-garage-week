# deep-agent

The Module 2 research agent — the same harness from Module 1, built as a [Managed Deep Agent](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview) (MDA) instead of a hand-built `create_deep_agent` + server. See `agent.py`'s docstring for the full `create_deep_agent` → `define_deep_agent` mapping.

## Setup

```bash
cd agents/deep_agent
cp .env.example .env   # fill in your keys
uv sync
```

## Run locally

```bash
uv run mda dev
```

Opens a local Agent Server + LangSmith Studio.

## Deploy

```bash
uv run mda deploy
```

Defaults to the GCP US SaaS region — see `.env.example` if your LangSmith workspace is in a different region.
