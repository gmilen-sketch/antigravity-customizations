# Antigravity Customizations Suite — Script, Hook, Sidecar & MCP Workflow Directory (`v1.4.0`)

## 1. Lifecycle Hooks (`hooks.json` & `src/hooks/`)
| Hook Script | Event Binding | Purpose |
| :--- | :--- | :--- |
| `src/hooks/run_hook_safe.sh` | All Hook Events (`PreInvocation`, `PreToolUse`, `Stop`) | Fail-open POSIX `/bin/sh` wrapper enforcing `PYTHONDONTWRITEBYTECODE=1` and `python3 -B` with fallback JSON (`{}` or `{"decision":"allow"}`). |
| `src/hooks/execution_mode_router.py` | `PreInvocation`, `Stop` | Classifies SWE/benchmark sandbox turns vs. enterprise domain turns and strips Turn-0 `<ADDITIONAL_METADATA>` / `<SYSTEM_MESSAGE>` blocks (`RC-1` / `L3b`). |
| `src/hooks/lazy_plugin_bootstrap.py` | `PreInvocation` (Handler 1) & CLI (`--backup-existing`, `--merge-legacy`) | `< 1 ms` warm-path check; cold-start seeds Knowledge Graph (`resources/knowledge_graph.seed.json`), backs up prior customizations (`--backup-existing` + `LEGACY_CUSTOMIZATIONS_REVIEW.md`), merges legacy rules/hooks/MCPs (`--merge-legacy`), provisions `projects/automations.json` (`R5`), and detects non-dev adopter hosts (`NONDEV-BUG-1..3`). |
| `src/hooks/multi_harness_hook_adapter.py` | `PreInvocation`, `PreToolUse`, `Stop` | Normalizes Antigravity (`rootConversationId`, `toolName`, `toolArgs`) and Claude Code (`session_id`, `tool_name`, `tool_input`) hook payloads. |
| `src/hooks/kg_pre_invocation_hook.py` | `PreInvocation` (Handler 2) | Resolves sub-millisecond Knowledge Graph entities from `/dev/shm/kg_warm_cache.json`, suppresses negated terms (`KG-N5`), deduplicates Turn-0 ephemeral kernels (`EPH-ONCE-01`), and enforces strict `hooks.proto` `PreInvocationHookResult`. |
| `src/hooks/sentinel_dispatch.py` | `PreToolUse` | Normalizes dual tool schemas (`AGW-W12-11`), enforces destructive command protection, file bounds, model catalog hygiene (`Rule #28`), control-plane boundary checks (`AGW-W12-05`), and code-safe PII anonymization (`AGW-W12-07`). |
| `src/hooks/agent_stop_black_hat_gate.py` | `Stop` | Enforces the 2-Stage `black-hat-goldfish` -> `black-hat-judge` completion gate when `mutations > 0`, with `Case R` reactive `/task-` wakeup unlock and `LL-2` pre-return hygiene checks. |
| `src/hooks/black_hat_analyzer.py` | CLI / Pre-Commit | Static AST, JSON, silent-fallback, and SHA-256 clean-room IP verifier (`--target <dir>`). |
| `tests/test_customizations_suite.py` & `tests/test_v140_wave12_and_hooks.py` | Unittest Suite (`27` Tests) | Clean-room verification suite covering all 7 primitives, copy-paste deployment & legacy backup/merge, 6-scenario Dreaming lifecycle, and all 19 `v1.4.0` hook stability fixes + Wave-12 slim kernels (`AGW-W12-01..13`). |

## 2. Sidecars (`sidecars.json` & `sidecars/`)
| Sidecar ID | Manifest Path | Runtime Mode | Description |
| :--- | :--- | :--- | :--- |
| `autonomy-dashboard` | `sidecars/autonomy-dashboard/sidecar.json` | `SIDECAR_UI_ENTRYPOINT_AUX_PANE` (`server.py` / `main.mjs`) | Interactive AuxPane Web UI with `/preload.js` bridge, 17 modern root CSS theme tokens, and live `/api/status` telemetry. |
| `kg_cdc_watcher` | `sidecars/kg_cdc_watcher/sidecar.json` | Background daemon (`watcher.py`) | Streams real-time file modification events into Bitemporal Knowledge Graph memory (`/dev/shm/kg_cdc_events.jsonl`). |
| `daily-nightly-dreaming-engine` | `sidecars/daily-nightly-dreaming-engine/sidecar.json` | Scheduled cron (`30 0 * * *`) | Runs nightly ACT-R power-law decay, 8-Mutant Saboteur anti-overfitting checks, and Knowledge Graph consolidation. |

## 3. Eager-Loaded MCP Servers (`mcp_config.json` & `.mcp.json`)
| MCP Server Key | Entrypoint | Transport & Loading |
| :--- | :--- | :--- |
| `autonomy_engine` | `src/autonomy_engine/mcp_autonomy_hub.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `knowledge_graph` | `src/knowledge_graph/kg_mcp_server.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `diagram_renderer` | `src/diagram_renderer/diagram_mcp_server.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `six_hats_evaluator` | `src/six_hats_evaluator/six_hats_mcp_server.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `playwright_scraper` | `src/playwright_scraper/playwright_mcp_server.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `deep_research` | `src/mcp_deep_research.py` | Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
| `google_workspace` | `src/mcp_google_workspace/index.js` | Node Stdio (`_meta: {"antigravity/alwaysLoad": true}`) |
