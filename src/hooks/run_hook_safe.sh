#!/bin/sh
# ==============================================================================
# Role: Fail-Open Bytecode-Free Hook Wrapper (run_hook_safe.sh v1.4.0)
# Purpose: Wraps Python lifecycle hooks (PreInvocation, PreToolUse, PostToolUse,
#          Stop) in a POSIX /bin/sh fail-open envelope with PYTHONDONTWRITEBYTECODE=1
#          and python3 -B so missing dependencies, transient timeouts, or
#          syntax errors never block the host agent harness or emit .pyc files.
# How It Is Used: Invoked by hooks.json, plugins/*/hooks.json, and agents/*/hooks.json
#                 via "./src/hooks/run_hook_safe.sh ./src/hooks/<script>.py [args...]".
# ==============================================================================
export PYTHONDONTWRITEBYTECODE=1

EVENT_MODE=""
for arg in "$@"; do
  case "$arg" in
    PreInvocation|pre-invocation|UserPromptSubmit|PostToolUse|post-tool-use)
      EVENT_MODE="empty_json"
      ;;
    *lazy_plugin_bootstrap.py*|*kg_pre_invocation_hook.py*)
      EVENT_MODE="empty_json"
      ;;
  esac
done

OUT=$(python3 -B "$@" 2>/dev/null)
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
