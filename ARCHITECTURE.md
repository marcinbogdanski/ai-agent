# Overview
**aiagent** is a small, explicit agent loop that delegates capability via tools and MCP. It favors clarity over cleverness and is built to be modified.

Key decisions:
- **Provider**: Anthropic (v0.1). Usage is read from provider metadata and printed/logged.
- **Context**: `AGENT.md` (≤ 64 KB) prepended to the system prompt each session.
- **Loop**: REPL chat with tool-call support and a cap of **6** tool calls per user turn.
- **Memory**: Session-only (process memory); `/memory` appends to `AGENT.md` persistently.
- **Logging**: Human logs to terminal; structured JSONL per session.
- **MCP**: Static servers (e.g., Playwright at `127.0.0.1:8710`), tools exposed as `mcp.<server>.<tool>`.

---

# Data Model

## Messages
```python
@dataclass
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict]  # provider-specific segments allowed
    name: str | None = None    # tool name for tool results
    tool_call_id: str | None = None
```

## ToolSpec & Registry
```python
@dataclass
class ToolSpec:
    name: str
    description: str
    schema: dict  # JSON-schema for args
    handler: Callable[[dict], ToolResult]

@dataclass
class ToolResult:
    content: str  # text payload (UTF-8)
    ok: bool
    meta: dict    # e.g., exit_code, truncated, bytes
```

Tools are registered at startup:
```python
tools = {
  "fs.list": ToolSpec(...),
  "fs.read": ToolSpec(...),
  "fs.write": ToolSpec(...),
  "shell.exec": ToolSpec(...),
  # MCP tools discovered from static config → namespaced as mcp.<server>.<tool>
}
```

## Logging Event Schema (stable keys)
Each JSONL record is a single-line JSON object with keys:
```
ts, level, event, session_id, turn, actor, model,
input, output, tool_name, prompt_tokens, completion_tokens, thinking_tokens,
latency_ms, error
```
`event` is one of: `session_start`, `user_message`, `assistant_message`, `tool_call`, `tool_result`, `mcp_call`, `mcp_result`, `session_clear`, `error`.

Example (pretty-printed for docs):
```json
{
  "ts": "2025-08-25T12:34:56.789Z",
  "level": "INFO",
  "event": "assistant_message",
  "session_id": "9f8e...",
  "turn": 3,
  "actor": "assistant",
  "model": "claude-3.5-sonnet",
  "output": "Here's the plan...",
  "prompt_tokens": 1420,
  "completion_tokens": 361,
  "thinking_tokens": 128,
  "latency_ms": 2890
}
```

---

# Provider Integration (Anthropic v0.1)
- **Model**: `claude-3.5-sonnet` by default.
- **Temperature**: not sent unless `--temp` is specified.
- **Usage**: read `input_tokens`, `output_tokens`, and if available `thinking_tokens`; compute total.
- **Retries**: Up to 2 on 429/5xx with exponential backoff.
- **No streaming**: requests are single-shot per turn.
- **Function/Tool use**: Anthropic’s tool use format is supported; OpenAI-style is planned later.

## Prompt/Context Layout
On session start:
1. Read `aiagent/agent/memory/AGENT.md` (truncate to **64 KB** if larger).
2. Load `aiagent/agent/prompts/system.md`.
3. Compose system content: `system.md` + separator + `AGENT.md excerpt`.

Per turn, messages look like:
```
[system: composed system content]
[user: <text or slash command expansion>]
[assistant/tool turns: as produced by the provider]
```

---

# Tooling

## Filesystem Tool
- **fs.list(path: str) -> list[str]**
- **fs.read(path: str) -> str** (UTF-8 only)
- **fs.write(path: str, content: str, create_dirs: bool = True) -> None**
  - Writes are **atomic**: write to temp file in same directory, then `os.replace`.

## Shell Tool
- **shell.exec(cmd: str, timeout_s: int = 120) -> {exit_code, stdout, stderr, truncated}**
  - Uses `/bin/bash -lc`.
  - Captures stdout/stderr; each truncated above **200 KB** with a note.
  - On non-zero exit: returns `{ok=False, exit_code,...}` but does **not** raise; the model decides next steps.

## MCP Adapter
- Static configuration maps server name → transport.
  - Example: `playwright` → TCP `127.0.0.1:8710`.
- On startup, the adapter connects, lists tools, and registers them as `mcp.<server>.<tool>` with schemas.
- Tool calls: the agent marshals provider tool-use calls to MCP requests and returns results as text payloads.

---

# CLI

## Entrypoint
`aiagent` is the entrypoint.

- `aiagent` → interactive REPL
- `aiagent --exec "..."` → one-shot input (no multiline)
- `--debug` → DEBUG logs in terminal
- `--model` → override model name
- `--temp` → set temperature (omit to leave unset)

## Slash Commands (handled client-side)
- `/memory <text>` → append `* <text>` to the **end of AGENT.md** (exact text, no timestamp/section); also prints a confirmation line.
- `/commit <msg>` → dispatches to shell tool as `git add -A && git commit -m "<msg>"`.
- `/clear` → rotates to a new JSONL file and resets conversation state.
- `/quit` → exits process.

---

# Agent Loop (pseudo-code)
```python
def run_turn(user_input: str):
    if is_slash_cmd(user_input):
        result = handle_slash_cmd(user_input)
        log(event="tool_result", actor="tool", output=result)
        print(result.human_message)
        return

    messages = build_messages(system_ctx, transcript, user_input)

    for attempt in range(3):  # 1 try + 2 retries on 429/5xx
        t0 = now()
        resp = anthropic_client.complete(messages, tools=registry.schemas())
        latency = now() - t0
        usage = extract_usage(resp)
        log_assistant(resp, usage, latency)

        tool_calls = extract_tool_calls(resp)
        if not tool_calls:
            print(render_human(resp))
            print_usage(usage)
            transcript.append(resp)
            return

        for i, call in enumerate(tool_calls[:6]):  # cap at 6 tool calls
            spec = registry.get(call.name)
            args = validate(spec.schema, call.args)
            result = spec.handler(args)
            log_tool(spec.name, args, result)
            messages.append(tool_result_message(call.id, result))

        # re-ask the model with tool results
        continue
```

---

# Error Handling
- **API key missing**: exit non-zero with a clear message.
- **Provider errors (429/5xx)**: retry up to 2 times with backoff; then log `error` and print a concise failure line.
- **Tool exceptions**: converted into `{ok=False, error: <msg>}` tool results; included in messages.
- **Shell timeouts**: `exit_code=124` equivalent + `truncated=False`, `stderr` includes timeout note.

---

# Security Model (deliberately permissive for Docker use)
- No sandbox/jail; working directory is the current process directory.
- Outbound network allowed.
- No prompt-injection defenses; rely on user-in-the-loop and Docker isolation.

---

# Testing & Quality
- **pytest** for unit tests (tools, loop happy-path, MCP adapter handshake mocked)
- **ruff + black** for lint/format
- **mypy** type checks

---

# Performance Targets (soft)
- Cold start (first CLI prompt to first token): under 5s with warm network
- Typical single-shot turn (no tools): under 3s
