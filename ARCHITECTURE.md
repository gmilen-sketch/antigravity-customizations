# Architecture — Antigravity Customizations Suite (v1.4.0)

## 1. Design Philosophy: Pure Customizations, Zero Server Infrastructure

Unlike `antigravity-web-hub` (which bundles the self-hosted Web IDE reverse proxy, Vertex AI protocol gateway, `bootstrap.js` browser polyfill, Nginx, and Terraform), **`antigravity-customizations`** contains **strictly the portable agentic customizations**.

## 2. Cross-Harness Compatibility Matrix

| Feature | Antigravity (`agy` & 2.0) | Claude Code (`claude`) | Cursor / Windsurf / Cloud Code |
| :--- | :--- | :--- | :--- |
| **Manifest Entrypoint** | [plugin.json](plugin.json), [hooks.json](hooks.json) | [CLAUDE.md](CLAUDE.md), [.claude/settings.json](.claude/settings.json) | [AGENTS.md](AGENTS.md), [.cursorrules](.cursorrules), [.mcp.json](.mcp.json) |
| **Pre-Turn Grounding** | `PreInvocation` ([kg_pre_invocation](src/hooks/kg_pre_invocation_hook.py)) | `UserPromptSubmit` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | MCP `query_knowledge_graph` |
| **Pre-Tool Safety Gate** | `PreToolUse` ([sentinel_dispatch](src/hooks/sentinel_dispatch.py)) | `PreToolUse` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | MCP `verify_quality_circuit_breakers` |
| **Adversarial Stop Gate** | `Stop` ([black_hat_gate](src/hooks/agent_stop_black_hat_gate.py)) | `Stop` ([adapter](src/hooks/multi_harness_hook_adapter.py)) | [Goldfish](.claude/agents/black-hat-goldfish.md) & [Judge](.claude/agents/black-hat-judge.md) |
| **20 PD-Q Skills** | [skills/](skills/) & [skills.json](skills.json) | [.claude/commands/](.claude/commands/) (`/<name>`) | `.agents/skills/<name>/SKILL.md` |
| **5 Custom Subagents** | [agents/](agents/) (`preloadSkills`) | [.claude/agents/](.claude/agents/) | `.agents/agents/<name>/agent.md` |
| **7 MCP Servers** | [mcp_config.json](mcp_config.json) (`alwaysLoad`) | [.mcp.json](.mcp.json) | [.mcp.json](.mcp.json) |
