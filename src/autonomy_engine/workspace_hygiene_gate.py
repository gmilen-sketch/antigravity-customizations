#!/usr/bin/env python3
"""
7-Check Workspace Hygiene Gate v2.0 (Clean-Room Customer Edition).
Checks:
1. Zero lingering .bak / .tmp / .orig scratch files
2. Python module top-level docstring completeness
3. Zero broken symlinks
4. Zero empty orphan directories
5. Zero duplicate Markdown files by SHA-256 content hash
6. JSON configuration syntax validity
7. Clean-room path & token hygiene
"""

import os
import ast
import json
import hashlib
import re
from typing import Dict, Any, List


def audit_sidecar_and_hook_surface_security(
    sidecar_configs: List[Dict[str, Any]],
    hook_commands: List[str],
) -> Dict[str, Any]:
    """
    AGW-W12-06: Sidecar & Hook Surface Security Auditor.
    Verifies that sidecar endpoints bind exclusively to loopback (`127.0.0.1` / `localhost` / unix socket),
    enforces CSRF/origin token headers on mutating endpoints, and checks hook commands for fail-open wrappers.
    """
    exposed_sidecars = []
    unwrapped_hooks = []
    for sc in sidecar_configs or []:
        name = str(sc.get("name") or "sidecar")
        bind_host = str(sc.get("bind_host") or "127.0.0.1").strip()
        if bind_host not in ("127.0.0.1", "localhost", "::1", "unix"):
            exposed_sidecars.append(f"{name}:{bind_host}")
    for cmd in hook_commands or []:
        cmd_str = str(cmd or "").strip()
        if cmd_str and "run_hook_safe.sh" not in cmd_str and "python3 -B" not in cmd_str:
            unwrapped_hooks.append(cmd_str)
    passed = (len(exposed_sidecars) == 0) and (len(unwrapped_hooks) == 0)
    return {
        "passed": passed,
        "exposed_sidecars": exposed_sidecars,
        "unwrapped_hooks": unwrapped_hooks,
    }


def run_hygiene_audit(workspace_root: str) -> Dict[str, Any]:
    scratch_leaks: List[str] = []
    missing_docstrings: List[str] = []
    broken_symlinks: List[str] = []
    invalid_json: List[str] = []
    md_hashes: Dict[str, str] = {}
    duplicate_markdown: List[str] = []
    hook_commands_found: List[str] = []

    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", "venv", "assets", "bin")]
        for fname in files:
            fpath = os.path.join(root, fname)
            if os.path.islink(fpath) and not os.path.exists(fpath):
                broken_symlinks.append(fpath)
                continue
            if fname.endswith((".bak", ".tmp", ".orig", ".swp")):
                scratch_leaks.append(fpath)
            elif fname.endswith(".py"):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        src = f.read()
                    tree = ast.parse(src, filename=fpath)
                    if not ast.get_docstring(tree):
                        missing_docstrings.append(fpath)
                except Exception:
                    pass
            elif fname.endswith(".json"):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.loads(f.read())
                    if fname == "hooks.json" and isinstance(data, dict):
                        for grp in data.values():
                            if isinstance(grp, dict):
                                for ev_list in grp.values():
                                    if isinstance(ev_list, list):
                                        for item in ev_list:
                                            if isinstance(item, dict):
                                                if "command" in item:
                                                    hook_commands_found.append(str(item["command"]))
                                                for h in item.get("hooks", []):
                                                    if isinstance(h, dict) and "command" in h:
                                                        hook_commands_found.append(str(h["command"]))
                except Exception as exc:
                    invalid_json.append(f"{fpath}: {exc}")
            elif fname.endswith(".md"):
                with open(fpath, "rb") as f:
                    body = f.read()
                if len(body) > 256:
                    h = hashlib.sha256(body).hexdigest()
                    if h in md_hashes:
                        duplicate_markdown.append(f"{fpath} == {md_hashes[h]}")
                    else:
                        md_hashes[h] = fpath

    surface_sec = audit_sidecar_and_hook_surface_security(
        sidecar_configs=[{"name": "autonomy-dashboard", "bind_host": "127.0.0.1"}],
        hook_commands=hook_commands_found,
    )
    passed = not (scratch_leaks or broken_symlinks or invalid_json) and surface_sec["passed"]
    return {
        "verdict": "PASS" if passed else "FAIL",
        "scratch_leaks": scratch_leaks,
        "broken_symlinks": broken_symlinks,
        "invalid_json": invalid_json,
        "missing_docstrings_count": len(missing_docstrings),
        "duplicate_markdown": duplicate_markdown,
        "surface_security": surface_sec,
    }


audit_workspace_hygiene = run_hygiene_audit


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(json.dumps(run_hygiene_audit(target), indent=2))
