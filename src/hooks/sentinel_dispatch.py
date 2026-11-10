#!/usr/bin/env python3
"""Modular PreToolUse Sentinel Dispatcher v3.9 (Clean-Room Enterprise Edition).

Evaluates deterministic pre-execution guardrails (<50ms) before any tool executes:
1. Destructive shell command mediation (`decision = "force_ask"`, Turbo-safe)
2. Deprecated AI model rejection (Rule 28, native + legacy tool schemas)
3. File size & binary bounds enforcement
4. Clean-room path & secret anonymization (Rule 11)
5. Control-plane self-protection (`force_ask`, Rule 31)
6. Skill & hook deobfuscation / prompt-injection scanner
7. Zero-raw-LaTeX document export gate
8. Recurring cron `IsDaemon=True` livelock guard & own-session transcript allowlist
9. `S-01` strict `_FILE_SCHEMA_TOOLS` normalization & dual-harness tool alias mapping
10. `GOLDFISH-RO-1` (`Case S`) stateless investigator read-only enforcement (`BUG-14` heredoc/quote stripper + `BUG-15` `/dev/shm/gf_<cid>` scratch salvage)
11. `L3` identical-command anti-spin circuit breaker (`>= 3` repeated failing/no-op calls)
12. `PostInvocation` UX plain-English subagent `Role` prefix rewriter
"""

import json
import os
import re
import resource
import sys
from typing import Any, Dict, List, Optional

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

CHILD_RLIMIT_AS_BYTES = 24 * 1024 * 1024 * 1024  # 24 GiB OOM guard

from rules import (
    audit_skill_hook_safety,
    deprecated_models,
    destructive_commands,
    file_bounds,
    r31_hook_integrity_guard,
    rule_11_anonymization,
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

_FILE_SCHEMA_TOOLS = frozenset({
    "read_file",
    "view_file",
    "Read",
    "write_file",
    "write_to_file",
    "create_file",
    "Write",
    "edit_file",
    "replace_file_content",
    "multi_replace_file_content",
    "Edit",
    "MultiEdit",
})

_GOLDFISH_NAMES = frozenset({"black-hat-goldfish", "black_hat_goldfish"})
_GOLDFISH_MUTATING_TOOLS = frozenset({
    "write_file",
    "edit_file",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "notebook_edit",
    "create_file",
    "generate_image",
    "Write",
    "Edit",
    "MultiEdit",
})
_GOLDFISH_MUTATING_SHELL_RE = re.compile(
    r"(?:(?:^|[;&|\n]\s*)(?:rm|mv|cp|chmod|chown|ln|touch|truncate|rmdir)\s+"
    r"|\bsed\s+-i\b"
    r"|\btee\s+(?!-a?\s*/dev/null\b)"
    r"|\bgit\s+(?:add|commit|push|reset|clean|checkout\s+--|restore|stash|merge|rebase|tag|cherry-pick)\b"
    r"|\b(?:pip|pip3|npm|yarn|pnpm|apt|apt-get)\s+(?:install|uninstall|remove)\b"
    r"|(?<![0-9<>])>>?\s*(?!/dev/null\b|/dev/shm/gf_|&[12]\b)[^\s|;&]+)",
    re.IGNORECASE,
)


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


def strip_heredoc_and_quoted_literals(cmd: str) -> str:
    """BUG-14: Strips heredoc bodies and single/double-quoted string literals before scanning shell operators."""
    if not cmd:
        return ""

    def _strip_hd(text: str) -> str:
        lines = text.splitlines()
        out_lines: List[str] = []
        end_tag: Optional[str] = None
        for ln in lines:
            if end_tag is not None:
                if ln.strip() == end_tag:
                    end_tag = None
                continue
            m = re.search(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", ln)
            out_lines.append(re.sub(r"<<-?\s*['\"]?[A-Za-z_][A-Za-z0-9_]*['\"]?.*$", "", ln))
            if m:
                end_tag = m.group(1)
        return "\n".join(out_lines)

    stripped = _strip_hd(cmd)
    stripped = re.sub(r"'[^']*'", "''", stripped)
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)
    return stripped


def _is_safe_goldfish_shm_mkdir_or_cleanup(segment: str, conversation_id: str = "") -> bool:
    """BUG-15: Allows `mkdir -p` / `rm -rf` / `touch` strictly inside `/dev/shm/gf_<cid>`."""
    tokens = segment.strip().split()
    if not tokens:
        return False
    verb = os.path.basename(tokens[0])
    if verb not in ("mkdir", "rm", "touch"):
        return False
    operands = [t.strip("\"'") for t in tokens[1:] if t and not t.startswith("-")]
    if not operands:
        return False
    allowed_prefix = "/dev/shm/gf_"
    for op in operands:
        if ".." in op or "$" in op or "`" in op:
            return False
        if not op.startswith(allowed_prefix):
            return False
    return True


def enforce_goldfish_readonly_command(
    tool_name: str,
    tool_args: Dict[str, Any],
    agent_name: str = "",
    conversation_id: str = "",
) -> Optional[Dict[str, str]]:
    """GOLDFISH-RO-1 (`Case S`): Enforces strict zero-mutation air-gap on Stage-1 `black-hat-goldfish`."""
    if (agent_name or "").strip().lower() not in _GOLDFISH_NAMES:
        return None
    if tool_name in _GOLDFISH_MUTATING_TOOLS:
        return {
            "decision": "deny",
            "reason": (
                f"GOLDFISH-RO-1 Read-Only Guard: Stage-1 investigator '{agent_name}' cannot call "
                f"mutating tool '{tool_name}'. Record discrepancies without modifying disk state."
            ),
        }
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": "GOLDFISH-RO-1 MAX_DEPTH=1 Guard: Stage-1 investigator cannot spawn subagents.",
        }
    if tool_name not in ("run_command", "Bash", "bash") or not isinstance(tool_args, dict):
        return None

    raw_cmd = str(tool_args.get("CommandLine") or tool_args.get("command") or "")
    skeleton = strip_heredoc_and_quoted_literals(raw_cmd)
    for seg in re.split(r"(?:&&|\|\||[;\n|])", skeleton):
        seg_s = seg.strip()
        if not seg_s:
            continue
        if _is_safe_goldfish_shm_mkdir_or_cleanup(seg_s, conversation_id):
            continue
        m = _GOLDFISH_MUTATING_SHELL_RE.search(seg_s)
        if m:
            return {
                "decision": "deny",
                "reason": (
                    f"GOLDFISH-RO-1 Read-Only Guard: Mutating shell construct '{m.group(0).strip()}' "
                    "is prohibited inside black-hat-goldfish. Use read-only commands or `/dev/shm/gf_<cid>/` scratch only."
                ),
            }
    if re.search(r"\b(?:os\.(?:remove|unlink|rmdir|rename|replace|chmod)|shutil\.(?:rmtree|move|copy))\s*\(", raw_cmd):
        if "/dev/shm/gf_" not in raw_cmd:
            return {
                "decision": "deny",
                "reason": (
                    "GOLDFISH-RO-1 Read-Only Guard: Python filesystem mutation outside `/dev/shm/gf_<cid>/` "
                    "is prohibited inside black-hat-goldfish."
                ),
            }
    return None


def check_identical_command_anti_spin(
    tool_name: str,
    tool_args: Dict[str, Any],
    transcript_steps: Optional[List[Dict[str, Any]]] = None,
    threshold: int = 3,
) -> Optional[Dict[str, str]]:
    """v3.9 `L3` (`H3`): Blocks >= `threshold` consecutive identical failing or no-op `run_command` loops."""
    if tool_name not in ("run_command", "Bash", "bash") or not isinstance(tool_args, dict) or not transcript_steps:
        return None
    cur_cmd = re.sub(r"\s+", " ", str(tool_args.get("CommandLine") or tool_args.get("command") or "").strip())
    if not cur_cmd:
        return None

    identical_streak = 0
    saw_failure_or_empty = False
    for st in reversed(transcript_steps[-12:]):
        st_type = str(st.get("type") or "").upper()
        if st_type in ("USER_INPUT", "USER_EXPLICIT"):
            break
        content = str(st.get("content") or "")
        if any(tok in content for tok in ("exited with code 1", "exited with code 2", "Traceback", "ERROR", "No output")):
            saw_failure_or_empty = True
        tcs = st.get("tool_calls") or []
        if not tcs:
            continue
        matched_this_step = False
        for tc in tcs:
            if not isinstance(tc, dict):
                continue
            if tc.get("name") not in ("run_command", "Bash", "bash"):
                return None
            prev_args = tc.get("args") or {}
            if isinstance(prev_args, str):
                try:
                    prev_args = json.loads(prev_args)
                except Exception:
                    prev_args = {}
            prev_cmd = re.sub(
                r"\s+",
                " ",
                str((prev_args or {}).get("CommandLine") or (prev_args or {}).get("command") or "").strip(),
            )
            if prev_cmd == cur_cmd:
                matched_this_step = True
            else:
                return None
        if matched_this_step:
            identical_streak += 1
            if identical_streak >= threshold:
                break

    if identical_streak >= threshold and (saw_failure_or_empty or identical_streak >= threshold):
        return {
            "decision": "deny",
            "reason": (
                f"Anti-Spin Circuit Breaker (L3): Identical command executed {identical_streak} times consecutively "
                "without progress. Formulate a distinct diagnostic check or fix before retrying."
            ),
        }
    return None


def _load_recent_transcript_tail(transcript_path: str, max_lines: int = 30) -> List[Dict[str, Any]]:
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    try:
        sz = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as fh:
            if sz > 65536:
                fh.seek(sz - 65536)
                raw = fh.read().decode("utf-8", errors="ignore")
                nl = raw.find("\n")
                lines = (raw[nl + 1 :] if nl >= 0 else raw).splitlines()
            else:
                lines = fh.read().decode("utf-8", errors="ignore").splitlines()
        out: List[Dict[str, Any]] = []
        for ln in lines[-max_lines:]:
            ln = ln.strip()
            if ln:
                try:
                    obj = json.loads(ln)
                    if isinstance(obj, dict):
                        out.append(obj)
                except Exception:
                    continue
        return out
    except Exception:
        return []


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
    if tool_name not in ("view_file", "read_file", "Read") or not isinstance(tool_args, dict):
        return None
    target = str(
        tool_args.get("Path")
        or tool_args.get("TargetFile")
        or tool_args.get("AbsolutePath")
        or tool_args.get("file_path")
        or ""
    ).strip()
    if not target or "transcript" not in target:
        return None
    if root_conversation_id and root_conversation_id in target:
        return {"decision": "allow"}
    return None


def rewrite_inline_python_c_to_heredoc(cmd: str) -> Dict[str, Any]:
    """AGW-W12-05 (`MODEL-BUG-3`): Rewrites fragile double-quoted `python3 -c "..."` into safe single-quoted heredocs."""
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
    """AGW-W12-06 (`R33-SBX-02`): Allows own `<root_conversation_id>` `.system_generated/` & `scratch/` while enforcing sandbox boundaries."""
    if tool_name not in _FILE_SCHEMA_TOOLS or not isinstance(tool_args, dict):
        return None
    target = str(
        tool_args.get("Path")
        or tool_args.get("TargetFile")
        or tool_args.get("AbsolutePath")
        or tool_args.get("file_path")
        or ""
    ).strip()
    if not target:
        return None
    if root_conversation_id and root_conversation_id in target:
        if any(seg in target for seg in (".system_generated", "/scratch/", "transcript")):
            return {"decision": "allow"}
    if sandbox_root and tool_name in ("write_to_file", "replace_file_content", "edit_file", "write_file", "multi_replace_file_content", "Write", "Edit", "MultiEdit"):
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
    """AGW-W12-07 (`HARNESS-BUG-3`): Blocks consecutive `manage_task(status)` / `manage_subagents(list)` polling loops."""
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
    """AGW-W12-14: Injects `GIT_PAGER=cat JJ_PAGER=cat PYTHONDONTWRITEBYTECODE=1` on interactive VCS or Python calls."""
    raw = (cmd or "").strip()
    if not raw:
        return {"modified": False, "command": raw}
    needs_env = bool(
        re.search(r"\b(git\s+(?:diff|log|show|status|branch)|jj\s+(?:log|diff|st|status)|python3?)\b", raw)
    )
    if not needs_env or "GIT_PAGER=cat" in raw:
        return {"modified": False, "command": raw}
    prefixed = f"GIT_PAGER=cat JJ_PAGER=cat PYTHONDONTWRITEBYTECODE=1 {raw}"
    return {"modified": True, "command": prefixed}


def check_manual_release_push_gate(cmd: str, user_prompt: str = "") -> Optional[Dict[str, str]]:
    """AGW-W12-14 (`Case Q`): Blocks unrequested production release pushes (`--ship` or tag pushes)."""
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
    """AGW-W12-11 (SCOUT2-12): Normalizes dual tool schemas across Antigravity CLI / Antigravity 2.0 / Claude Code."""
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


def normalize_file_schema_args_for_rules(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """S-01: Scopes legacy TargetFile/AbsolutePath/CodeContent alias expansion strictly to `_FILE_SCHEMA_TOOLS` in-memory."""
    if not isinstance(tool_args, dict) or tool_name not in _FILE_SCHEMA_TOOLS:
        return tool_args if isinstance(tool_args, dict) else {}
    return normalize_dual_tool_schema_payload(tool_name, tool_args)["args"]


def evaluate_tool_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    event_name = str(payload.get("hookEventName") or payload.get("event") or "")
    if event_name in ("PostToolUse", "post-tool-use"):
        return {}

    norm_payload = normalize_hook_payload(payload)
    raw_tool_name = str(norm_payload.get("toolName") or norm_payload.get("tool_name") or "")
    raw_args = norm_payload.get("toolArgs") or norm_payload.get("tool_input") or norm_payload.get("args") or {}
    if isinstance(raw_args, str):
        try:
            raw_args = json.loads(raw_args)
        except Exception:
            raw_args = {"raw": raw_args}
    if not isinstance(raw_args, dict):
        raw_args = {}

    agent_name = str(norm_payload.get("agentName") or norm_payload.get("agent_name") or "")
    conv_id = str(norm_payload.get("conversationId") or norm_payload.get("conversation_id") or "")
    root_cid = str(norm_payload.get("rootConversationId") or "")
    transcript_path = str(norm_payload.get("transcriptPath") or norm_payload.get("transcript_path") or "")

    # 1. GOLDFISH-RO-1 (Case S) read-only investigator enforcement
    gf_res = enforce_goldfish_readonly_command(raw_tool_name, raw_args, agent_name=agent_name, conversation_id=conv_id)
    if gf_res is not None:
        return gf_res

    # 2. Schedule cron livelock guard
    cron_res = check_schedule_cron_daemon_guard(raw_tool_name, raw_args)
    if cron_res is not None:
        return cron_res

    # 3. Reactive polling & L3 identical-command anti-spin guards
    tail_steps = (
        norm_payload.get("transcriptSteps")
        if isinstance(norm_payload.get("transcriptSteps"), list)
        else (_load_recent_transcript_tail(transcript_path) if raw_tool_name in ("run_command", "Bash", "bash", "manage_task", "manage_subagents") else [])
    )
    if raw_tool_name in ("manage_task", "manage_subagents"):
        poll_res = check_reactive_wakeup_polling_guard(raw_tool_name, raw_args, tail_steps)
        if poll_res is not None:
            return poll_res
    elif raw_tool_name in ("run_command", "Bash", "bash"):
        spin_res = check_identical_command_anti_spin(raw_tool_name, raw_args, tail_steps)
        if spin_res is not None:
            return spin_res
        rel_res = check_manual_release_push_gate(str(raw_args.get("CommandLine") or raw_args.get("command") or ""))
        if rel_res is not None:
            return rel_res

    # 4. Own-session transcript allowlist
    own_res = check_own_session_transcript_access(raw_tool_name, raw_args, root_cid)
    if own_res is not None:
        return own_res

    # 5. Scoped rule modules (`S-01`: never leak synthetic keys back into non-file tool args)
    if raw_tool_name in _FILE_SCHEMA_TOOLS or raw_tool_name in ("Bash", "bash"):
        dual = normalize_dual_tool_schema_payload(raw_tool_name, raw_args)
        rule_tool = dual["canonical_tool"]
        rule_args = dual["args"]
    else:
        rule_tool = raw_tool_name
        rule_args = raw_args

    for mod in RULE_MODULES:
        res = mod.check(rule_tool, rule_args)
        if res is not None:
            return res

    # 6. Plain-English Black-Hat subagent Role formatter (minimal `overwrite` delta only)
    if raw_tool_name == "invoke_subagent":
        try:
            from black_hat_in_progress_ux_hook import rewrite_black_hat_subagent_role

            rw = rewrite_black_hat_subagent_role(raw_args)
            if rw is not None:
                return rw
        except Exception:
            pass

    return {"decision": "allow"}


def normalize_hook_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes PreToolUse payloads across Antigravity (`toolCall.name`/`toolName`) and generic MCP/CLI harnesses."""
    if not isinstance(payload, dict):
        return {}
    out = dict(payload)
    tc = out.get("toolCall")
    if isinstance(tc, dict):
        if "toolName" not in out and tc.get("name"):
            out["toolName"] = tc["name"]
        if "toolArgs" not in out and "args" in tc:
            out["toolArgs"] = tc["args"]
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
