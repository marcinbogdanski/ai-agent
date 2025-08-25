# Overview
**aiagent** is a small, explicit agent loop that delegates capability via tools and MCP. It favors clarity over cleverness and is built to be modified.

Key decisions:
- **Provider**: Anthropic. Usage is read from provider metadata and printed/logged.
- **Context**: `AGENT.md` prepended to the system prompt each session.
- **Loop**: REPL chat with tool-call support.
- **Memory**: Session-only (process memory). User can edit `AGENT.md` for persistent memory.
- **Logging**: Human logs to terminal; structured JSONL per session.
- **MCP**: Static servers (e.g., Playwright at `127.0.0.1:8710`), tools exposed as `mcp.<server>.<tool>`.

---

# Data Model

## Messages
```python
@dataclass
class Message:
    # Exact schema TBD, this is rough example only, consult code
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict]  # provider-specific segments allowed
    name: str | None = None    # tool name for tool results
    tool_call_id: str | None = None
```

## ToolSpec & Registry
```python
@dataclass
class ToolSpec:
    # Exact schema TBD, this is rough example only, consult code
    name: str
    description: str
    schema: dict  # JSON-schema for args
    handler: Callable[[dict], ToolResult]

@dataclass
class ToolResult:
    # Exact schema TBD, this is rough example only, consult code
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
  # MCP tools discovered from static config -> namespaced as mcp.<server>.<tool>
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
    "role": "assistant",
    "content": "Here's teh plan...",
    "..": ".."
}
```

---

# Provider Integration (Anthropic v0.1)
- **Model**: `claude-3.5-sonnet` by default.
- **Usage**: read `input_tokens`, `output_tokens`, and if available `thinking_tokens`; compute total.
- **No streaming**: requests are single-shot per turn.
- **Function/Tool use**: Anthropic’s tool use format is supported; OpenAI-style is planned later.

## Prompt/Context Layout
On session start:
1. Read `AGENT.md` and inject into conversation.
2. Load `aiagent/agent/prompts/system.md` and use as system prompt
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

- `aiagent` -> interactive REPL
- `aiagent --exec "..."` -> one-shot input (no multiline)

## Slash Commands (handled client-side)
- `/clear` -> rotates to a new JSONL file and resets conversation state.
- `/quit` -> exits process.

---

# Agent Loop (pseudo-code)
```python

class Agent:
    def __init__(api_key):
        self.api_key = api_key
        self.provider = ...
        self.conversation = ...  # history of messages
        self.system_prompt = ...
        self.agent_file = ... # read AGENT.md


    def multi_step(user_message: str)
        # LLM API call
        llm_response = self.conversation.send_message(user_message)
        print(llm_response)

        while True:
            if is_tool_call(llm_response):
                tool_call_result = self.perform_tool_call(llm_response)
                llm_response = self.conversation.send_message(tool_call_result)
                print(llm_response)
```

---

# Security Model (deliberately permissive for Docker use)
- No sandbox/jail; working directory is the current process directory.
- Outbound network allowed.
- No prompt-injection defenses; rely on user-in-the-loop and Docker isolation.

---

# Testing & Quality
- **pytest** for unit tests (tools, loop happy-path, MCP adapter handshake mocked)

