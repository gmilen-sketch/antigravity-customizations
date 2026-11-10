# Antigravity Customizations Suite — Script, Hook, Sidecar & MCP Workflow Directory (`v1.5.0`)

## 1. Lifecycle Hooks, Benchmark Runner & Security Gate (`hooks.json`, `src/hooks/` & `scripts/`)
| Hook / Script Module | Event / Mode Binding | Purpose |
| :--- | :--- | :--- |
| [**run_hook_safe.sh**](src/hooks/run_hook_safe.sh) | All Hook Events | Fail-open POSIX `/bin/sh` wrapper enforcing `PYTHONDONTWRITEBYTECODE=1`, `PYTHONSAFEPATH=1`, multi-path lookup, and `{}` vs `{"decision":"allow"}` fail-open. |
| [**execution_mode_router.py**](src/hooks/execution_mode_router.py) | `PreInvocation`, `Stop` | Classifies SWE/benchmark sandbox turns vs. enterprise domain turns and strips Turn-0 metadata/system blocks. |
| [**lazy_plugin_bootstrap.py**](src/hooks/lazy_plugin_bootstrap.py) | `PreInvocation` & CLI | `< 1 ms` warm check; initializes empty Knowledge Graph skeleton, backs up prior customizations (`--backup-existing`), and merges legacy configs (`--merge-legacy`). |
| [**multi_harness_hook_adapter.py**](src/hooks/multi_harness_hook_adapter.py) | All Hook Events | Bridges Antigravity (`PreInvocation`, `PostInvocation`, `PreToolUse`, `Stop`) and Claude Code (`UserPromptSubmit`, `PreToolUse`, `Stop`) hook payloads. |
| [**kg_pre_invocation_hook.py**](src/hooks/kg_pre_invocation_hook.py) | `PreInvocation` | Emits strict `HookSystemMessage`, `/dev/shm` turn-hook cache, Dual-Mode SWE classifier, `KG-N5` negation filter, and `okf:*` dossier grounding. |
| [**black_hat_in_progress_ux_hook.py**](src/hooks/black_hat_in_progress_ux_hook.py) | `PostInvocation` | Injects zero-token `[!WARNING]` UI verification banner, holds back `<artifact>.metadata.json` `userFacing` cards until Judge `APPROVED`, and rewrites subagent `Role` prefixes. |
| [**sentinel_dispatch.py**](src/hooks/sentinel_dispatch.py) | `PreToolUse` | Enforces `force_ask` destructive/control-plane mediation, `GOLDFISH-RO-1` read-only subagent command guard, `L3` identical-command anti-spin, and retired model blocks. |
| [**agent_stop_black_hat_gate.py**](src/hooks/agent_stop_black_hat_gate.py) | `Stop` | Enforces `v4.18` Adaptive `K=1..3` `[SHARD:<id>]` Multi-Goldfish -> Holistic Judge (`C6-Multi`/`C6-Holistic`) gate, `C3b` transcript mutation check, and `Case R` reactive unlock. |
| [**black_hat_analyzer.py**](src/hooks/black_hat_analyzer.py) | CLI / Pre-Commit | Static AST, JSON, silent-fallback, UTF-8/binary extension, corporate token, and 95-digest SHA-256 clean-room IP verifier (`--target <dir>`). |
| [**run_ab_benchmark.py**](scripts/run_ab_benchmark.py) | `--self-test` / CLI | Turnkey 28-task Paired Harness A/B Benchmark Orchestrator (`--mode dual-daemon` & `--mode harbor`) with Wilcoxon/McNemar statistics. |
| [**test_customizations_suite.py**](tests/test_customizations_suite.py) | Unittest Suite | Hermetic clean-room suite across [test_customizations_suite.py](tests/test_customizations_suite.py), [test_v140_wave12_and_hooks.py](tests/test_v140_wave12_and_hooks.py), and [test_v150_v390_sync_and_ip_audit.py](tests/test_v150_v390_sync_and_ip_audit.py). |

## 2. Sidecars (`sidecars.json` & `sidecars/`)
| Sidecar | Runtime Mode | Description |
| :--- | :--- | :--- |
| [**autonomy-dashboard**](sidecars/autonomy-dashboard/sidecar.json) | AuxPane Web UI | Interactive AuxPane UI (`server.py` / `main.mjs`) with `/preload.js` bridge, 17 CSS theme tokens, and live `/api/status` telemetry. |
| [**kg_cdc_watcher**](sidecars/kg_cdc_watcher/sidecar.json) | Background Daemon | Streams real-time file modification events (`watcher.py`) into Bitemporal Knowledge Graph memory. |
| [**daily-nightly-dreaming-engine**](sidecars/daily-nightly-dreaming-engine/sidecar.json) | Scheduled Cron | Runs nightly (`30 0 * * *`) ACT-R power-law decay, 7-day patch TTL checks, 8-Mutant Saboteur anti-overfitting gate, and KG consolidation. |

## 3. Eager-Loaded MCP Servers (`10` Servers in `mcp_config.json` & `.mcp.json`)
| MCP Server | Entrypoint | Transport & Loading |
| :--- | :--- | :--- |
| `autonomy_engine` | [mcp_autonomy_hub.py](src/autonomy_engine/mcp_autonomy_hub.py) | Stdio (`alwaysLoad: true`) |
| `knowledge_graph` | [kg_mcp_server.py](src/knowledge_graph/kg_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `diagram_renderer` | [diagram_mcp_server.py](src/diagram_renderer/diagram_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `six_hats_evaluator` | [six_hats_mcp_server.py](src/six_hats_evaluator/six_hats_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `playwright_scraper` | [playwright_mcp_server.py](src/playwright_scraper/playwright_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `deep_research` | [mcp_deep_research.py](src/mcp_deep_research.py) | Stdio (`alwaysLoad: true`) |
| `google_workspace` | [index.js](src/mcp_google_workspace/index.js) | Node Stdio (`alwaysLoad: true`) |
| `browser_cdp` | [browser_cdp_mcp.py](src/mcp_servers/browser_cdp_mcp.py) | Stdio (`alwaysLoad: true`) |
| `cloud_telemetry` | [cloud_telemetry_mcp.py](src/mcp_servers/cloud_telemetry_mcp.py) | Stdio (`alwaysLoad: true`) |
| `workspace_docs` | [workspace_docs_mcp.py](src/mcp_servers/workspace_docs_mcp.py) | Stdio (`alwaysLoad: true`) |
