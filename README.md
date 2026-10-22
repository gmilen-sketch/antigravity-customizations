# Antigravity Customizations Suite (v1.4.0)

**Release:** `v1.4.0` · **Tests:** `27/27 Passing` · **Scope:** `7 Primitives + 4 Domain Packs` · **License:** [MIT](LICENSE)

**Quick Links:** [Copy-Paste Prompt](#-option-0-copy-paste-prompt-for-your-agent-harness) · [All Prompts](DEPLOY_PROMPT.md) · [4 Domain Packs](#-all-in-one-plugin-role-bundle--4-modular-domain-plugin-packs) · [Included Components](#-what-is-included-v140--19-clean-room-stability--wave-12-upgrades) · [Skills & Subagents](AGENT_DIRECTORY.md) · [Workflows & MCPs](WORKFLOW_DIRECTORY.md) · [Architecture](ARCHITECTURE.md)

* **Complete 7-Primitive Customizations Suite**: Ships [plugin.json](plugin.json) (20 discovery keywords), [20 PD-Q Skills](skills/) (7 Tier-1 in [skills.json](skills.json)), [5 Subagents](agents/) with scoped hooks, [3 Arm B Rules](rules/), `ParseHooks`-compliant [hooks.json](hooks.json) with [run_hook_safe.sh](src/hooks/run_hook_safe.sh) and Turn-1 [lazy_plugin_bootstrap.py](src/hooks/lazy_plugin_bootstrap.py), [7 Eager MCP Servers](mcp_config.json), and [3 Zero-Permission Sidecars](sidecars.json).
* **Modular Packs, Wave-12 Kernels & Safe Legacy Merge**: Includes [4 Modular Domain Packs](plugins/), the [Dual-Mode Router](src/hooks/execution_mode_router.py), 12 Wave-12 slim kernels (`AGW-W12-01` to `13`), automatic backup and non-destructive merge of prior user customizations (`--backup-existing` and `--merge-legacy`), and the [Enterprise Role Bundle](_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json) — with zero Web Hub server or proxy bloat.
* **Cross-Harness Ready**: Installs in one command across **Antigravity CLI** (`agy`), **Antigravity 2.0 IDE / Web**, **Claude Code** (`claude`), **Cursor**, **Windsurf**, **Google Cloud Code**, and any MCP-compatible harness.

---

## 🚀 1-Command Quick Start & Copy-Paste Agent Deployment Prompt

### 💬 Option 0: Copy-Paste Prompt for Your Agent Harness

Paste this prompt directly into **Antigravity 2.0 IDE / Web**, **Antigravity CLI**, **Claude Code**, **Cursor**, **Windsurf**, or **Cloud Code** (4 additional modular, legacy-merge, and rollback prompts are in [DEPLOY_PROMPT.md](DEPLOY_PROMPT.md)):

```text
Deploy and verify the Antigravity Customizations Suite (v1.4.0) without interactive
prompts, safely backing up and reviewing any pre-existing user customizations:

1. Clone or update the clean-room repository into ~/antigravity-customizations:
   git clone --depth 1 \
     https://github.com/gmilen-sketch/antigravity-customizations.git \
     "$HOME/antigravity-customizations" 2>/dev/null || \
   (git -C "$HOME/antigravity-customizations" fetch --depth 1 origin main && \
    git -C "$HOME/antigravity-customizations" reset --hard origin/main)

2. Back up pre-existing rules, skills, subagents, hooks, and MCP configs, install
   all 7 primitives + 4 domain packs, and run the 27-test verification suite:
   cd "$HOME/antigravity-customizations" && \
     python3 -B src/hooks/lazy_plugin_bootstrap.py --backup-existing --home "$HOME" && \
     ./scripts/install.sh --target all --verify && \
     (command -v agy >/dev/null 2>&1 && agy plugin install "$PWD" || true)

3. If a local Antigravity Language Server is listening on port 8080 or 8081, probe
   GetAllSkills, GetAllCustomAgentConfigs, and GetMcpServerStates to confirm live load.

4. Inspect ~/.gemini/antigravity/plugin_data/antigravity-customizations/
   LEGACY_CUSTOMIZATIONS_REVIEW.md: if pre-existing customizations were found, list
   what coexists automatically vs. what can be merged via `lazy_plugin_bootstrap.py
   --merge-legacy --home "$HOME"`, and output a 3-column verification table.
```

### Option A: Antigravity CLI (`agy`) & Antigravity 2.0 (v2.24.0+ / CLI v1.4.0+)

```bash
# Install directly via native Antigravity plugin manager:
agy plugin install .

# Or install the full plugin bundle + 4 domain packs and verify:
./scripts/install.sh --target agy --verify

# Clean-slate uninstall (restores backed-up rules and removes plugin_data):
./scripts/uninstall.sh
```

### Option B: Claude Code (`claude` CLI)

```bash
# Install global Claude Code hooks, subagents, and 20 slash commands:
./scripts/install.sh --target claude-code

# Or run claude inside this repo (loads CLAUDE.md, settings.json, .mcp.json):
claude
```

### Option C: Cursor / Windsurf / Cloud Code / All Harnesses

```bash
# Install across all harnesses simultaneously:
./scripts/install.sh --target all --verify
```

---

## 🧩 All-In-One Plugin, Role Bundle & 4 Modular Domain Plugin Packs

To prevent an all-or-nothing toggle in the Antigravity UI **Plugins** page, this repository provides the root all-in-one plugin ([plugin.json](plugin.json)), the curated role bundle ([bundle.json](_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json)), and **4 modular domain plugins** under [plugins/](plugins/) (registered via [plugins.json](plugins.json)):

| Plugin / Bundle | Scope | Bundled Capabilities |
| :--- | :--- | :--- |
| [**All-In-One Plugin**](plugin.json) | Root Suite | All 20 PD-Q skills (7 Tier-1 in [skills.json](skills.json)), 5 subagents, 3 Arm B rules, 3 named hooks, 7 MCP servers, and 3 sidecars (AuxPane UI, CDC Watcher, Nightly Dreaming) |
| [**Enterprise Role Bundle**](_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json) | Team Bundle | Conforms to `bundle.schema.json` (`v1`), grouping the root plugin and 4 domain packs for one-step team onboarding |
| [**Core Governance**](plugins/agy-core-governance/) | P0/P1 & Gate | 14-Pillar P0/P1 Quality Engine, Goldfish, Judge, and Critic subagents, `PreToolUse` & `Stop` hooks, Autonomy & Six-Hats MCPs |
| [**Knowledge Graph**](plugins/agy-knowledge-graph/) | OKF v0.2 & CDC | Bitemporal Knowledge Graph ([seed.json](resources/knowledge_graph.seed.json)), `PreInvocation` [bootstrap](src/hooks/lazy_plugin_bootstrap.py) + entity hook, 3 sidecars, Dreaming & Housekeeper subagents, KG MCP |
| [**Cloud Architect**](plugins/agy-cloud-architect/) | Cloud & FinOps | 5 Cloud Architecture, FinOps FOCUS CUD Audit, Migration Center, Deep Research, and Diagram Renderer skills + Diagram & Research MCPs |
| [**Workspace Automation**](plugins/agy-workspace-automation/) | Docs & Browser | 6 Google Docs, Slides, Task Sync, Issue Tracker, Web Builder, and Playwright Browser skills + Workspace & Playwright MCPs |

---

## 📦 What Is Included (`v1.4.0` — 19 Clean-Room Stability & Wave-12 Upgrades)

| Component | Count | Capabilities |
| :--- | :--- | :--- |
| [**Plugin & Pack Manifests**](plugin.json) | 6 Manifests | Root [plugin.json](plugin.json) (20 discovery keywords, [logo](assets/logo.svg), 3 suggested prompts), [role bundle](_agents/bundles/enterprise_architect/), and 4 modular [domain packs](plugins/) |
| [**Fail-Open Hook & Router**](src/hooks/run_hook_safe.sh) | `< 1 ms` | Fail-open POSIX wrapper ([run_hook_safe.sh](src/hooks/run_hook_safe.sh)) + dual-mode router ([execution_mode_router.py](src/hooks/execution_mode_router.py)) stripping metadata/system blocks |
| [**Turn-1 Reconciler & Seed KG**](src/hooks/lazy_plugin_bootstrap.py) | `< 1 ms` warm | Seeds [knowledge_graph.seed.json](resources/knowledge_graph.seed.json), backs up prior customizations (`--backup-existing`), reviews & merges legacy configs (`--merge-legacy`) |
| [**Zero-Permission Sidecars**](sidecars.json) | 3 Sidecars | [AuxPane Dashboard](sidecars/autonomy-dashboard/sidecar.json), [KG CDC Watcher](sidecars/kg_cdc_watcher/sidecar.json), and [Nightly Dreaming](sidecars/daily-nightly-dreaming-engine/sidecar.json), all zero-permission |
| [**Lifecycle & Subagent Hooks**](hooks.json) | 5 Hooks | 3 root `ParseHooks` hooks ([hooks.json](hooks.json)) + 2 subagent-scoped hooks for [Goldfish](agents/black-hat-goldfish/hooks.json) and [Judge](agents/black-hat-judge/hooks.json) |
| [**Two-Tier PD-Q Skills**](AGENT_DIRECTORY.md) | 20 Skills | 7 Tier-1 always-on skills in [skills.json](skills.json) (`-58%` token drop) + 13 Tier-2 skills activated dynamically by [kg_pre_invocation_hook.py](src/hooks/kg_pre_invocation_hook.py) |
| [**Arm B Sentinel Rules**](rules.json) | 3 Rules | [GEMINI.md](rules/GEMINI.md), [AGENTS.md](rules/AGENTS.md), and [no-bullshit.md](rules/no-bullshit.md) (`< 7 KB` total, `< 12%` of rule budget) |
| [**14-Pillar Engine & Wave-12**](src/autonomy_engine/) | 31 Modules | P0/P1 circuit breakers, 12 Wave-12 slim kernels, AAAK compressor, [BM25F + Graph-RAG](src/knowledge_graph/), [OKF v0.2 kb/](kb/), and 8-Mutant Saboteur gate |
| [**Eager-Loaded MCP Servers**](mcp_config.json) | 7 Servers | [mcp_config.json](mcp_config.json) & [.mcp.json](.mcp.json) with native `${PLUGIN_ROOT}` expansion and `alwaysLoad: true` |

---

## 🧪 Verification & Clean-Room Audit

Run the 27-test verification suite ([tests/test_customizations_suite.py](tests/test_customizations_suite.py) and [tests/test_v140_wave12_and_hooks.py](tests/test_v140_wave12_and_hooks.py) — zero bytecode, zero Web Hub files, zero binary/internal leaks across all tracked files and `git log -p`, E2E 6-scenario Dreaming & Anti-Overfitting lifecycle, copy-paste deployment & legacy backup/merge verification, and all 19 `v1.4.0` stability + Wave-12 kernel assertions):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_customizations_suite.py -v
```
