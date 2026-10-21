# Antigravity Customizations Suite (v1.4.0 — Unified Plugin, Zero-Touch Turn-1 Reconciler, Dual-Mode Router & Wave-12 Kernels)

> **100% Standalone Customer-Facing Customizations Package** — Bundles all **7 Antigravity Plugin Primitives** (`plugin.json` with 20 discovery `keywords`, `20 PD-Q Skills` with 7 Tier-1 `include_only` token optimization, `5 Subagents` with subagent-scoped `hooks.json`, `3 Arm B Sentinel Rules`, `jsonhook.ParseHooks()`-compliant `hooks.json` with `run_hook_safe.sh` fail-open wrapper + Zero-Touch Turn-1 `lazy_plugin_bootstrap.py`, `7 Eager MCP Servers`, and `3 Zero-Permission Sidecars`) plus **4 Modular Domain Plugin Packs** (`plugins/agy-*`), **Dual-Mode Execution Router** (`src/hooks/execution_mode_router.py`), **12 Wave-12 Graduated Slim Kernels (`AGW-W12-01..13`)**, and an official **Role Bundle** (`_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json`) — with **zero Web Hub server, zero external proxy, and zero Nginx/Terraform infrastructure**.

Loadable in one command into **Antigravity CLI (`agy`)**, **Antigravity 2.0 IDE / Web**, **Claude Code (`claude` CLI)**, **Cursor**, **Windsurf**, **Google Cloud Code**, or any MCP-compatible agent harness.

---

## 🚀 1-Command Quick Start & Clean-Slate Uninstall

### Option A: Antigravity CLI (`agy`) & Antigravity 2.0 (v2.24.0+ / CLI v1.4.0+)

```bash
# Install directly via native Antigravity plugin manager:
agy plugin install .

# Or install the full plugin bundle + 4 modular domain plugins into ~/.gemini/config/plugins/:
./scripts/install.sh --target agy

# Clean-slate uninstall (restores backed-up standalone rules and removes plugin_data):
./scripts/uninstall.sh
```

### Option B: Claude Code (`claude` CLI)

```bash
# Install global Claude Code hooks, subagents (.claude/agents/), and 20 slash commands (.claude/commands/):
./scripts/install.sh --target claude-code

# Or run claude directly inside this repository (auto-loads CLAUDE.md, .claude/settings.json, and .mcp.json):
claude
```

### Option C: Cursor / Windsurf / Cloud Code / All Harnesses

```bash
# Install across all harnesses simultaneously:
./scripts/install.sh --target all
```

---

## 🧩 All-In-One Plugin, Role Bundle & 4 Modular Domain Plugin Packs

To prevent an all-or-nothing toggle in the Antigravity UI **Plugins** page, this repository provides the root all-in-one plugin (`antigravity-customizations`), the curated role bundle (`_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json`), and **4 modular domain plugins** under `plugins/` (registered via `plugins.json`):

| Plugin / Bundle | Path | Bundled Capabilities |
| :--- | :--- | :--- |
| **`antigravity-customizations` (All-In-One)** | `./plugin.json` | All `20` PD-Q skills (`7` Tier-1 in `skills.json` `include_only`), `5` subagents, `3` `Arm B` rules, `3` named hooks (`ParseHooks` schema), `7` MCP servers, and `3` sidecars (`autonomy-dashboard`, `kg_cdc_watcher`, `daily-nightly-dreaming-engine`) |
| **Role Bundle (`enterprise_architect`)** | `_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json` | Conforms to `bundle.schema.json` (`v1`), grouping the root plugin and 4 domain packs for team onboarding |
| **`agy-core-governance`** | `plugins/agy-core-governance/` | 14-Pillar P0/P1 Quality Engine, `black-hat-goldfish`, `black-hat-judge`, `black-hat-critic`, `PreToolUse` & `Stop` hooks, `autonomy_engine` & `six_hats_evaluator` MCPs |
| **`agy-knowledge-graph`** | `plugins/agy-knowledge-graph/` | Bitemporal Knowledge Graph (`OKF v0.2` + `resources/knowledge_graph.seed.json`), `PreInvocation` `lazy_plugin_bootstrap.py` + entity hook, `3` Sidecars, `dreaming-improvement-reasoner`, `workspace-housekeeper`, `knowledge_graph` MCP |
| **`agy-cloud-architect`** | `plugins/agy-cloud-architect/` | `5` Cloud Architecture, FinOps FOCUS CUD Audit, Migration Center, Deep Research, and Diagram Renderer skills + `diagram_renderer` & `deep_research` MCPs |
| **`agy-workspace-automation`** | `plugins/agy-workspace-automation/` | `6` Google Docs, Slides, Task Sync, Issue Tracker, Web Builder, and Playwright Browser skills + `google_workspace` & `playwright_scraper` MCPs |

---

## 📦 What Is Included (`v1.4.0` — 19 Clean-Room Stability & Wave-12 Upgrades)

| Category | Path | Count | Description |
|---|---|---|---|
| **Plugin, Bundle & Modular Manifests** | `plugin.json`, `_agents/bundles/`, `plugins/agy-*/` | `1` Root + `1` Bundle + `4` Packs | Strict manifest schema (`20` discovery `keywords`, zero deprecated duplicate `tags`), `displayName`, `logo`, 3 `suggestedPrompts`, and `bundle.schema.json` role bundle |
| **Fail-Open Wrapper & Dual-Mode Router** | `src/hooks/run_hook_safe.sh`, `src/hooks/execution_mode_router.py` | `< 1 ms` overhead | Fail-open POSIX `/bin/sh` wrapper (`PYTHONDONTWRITEBYTECODE=1`, `python3 -B`) + SWE sandbox vs. enterprise domain router stripping `<ADDITIONAL_METADATA>` and `<SYSTEM_MESSAGE>` |
| **Zero-Touch Turn-1 Reconciler & Seed KG** | `src/hooks/lazy_plugin_bootstrap.py` & `resources/knowledge_graph.seed.json` | `< 1 ms` warm / `< 25 ms` cold | Seeds `knowledge_graph.json` and `/dev/shm/kg_warm_cache.json`, backs up duplicate rules (`R1`), provisions `projects/automations.json` (`R5`), and guards non-dev adopter hosts (`NONDEV-BUG-1..3`) |
| **Zero-Permission Sidecar Suite** | `sidecars/` & `sidecars.json` | `3` Sidecars | `autonomy-dashboard` (`SIDECAR_UI_ENTRYPOINT_AUX_PANE`), `kg_cdc_watcher` (`watcher.py`), and `daily-nightly-dreaming-engine` (`builtin: "schedule"`), all with `PluginNeedsSetup == false` |
| **Native `ParseHooks` Lifecycle Hooks** | `hooks.json` & `agents/*/hooks.json` | `3` Root + `2` Subagent Hooks | Top-level named hooks (`sentinel-policy-guard`, `knowledge-graph-grounding`, `black-hat-completion-gate`) + subagent-scoped `agents/black-hat-{goldfish,judge}/hooks.json` (`R3`) |
| **Two-Tier `PD-Q` Skills & Routing Indexes** | `skills/`, `skills.json`, `AGENT_DIRECTORY.md`, `WORKFLOW_DIRECTORY.md` | `7` Tier-1 + `13` Tier-2 (`20` total) | `skills.json` `include_only` restricts always-on `<skills>` to 7 Tier-1 skills (`-58%` token drop) while `kg_pre_invocation_hook.py` dynamically activates Tier-2 skills |
| **`Arm B` High-Density Sentinel Rules** | `rules/{GEMINI,AGENTS,no-bullshit}.md` & `rules.json` | `3` Rules | Total size `< 7 KB` (`< 12%` of the `20,000`-token `defaultRulesBudget`) |
| **14-Pillar Autonomy Engine, Wave-12 Kernels & OKF v0.2** | `src/autonomy_engine/`, `src/knowledge_graph/`, `kb/` | `31` Python modules + `kb/` | P0 (`CB-1..CB-7`), P1 (`P1-CB-1..P1-CB-8`), Wave-12 kernels (`AGW-W12-01..13`), AAAK compressor, Polyphonic BM25F + Graph-RAG retriever, Self-Grill prior engine, 8-Mutant Saboteur gate |
| **Eager-Loaded MCP Servers** | `mcp_config.json` & `.mcp.json` | `7` MCP servers | Native `${PLUGIN_ROOT}` & `${PLUGIN_DATA}` expansion + `_meta: {"antigravity/alwaysLoad": true}` |

---

## 🧪 Verification & Clean-Room Audit

Run the 26-test verification suite (zero bytecode, zero Web Hub files, zero binary/internal leaks across all tracked files and `git log -p`, E2E 6-scenario Dreaming & Anti-Overfitting lifecycle, and all 19 `v1.4.0` stability + Wave-12 kernel assertions):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_customizations_suite.py -v
```
