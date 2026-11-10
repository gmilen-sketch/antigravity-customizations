#!/bin/sh
# ==============================================================================
# Role: Fail-Open Bytecode-Free Hook Wrapper (run_hook_safe.sh v1.5.0)
# Purpose: Resolves target Python lifecycle hooks (PreInvocation, PostInvocation,
#          PreToolUse, PostToolUse, Stop) across repository src/hooks/, plugin
#          roots, and ~/.gemini/antigravity/bin/hooks/, executing under POSIX
#          /bin/sh with PYTHONDONTWRITEBYTECODE=1, PYTHONSAFEPATH=1, and
#          python3 -B so missing dependencies or transient errors fail open
#          cleanly without emitting .pyc files.
# How It Is Used: Invoked by hooks.json, plugins/*/hooks.json, and
#                 agents/*/hooks.json via:
#                   ./src/hooks/run_hook_safe.sh ./src/hooks/<script>.py [args...]
# ==============================================================================
export PYTHONDONTWRITEBYTECODE=1
export PYTHONSAFEPATH=1

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_RAW="${1:-}"
if [ -z "$TARGET_RAW" ]; then
  printf '{}\n'
  exit 0
fi
shift

EVENT_MODE=""
for arg in "$TARGET_RAW" "$@"; do
  case "$arg" in
    PreInvocation|pre-invocation|PostInvocation|post-invocation|UserPromptSubmit|PostToolUse|post-tool-use)
      EVENT_MODE="empty_json"
      ;;
    *lazy_plugin_bootstrap.py*|*kg_pre_invocation_hook.py*|*black_hat_in_progress_ux_hook.py*)
      EVENT_MODE="empty_json"
      ;;
  esac
done

BASE_NAME=$(basename -- "$TARGET_RAW")
RESOLVED=""
for CAND in \
  "$TARGET_RAW" \
  "$SCRIPT_DIR/$TARGET_RAW" \
  "$SCRIPT_DIR/$BASE_NAME" \
  "$HOME/.gemini/antigravity/bin/hooks/$BASE_NAME"; do
  if [ -n "$CAND" ] && [ -f "$CAND" ]; then
    RESOLVED="$CAND"
    break
  fi
done

if [ -z "$RESOLVED" ]; then
  if [ "$EVENT_MODE" = "empty_json" ]; then
    printf '{}\n'
  else
    printf '{"decision":"allow"}\n'
  fi
  exit 0
fi

OUT=$(python3 -B "$RESOLVED" "$@" 2>/dev/null)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ] || [ -z "$OUT" ]; then
  if [ "$EVENT_MODE" = "empty_json" ]; then
    printf '{}\n'
  else
    printf '{"decision":"allow"}\n'
  fi
  exit 0
fi

printf '%s\n' "$OUT"
exit 0
