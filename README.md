# AI Agent — a tiny AI agent

**aiagent** is a minimal but realistic Python agent intended for learning. It focuses on a clean, correct core loop with just enough features to be useful:

- Chat REPL and one-shot execution
- Anthropic provider (v0.1), token usage display
- Tool calling: filesystem (list/read/write) and shell (bash)
- Memory file **AGENT.md** auto-loaded on session start; `/memory` appends bullet points
- Model Context Protocol (MCP) client with static configuration (e.g., Playwright MCP over TCP)
- Structured JSONL logs per session; terminal logs with levels
- Linux-only, Python 3.13; run in a Docker container (no sandboxing inside the app)

This project is built for personal use by a senior engineer; it is open-sourced but not distributed as a package.

---

# Quickstart

## Requirements
- Python **3.13** (Linux)
- `ANTHROPIC_API_KEY` environment variable set
- (Optional) A running MCP server (e.g., Playwright MCP) reachable via TCP

## Install (dev)
```bash
# clone repo
cd aiagent
python3.13 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .  # local dev install via pyproject.toml
```

## Configure (v0.1 hard-coded)
No config file is required for v0.1. Anthropic model defaults to `claude-3.5-sonnet` (exact name may be adjusted in code). MCP servers are statically listed in code (e.g., Playwright at `127.0.0.1:8710`).

## Run
```bash
# Start interactive chat (REPL)
aiagent

# One-shot execution (behaves like pasting the string into chat and pressing Enter)
aiagent --exec "Generate a README skeleton for my project"

# Slash commands (type these inside REPL or pass via --exec)
/memory Remember to refactor fs.write to be atomic
/commit "checkpoint before adding MCP"
/clear   # starts a new conversation & rotates log file
/quit
```

## Environment
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Logging
- Terminal: human logs at INFO (use `--debug` to increase verbosity)
- Files: JSONL in `./.aiagent/logs/session-YYYYmmdd-HHMMSS.jsonl`

Each turn prints **usage** after the model reply, e.g.:
```
usage: input=1234, output=987, thinking=256, total=2477
```
(If the provider does not report `thinking`, that field is omitted.)

---

# What it can do (v0.1)
- Chat with the LLM (Anthropic)
- Call tools when prompted by the user or as part of the model plan
- Append memory items to `AGENT.md` via `/memory <text>` (exact bullet point at file end)
- Execute bash commands via the Shell tool (120s timeout, 200KB stdout/stderr truncation)
- List/read/write text files via Filesystem tool (writes are atomic)
- Use MCP tools exposed by configured MCP servers (namespaced as `mcp.<server>.<tool>`)

# What it will not do (v0.1)
- Streaming tokens
- Multi-provider routing (Anthropic only)
- History management or persistence beyond logs
- Vector memory / RAG
- Guardrails / sandboxing (intended to run inside Docker)

---

# Repository Layout
```
aiagent/
  aiagent/             # Python package
    __init__.py
    agent/
      loop.py          # core agent loop
      message.py       # message / turn models
      prompts/
        system.md      # default system prompt
      tools/
        fs.py          # list/read/write (text only)
        shell.py       # bash exec with timeout and truncation
        mcp_client.py  # MCP adapter and tool registry bridge
      providers/
        anthropic_client.py  # Anthropic API wrapper
      logging/
        jsonl.py       # structured JSONL logging
  cli/
    __init__.py
    main.py            # entrypoint for `aiagent` CLI
  tests/
    test_fs.py
    test_shell.py
    test_loop.py
  README.md
  ARCHITECTURE.md
  ROADMAP.md
  pyproject.toml
  ruff.toml
  mypy.ini
```

---

# CLI
```
aiagent [--debug] [--temp FLOAT] [--model NAME] [--exec STRING]

Options:
  --exec STRING   Run a single prompt or slash command non-interactively.
  --debug         Increase terminal verbosity to DEBUG.
  --model NAME    Override model name (default configured in code).
  --temp FLOAT    Set temperature; if omitted, no temperature is sent to the provider.
  -h, --help      Show help.
```

**REPL**: multiline input is supported; submit on blank line. **--exec**: single line only.

**Slash commands** (enter inside REPL or via `--exec`):
- `/memory <text>` → append `* <text>` to end of `AGENT.md`.
- `/commit <msg>` → `git add -A && git commit -m "<msg>"` via Shell tool.
- `/clear` → start a new conversation and rotate JSONL file.
- `/quit` → exit.

---

# Success Demo (Playwright MCP)
Goal: “Login to website `https://abcd.com` using username X, password Y, go to Billing → Invoice, download latest invoice.”

- Agent prompts may contain placeholders `{USERNAME}` `{PASSWORD}`.
- MCP server resolves secrets (not the agent).
- Download destination: `./downloads/`.
- Success criterion: a file matching `invoice*.pdf` exists in `./downloads/`.

Run example:
```bash
aiagent --exec "login to https://abcd.com then download latest invoice to ./downloads"
```

---

# License
No explicit license intended (personal educational project).
