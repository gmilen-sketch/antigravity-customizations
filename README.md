# Antigravity Customizations Suite (`v1.4.0`)

**Release:** `v1.4.0` &nbsp;|&nbsp; **Verification:** `27/27 Tests Passing` &nbsp;|&nbsp; **Primitives:** `7 Core + 4 Domain Packs` &nbsp;|&nbsp; **License:** [MIT](LICENSE)

**Quick Links:** [💬 Copy-Paste Agent Prompt](#-option-0-copy-paste-prompt-for-your-agent-harness-zero-manual-cli-required) • [📄 All Prompts (`DEPLOY_PROMPT.md`)](DEPLOY_PROMPT.md) • [🧩 4 Modular Packs](#-all-in-one-plugin-role-bundle--4-modular-domain-plugin-packs) • [📦 What Is Included](#-what-is-included-v140--19-clean-room-stability--wave-12-upgrades) • [📖 Skill & Subagent Directory (`AGENT_DIRECTORY.md`)](AGENT_DIRECTORY.md) • [⚙️ Workflow Directory (`WORKFLOW_DIRECTORY.md`)](WORKFLOW_DIRECTORY.md) • [🏗️ Architecture (`ARCHITECTURE.md`)](ARCHITECTURE.md)

* **100% Standalone Customer-Facing Customizations Package**: Bundles all **7 Antigravity Plugin Primitives** ([`plugin.json`](plugin.json) with `20` discovery `keywords`, [`20 PD-Q Skills`](skills/) with `7` Tier-1 [`skills.json`](skills.json) `include_only` token optimization, [`5 Subagents`](agents/) with subagent-scoped `hooks.json`, [`3 Arm B Sentinel Rules`](rules/), `jsonhook.ParseHooks()`-compliant [`hooks.json`](hooks.json) with [`run_hook_safe.sh`](src/hooks/run_hook_safe.sh) fail-open wrapper + Zero-Touch Turn-1 [`lazy_plugin_bootstrap.py`](src/hooks/lazy_plugin_bootstrap.py), [`7 Eager MCP Servers`](mcp_config.json), and [`3 Zero-Permission Sidecars`](sidecars.json)).
* **Modular & Multi-Harness Ready**: Ships with **4 Modular Domain Plugin Packs** ([`plugins/agy-*`](plugins/)), **Dual-Mode Execution Router** ([`src/hooks/execution_mode_router.py`](src/hooks/execution_mode_router.py)), **12 Wave-12 Graduated Slim Kernels (`AGW-W12-01..13`)**, **Prior Customization Backup & Non-Destructive Merge (`--backup-existing` / `--merge-legacy`)**, and an official **Role Bundle** ([`bundle-antigravity-customizations.json`](_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json)) — with **zero Web Hub server, zero external proxy, and zero Nginx/Terraform infrastructure**.
* **Supported Harnesses**: Loadable in one command into **Antigravity CLI (`agy`)**, **Antigravity 2.0 IDE / Web**, **Claude Code (`claude` CLI)**, **Cursor**, **Windsurf**, **Google Cloud Code**, or any MCP-compatible agent harness.

---

## 🚀 1-Command Quick Start & Copy-Paste Agent Deployment Prompt

### 💬 Option 0: Copy-Paste Prompt for Your Agent Harness (Zero Manual CLI Required)

Copy and paste the prompt below directly into **Antigravity 2.0 IDE**, **Antigravity Web Hub**, **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **Cursor**, **Windsurf**, or **Google Cloud Code** (additional modular and rollback prompts are in [`DEPLOY_PROMPT.md`](DEPLOY_PROMPT.md)):

```text
Deploy and verify the Antigravity Customizations Suite (v1.4.0) in this environment, safely backing up and reviewing any pre-existing user customizations, by executing these exact steps without interactive prompts:

1. Clone or update the clean-room repository into ~/antigravity-customizations:
   if [ -d "$HOME/antigravity-customizations/.git" ]; then
     git -C "$HOME/antigravity-customizations" fetch --depth 1 origin main && git -C "$HOME/antigravity-customizations" reset --hard origin/main
   else
     rm -rf "$HOME/antigravity-customizations"
     git clone --depth 1 https://github.com/gmilen-sketch/antigravity-customizations.git "$HOME/antigravity-customizations"
   fi

2. Back up any pre-existing user customizations (rules, skills, subagents, hooks.json, mcp_config.json, CLAUDE.md, .cursorrules) into ~/.gemini/antigravity/plugin_data/antigravity-customizations/legacy_standalone_backup/ before installing:
   python3 -B "$HOME/antigravity-customizations/src/hooks/lazy_plugin_bootstrap.py" --backup-existing --home "$HOME"

3. Install the Unified Plugin, 4 Modular Domain Packs (agy-core-governance, agy-knowledge-graph, agy-cloud-architect, agy-workspace-automation), Role Bundle, Bitemporal Knowledge Graph, 20 PD-Q Skills, 5 Subagents, 3 Arm B Rules, 3 ParseHooks Lifecycle Hooks, 7 Eager MCP Servers, and 3 Zero-Permission Sidecars, and run the built-in 7-primitive + unit-test verifier:
   cd "$HOME/antigravity-customizations" && ./scripts/install.sh --target all --verify

4. If the native `agy` CLI is available on PATH, also register the root plugin via:
   command -v agy >/dev/null 2>&1 && agy plugin install "$HOME/antigravity-customizations" || true

5. If an Antigravity 2.0 / Web Hub Language Server is listening locally on port 8080 or 8081, probe `/exa.language_server_pb.LanguageServerService/GetAllSkills`, `GetAllCustomAgentConfigs`, and `GetMcpServerStates` to confirm live runtime registration.

6. Review `~/.gemini/antigravity/plugin_data/antigravity-customizations/LEGACY_CUSTOMIZATIONS_REVIEW.md` (and `legacy_customizations_review.json`):
   - If pre-existing customizations were found (`discovered_count > 0`), list every backed-up rule, skill, subagent, hook, and MCP server, explain which items already coexist automatically (`AUTO_COEXISTING`) vs. which are ready to merge (`BACKED_UP_FOR_MERGE`), and offer to run `python3 -B "$HOME/antigravity-customizations/src/hooks/lazy_plugin_bootstrap.py" --merge-legacy --home "$HOME"` to non-destructively integrate custom rules (`legacy-user-customizations.md`), custom hooks, and custom MCP servers alongside the v1.4.0 suite.

7. Report a 3-column Markdown table (`Target | Behavior & Outcome | Status`) confirming all 7 customization primitives, pre-existing customization backup/integration status, and the clean-room unit test suite passed with exit code 0.
```

### Option A: Antigravity CLI (`agy`) & Antigravity 2.0 (v2.24.0+ / CLI v1.4.0+)

```bash
# Install directly via native Antigravity plugin manager:
agy plugin install .

# Or install the full plugin bundle + 4 modular domain plugins into ~/.gemini/config/plugins/ and verify:
./scripts/install.sh --target agy --verify

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
./scripts/install.sh --target all --verify
```

---

## 🧩 All-In-One Plugin, Role Bundle & 4 Modular Domain Plugin Packs

To prevent an all-or-nothing toggle in the Antigravity UI **Plugins** page, this repository provides the root all-in-one plugin ([`plugin.json`](plugin.json)), the curated role bundle ([`bundle.json`](_agents/bundles/enterprise_architect/bundle-antigravity-customizations.json)), and **4 modular domain plugins** under [`plugins/`](plugins/) (registered via [`plugins.json`](plugins.json)):

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

Run the 27-test verification suite ([`tests/test_customizations_suite.py`](tests/test_customizations_suite.py) + [`tests/test_v140_wave12_and_hooks.py`](tests/test_v140_wave12_and_hooks.py) — zero bytecode, zero Web Hub files, zero binary/internal leaks across all tracked files and `git log -p`, E2E 6-scenario Dreaming & Anti-Overfitting lifecycle, copy-paste deployment & legacy backup/merge verification, and all 19 `v1.4.0` stability + Wave-12 kernel assertions):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_customizations_suite.py -v
```
