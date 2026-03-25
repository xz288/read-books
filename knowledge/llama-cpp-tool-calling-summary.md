# YiBot Tool Calling Fix — Brief Summary

## Problem
YiBot (OpenClaw + llama.cpp + Qwen3.5-9B) could not use tools (exec, gh, curl). The bot always responded "I don't have exec" despite correct configuration.

## Root Causes
1. **Grammar overflow** — OpenClaw sends all tools as JSON schemas to llama.cpp, which converts them to GBNF grammar. The `sessions_spawn` tool had a `char{0,6700000}` rule that exceeded llama.cpp's grammar parser limit, crashing the grammar and falling back to unconstrained text output.
2. **Missing exec-approvals.json** — OpenClaw requires this file to exist before including the `exec` tool in the tool set at all.
3. **Poisoned conversation history** — 20,000+ tokens of "I don't have exec" responses confused the model even after fixes were applied.

## Fix
1. **Tool-filter proxy** (`tool-proxy.py`) — a small Python HTTP proxy running on port 8079, sitting between OpenClaw (:8079) and llama.cpp (:8080). It strips `sessions_spawn` from every chat completions request before llama.cpp sees it, preventing the grammar overflow.
2. **Recreated exec-approvals.json** — with correct format allowing `curl.exe`, `gh.exe`, `cmd.exe`, `powershell.exe`.
3. **Fresh session** — started a new conversation to clear poisoned history.

## Result
- Bot runs exec commands, fetches weather via curl, creates GitHub repos via gh CLI.
- Proxy auto-starts at login via Windows scheduled task.
