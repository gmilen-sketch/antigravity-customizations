# Antigravity Customizations Suite — Script, Hook, Sidecar & MCP Workflow Directory (`v1.4.0`)

## 1. Lifecycle Hooks (`hooks.json` & `src/hooks/`)
| Hook / Test Module | Event Binding | Purpose |
| :--- | :--- | :--- |
| [**run_hook_safe.sh**](src/hooks/run_hook_safe.sh) | All Hook Events | Fail-open POSIX `/bin/sh` wrapper enforcing `PYTHONDONTWRITEBYTECODE=1` and `python3 -B` with fallback JSON. |
| [**execution_mode_router.py**](src/hooks/execution_mode_router.py) | `PreInvocation`, `Stop` | Classifies SWE/benchmark sandbox turns vs. enterprise domain turns and strips Turn-0 metadata/system blocks. |
| [**lazy_plugin_bootstrap.py**](src/hooks/lazy_plugin_bootstrap.py) | `PreInvocation` & CLI | `< 1 ms` warm check; seeds Knowledge Graph, backs up prior customizations (`--backup-existing`), and merges legacy configs (`--merge-legacy`). |
| [**multi_harness_hook_adapter.py**](src/hooks/multi_harness_hook_adapter.py) | All Hook Events | Normalizes Antigravity (`rootConversationId`, `toolName`) and Claude Code (`session_id`, `tool_name`) hook payloads. |
| [**kg_pre_invocation_hook.py**](src/hooks/kg_pre_invocation_hook.py) | `PreInvocation` | Resolves Knowledge Graph entities from warm cache, suppresses negated terms (`KG-N5`), and deduplicates Turn-0 kernels. |
| [**sentinel_dispatch.py**](src/hooks/sentinel_dispatch.py) | `PreToolUse` | Normalizes dual tool schemas (`AGW-W12-11`), blocks destructive commands, and enforces model catalog & PII hygiene. |
| [**agent_stop_black_hat_gate.py**](src/hooks/agent_stop_black_hat_gate.py) | `Stop` | Enforces the 2-Stage Goldfish -> Judge completion gate when `mutations > 0`, with `Case R` reactive wakeup unlock. |
| [**black_hat_analyzer.py**](src/hooks/black_hat_analyzer.py) | CLI / Pre-Commit | Static AST, JSON, silent-fallback, and SHA-256 clean-room IP verifier (`--target <dir>`). |
| [**test_customizations_suite.py**](tests/test_customizations_suite.py) | Unittest (`27` Tests) | Runs 21 core tests + 6 Wave-12/hook tests in [test_v140_wave12_and_hooks.py](tests/test_v140_wave12_and_hooks.py). |

## 2. Sidecars (`sidecars.json` & `sidecars/`)
| Sidecar | Runtime Mode | Description |
| :--- | :--- | :--- |
| [**autonomy-dashboard**](sidecars/autonomy-dashboard/sidecar.json) | AuxPane Web UI | Interactive AuxPane UI (`server.py` / `main.mjs`) with `/preload.js` bridge, 17 CSS theme tokens, and live `/api/status` telemetry. |
| [**kg_cdc_watcher**](sidecars/kg_cdc_watcher/sidecar.json) | Background Daemon | Streams real-time file modification events (`watcher.py`) into Bitemporal Knowledge Graph memory. |
| [**daily-nightly-dreaming-engine**](sidecars/daily-nightly-dreaming-engine/sidecar.json) | Scheduled Cron | Runs nightly (`30 0 * * *`) ACT-R power-law decay, 8-Mutant Saboteur anti-overfitting checks, and KG consolidation. |

## 3. Eager-Loaded MCP Servers (`mcp_config.json` & `.mcp.json`)
| MCP Server | Entrypoint | Transport & Loading |
| :--- | :--- | :--- |
| `autonomy_engine` | [mcp_autonomy_hub.py](src/autonomy_engine/mcp_autonomy_hub.py) | Stdio (`alwaysLoad: true`) |
| `knowledge_graph` | [kg_mcp_server.py](src/knowledge_graph/kg_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `diagram_renderer` | [diagram_mcp_server.py](src/diagram_renderer/diagram_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `six_hats_evaluator` | [six_hats_mcp_server.py](src/six_hats_evaluator/six_hats_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `playwright_scraper` | [playwright_mcp_server.py](src/playwright_scraper/playwright_mcp_server.py) | Stdio (`alwaysLoad: true`) |
| `deep_research` | [mcp_deep_research.py](src/mcp_deep_research.py) | Stdio (`alwaysLoad: true`) |
| `google_workspace` | [index.js](src/mcp_google_workspace/index.js) | Node Stdio (`alwaysLoad: true`) |
