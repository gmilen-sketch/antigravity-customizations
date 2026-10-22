# Copy-Paste Agent Deployment Prompts (`v1.4.0`)

Copy and paste any of the prompts below directly into **Antigravity 2.0 IDE**, **Antigravity Web Hub**, **Antigravity CLI (`agy`)**, **Claude Code (`claude`)**, **Cursor**, **Windsurf**, or **Google Cloud Code**. Your agent will autonomously back up any pre-existing user customizations, clone and install all 7 customization primitives, run the full clean-room verification suite, review how your backed-up customizations can be integrated alongside the deployed suite, and output a 3-column readiness scorecard.

---

## 🚀 Prompt 1: Full Zero-Touch Deployment, Pre-Existing Backup & Integration Review (Recommended)

Paste this prompt into a fresh or existing agent session to deploy the complete **Antigravity Customizations Suite (`v1.4.0`)** while safely backing up and reviewing any prior customizations:

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

---

## 🔄 Prompt 2: One-Step Integration of Backed-Up User Customizations (`--merge-legacy`)

If **Prompt 1** detected pre-existing customizations in `LEGACY_CUSTOMIZATIONS_REVIEW.md` (`discovered_count > 0`), paste this prompt to automatically merge them alongside the deployed `v1.4.0` suite without overwriting any of the 7 core primitives:

```text
Run `python3 -B "$HOME/antigravity-customizations/src/hooks/lazy_plugin_bootstrap.py" --merge-legacy --home "$HOME"` to integrate my backed-up custom rules into `~/.gemini/config/rules/legacy-user-customizations.md`, merge my custom top-level hooks into `~/.gemini/config/hooks.json`, and merge my custom `mcpServers` entries into `~/.gemini/config/mcp_config.json`, then verify with `cd "$HOME/antigravity-customizations" && ./scripts/install.sh --target all --verify`.
```

---

## 🧩 Prompt 3: Selective Modular Domain Pack Deployment (Antigravity 2.0 UI / CLI)

Paste this prompt if you want to install the suite for **Antigravity 2.0 / `agy` CLI only** and selectively toggle the 4 modular domain packs (`agy-core-governance`, `agy-knowledge-graph`, `agy-cloud-architect`, `agy-workspace-automation`):

```text
Clone https://github.com/gmilen-sketch/antigravity-customizations.git into ~/antigravity-customizations, run `./scripts/install.sh --target agy --verify`, inspect `~/.gemini/antigravity/plugin_data/antigravity-customizations/LEGACY_CUSTOMIZATIONS_REVIEW.md` for any backed-up user customizations, and list the 5 installed plugin directories under ~/.gemini/config/plugins/ (`antigravity-customizations`, `agy-core-governance`, `agy-knowledge-graph`, `agy-cloud-architect`, `agy-workspace-automation`) in a 3-column status table.
```

---

## 🧹 Prompt 4: Clean-Slate Rollback & Uninstall Prompt

Paste this prompt to cleanly remove all installed customizations and restore any backed-up user rules:

```text
Run `"$HOME/antigravity-customizations/scripts/uninstall.sh"` to remove the Antigravity Customizations Suite, restore any backed-up standalone rules in ~/.gemini/config/rules/, and verify that ~/.gemini/config/plugins/antigravity-customizations has been cleanly removed.
```

---

## 📊 Expected Verification Output Scorecard

When **Prompt 1** completes, your agent will output a verification summary matching this baseline:

| Target | Behavior & Outcome | Status |
| :--- | :--- | :--- |
| `legacy_standalone_backup/` & `LEGACY_CUSTOMIZATIONS_REVIEW.md` | Pre-existing rules, skills, subagents, hooks, and MCPs backed up & reviewed for side-by-side integration | ✅ |
| `plugin.json` & `plugins/agy-*` | Root `v1.4.0` plugin, `enterprise_architect` bundle, and `4` modular packs installed | ✅ |
| `knowledge_graph.json` (`OKF v0.2`) | Bitemporal Knowledge Graph seeded (`17` nodes, `31` edges, `< 1 ms` warm cache) | ✅ |
| `skills.json` (`20` PD-Q Skills) | `7` Tier-1 always-on skills (`-58%` token drop) + `13` Tier-2 dynamic skills active | ✅ |
| `agents.json` (`5` Subagents) | `black-hat-goldfish`, `black-hat-judge`, `black-hat-critic`, `dreaming`, `housekeeper` ready | ✅ |
| `rules.json` (`3` Arm B Rules) | `GEMINI.md`, `AGENTS.md`, and `no-bullshit.md` (`< 7 KB` total budget) active | ✅ |
| `hooks.json` (`ParseHooks` Schema) | `sentinel-policy-guard`, `knowledge-graph-grounding`, `black-hat-completion-gate` active | ✅ |
| `mcp_config.json` & `sidecars.json` | `7` Eager MCP servers (`alwaysLoad: true`) + `3` zero-permission sidecars ready | ✅ |
| `tests/test_customizations_suite.py` | All `27/27` clean-room, Wave-12, Dreaming, and deployment verification tests pass | ✅ |
