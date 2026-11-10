#!/usr/bin/env python3
"""Rule 31 Control-Plane Self-Protection Gate (`force_ask` Clean-Room Edition).

Escalates autonomous agent mutations targeting `hooks.json`, `plugin.json`,
`mcp_config.json`, `mcp.json`, or active hook enforcement scripts via
`decision = "force_ask"` (enforced even in Turbo mode) unless explicitly
authorized via `ANTIGRAVITY_ALLOW_HOOK_ADMIN=1`.
"""

import os
import re
from typing import Any, Dict, List, Optional

PROTECTED_BASENAMES = {
    "hooks.json",
    "mcp_config.json",
    "mcp.json",
    "sentinel_dispatch.py",
    "agent_stop_black_hat_gate.py",
    "black_hat_in_progress_ux_hook.py",
    "multi_harness_hook_adapter.py",
    "kg_pre_invocation_hook.py",
    "run_hook_safe.sh",
    "r31_hook_integrity_guard.py",
}

_WRITE_TOOLS = frozenset({
    "write_file",
    "edit_file",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
})


def verify_comment_author_trust_and_shell_boundary(
    comment_author: str,
    authenticated_user: str,
    allowed_maintainers: List[str],
    shell_command: str,
) -> Dict[str, Any]:
    """AGW-W12-05: Verifies comment-author trust and inspects shell command chains for control-plane mutation bypasses."""
    author_norm = (comment_author or "").strip().lower()
    user_norm = (authenticated_user or "").strip().lower()
    maintainers = {m.strip().lower() for m in (allowed_maintainers or []) if m}
    author_trusted = bool(author_norm and (author_norm == user_norm or author_norm in maintainers))

    cmd = shell_command or ""
    subshell_bypass = bool(
        re.search(r"\b(?:eval|python3?\s+-c|sh\s+-c|bash\s+-c)\b", cmd)
        and any(b in cmd for b in PROTECTED_BASENAMES)
    )
    direct_mutation = any(
        re.search(r"(>|>>|\brm\b|\bmv\b|\bsed\s+-i|\btee\b|\bcp\b).*" + re.escape(b), cmd)
        for b in PROTECTED_BASENAMES
    )
    shell_safe = not (subshell_bypass or direct_mutation)
    return {
        "passed": author_trusted and shell_safe,
        "author_trusted": author_trusted,
        "shell_safe": shell_safe,
        "subshell_bypass_detected": subshell_bypass,
    }


def check_case_q_manual_release_lock(target_path: str, is_release_sync: bool = False) -> Dict[str, Any]:
    """Case Q Manual Release Lock: Blocks background daemon/dreaming writes to live user plugin/rule directories."""
    norm = (target_path or "").replace("\\", "/")
    is_live_system_target = any(
        seg in norm
        for seg in ("/.gemini/config/plugins/", "/.gemini/config/rules/", "/.claude/settings.json")
    )
    allowed = (not is_live_system_target) or bool(is_release_sync) or os.environ.get("ANTIGRAVITY_ALLOW_HOOK_ADMIN") == "1"
    return {
        "allowed": allowed,
        "is_live_system_target": is_live_system_target,
        "decision": "allow" if allowed else "deny",
    }


def check(tool_name: str, tool_args: Dict[str, Any]) -> Optional[Dict[str, str]]:
    if os.environ.get("ANTIGRAVITY_ALLOW_HOOK_ADMIN") == "1":
        return None
    if tool_name in _WRITE_TOOLS:
        target = str(
            tool_args.get("Path")
            or tool_args.get("TargetFile")
            or tool_args.get("file_path")
            or ""
        )
        base = os.path.basename(target)
        if base in PROTECTED_BASENAMES:
            return {
                "decision": "force_ask",
                "reason": (
                    f"Control-Plane Integrity Guard: Modifying protected control-plane file "
                    f"'{base}' requires explicit human confirmation."
                ),
            }
    elif tool_name == "run_command":
        cmd = str(tool_args.get("CommandLine") or tool_args.get("command") or "")
        boundary = verify_comment_author_trust_and_shell_boundary(
            comment_author="local_operator",
            authenticated_user="local_operator",
            allowed_maintainers=["local_operator"],
            shell_command=cmd,
        )
        if not boundary["shell_safe"]:
            return {
                "decision": "force_ask",
                "reason": (
                    "Control-Plane Integrity Guard: Shell or subshell mutation targeting protected "
                    "control-plane files requires explicit human confirmation."
                ),
            }
    return None


check_r31_integrity = check
