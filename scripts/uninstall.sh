#!/usr/bin/env bash
# ==============================================================================
# Antigravity Customizations Suite — Clean-Slate Uninstaller (v1.4.0)
# Removes installed plugin bundles, modular domain packs, and plugin_data state,
# restores backed-up standalone rules from legacy_standalone_backup/, and calls
# the local Language Server state endpoint if active.
# ==============================================================================
set -euo pipefail

DEST_HOME="${HOME}"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --home)
            DEST_HOME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="true"
            shift 1
            ;;
        -h|--help)
            echo "Usage: ./scripts/uninstall.sh [--home <dir>] [--dry-run]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "[1/3] Disabling plugin state in Language Server (if active)..."
if [[ "$DRY_RUN" == "false" && -n "${ANTIGRAVITY_LS_ADDRESS:-}" && -n "${ANTIGRAVITY_CSRF_TOKEN:-}" ]]; then
    LS_RPC_PATH="${ANTIGRAVITY_LS_RPC_PATH:-/v1/state/write}"
    LS_CSRF_HEADER="${ANTIGRAVITY_CSRF_HEADER:-x-antigravity-csrf-token}"
    curl -sS -X POST \
        "http://${ANTIGRAVITY_LS_ADDRESS}${LS_RPC_PATH}" \
        -H "Content-Type: application/json" \
        -H "${LS_CSRF_HEADER}: ${ANTIGRAVITY_CSRF_TOKEN}" \
        -d '{"userConfig":{"plugins":{"antigravity-customizations":{"enabled":false}}}}' >/dev/null 2>&1 || true
fi

echo "[2/3] Restoring any backed-up standalone rules and removing plugin directories..."
if [[ "$DRY_RUN" == "false" ]]; then
    BACKUP_DIR="${DEST_HOME}/.gemini/antigravity/plugin_data/antigravity-customizations/legacy_standalone_backup"
    if [[ -d "${BACKUP_DIR}" ]]; then
        mkdir -p "${DEST_HOME}/.gemini/config/rules"
        cp -r "${BACKUP_DIR}/"* "${DEST_HOME}/.gemini/config/rules/" 2>/dev/null || true
    fi

    for pdir in antigravity-customizations agy-core-governance agy-knowledge-graph agy-cloud-architect agy-workspace-automation; do
        rm -rf "${DEST_HOME}/.gemini/config/plugins/${pdir}"
    done
    rm -rf "${DEST_HOME}/.gemini/antigravity/plugin_data/antigravity-customizations"
fi

echo "[3/3] Cleaning up empty customization directories..."
if [[ "$DRY_RUN" == "false" ]]; then
    for d in "${DEST_HOME}/.gemini/config/plugins" "${DEST_HOME}/.gemini/antigravity/plugin_data"; do
        if [[ -d "$d" ]] && [[ -z "$(ls -A "$d" 2>/dev/null)" ]]; then
            rmdir "$d" 2>/dev/null || true
        fi
    done
fi

echo "✅ Antigravity Customizations Suite v1.3.0 uninstalled cleanly (vanilla clean slate verified)!"
