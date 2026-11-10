# Architecture — Antigravity Customizations Suite (v1.5.0)

## 1. Design Philosophy: Pure Customizations, Zero Server Infrastructure

Unlike `antigravity-web-hub` (which bundles the self-hosted Web IDE reverse proxy, Vertex AI protocol gateway, `bootstrap.js` browser polyfill, Nginx, and Terraform), **`antigravity-customizations`** contains **strictly the portable agentic customizations** synchronized with Antigravity Web Hub `v3.9.0` (Antigravity Core `2.29.1+` & CLI `1.5.3+`).

## 2. Cross-Harness Compatibility Matrix

| Feature | Antigravity (`agy` & 2.29+) | Claude Code (`claude`) | Cursor / Windsurf / Cloud Code |
| :--- | :--- | :--- | :--- |
| **Manifest Entrypoint** | [plugin.json](plugin.json), [hooks.json](hooks.json) | [CLAUDE.md](CLAUDE.md), [.claude/settings.json](.claude/settings.json) | [AGENTS.md](AGENTS.md), [.cursorrules](.cursorrules), [.mcp.json](.mcp.json) |
| **Pre-Turn Grounding** | `PreInvocation` ([kg_pre_invocation](src/hooks/kg_pre_invocation_hook.py) `HookSystemMessage`) | `UserPromptSubmit` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | MCP `query_knowledge_graph` |
| **In-Progress UX Holdback** | `PostInvocation` ([ux_hook](src/hooks/black_hat_in_progress_ux_hook.py)) | [adapter](src/hooks/multi_harness_hook_adapter.py) | Native Markdown alert cards |
| **Pre-Tool Safety Gate** | `PreToolUse` ([sentinel_dispatch](src/hooks/sentinel_dispatch.py) `force_ask` + `GOLDFISH-RO-1`) | `PreToolUse` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | MCP `verify_quality_circuit_breakers` |
| **Adversarial Stop Gate** | `Stop` ([black_hat_gate](src/hooks/agent_stop_black_hat_gate.py) `v4.18` `K=1..3` shards) | `Stop` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | [Goldfish](.claude/agents/black-hat-goldfish.md) & [Judge](.claude/agents/black-hat-judge.md) |
| **20 PD-Q Skills** | [skills/](skills/) & [skills.json](skills.json) | [.claude/commands/](.claude/commands/) (`/<name>`) | `.agents/skills/<name>/SKILL.md` |
| **5 Custom Subagents** | [agents/](agents/) (`preloadSkills` + `hooks.json`) | [.claude/agents/](.claude/agents/) | `.agents/agents/<name>/agent.md` |
| **10 MCP Servers** | [mcp_config.json](mcp_config.json) (`alwaysLoad`) | [.mcp.json](.mcp.json) | [.mcp.json](.mcp.json) |
