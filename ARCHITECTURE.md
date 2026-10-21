# Architecture — Antigravity Customizations Suite (v1.0.0)

## 1. Design Philosophy: Pure Customizations, Zero Server Infrastructure

Unlike `antigravity-web-hub` (which bundles the self-hosted Web IDE reverse proxy, Vertex AI protocol gateway, `bootstrap.js` browser polyfill, Nginx, and Terraform), **`antigravity-customizations`** contains **strictly the portable agentic customizations**.

## 2. Cross-Harness Compatibility Matrix

| Feature | Antigravity CLI (`agy`) & 2.0 | Claude Code (`claude`) | Cursor / Windsurf / Cloud Code |
|---|---|---|---|
| **Plugin / Manifest Entrypoint** | `plugin.json`, `.antigravity-plugin/plugin.json` | `CLAUDE.md`, `.claude/settings.json` | `AGENTS.md`, `.cursorrules`, `.mcp.json` |
| **Pre-Turn Grounding Hook** | `PreInvocation` (`kg_pre_invocation_hook.py`) | `UserPromptSubmit` (`multi_harness_hook_adapter.py`) | MCP `query_knowledge_graph` / `kg_search_entities` |
| **Pre-Tool Safety Gate** | `PreToolUse` (`sentinel_dispatch.py`) | `PreToolUse` (`multi_harness_hook_adapter.py`) | MCP `verify_quality_circuit_breakers` |
| **Adversarial Stop Gate** | `Stop` (`agent_stop_black_hat_gate.py`) | `Stop` (`multi_harness_hook_adapter.py`) | `.claude/agents/black-hat-{goldfish,judge}.md` |
| **20 `PD-Q` Skills** | `skills/<name>/SKILL.md` (`skills.json`) | `.claude/commands/<name>.md` (`/<name>`) | `.agents/skills/<name>/SKILL.md` |
| **5 Custom Subagents** | `agents/<name>/agent.md` (`preloadSkills`) | `.claude/agents/<name>.md` | `.agents/agents/<name>/agent.md` |
| **7 MCP Servers** | `mcp_config.json` (`_meta.antigravity/alwaysLoad`) | `.mcp.json` | `.mcp.json` |
