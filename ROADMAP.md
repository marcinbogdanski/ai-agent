# v0.1 — Minimal viable agent (this repo)
**Scope**
- Chat REPL and `--exec` one-shot
- Anthropic provider only; no streaming
- Context: `system.md` + `AGENT.md`
- Tools: `fs.list`, `fs.read`, `fs.write` (text, atomic); `shell.exec`
- MCP client: static servers; Playwright via TCP `127.0.0.1:8710`; namespaced tools
- Slash commands: `/clear`, `/quit`
- Logging: JSONL per session in `./.aiagent/logs/`; usage printed after replies

**Demo**
- Playwright MCP: login to site with placeholders, navigate to Billing → Invoice, download latest to `./downloads/`, confirm `invoice*.pdf` exists

---

# v0.2 — Quality-of-life
- Config file `config.json` (optional), precedence: CLI > env > config file

---

# v0.3 — Deeper tooling & providers
- OpenAI and/or OpenRouter provider support with function calling

---
