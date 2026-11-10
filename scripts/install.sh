#!/usr/bin/env bash
# ==============================================================================
# Antigravity Customizations Suite — Universal Multi-Harness Installer (v1.5.0)
# Zero Web Hub / Zero Proxy Edition. Installs the Unified 7-Primitive Plugin,
# Zero-Touch Turn-1 Reconciler (`lazy_plugin_bootstrap.py`), Bitemporal Knowledge
# Graph (`OKF v0.2` + `resources/knowledge_graph.seed.json`), 20 PD-Q Skills,
# 5 Custom Subagents (with subagent-scoped `hooks.json`), 3 Sidecars (AuxPane UI,
# CDC Watcher, Nightly Dreaming), 4 Modular Domain Plugins, Role Bundle, and
# 10 FastMCP/Node MCP Servers into:
#   1. Antigravity CLI (`agy`) & Antigravity 2.0 (`~/.gemini/config/plugins/` & `~/.gemini/antigravity/`)
#   2. Claude Code (`claude` CLI — `~/.claude/` or workspace `.claude/`)
#   3. Cursor / Windsurf / Cloud Code (`~/.cursor/` or workspace `.agents/`)
# ==============================================================================
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="all"
DEST_HOME="${HOME}"
DRY_RUN="false"
RUN_VERIFY="false"
PLUGIN_ONLY="false"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --home)
            DEST_HOME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="true"
            shift 1
            ;;
        --verify)
            RUN_VERIFY="true"
            shift 1
            ;;
        --plugin-only)
            PLUGIN_ONLY="true"
            shift 1
            ;;
        -h|--help)
            echo "Usage: ./scripts/install.sh [--target all|agy|antigravity|claude-code|cursor|cloud-code] [--home <dir>] [--plugin-only] [--dry-run] [--verify]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

export AGY_CLI_AUTO_COMPACT_OVERRIDE="${AGY_CLI_AUTO_COMPACT_OVERRIDE:-80%}"
export JJ_PAGER="${JJ_PAGER:-cat}"

echo "[1/4] Backing up pre-existing user customizations, initializing Bitemporal Knowledge Graph & Turn-1 Reconciler..."
if [[ "$DRY_RUN" == "false" ]]; then
    mkdir -p "${DEST_HOME}/.gemini/antigravity"
    python3 -B "${REPO_ROOT}/src/hooks/lazy_plugin_bootstrap.py" --backup-existing --home "${DEST_HOME}" >/dev/null 2>&1 || true
    python3 -B "${REPO_ROOT}/src/hooks/lazy_plugin_bootstrap.py" --full-host-reconcile --home "${DEST_HOME}" >/dev/null 2>&1 || true
    KG_JSON_PATH="${DEST_HOME}/.gemini/antigravity/knowledge_graph.json" \
        python3 -B "${REPO_ROOT}/src/knowledge_graph/init_knowledge_graph.py" >/dev/null 2>&1 || true
fi

install_agy() {
    echo "[2/4] Installing Unified v1.5.0 Plugin Bundle, Role Bundle & 4 Modular Packs into Antigravity (${DEST_HOME}/.gemini/config)..."
    [[ "$DRY_RUN" == "true" ]] && return 0
    local PLUGIN_DEST="${DEST_HOME}/.gemini/config/plugins/antigravity-customizations"
    mkdir -p "${DEST_HOME}/.gemini/config/plugins" "${PLUGIN_DEST}" "${DEST_HOME}/.gemini/antigravity/bin" "${DEST_HOME}/kb"
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/kb/" 2>/dev/null || true
    mkdir -p "${DEST_HOME}/.gemini/antigravity/kb" "${DEST_HOME}/.gemini/antigravity/bin/kb" "${DEST_HOME}/.gemini/antigravity/sidecars"
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/.gemini/antigravity/kb/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/.gemini/antigravity/bin/kb/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/sidecars/"* "${DEST_HOME}/.gemini/antigravity/sidecars/" 2>/dev/null || true

    # Populate full self-contained native plugin bundle under ~/.gemini/config/plugins/antigravity-customizations/
    for item in VERSION README.md LICENSE AGENT_DIRECTORY.md WORKFLOW_DIRECTORY.md plugin.json sidecars.json agents.json skills.json rules.json hooks.json mcp_config.json assets resources skills agents rules sidecars src kb _agents; do
        [[ -e "${REPO_ROOT}/${item}" ]] || continue
        rm -rf "${PLUGIN_DEST:?}/${item}"
        cp -r "${REPO_ROOT}/${item}" "${PLUGIN_DEST}/${item}"
    done

    # Materialize all 4 modular domain plugins under ~/.gemini/config/plugins/ as 100% self-contained bundles
    REPO_ROOT="${REPO_ROOT}" PLUGINS_INSTALL_ROOT="${DEST_HOME}/.gemini/config/plugins" PYTHONDONTWRITEBYTECODE=1 python3 -B - << 'PYMOD'
import json, os, pathlib, re, shutil

repo = pathlib.Path(os.environ["REPO_ROOT"])
dest_root = pathlib.Path(os.environ["PLUGINS_INSTALL_ROOT"])
src_plugins = repo / "plugins"

skill_name_to_dir = {}
for sdir in (repo / "skills").iterdir():
    if sdir.is_dir() and (sdir / "SKILL.md").is_file():
        txt = (sdir / "SKILL.md").read_text(encoding="utf-8")
        m = re.search(r"^name:\s*([A-Za-z0-9_-]+)", txt, flags=re.MULTILINE)
        sname = m.group(1) if m else sdir.name.replace("_", "-")
        skill_name_to_dir[sname] = sdir
        skill_name_to_dir[sdir.name] = sdir

if src_plugins.is_dir():
    for mod in sorted(src_plugins.iterdir()):
        if not mod.is_dir():
            continue
        target = dest_root / mod.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(mod, target)
        for shared in ("VERSION", "LICENSE", "src", "resources", "kb"):
            s_path = repo / shared
            if s_path.is_dir():
                shutil.copytree(s_path, target / shared, dirs_exist_ok=True)
            elif s_path.is_file():
                shutil.copy2(s_path, target / shared)

        if (target / "mcp_config.json").is_file():
            mtxt = (target / "mcp_config.json").read_text(encoding="utf-8")
            (target / "mcp_config.json").write_text(mtxt.replace("${PLUGIN_ROOT}/../../src/", "${PLUGIN_ROOT}/src/"), encoding="utf-8")

        if (target / "hooks.json").is_file():
            htxt = (target / "hooks.json").read_text(encoding="utf-8")
            (target / "hooks.json").write_text(htxt.replace("../../src/hooks/", "./src/hooks/"), encoding="utf-8")

        if (target / "skills.json").is_file():
            sdata = json.loads((target / "skills.json").read_text(encoding="utf-8"))
            inc = set(sdata.get("entries", [{}])[0].get("include_only", []))
            (target / "skills").mkdir(parents=True, exist_ok=True)
            for sname in sorted(inc):
                sdir = skill_name_to_dir.get(sname)
                if sdir and sdir.is_dir():
                    shutil.copytree(sdir, target / "skills" / sdir.name, dirs_exist_ok=True)
            sdata["entries"][0]["path"] = "skills"
            (target / "skills.json").write_text(json.dumps(sdata, indent=2) + "\n", encoding="utf-8")

        if (target / "agents.json").is_file():
            adata = json.loads((target / "agents.json").read_text(encoding="utf-8"))
            inc = set(adata.get("entries", [{}])[0].get("include_only", []))
            (target / "agents").mkdir(parents=True, exist_ok=True)
            for aname in sorted(inc):
                adir = repo / "agents" / aname
                if adir.is_dir():
                    shutil.copytree(adir, target / "agents" / aname, dirs_exist_ok=True)
            adata["entries"][0]["path"] = "agents"
            (target / "agents.json").write_text(json.dumps(adata, indent=2) + "\n", encoding="utf-8")

        if (target / "rules.json").is_file():
            shutil.copytree(repo / "rules", target / "rules", dirs_exist_ok=True)
            rdata = json.loads((target / "rules.json").read_text(encoding="utf-8"))
            rdata["entries"][0]["path"] = "rules"
            (target / "rules.json").write_text(json.dumps(rdata, indent=2) + "\n", encoding="utf-8")

        if (target / "sidecars.json").is_file():
            shutil.copytree(repo / "sidecars", target / "sidecars", dirs_exist_ok=True)
            scdata = json.loads((target / "sidecars.json").read_text(encoding="utf-8"))
            scdata["entries"][0]["path"] = "sidecars"
            (target / "sidecars.json").write_text(json.dumps(scdata, indent=2) + "\n", encoding="utf-8")
PYMOD

    for mod in autonomy_engine knowledge_graph hooks diagram_renderer mcp_google_workspace mcp_node_stub mcp_servers playwright_scraper six_hats_evaluator; do
        rm -rf "${DEST_HOME}/.gemini/antigravity/bin/${mod}"
        cp -r "${REPO_ROOT}/src/${mod}" "${DEST_HOME}/.gemini/antigravity/bin/${mod}"
        chmod +x "${DEST_HOME}/.gemini/antigravity/bin/${mod}"/*.py "${DEST_HOME}/.gemini/antigravity/bin/${mod}"/*.sh 2>/dev/null || true
    done
    cp "${REPO_ROOT}/src/mcp_deep_research.py" "${DEST_HOME}/.gemini/antigravity/bin/mcp_deep_research.py"
    chmod +x "${DEST_HOME}/.gemini/antigravity/bin/mcp_deep_research.py" 2>/dev/null || true
    sed "s|\./src/hooks/|${PLUGIN_DEST}/src/hooks/|g" "${REPO_ROOT}/hooks.json" > "${DEST_HOME}/.gemini/antigravity/hooks.json"
    sed 's|${PLUGIN_ROOT}|'"${PLUGIN_DEST}"'|g' "${REPO_ROOT}/mcp_config.json" > "${DEST_HOME}/.gemini/antigravity/mcp_config.json"

    if [[ "$PLUGIN_ONLY" != "true" ]]; then
        mkdir -p "${DEST_HOME}/.gemini/skills" "${DEST_HOME}/.gemini/agents"
        cp -r "${REPO_ROOT}/skills" "${DEST_HOME}/.gemini/config/"
        cp -r "${REPO_ROOT}/agents" "${DEST_HOME}/.gemini/config/"
        cp -r "${REPO_ROOT}/rules" "${DEST_HOME}/.gemini/config/"
        cp -r "${REPO_ROOT}/skills/"* "${DEST_HOME}/.gemini/skills/" 2>/dev/null || true
        cp -r "${REPO_ROOT}/agents/"* "${DEST_HOME}/.gemini/agents/" 2>/dev/null || true
        sed "s|\./src/hooks/|${PLUGIN_DEST}/src/hooks/|g" "${REPO_ROOT}/hooks.json" > "${DEST_HOME}/.gemini/config/hooks.json"
        sed 's|${PLUGIN_ROOT}|'"${PLUGIN_DEST}"'|g' "${REPO_ROOT}/mcp_config.json" > "${DEST_HOME}/.gemini/config/mcp_config.json"
    fi

    # Enable PluginUserConfig in ~/.gemini/config/config.json without clobbering existing user keys
    DEST_CFG="${DEST_HOME}/.gemini/config/config.json" PYTHONDONTWRITEBYTECODE=1 python3 -B - << 'PYCFG' || true
import json, os
cfg_path = os.environ["DEST_CFG"]
data = {}
if os.path.exists(cfg_path):
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
plugins = data.setdefault("plugins", {})
plugins.setdefault("antigravity-customizations", {})["enabled"] = True
with open(cfg_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
PYCFG

    # Live-enable in Language Server state store if reachable (zero restart required)
    local ls_rpc_path="${ANTIGRAVITY_LS_RPC_PATH:-/v1/state/write}"
    local ls_csrf_header="${ANTIGRAVITY_CSRF_HEADER:-x-antigravity-csrf-token}"
    if [[ -n "${ANTIGRAVITY_LS_ADDRESS:-}" && -n "${ANTIGRAVITY_CSRF_TOKEN:-}" ]]; then
        curl -sS -X POST \
            "http://${ANTIGRAVITY_LS_ADDRESS}${ls_rpc_path}" \
            -H "Content-Type: application/json" \
            -H "${ls_csrf_header}: ${ANTIGRAVITY_CSRF_TOKEN}" \
            -d '{"userConfig":{"plugins":{"antigravity-customizations":{"enabled":true}}}}' >/dev/null 2>&1 || true
    fi
}

install_claude_code() {
    echo "[3/4] Installing into Claude Code (${DEST_HOME}/.claude)..."
    [[ "$DRY_RUN" == "true" ]] && return 0
    mkdir -p "${DEST_HOME}/.claude/agents" "${DEST_HOME}/.claude/commands"
    cp -r "${REPO_ROOT}/.claude/agents/"* "${DEST_HOME}/.claude/agents/"
    cp -r "${REPO_ROOT}/.claude/commands/"* "${DEST_HOME}/.claude/commands/"
    cp "${REPO_ROOT}/CLAUDE.md" "${DEST_HOME}/.claude/CLAUDE.md"
    sed "s|src/hooks/|${REPO_ROOT}/src/hooks/|g" "${REPO_ROOT}/.claude/settings.json" > "${DEST_HOME}/.claude/settings.json"
}

install_cursor_and_cloud_code() {
    echo "[4/4] Installing into Cursor / Windsurf / Cloud Code (${DEST_HOME}/.cursor & ${DEST_HOME}/.agents)..."
    [[ "$DRY_RUN" == "true" ]] && return 0
    mkdir -p "${DEST_HOME}/.cursor" "${DEST_HOME}/.agents"
    cp -r "${REPO_ROOT}/skills" "${DEST_HOME}/.agents/"
    cp -r "${REPO_ROOT}/agents" "${DEST_HOME}/.agents/"
    cp -r "${REPO_ROOT}/rules" "${DEST_HOME}/.agents/"
    sed "s|\"src/|\"${REPO_ROOT}/src/|g" "${REPO_ROOT}/.mcp.json" > "${DEST_HOME}/.cursor/mcp.json"
}

case "$TARGET" in
    all)
        install_agy
        install_claude_code
        install_cursor_and_cloud_code
        ;;
    agy|antigravity)
        install_agy
        ;;
    claude|claude-code)
        install_claude_code
        ;;
    cursor|cloud-code|windsurf)
        install_cursor_and_cloud_code
        ;;
    *)
        echo "Unsupported --target: $TARGET" >&2
        exit 1
        ;;
esac

echo "✅ Antigravity Customizations Suite v1.5.0 installed successfully for target '${TARGET}'!"

if [[ "$RUN_VERIFY" == "true" && "$DRY_RUN" == "false" ]]; then
    echo "[5/5] Verifying 7 Antigravity Customization Primitives & Clean-Room Test Suite..."
    DEST_HOME="${DEST_HOME}" REPO_ROOT="${REPO_ROOT}" PYTHONDONTWRITEBYTECODE=1 python3 -B - << 'PYEOF'
import json
import os
import pathlib
import subprocess
import sys

dest_home = pathlib.Path(os.environ["DEST_HOME"])
repo_root = pathlib.Path(os.environ["REPO_ROOT"])
plugin_dir = dest_home / ".gemini" / "config" / "plugins" / "antigravity-customizations"
mod_names = ("agy-core-governance", "agy-knowledge-graph", "agy-cloud-architect", "agy-workspace-automation")

self_contained_ok = (plugin_dir / "plugin.json").is_file() and (plugin_dir / "README.md").is_file()
for mp in mod_names:
    mdir = dest_home / ".gemini" / "config" / "plugins" / mp
    if not (mdir / "plugin.json").is_file() or not (mdir / "assets" / "logo.svg").is_file():
        self_contained_ok = False
    for jf in mdir.glob("*.json"):
        if "../../" in jf.read_text(encoding="utf-8"):
            self_contained_ok = False

hooks_target = dest_home / ".gemini" / "config" / "hooks.json"
if not hooks_target.is_file():
    hooks_target = plugin_dir / "hooks.json"
mcp_target = dest_home / ".gemini" / "config" / "mcp_config.json"
if not mcp_target.is_file():
    mcp_target = plugin_dir / "mcp_config.json"

checks = {
    "1_plugin_and_4_modular_packs": self_contained_ok,
    "2_bitemporal_knowledge_graph": (dest_home / ".gemini" / "antigravity" / "knowledge_graph.json").is_file(),
    "3_twotier_20_pdq_skills": len(json.loads((plugin_dir / "skills.json").read_text(encoding="utf-8")).get("skills", [])) == 20,
    "4_five_custom_subagents": len(json.loads((plugin_dir / "agents.json").read_text(encoding="utf-8")).get("agents", [])) == 5,
    "5_three_arm_b_rules": len(json.loads((plugin_dir / "rules.json").read_text(encoding="utf-8")).get("rules", [])) == 3,
    "6_parsehooks_lifecycle_hooks": len(json.loads(hooks_target.read_text(encoding="utf-8"))) >= 3,
    "7_ten_eager_mcps_and_3_sidecars": len(json.loads(mcp_target.read_text(encoding="utf-8")).get("mcpServers", {})) >= 10,
    "8_legacy_customizations_review_manifest": (dest_home / ".gemini" / "antigravity" / "plugin_data" / "antigravity-customizations" / "LEGACY_CUSTOMIZATIONS_REVIEW.md").is_file(),
}

if not all(checks.values()):
    print(json.dumps({"verdict": "FAIL", "checks": checks}, indent=2))
    sys.exit(1)

if os.environ.get("AGY_INSTALL_VERIFY_IN_PROGRESS") != "1":
    subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(repo_root / "tests"), "-p", "test_*.py"],
        cwd=str(repo_root),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "AGY_INSTALL_VERIFY_IN_PROGRESS": "1"},
        check=True,
    )
print(json.dumps({"verdict": "PASS", "version": "1.5.0", "primitives_verified": "7/7", "checks": checks}, indent=2))
PYEOF
fi
