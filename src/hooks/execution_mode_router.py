#!/usr/bin/env python3
"""
Role: Dual-Mode Execution & Metadata Router (`execution_mode_router.py` v1.4.0)
Purpose: Classifies each turn into SWE/benchmark sandbox mode vs. enterprise domain
         workspace mode, strips Turn-0 `<ADDITIONAL_METADATA>` blocks (`RC-1` / `L3b`)
         so ephemeral environment metadata never pollutes Knowledge Graph entity scoring,
         and selects the appropriate verification and token-budget profile.
How It Is Used: Imported by `src/hooks/kg_pre_invocation_hook.py` and
                `src/hooks/agent_stop_black_hat_gate.py`, or invoked via CLI
                `python3 -B src/hooks/execution_mode_router.py --self-test`.
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict

sys.dont_write_bytecode = True

ADDITIONAL_METADATA_RE = re.compile(r"<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>", re.IGNORECASE)
SYSTEM_MESSAGE_RE = re.compile(r"<SYSTEM_MESSAGE>[\s\S]*?</SYSTEM_MESSAGE>", re.IGNORECASE)

SWE_SANDBOX_MARKERS = (
    "/testbed",
    "/workspace/swe-bench",
    "terminal-bench",
    "tbench",
    "swebench",
    "pytest",
    "unittest discover",
)


def strip_turn0_metadata(raw_text: str) -> str:
    """Strips `<ADDITIONAL_METADATA>` and `<SYSTEM_MESSAGE>` blocks from Turn-0 user inputs."""
    if not raw_text:
        return ""
    cleaned = ADDITIONAL_METADATA_RE.sub("", raw_text)
    cleaned = SYSTEM_MESSAGE_RE.sub("", cleaned)
    return cleaned.strip()


def classify_execution_mode(
    prompt_text: str = "",
    cwd: str = "",
    env: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Determines whether the active session is running inside an isolated SWE benchmark
    sandbox (`swe_sandbox`) or an enterprise domain workspace (`enterprise_domain`).
    """
    env_map = env if env is not None else dict(os.environ)
    clean_prompt = strip_turn0_metadata(prompt_text)
    combined = f"{clean_prompt}\n{cwd}".lower()

    is_swe_flag = env_map.get("ANTIGRAVITY_SWE_SANDBOX") == "1" or env_map.get("TBENCH_SANDBOX") == "1"
    matched_markers = [m for m in SWE_SANDBOX_MARKERS if m in combined]
    is_isolated_swe = bool(is_swe_flag or (cwd.startswith("/testbed") or "terminal-bench" in combined))

    mode = "swe_sandbox" if is_isolated_swe else "enterprise_domain"
    return {
        "mode": mode,
        "is_isolated_swe": is_isolated_swe,
        "matched_markers": matched_markers,
        "cleaned_prompt": clean_prompt,
        "metadata_stripped": clean_prompt != (prompt_text or "").strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dual-Mode Execution Router v1.4.0")
    parser.add_argument("--prompt", default="", help="Raw prompt text")
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory")
    parser.add_argument("--self-test", action="store_true", help="Run hermetic self-test")
    args = parser.parse_args()

    if args.self_test:
        sample = "<ADDITIONAL_METADATA>os: linux</ADDITIONAL_METADATA>\n<SYSTEM_MESSAGE>internal</SYSTEM_MESSAGE>\nFix bug in /testbed/app.py"
        res = classify_execution_mode(sample, cwd="/testbed")
        ok = (
            res["mode"] == "swe_sandbox"
            and res["is_isolated_swe"] is True
            and res["metadata_stripped"] is True
            and "<ADDITIONAL_METADATA>" not in res["cleaned_prompt"]
        )
        print(json.dumps({"verdict": "PASS" if ok else "FAIL", "result": res}))
        return 0 if ok else 1

    print(json.dumps(classify_execution_mode(args.prompt, cwd=args.cwd), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
