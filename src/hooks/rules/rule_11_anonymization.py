#!/usr/bin/env python3
"""Rule 11: Clean-Room Path, Code-Fence-Safe PII Scrubber & Secret Anonymization Gate (`AGW-W12-07`)."""
import hashlib
import os
import re
from typing import Dict, Any, List, Optional

_HOME_PATH_RE = re.compile(r"(?:/[A-Za-z0-9_.-]+)*/home/[A-Za-z0-9_.-]+|/Users/[A-Za-z0-9_.-]+")
_EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
_SAFE_DOMAINS = {"example.com", "example.org", "localhost", "users.noreply.github.com"}


def redact_code_safe_pii_and_partition_spool(
    markdown_text: str,
    session_id: str = "default-session",
    spool_root: str = "/dev/shm",
) -> Dict[str, Any]:
    """
    AGW-W12-07: Scrubs local workstation home paths and non-example email addresses across
    prose while preserving fenced code block syntax structure, and computes a per-session
    partitioned spool path (`<spool_root>/agw_spool_<hash>.json`) to eliminate multi-tenant collisions.
    """
    raw = markdown_text or ""
    redactions = 0

    def _replace_email(match: re.Match) -> str:
        nonlocal redactions
        domain = match.group(2).lower()
        if domain in _SAFE_DOMAINS:
            return match.group(0)
        redactions += 1
        return "<USER_LDAP>@example.com"

    def _scrub_segment(seg: str) -> str:
        nonlocal redactions
        home_hits = len(_HOME_PATH_RE.findall(seg))
        if home_hits:
            redactions += home_hits
            seg = _HOME_PATH_RE.sub("<USER_HOME_DIR>", seg)
        seg = _EMAIL_RE.sub(_replace_email, seg)
        return seg

    parts = re.split(r"(```[\s\S]*?```)", raw)
    cleaned_parts: List[str] = []
    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            # Inside code blocks, only scrub raw workstation home paths while preserving code syntax
            home_hits = len(_HOME_PATH_RE.findall(part))
            if home_hits:
                redactions += home_hits
                part = _HOME_PATH_RE.sub("<USER_HOME_DIR>", part)
            cleaned_parts.append(part)
        else:
            cleaned_parts.append(_scrub_segment(part))

    sid_hash = hashlib.sha256((session_id or "default").encode("utf-8")).hexdigest()[:12]
    partitioned_spool = os.path.join(spool_root, f"agw_spool_{sid_hash}.json")
    return {
        "scrubbed_text": "".join(cleaned_parts),
        "redactions_count": redactions,
        "partitioned_spool_path": partitioned_spool,
        "code_fences_preserved": raw.count("```") == "".join(cleaned_parts).count("```"),
    }


def check(tool_name: str, tool_args: Dict[str, Any]) -> Optional[Dict[str, str]]:
    if tool_name in ("write_to_file", "replace_file_content", "write_file", "edit_file"):
        target = str(tool_args.get("TargetFile", tool_args.get("Path", "")))
        content = (
            str(tool_args.get("CodeContent", ""))
            + str(tool_args.get("ReplacementContent", ""))
            + str(tool_args.get("Content", ""))
            + str(tool_args.get("Replacement", ""))
        )
        home_dir = os.path.expanduser("~")
        if "/public/" in target or "README.md" in target:
            if home_dir and len(home_dir) > 6 and home_dir in content:
                return {
                    "decision": "block",
                    "reason": "Rule 11 Violation: Hardcoded local workstation path detected in shared/public artifact.",
                }
    return None
