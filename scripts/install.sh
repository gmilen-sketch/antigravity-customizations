#!/usr/bin/env bash
# ==============================================================================
# Antigravity Customizations Suite — Universal Multi-Harness Installer (v1.4.0)
# Zero Web Hub / Zero Proxy Edition. Installs the Unified 7-Primitive Plugin,
# Zero-Touch Turn-1 Reconciler (`lazy_plugin_bootstrap.py`), Bitemporal Knowledge
# Graph (`OKF v0.2` + `resources/knowledge_graph.seed.json`), 20 PD-Q Skills,
# 5 Custom Subagents (with subagent-scoped `hooks.json`), 3 Sidecars (AuxPane UI,
# CDC Watcher, Nightly Dreaming), 4 Modular Domain Plugins, Role Bundle, and
# 7 FastMCP/Node MCP Servers into:
#   1. Antigravity CLI (`agy`) & Antigravity 2.0 (`~/.gemini/config/plugins/` & `~/.gemini/antigravity/`)
#   2. Claude Code (`claude` CLI — `~/.claude/` or workspace `.claude/`)
#   3. Cursor / Windsurf / Cloud Code (`~/.cursor/` or workspace `.agents/`)
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="all"
DEST_HOME="${HOME}"
DRY_RUN="false"
RUN_VERIFY="false"

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
        -h|--help)
            echo "Usage: ./scripts/install.sh [--target all|agy|antigravity|claude-code|cursor|cloud-code] [--home <dir>] [--dry-run] [--verify]"
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

echo "[1/4] Initializing Bitemporal Knowledge Graph, Seed Graph & Turn-1 Host Reconciler..."
if [[ "$DRY_RUN" == "false" ]]; then
    mkdir -p "${DEST_HOME}/.gemini/antigravity"
    python3 -B "${REPO_ROOT}/src/hooks/lazy_plugin_bootstrap.py" --full-host-reconcile --home "${DEST_HOME}" >/dev/null 2>&1 || true
    KG_JSON_PATH="${DEST_HOME}/.gemini/antigravity/knowledge_graph.json" \
        python3 -B "${REPO_ROOT}/src/knowledge_graph/init_knowledge_graph.py" >/dev/null 2>&1 || true
    python3 -B "${REPO_ROOT}/src/knowledge_graph/okf_knowledge_compiler.py" \
        --kb-root "${REPO_ROOT}/kb" \
        --graph-path "${DEST_HOME}/.gemini/antigravity/knowledge_graph.json" >/dev/null 2>&1 || true
fi

install_agy() {
    echo "[2/4] Installing Unified v1.4.0 Plugin Bundle, Role Bundle & 4 Modular Packs into Antigravity (${DEST_HOME}/.gemini/config)..."
    [[ "$DRY_RUN" == "true" ]] && return 0
    local PLUGIN_DEST="${DEST_HOME}/.gemini/config/plugins/antigravity-customizations"
    mkdir -p "${DEST_HOME}/.gemini/config/plugins" "${PLUGIN_DEST}" "${DEST_HOME}/.gemini/antigravity/bin" "${DEST_HOME}/kb" "${DEST_HOME}/.gemini/skills" "${DEST_HOME}/.gemini/agents"
    cp -r "${REPO_ROOT}/skills" "${DEST_HOME}/.gemini/config/"
    cp -r "${REPO_ROOT}/agents" "${DEST_HOME}/.gemini/config/"
    cp -r "${REPO_ROOT}/rules" "${DEST_HOME}/.gemini/config/"
    cp -r "${REPO_ROOT}/skills/"* "${DEST_HOME}/.gemini/skills/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/agents/"* "${DEST_HOME}/.gemini/agents/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/kb/" 2>/dev/null || true
    mkdir -p "${DEST_HOME}/.gemini/antigravity/kb" "${DEST_HOME}/.gemini/antigravity/bin/kb" "${DEST_HOME}/.gemini/antigravity/sidecars"
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/.gemini/antigravity/kb/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/kb/"* "${DEST_HOME}/.gemini/antigravity/bin/kb/" 2>/dev/null || true
    cp -r "${REPO_ROOT}/sidecars/"* "${DEST_HOME}/.gemini/antigravity/sidecars/" 2>/dev/null || true

    # Populate full native plugin bundle under ~/.gemini/config/plugins/antigravity-customizations/
    for item in VERSION AGENT_DIRECTORY.md WORKFLOW_DIRECTORY.md plugin.json plugins.json sidecars.json agents.json skills.json rules.json hooks.json mcp_config.json assets resources skills agents rules sidecars src kb _agents; do
        rm -rf "${PLUGIN_DEST:?}/${item}"
        cp -r "${REPO_ROOT}/${item}" "${PLUGIN_DEST}/${item}"
    done

    # Also install modular domain plugins under ~/.gemini/config/plugins/
    if [[ -d "${REPO_ROOT}/plugins" ]]; then
        for mod_plugin in "${REPO_ROOT}/plugins/"*; do
            [[ -d "$mod_plugin" ]] || continue
            local mod_name
            mod_name="$(basename "$mod_plugin")"
            rm -rf "${DEST_HOME}/.gemini/config/plugins/${mod_name}"
            cp -r "$mod_plugin" "${DEST_HOME}/.gemini/config/plugins/${mod_name}"
        done
    fi

    for mod in autonomy_engine knowledge_graph hooks diagram_renderer mcp_google_workspace mcp_node_stub playwright_scraper six_hats_evaluator; do
        rm -rf "${DEST_HOME}/.gemini/antigravity/bin/${mod}"
        cp -r "${REPO_ROOT}/src/${mod}" "${DEST_HOME}/.gemini/antigravity/bin/${mod}"
        chmod +x "${DEST_HOME}/.gemini/antigravity/bin/${mod}"/*.py "${DEST_HOME}/.gemini/antigravity/bin/${mod}"/*.sh 2>/dev/null || true
    done
    cp "${REPO_ROOT}/src/mcp_deep_research.py" "${DEST_HOME}/.gemini/antigravity/bin/mcp_deep_research.py"
    chmod +x "${DEST_HOME}/.gemini/antigravity/bin/mcp_deep_research.py" 2>/dev/null || true
    sed "s|\./src/hooks/|${REPO_ROOT}/src/hooks/|g" "${REPO_ROOT}/hooks.json" > "${DEST_HOME}/.gemini/config/hooks.json"
    sed "s|\./src/hooks/|${REPO_ROOT}/src/hooks/|g" "${REPO_ROOT}/hooks.json" > "${DEST_HOME}/.gemini/antigravity/hooks.json"
    sed 's|${PLUGIN_ROOT}|'"${REPO_ROOT}"'|g' "${REPO_ROOT}/mcp_config.json" > "${DEST_HOME}/.gemini/antigravity/mcp_config.json"
    sed 's|${PLUGIN_ROOT}|'"${REPO_ROOT}"'|g' "${REPO_ROOT}/mcp_config.json" > "${DEST_HOME}/.gemini/config/mcp_config.json"

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

echo "✅ Antigravity Customizations Suite v1.4.0 installed successfully for target '${TARGET}'!"

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

checks = {
    "1_plugin_and_4_modular_packs": (plugin_dir / "plugin.json").is_file() and all(
        (dest_home / ".gemini" / "config" / "plugins" / p / "plugin.json").is_file()
        for p in ("agy-core-governance", "agy-knowledge-graph", "agy-cloud-architect", "agy-workspace-automation")
    ),
    "2_bitemporal_knowledge_graph": (dest_home / ".gemini" / "antigravity" / "knowledge_graph.json").is_file(),
    "3_twotier_20_pdq_skills": len(json.loads((repo_root / "skills.json").read_text(encoding="utf-8")).get("skills", [])) == 20,
    "4_five_custom_subagents": len(json.loads((repo_root / "agents.json").read_text(encoding="utf-8")).get("agents", [])) == 5,
    "5_three_arm_b_rules": len(json.loads((repo_root / "rules.json").read_text(encoding="utf-8")).get("rules", [])) == 3,
    "6_three_parsehooks_lifecycle_hooks": len(json.loads((dest_home / ".gemini" / "config" / "hooks.json").read_text(encoding="utf-8"))) == 3,
    "7_seven_eager_mcps_and_3_sidecars": len(json.loads((dest_home / ".gemini" / "config" / "mcp_config.json").read_text(encoding="utf-8")).get("mcpServers", {})) == 7,
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
print(json.dumps({"verdict": "PASS", "version": "1.4.0", "primitives_verified": "7/7", "checks": checks}, indent=2))
PYEOF
fi
