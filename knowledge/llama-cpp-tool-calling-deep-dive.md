# YiBot Tool Calling Fix — Deep Dive

## Environment
- OpenClaw 2026.3.2
- llama.cpp build 8467, running Qwen3.5-9B-Q4_K_M.gguf
- RTX 2080 Ti, Windows 11
- Channels: Telegram, Discord
- llama-server flags: `--jinja` (required for Qwen tool call format)

---

## How llama.cpp Tool Calling Works

When OpenClaw sends a chat completions request with a `tools` array:
1. llama.cpp receives the tools JSON schemas
2. With `--jinja`, it applies the Qwen3.5 chat template which generates GBNF (grammar) rules from the tool schemas
3. The GBNF grammar constrains model output to only valid tool call XML: `<tool_call><function=name>...</function></tool_call>`
4. After generation, llama.cpp converts the XML to OpenAI-format `tool_calls` JSON
5. OpenClaw receives the tool call, executes it, and sends the result back

If grammar compilation fails:
- llama.cpp falls back to `peg-native` (unconstrained generation)
- Model outputs XML tool calls anyway (from training), but llama.cpp does NOT convert them
- OpenClaw receives raw XML → "Failed to parse input at pos N: `<tool_call>`"
- Bot responds as if it has no tools

**Key diagnostic**: `Chat format: peg-native` in llama-server log = grammar not active.
`failed to parse grammar` = grammar compilation crashed.

---

## Root Cause 1: Grammar Overflow (sessions_spawn)

The `sessions_spawn` tool schema includes an `attachments` field with `maxLength: 6700000`. llama.cpp's grammar generator produces:
```
tool-sessions-spawn-arg-attachments-schema-item-content ::= "\"" char{0,6700000} "\"" space
```

llama.cpp has an internal sanity check: `number of repetitions exceeds sane defaults`. This check fires on `{0,6700000}`, immediately aborting grammar compilation. The entire tool set — including `exec` — is lost.

### What We Tried (and Why It Failed)
- `sessions_spawn: { "enabled": false }` in `agent.json` → **ignored completely**. The `tools` section in agent.json does NOT control what tools are sent to the model. OpenClaw determines the tool set from the profile and skills, not agent.json overrides.
- `coding-agent: { "enabled": false }` in skills → did not remove sessions_spawn (it's part of the `coding` profile itself, not injected by coding-agent)
- Switching to `minimal` profile → zero tools sent, `peg-native` loop
- `--grammar-lazy-greed` flag → does not affect the grammar parser sanity check

### The Fix: Tool-Filter Proxy
A Python HTTP proxy intercepts every POST to `/v1/chat/completions` before it reaches llama.cpp, removes `sessions_spawn` (and `message`) from the `tools` array, then forwards the modified request. Without `sessions_spawn`, the grammar compiles successfully.

```
OpenClaw → :8079 (tool-proxy.py) → :8080 (llama-server)
```

The proxy also handles:
- Chunked transfer encoding
- Streaming responses (SSE)
- `tool_choice` cleanup if a stripped tool was explicitly selected

---

## Root Cause 2: Missing exec-approvals.json

OpenClaw requires `exec-approvals.json` to exist before including the `exec` tool in the tool set sent to the model. If the file is absent, exec is silently excluded — no error, no warning.

### Correct Format
```json
{
  "version": 1,
  "defaults": { "security": "deny", "ask": "off", "askFallback": "deny", "autoAllowSkills": false },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "off",
      "askFallback": "deny",
      "autoAllowSkills": false,
      "allowlist": [
        { "id": "curl",       "pattern": "**/curl.exe" },
        { "id": "gh",         "pattern": "**/gh.exe" },
        { "id": "cmd",        "pattern": "**/cmd.exe" },
        { "id": "powershell", "pattern": "**/powershell.exe" }
      ]
    }
  }
}
```

- `security: "allowlist"` — only patterns in the allowlist can run
- `ask: "off"` — no interactive approval prompts (bot is unattended)
- `pattern` — glob matching against the resolved binary path

---

## Root Cause 3: Poisoned Conversation History

After many failed attempts, the conversation accumulated 20,000+ tokens of "I don't have exec" responses. Even after exec became available in the tool set and the grammar compiled correctly, the model continued following the pattern established in its context window.

**Why this overrides grammar**: If grammar fails (root cause 1), the model generates unconstrained text. Without grammar, conversation history dominates. With grammar active (`root ::= tool-call`), the model is physically constrained to output only tool call XML — it cannot say "I don't have exec." So the poisoned history only matters when grammar is broken.

**Fix**: Start a fresh session (new channel / `/clear` command) to give the model a clean context.

---

## Configuration Reference

### Files Modified
| File | Change |
|------|--------|
| `openclaw.json` | `tools.profile: "coding"`, baseUrl → `:8079`, skills: coding-agent disabled |
| `agents/main/agent/models.json` | baseUrl → `:8079` |
| `agents/main/agent/auth-profiles.json` | baseUrl → `:8079` (this is the actual connection URL OpenClaw uses) |
| `agents/main/agent/prompt.txt` | Added exec output instruction, gh full path instruction |
| `exec-approvals.json` | Created with correct format and allowlist |
| `tool-proxy.py` | Created — strips sessions_spawn/message from tool schemas |
| `start-proxy.vbs` | VBScript launcher (no console window) |

### Auto-Start
Both OpenClaw gateway and the tool proxy are registered as Windows scheduled tasks triggered at logon:
- `OpenClaw Gateway` — starts the main OpenClaw process
- `OpenClaw Tool Proxy` — starts `tool-proxy.py` via `start-proxy.vbs`, 30-second delay after logon

### GitHub CLI Scopes
Current: `gist`, `read:org`, `repo`, `workflow`
Missing (intentionally): `delete_repo` — omitted for safety since deletion is irreversible.
To add later: `gh auth refresh -h github.com -s delete_repo`

---

## Key Lessons

1. **agent.json `tools` section is not a tool filter** — it appears to be ignored by OpenClaw when determining what tools to send to the model. Only profile + skills + exec-approvals.json control the actual tool set.
2. **auth-profiles.json is the real connection URL** — openclaw.json and models.json also have baseUrl, but auth-profiles.json is what OpenClaw actually uses for API calls. All three must be updated together.
3. **Grammar failure is silent from the bot's perspective** — the bot just says "I don't have exec" with no indication that a grammar crash occurred. Always check the llama-server log for `failed to parse grammar`.
4. **peg-native ≠ broken** — `Chat format: peg-native` in the log is normal for Qwen models with `--jinja`. It does NOT mean tools are absent. The presence/absence of grammar rules and `failed to parse grammar` is what matters.
5. **The `--jinja` flag is mandatory** — without it, llama.cpp doesn't apply the Qwen chat template, so tool call XML is never generated or parsed correctly.
