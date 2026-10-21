# Changelog

## [1.4.0] - 2026-10-21

### Added
- **7 Group A Hook, Runtime & Manifest Stability Fixes**: Fail-open POSIX hook wrapper (`src/hooks/run_hook_safe.sh`), `KG-N5` negation filter + `EPH-ONCE-01` session dedup + `RC-8` strict `PreInvocationHookResult` schema (`src/hooks/kg_pre_invocation_hook.py`), `AGW-W12-11` dual `PreToolUse` payload normalizer + `{}` on `PostToolUse` (`src/hooks/sentinel_dispatch.py`), `Case R` reactive subagent wakeup (`src/hooks/agent_stop_black_hat_gate.py`), SWE sandbox vs. enterprise domain execution mode router (`src/hooks/execution_mode_router.py`), `NONDEV-BUG-1..3` non-dev adopter guard (`src/hooks/lazy_plugin_bootstrap.py`), and removal of deprecated duplicate `"tags"` from all 8 `plugin.json` manifests.
- **12 Group B Wave-12 Graduated Slim Kernels (`AGW-W12-01..13`)**: Waterfilling + Bradley-Terry + G-Theory consensus and cached transcript re-judging (`unified_eval_router.py`), Kitagawa-Oaxaca mix-shift attribution (`dreaming_engine.py`), compaction boundary audit (`resilient_steer_harvester.py`), traceback-preserving tail slicer (`single_turn_replay.py`), untrusted comment author & shell boundary guard (`r31_hook_integrity_guard.py`), code-safe PII scrubber (`rule_11_anonymization.py`), Popperian counterexample veto (`delphi_six_hats_task_router.py`), sidecar/hook surface security scanner (`workspace_hygiene_gate.py`), commitment follow-up decay & Tab 1 stability auditor (`agent_ssot_formatter.py`), and SQLite WAL flush before headless CDP (`cdp_navigator.py`).
- **Foundational Knowledge Graph Seed & Hermetic Test Suite**: Seeded 17 foundational + core architectural KG nodes (`31` edges) in `src/knowledge_graph/init_knowledge_graph.py` and verified `26/26` hermetic unit tests (`tests/test_customizations_suite.py` + `tests/test_v140_wave12_and_hooks.py`).

## [1.0.0] - 2026-10-16

### Added
- **Initial Clean-Room Release of `antigravity-customizations`**: Extracted all 14 Autonomy Engine pillars, Bitemporal Knowledge Graph (`OKF v0.2`), 20 `PD-Q` skills, 5 custom subagents (`preloadSkills`), 3 lifecycle hooks (`rootConversationId` support), and 7 FastMCP/Node MCP servers (`_meta: {"antigravity/alwaysLoad": true}`) into a standalone customer-facing repository with zero Web Hub / external proxy dependencies.
- **Universal Multi-Harness Adapter (`src/hooks/multi_harness_hook_adapter.py`) & Installer (`scripts/install.sh`)**: Added native support for Antigravity CLI (`agy`), Antigravity 2.0 IDE/Web, Claude Code (`CLAUDE.md`, `.claude/settings.json`, `.claude/agents/*.md`, `.claude/commands/*.md`, `.mcp.json`), Cursor (`.cursorrules`), and Cloud Code (`AGENTS.md`, `GEMINI.md`).
