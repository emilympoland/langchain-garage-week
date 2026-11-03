# Modular Workshops

This repository contains hands-on tutorials for learning LangChain, LangGraph, and Deep Agents.

This is a condensed version of LangChain Academy, intended to be run in a session with a LangChain engineer. If you're interested in going into more depth, or working through tutorials on your own, check out [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph)! LangChain Academy has helpful pre-recorded videos from our LangChain engineers.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment variables
cp .env.example .env
# Edit .env and fill in your keys
```

| Key | Required for | Get one |
|-----|--------------|---------|
| `OPENAI_API_KEY` | Modules 1-3 (default model) | <https://platform.openai.com> |
| `LANGSMITH_API_KEY` | Modules 2 & 3 (recommended for all) | <https://smith.langchain.com> |
| `LANGSMITH_API_KEY_GATEWAY` / `WORKSPACE_ID` | Module 2 §1 (LangSmith Gateway policies) | same key as `LANGSMITH_API_KEY`; workspace ID from LangSmith Settings → Workspace |
| `TAVILY_API_KEY` | Modules 1 & 3 (web search tool) | <https://tavily.com> |

```bash
# 3. Start Jupyter
uv run jupyter notebook
```

Open whichever module(s) your recipe calls for.

## Switching Models

Module 1 and Module 3 import `model` from `utils/models.py` (Module 2's deployable agent has its own separate config — see below). Pick exactly one `MODEL_SPEC` / `API_KEY_ENV` pair there to swap providers — no notebook edits required.

```python
# utils/models.py

# OpenAI, direct (default)
MODEL_SPEC = {"model": "openai:gpt-5.6-luna", "use_responses_api": True}
API_KEY_ENV = "OPENAI_API_KEY"

# Anthropic
# MODEL_SPEC = {"model": "anthropic:claude-sonnet-5"}
# API_KEY_ENV = "ANTHROPIC_API_KEY"

# Azure OpenAI
# MODEL_SPEC = {"model": "azure_openai:gpt-5.6-terra", "azure_deployment": "gpt-5.6-terra"}
# API_KEY_ENV = "AZURE_OPENAI_API_KEY"

# AWS Bedrock -- authenticates via the AWS credential chain, not a single key.
# Also swap the final `model = ...` line for `model = init_chat_model(**MODEL_SPEC)`.
# MODEL_SPEC = {"model": "bedrock_converse:anthropic.claude-sonnet-4-20250514-v1:0"}
# API_KEY_ENV = None
```

`utils/models.py` also ships a commented-out **LangSmith Gateway** block, for routing Module 1 and Module 3's model calls through the gateway too. Module 2 §1.4 walks through the same technique for the deployable agent itself, which has its own model config in `agents/deep_agent/agent.py`.

## Deploy + Govern (Module 2)

Module 2 first creates a workspace-level **LangSmith Gateway** policy (PII / secrets redaction), routes a demo agent through the gateway, then deploys the agent at `agents/deep_agent/` with [Managed Deep Agents](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview) (MDA) via the `mda` CLI — the same Deep Agents harness from Module 1, packaged as a `define_deep_agent` project instead of a hand-built `create_deep_agent` + server.

`agents/deep_agent/` is its own self-contained project (own `pyproject.toml`, own `.env`), so the `mda` toolchain stays isolated from this workshop's notebook environment. Its model config lives directly in `agents/deep_agent/agent.py` — flip on the commented-out Gateway block there and the deployed agent routes through the policy from §1.1, no extra deploy flags needed.

Your `LANGSMITH_API_KEY` must have deployment permissions (use a `lsv2_sk_...` service key). The Gateway block reads `LANGSMITH_API_KEY_GATEWAY` (the same key under a non-reserved name, since `LANGSMITH_API_KEY` is reserved for the deployment's own auth).

Wherever your LangSmith workspace isn't on the GCP US SaaS region (the default for `mda deploy`), set `LANGSMITH_ENDPOINT` to match it in `agents/deep_agent/.env` before your first deploy — see the comment in that file's `.env.example`.

## Project Structure

```
modular-workshops/
├── README.md                       (this file — recipes + setup)
├── pyproject.toml                  (shared dependencies)
├── .env.example
├── utils/
├── agents/
│   ├── research_agent.py           (shared agent factory — Module 1 references, Module 3 imports for eval)
│   └── deep_agent/                 (deployable + governed agent for Module 2 — its own project, `mda deploy`)
│       ├── agent.py
│       ├── instructions.md
│       ├── memory.py
│       ├── tools/search.py
│       └── skills/
│           ├── linkedin-post/SKILL.md
│           └── twitter-post/SKILL.md
├── images/                         (diagrams used by the notebooks)
└── modules/
    ├── 01_deep_agents.ipynb        (Module 1)
    ├── 02_deploy_and_govern.ipynb  (Module 2)
    └── 03_langsmith.ipynb          (Module 3)
```

## Common Issues

**`mda deploy` fails with 403 / permission denied**
Your API key is a personal token. Generate a service key (`lsv2_sk_...`) in LangSmith settings.

**LangSmith could not identify the API key owner, or 403 on `mda` commands**
The key in `agents/deep_agent/.env` is wrong or revoked, or it isn't a personal key — `mda` reads `.env` first, so check it there. If you've also exported an old `LANGSMITH_API_KEY` in your shell, other tools may still pick that one up instead.

**Deploy fails with 401/403 even with a valid key**
Your LangSmith workspace needs access to deployments and the Managed Deep Agents beta — check your plan in LangSmith Settings.

**Context Hub conflict on `mda deploy`**
Someone edited `instructions.md` or `skills/` in the LangSmith UI since your last deploy. Answer the CLI prompt, or in CI pass `--context-strategy overwrite` (use your local files) or `--context-strategy keep-hub` (keep the UI edits).

**`sandbox/setup.sh` exited with code 1**
The managed sandbox image is Debian, so install Python packages with `apt-get install python3-<name>`, not `pip install`. (This project doesn't declare a `sandbox/` by default — only relevant if you add one.)

**Need a different LangSmith region?**
Set `LANGSMITH_ENDPOINT` in `agents/deep_agent/.env` before your first deploy, e.g. `https://eu.api.smith.langchain.com` — see the region note under Deploy + Govern above for the full table.

**Notebook can't find `utils` / `agents`**
Each module's setup cell prepends `project_root` (the workshop root) to `sys.path`. If you moved a notebook, update the `Path().resolve().parent` line to point at the workshop root.
