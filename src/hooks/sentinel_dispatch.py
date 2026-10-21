#!/usr/bin/env python3
"""
Modular PreToolUse Sentinel Dispatcher v2.1 (Clean-Room Customer Edition).
Evaluates deterministic pre-execution guardrails (<50ms) before any tool executes:
1. Destructive shell command prevention
2. Deprecated AI model rejection (Rule 28)
3. File size & binary bounds enforcement
4. Clean-room path & secret anonymization (Rule 11)
5. Control-plane self-protection (Rule 31)
6. Skill & hook deobfuscation / prompt-injection scanner
7. Zero-raw-LaTeX Google Workspace document export gate
8. Recurring cron `IsDaemon=True` livelock guard & own-session transcript/scratch read allowlist
"""

import os
import re
import resource
import sys
import json
from typing import Dict, Any, List, Optional

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
CHILD_RLIMIT_AS_BYTES = 24 * 1024 * 1024 * 1024  # 24 GiB OOM guard

from rules import (
    destructive_commands,
    deprecated_models,
    file_bounds,
    rule_11_anonymization,
    r31_hook_integrity_guard,
    audit_skill_hook_safety,
    zero_latex,
)

RULE_MODULES = [
    destructive_commands,
    deprecated_models,
    file_bounds,
    rule_11_anonymization,
    r31_hook_integrity_guard,
    audit_skill_hook_safety,
    zero_latex,
]


def check_schedule_cron_daemon_guard(tool_name: str, tool_args: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Blocks unbounded recurring CronExpression schedules that omit both IsDaemon=True and MaxIterations."""
    if tool_name != "schedule" or not isinstance(tool_args, dict):
        return None
    cron_expr = str(tool_args.get("CronExpression") or "").strip()
    if not cron_expr:
        return None
    is_daemon = bool(tool_args.get("IsDaemon") is True)
    max_iter = tool_args.get("MaxIterations")
    has_bounded_iter = isinstance(max_iter, int) and max_iter > 0
    if not is_daemon and not has_bounded_iter:
        return {
            "decision": "deny",
            "reason": (
                "Schedule Livelock Guard: Recurring CronExpression schedules must set "
                "IsDaemon=True (for standing jobs) or a positive MaxIterations bound "
                "so the parent session or subagent can terminate cleanly."
            ),
        }
    return None


def check_own_session_transcript_access(
    tool_name: str, tool_args: Dict[str, Any], root_conversation_id: str = ""
) -> Optional[Dict[str, str]]:
    """Allows reading own-session transcript/scratch files while blocking cross-session transcript exfiltration."""
    if tool_name not in ("view_file", "read_file") or not isinstance(tool_args, dict):
        return None
    target = str(
        tool_args.get("TargetFile")
        or tool_args.get("AbsolutePath")
        or tool_args.get("Path")
        or tool_args.get("file_path")
        or ""
    ).strip()
    if not target or "transcript" not in target:
        return None
    if root_conversation_id and root_conversation_id in target:
        return {"decision": "allow"}
    return None


def apply_rlimit_as(max_bytes: int = CHILD_RLIMIT_AS_BYTES) -> bool:
    """Applies a 24 GiB virtual address space cap (RLIMIT_AS) to prevent runaway child OOMs."""
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        new_soft = max_bytes if (soft == resource.RLIM_INFINITY or soft > max_bytes) else soft
        new_hard = max_bytes if (hard == resource.RLIM_INFINITY or hard > max_bytes) else hard
        if new_soft > new_hard:
            new_soft = new_hard
        resource.setrlimit(resource.RLIMIT_AS, (new_soft, new_hard))
        return True
    except Exception:
        return False


def rewrite_inline_python_c_to_heredoc(cmd: str) -> Dict[str, Any]:
    """
    AGW-W12-05 (`MODEL-BUG-3`): Detects fragile double-quoted `python3 -c "..."` commands
    containing nested quotes, f-strings, or newlines and rewrites them into safe single-quoted heredocs.
    """
    raw = (cmd or "").strip()
    m = re.search(r'\b(python3?(?:\s+-[Bu]+)*)\s+-c\s+"((?:[^"\\]|\\.)*)"', raw, flags=re.S)
    if not m:
        return {"rewritten": False, "command": raw}
    py_bin = m.group(1)
    body = m.group(2)
    if ('\\"' not in body) and ("\n" not in body) and ("{" not in body):
        return {"rewritten": False, "command": raw}
    clean_body = body.replace('\\"', '"').replace("\\n", "\n")
    heredoc = f"{py_bin} - << 'PYEOF'\n{clean_body}\nPYEOF"
    return {"rewritten": True, "command": heredoc, "original": raw}


def check_sandbox_and_own_cid_boundary(
    tool_name: str,
    tool_args: Dict[str, Any],
    root_conversation_id: str = "",
    sandbox_root: str = "",
) -> Optional[Dict[str, str]]:
    """
    AGW-W12-06 (`R33-SBX-02`): Explicitly allows reading the current session's own `<root_conversation_id>`
    `.system_generated/` (step/task stdout) and `scratch/` paths while enforcing sandbox boundaries.
    """
    if not isinstance(tool_args, dict):
        return None
    target = str(
        tool_args.get("TargetFile")
        or tool_args.get("AbsolutePath")
        or tool_args.get("Path")
        or tool_args.get("file_path")
        or ""
    ).strip()
    if not target:
        return None
    if root_conversation_id and root_conversation_id in target:
        if any(seg in target for seg in (".system_generated", "/scratch/", "transcript")):
            return {"decision": "allow"}
    if sandbox_root and tool_name in ("write_to_file", "replace_file_content", "edit_file", "write_file"):
        norm_t = os.path.abspath(os.path.expanduser(target))
        norm_s = os.path.abspath(os.path.expanduser(sandbox_root))
        if not (norm_t.startswith(norm_s) or norm_t.startswith("/tmp/") or norm_t.startswith("/dev/shm/")):
            return {
                "decision": "deny",
                "reason": f"Sandbox Boundary Guard: write target '{target}' is outside isolated sandbox '{sandbox_root}'.",
            }
    return None


def check_reactive_wakeup_polling_guard(
    tool_name: str,
    tool_args: Dict[str, Any],
    transcript_steps: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, str]]:
    """
    AGW-W12-07 (`HARNESS-BUG-3`): Blocks consecutive `manage_task(Action='status')` or
    `manage_subagents(Action='list')` polling loops unless a watchdog timeout notification arrived.
    """
    if tool_name not in ("manage_task", "manage_subagents") or not isinstance(tool_args, dict):
        return None
    action = str(tool_args.get("Action") or "").lower()
    if action not in ("status", "list"):
        return None
    steps = transcript_steps or []
    consecutive_polls = 0
    for st in reversed(steps[-8:]):
        content = str(st.get("content") or "")
        if "Background command is still running" in content or "NotificationTimeoutSeconds" in content:
            return None
        for tc in st.get("tool_calls") or []:
            if isinstance(tc, dict) and tc.get("name") in ("manage_task", "manage_subagents"):
                t_act = str((tc.get("args") or {}).get("Action") or "").lower()
                if t_act in ("status", "list"):
                    consecutive_polls += 1
    if consecutive_polls >= 2:
        return {
            "decision": "deny",
            "reason": (
                "Reactive Wakeup Guard: Do not poll background tasks or subagents in a loop. "
                "End your turn and wait for the system's automatic completion notification."
            ),
        }
    return None


def enforce_non_interactive_vcs_flags(cmd: str) -> Dict[str, Any]:
    """
    AGW-W12-14: Injects `GIT_PAGER=cat JJ_PAGER=cat PYTHONDONTWRITEBYTECODE=1` on interactive
    VCS or Python commands so subshells never hang on a TTY pager or emit `.pyc` artifacts.
    """
    raw = (cmd or "").strip()
    if not raw:
        return {"modified": False, "command": raw}
    needs_env = bool(re.search(r"\b(git\s+(?:diff|log|show|status|branch)|jj\s+(?:log|diff|st|status)|python3?)\b", raw))
    if not needs_env or "GIT_PAGER=cat" in raw:
        return {"modified": False, "command": raw}
    prefixed = f"GIT_PAGER=cat JJ_PAGER=cat PYTHONDONTWRITEBYTECODE=1 {raw}"
    return {"modified": True, "command": prefixed}


def check_manual_release_push_gate(cmd: str, user_prompt: str = "") -> Optional[Dict[str, str]]:
    """
    AGW-W12-14 (`Case Q`): Blocks unrequested production release pushes (`--ship` or tag pushes)
    unless explicitly requested by the user in the active prompt.
    """
    raw = (cmd or "").strip()
    if not re.search(r"((?<!\w)--ship\b|\bgit\s+push\s+\S+\s+refs/tags/)", raw):
        return None
    prompt_l = (user_prompt or "").lower()
    if any(k in prompt_l for k in ("ship release", "--ship", "push tag", "publish release")):
        return None
    return {
        "decision": "deny",
        "reason": "Release Push Gate (Case Q): '--ship' or tag release push requires explicit user authorization.",
    }


def normalize_dual_tool_schema_payload(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    AGW-W12-11 (SCOUT2-12): Normalizes dual tool schemas across Antigravity CLI / Antigravity 2.0 / Claude Code
    harnesses (`write_file`/`edit_file`/`read_file` vs `write_to_file`/`replace_file_content`/`view_file`)
    so every downstream Sentinel rule receives canonical keys without false-negative misses.
    """
    if not isinstance(tool_args, dict):
        return {"canonical_tool": tool_name, "args": {}}
    args = dict(tool_args)
    alias_map = {
        "write_file": "write_to_file",
        "create_file": "write_to_file",
        "Write": "write_to_file",
        "edit_file": "replace_file_content",
        "Edit": "replace_file_content",
        "MultiEdit": "replace_file_content",
        "read_file": "view_file",
        "Read": "view_file",
        "Bash": "run_command",
        "bash": "run_command",
    }
    canonical_tool = alias_map.get(tool_name, tool_name)

    target_path = (
        args.get("TargetFile")
        or args.get("Path")
        or args.get("AbsolutePath")
        or args.get("file_path")
        or args.get("path")
        or ""
    )
    if target_path:
        args.setdefault("TargetFile", target_path)
        args.setdefault("Path", target_path)
        args.setdefault("AbsolutePath", target_path)

    content_val = args.get("CodeContent") if "CodeContent" in args else args.get("Content", args.get("content"))
    if content_val is not None:
        args.setdefault("CodeContent", content_val)
        args.setdefault("Content", content_val)

    old_val = args.get("TargetContent") if "TargetContent" in args else args.get("Target", args.get("old_string"))
    if old_val is not None:
        args.setdefault("TargetContent", old_val)
        args.setdefault("Target", old_val)

    new_val = args.get("ReplacementContent") if "ReplacementContent" in args else args.get("Replacement", args.get("new_string"))
    if new_val is not None:
        args.setdefault("ReplacementContent", new_val)
        args.setdefault("Replacement", new_val)

    cmd_val = args.get("CommandLine") if "CommandLine" in args else args.get("command")
    if cmd_val is not None:
        args.setdefault("CommandLine", cmd_val)
        args.setdefault("command", cmd_val)

    return {"canonical_tool": canonical_tool, "args": args}


def evaluate_tool_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_name = str(payload.get("hookEventName") or payload.get("event") or "")
    if event_name in ("PostToolUse", "post-tool-use"):
        return {}

    norm_payload = normalize_hook_payload(payload)
    raw_tool_name = str(norm_payload.get("toolName") or norm_payload.get("tool_name") or "")
    raw_tool_args = norm_payload.get("toolArgs") or norm_payload.get("tool_input") or norm_payload.get("args") or {}
    if isinstance(raw_tool_args, str):
        try:
            raw_tool_args = json.loads(raw_tool_args)
        except Exception:
            raw_tool_args = {"raw": raw_tool_args}

    dual = normalize_dual_tool_schema_payload(raw_tool_name, raw_tool_args)
    tool_name = dual["canonical_tool"]
    tool_args = dual["args"]

    root_cid = str(norm_payload.get("rootConversationId") or "")
    cron_res = check_schedule_cron_daemon_guard(tool_name, tool_args)
    if cron_res is not None:
        return cron_res

    own_res = check_own_session_transcript_access(tool_name, tool_args, root_cid)
    if own_res is not None:
        return own_res

    for mod in RULE_MODULES:
        res = mod.check(tool_name, tool_args)
        if res is not None:
            return res

    return {"decision": "allow"}


def normalize_hook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes hook payloads across Antigravity (toolName/toolArgs/rootConversationId) and Claude Code / generic harnesses (tool_name/tool_input/session_id)."""
    if not isinstance(payload, dict):
        return {}
    out = dict(payload)
    if "toolName" not in out and "tool_name" in out:
        out["toolName"] = out["tool_name"]
    if "toolArgs" not in out and "tool_input" in out:
        out["toolArgs"] = out["tool_input"]
    root_cid = (
        out.get("rootConversationId")
        or out.get("root_conversation_id")
        or out.get("conversationId")
        or out.get("conversation_id")
        or out.get("session_id")
        or ""
    )
    if root_cid:
        out["rootConversationId"] = str(root_cid)
    return out


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    result = evaluate_tool_call(payload)
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
