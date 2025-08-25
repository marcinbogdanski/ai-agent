# v0.1 — Minimal viable agent (this repo)
**Scope**
- Chat REPL and `--exec` one-shot
- Anthropic provider only; no streaming; optional temperature, unset by default
- Context: `system.md` + `AGENT.md` (≤ 64 KB)
- Tools: `fs.list`, `fs.read`, `fs.write` (text, atomic); `shell.exec` (120s, 200KB cap)
- MCP client: static servers; Playwright via TCP `127.0.0.1:8710`; namespaced tools
- Slash commands: `/memory`, `/commit`, `/clear`, `/quit`
- Logging: JSONL per session in `./.aiagent/logs/`; usage printed after replies
- Retries: 2 on 429/5xx
- Tests: pytest for core pieces; ruff/black/mypy set up

**Demo**
- Playwright MCP: login to site with placeholders, navigate to Billing → Invoice, download latest to `./downloads/`, confirm `invoice*.pdf` exists

---

# v0.2 — Quality-of-life
- Config file `config.json` (optional), precedence: CLI > env > config file
- More robust CLI help and error messages; `--model-list` (static)
- Better shell tool UX: live line-by-line truncation notices; colored summaries
- Provider abstractions: OpenAI-compatible shim (no tool use yet)
- Optional structured terminal logs in JSON (toggle)
- Session transcript export command

---

# v0.3 — Deeper tooling & providers
- Git toolset beyond `/commit`: status, diff, apply patch
- Python runner tool (execute a small code snippet in a subprocess)
- OpenAI and/or OpenRouter provider support with function calling
- Per-turn configurable tool cap and timeouts via flags

---

# v0.4 — Memory & config polish
- Configurable memory management: include/exclude parts of `AGENT.md` by tags
- `/memory` categories (e.g., `* [todo] …`, `* [rule] …`), simple filter in prompt
- Prompt templates directory with hot-reload

---

# v0.5 — Observability & stability
- OpenTelemetry hooks (optional) to export traces
- Redaction of secrets in logs (simple regex-based at first)
- Better error taxonomies and retry/backoff tuning

---

# Stretch / nice-to-have (post v0.5)
- Streaming UI (partial tokens)
- Simple GUI playground (web)
- Vector store / RAG over repo docs
- Multi-agent orchestration or planning module (opt-in)

---

# Non-Goals (for now)
- Windows/macOS support
- Full sandboxing/guardrails beyond Docker
- Complex persistence or databases

---

# Success Criteria (recap)
- For the demo task, after a single `--exec` run, the expected invoice PDF exists under `./downloads/`, and logs contain a coherent sequence of MCP calls and tool results with accurate token usage accounting.
