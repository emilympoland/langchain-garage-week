# Modular Workshops

This repository is a hands-on, three-module arc: build a Deep Agent, deploy it as a Managed Deep Agent, then observe and iterate on it with LangSmith. By the end you'll have the knowledge to build and deploy your own managed deep agent and keep improving it in production.

This is a condensed version of LangChain Academy, intended to be run in a session with a LangChain engineer. If you're interested in going into more depth, or working through tutorials on your own, check out [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph)! LangChain Academy has helpful pre-recorded videos from our LangChain engineers.

## Modules

| Module | Notebook | Covers |
|---|---|---|
| 1. Deep Agents | [`modules/01_deep_agents.ipynb`](modules/01_deep_agents.ipynb) | Build an agent by hand with `create_deep_agent()`: custom tools, subagents, memory/backends, middleware, human-in-the-loop, AGENTS.md + skills |
| 2. Deploy | [`modules/02_deploy.ipynb`](modules/02_deploy.ipynb) | Ship that same agent as a [Managed Deep Agent](https://docs.langchain.com/langsmith/python/managed-deep-agents-overview) (MDA) — `create_deep_agent` → `define_deep_agent`, local dev with `mda dev`, and `mda deploy` to a hosted Agent Server |
| 3. LangSmith | [`modules/03_langsmith.ipynb`](modules/03_langsmith.ipynb) | Observe and improve the deployed agent: tracing + querying runs, offline evals (final-response + trajectory), online evals, and annotation queues |

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
| `LANGSMITH_API_KEY_GATEWAY` | Optional — LangSmith Gateway model routing in `utils/models.py` (Modules 1 & 3) | same key as `LANGSMITH_API_KEY`, under a non-reserved name |
| `TAVILY_API_KEY` | Modules 1 & 3 (web search tool) | <https://tavily.com> |

### Getting a LangSmith API key

1. Sign up at <https://smith.langchain.com>, then open **Settings → API Keys**.
2. Click **Create API Key**, set an expiration, and copy it immediately — LangSmith only shows it once.
3. **For Modules 1 and 3** (notebook tracing), a **Personal Access Token** is enough — it just inherits your own account's permissions. Put it in the root `.env` as `LANGSMITH_API_KEY`.
4. **For Module 2** (`mda deploy`), you need a **Service Key** instead — when creating the key, choose **Full Organization** or **Specific Workspaces** rather than a personal scope. Service keys start with `lsv2_sk_...`; a personal token doesn't have deployment permissions and `mda deploy` fails with a 403. Put this one in `agents/deep_agent/.env` as its own `LANGSMITH_API_KEY` (that project reads its own `.env`, not the workshop root's).

```bash
# 3. Start Jupyter
uv run jupyter notebook
```

Open whichever module(s) your recipe calls for.

## Project Structure

```
modular-workshops/
├── README.md                       (this file — recipes + setup)
├── pyproject.toml                  (shared dependencies)
├── .env.example
├── utils/
├── agents/
│   ├── research_agent.py           (shared agent factory — Module 1 references, Module 3 imports for eval)
│   └── deep_agent/                 (deployable agent for Module 2 — its own project, `mda deploy`)
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
    ├── 02_deploy.ipynb             (Module 2)
    └── 03_langsmith.ipynb          (Module 3)
```

## Common Issues

**`mda deploy` fails with 403 / permission denied**
Your API key is a personal token. Generate a service key (`lsv2_sk_...`) instead — see "Getting a LangSmith API key" under Setup above.

**LangSmith could not identify the API key owner, or 403 on `mda` commands**
The key in `agents/deep_agent/.env` is wrong or revoked, or it isn't a personal key — `mda` reads `.env` first, so check it there. If you've also exported an old `LANGSMITH_API_KEY` in your shell, other tools may still pick that one up instead.

**Deploy fails with 401/403 even with a valid key**
Your LangSmith workspace needs access to deployments and the Managed Deep Agents beta — check your plan in LangSmith Settings.

**Context Hub conflict on `mda deploy`**
Someone edited `instructions.md` or `skills/` in the LangSmith UI since your last deploy. Answer the CLI prompt, or in CI pass `--context-strategy overwrite` (use your local files) or `--context-strategy keep-hub` (keep the UI edits).

**`sandbox/setup.sh` exited with code 1**
The managed sandbox image is Debian, so install Python packages with `apt-get install python3-<name>`, not `pip install`. (This project doesn't declare a `sandbox/` by default — only relevant if you add one.)

**Need a different LangSmith region?**
Set `LANGSMITH_ENDPOINT` in `agents/deep_agent/.env` before your first deploy, e.g. `https://eu.api.smith.langchain.com` — see the comment in that file's `.env.example` for the full table.

**Notebook can't find `utils` / `agents`**
Each module's setup cell prepends `project_root` (the workshop root) to `sys.path`. If you moved a notebook, update the `Path().resolve().parent` line to point at the workshop root.
