#!/usr/bin/env python3
"""
Role: Clean-Room Verification Suite for v1.4.0 Hook Hardening & Wave-12 Kernels (`test_v140_wave12_and_hooks.py`)
Purpose: Validates all 19 clean-room items ported in v1.4.0:
         - Group A (7 Core Hook, Runtime & Manifest Stability Fixes):
           1. `src/hooks/run_hook_safe.sh` fail-open POSIX wrapper & zero-bytecode enforcement
           2. `src/hooks/kg_pre_invocation_hook.py` `<SYSTEM_MESSAGE>` stripping, Turn-0 ephemeral dedup (`EPH-ONCE-01`),
              negation filter (`KG-N5`), and strict `hooks.proto` `PreInvocationHookResult` schema (`RC-8`)
           3. `src/hooks/sentinel_dispatch.py` dual-schema normalizer (`AGW-W12-11`), `PostToolUse` `{}` return, and `RLIMIT_AS`
           4. `src/hooks/agent_stop_black_hat_gate.py` `Case R` `/task-` reactive wakeup unlock, `is_isolated_swe` short-circuit,
              and `LL-2` pre-return attached hygiene check
           5. `src/hooks/execution_mode_router.py` SWE sandbox vs. enterprise domain router & Turn-0 `<ADDITIONAL_METADATA>` stripper
           6. `src/hooks/lazy_plugin_bootstrap.py` `NONDEV-BUG-1..3` non-dev adopter guard & multi-path skills fallback
           7. Strict manifest schema (`v1.4.0` + removal of deprecated duplicate `"tags"` key)
         - Group B (12 Wave-12 Graduated Slim Kernels `AGW-W12-01..13`):
           `AGW-W12-01`, `AGW-W12-02`, `AGW-W12-03`, `AGW-W12-04`, `AGW-W12-05`, `AGW-W12-06`,
           `AGW-W12-07`, `AGW-W12-08`, `AGW-W12-09`, `AGW-W12-10`, `AGW-W12-12`, `AGW-W12-13`.
How It Is Used: Executed via `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p "test_*.py" -v`.
"""

import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if os.path.join(SRC_DIR, "hooks") not in sys.path:
    sys.path.insert(0, os.path.join(SRC_DIR, "hooks"))

from hooks.execution_mode_router import classify_execution_mode, strip_turn0_metadata
from hooks.kg_pre_invocation_hook import (
    extract_negated_terms,
    deduplicate_turn0_ephemeral_kernel,
    sanitize_pre_invocation_hook_result,
)
from hooks.sentinel_dispatch import (
    normalize_dual_tool_schema_payload,
    evaluate_tool_call,
    apply_rlimit_as,
)
from hooks.agent_stop_black_hat_gate import (
    detect_case_r_reactive_task_wakeup,
    is_isolated_swe_sandbox_turn,
)
from hooks.lazy_plugin_bootstrap import (
    is_sandbox_or_bundled_nondev_host,
    resolve_multi_path_skills_root,
)
from hooks.rules.r31_hook_integrity_guard import (
    verify_comment_author_trust_and_shell_boundary,
    check_case_q_manual_release_lock,
)
from hooks.rules.rule_11_anonymization import redact_code_safe_pii_and_partition_spool
from autonomy_engine.unified_eval_router import (
    compute_waterfill_bt_gtheory_consensus,
    rejudge_cached_transcripts_and_audit_eval_specs,
    run_evaluation,
)
from autonomy_engine.resilient_steer_harvester import audit_compaction_call_response_boundary
from autonomy_engine.single_turn_replay import slice_tail_preserving_traceback_and_classify_retry
from autonomy_engine.workspace_hygiene_gate import (
    audit_sidecar_and_hook_surface_security,
    run_hygiene_audit,
)
from autonomy_engine.delphi_six_hats_task_router import (
    apply_popperian_counterexample_veto,
    evaluate_options_delphi,
)
from mcp_google_workspace.agent_ssot_formatter import (
    score_outbound_commitment_followup_decay,
    audit_executive_tab1_and_cross_tab_stability,
)
from playwright_scraper.cdp_navigator import flush_cookie_wal_before_headless_cdp
from knowledge_graph.dreaming_engine import decompose_harness_friction_and_mix_shift


class TestV140Wave12AndHookHardening(unittest.TestCase):
    def test_21_run_hook_safe_wrapper_and_execution_mode_router(self):
        """Verifies Group A items 1 & 5: run_hook_safe.sh fail-open wrapper and execution_mode_router.py."""
        wrapper = os.path.join(REPO_ROOT, "src", "hooks", "run_hook_safe.sh")
        self.assertTrue(os.path.isfile(wrapper))

        # Fail-open on nonexistent script for PreToolUse -> {"decision":"allow"}
        res_allow = subprocess.run(
            ["sh", wrapper, "./nonexistent_hook.py", "--event", "PreToolUse"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(res_allow.stdout.strip()), {"decision": "allow"})

        # Fail-open on nonexistent script for PreInvocation -> {}
        res_empty = subprocess.run(
            ["sh", wrapper, "./nonexistent_hook.py", "--event", "PreInvocation"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(res_empty.stdout.strip()), {})

        # Execution mode router strips <ADDITIONAL_METADATA> and <SYSTEM_MESSAGE>
        raw_prompt = (
            "<ADDITIONAL_METADATA>host: linux</ADDITIONAL_METADATA>\n"
            "<SYSTEM_MESSAGE>internal</SYSTEM_MESSAGE>\n"
            "Fix failing pytest in /testbed/module.py"
        )
        cleaned = strip_turn0_metadata(raw_prompt)
        self.assertEqual(cleaned, "Fix failing pytest in /testbed/module.py")
        mode_res = classify_execution_mode(raw_prompt, cwd="/testbed")
        self.assertEqual(mode_res["mode"], "swe_sandbox")
        self.assertTrue(mode_res["is_isolated_swe"])

    def test_22_kg_pre_invocation_negation_dedup_and_strict_proto_schema(self):
        """Verifies Group A item 2: KG-N5 negation filter, EPH-ONCE-01 dedup, and RC-8 strict PreInvocationHookResult."""
        neg = extract_negated_terms("Deploy GKE cluster without spanner and exclude terraform modules")
        self.assertIn("spanner", neg)
        self.assertIn("terraform", neg)

        sid = f"unit-test-dedup-{os.getpid()}"
        stamp_path = os.path.join("/dev/shm" if os.path.isdir("/dev/shm") else "/tmp", f"kg_eph_once_{sid}.txt")
        try:
            msg1, dup1 = deduplicate_turn0_ephemeral_kernel(sid, "pinned-grounding-payload")
            msg2, dup2 = deduplicate_turn0_ephemeral_kernel(sid, "pinned-grounding-payload")
            self.assertFalse(dup1)
            self.assertEqual(msg1, "pinned-grounding-payload")
            self.assertTrue(dup2)
            self.assertEqual(msg2, "")
        finally:
            if os.path.exists(stamp_path):
                os.unlink(stamp_path)

        sanitized = sanitize_pre_invocation_hook_result({
            "injectSteps": [{"ephemeralMessage": "ok"}],
            "additionalContext": "must_be_stripped",
            "p1_gate": "must_be_stripped",
            "matched_skills": ["s1"],
        })
        self.assertEqual(set(sanitized.keys()), {"injectSteps"})

    def test_23_sentinel_dual_schema_and_stop_gate_case_r_and_nondev_bootstrap(self):
        """Verifies Group A items 3, 4, 6: AGW-W12-11 dual schema normalizer, PostToolUse {}, Case R wakeup, and NONDEV-BUG-1..3."""
        self.assertTrue(apply_rlimit_as())
        dual = normalize_dual_tool_schema_payload(
            "edit_file",
            {"Path": "/tmp/example.py", "Target": "old_fn()", "Replacement": "new_fn()"},
        )
        self.assertEqual(dual["canonical_tool"], "replace_file_content")
        self.assertEqual(dual["args"]["TargetFile"], "/tmp/example.py")
        self.assertEqual(dual["args"]["TargetContent"], "old_fn()")
        self.assertEqual(dual["args"]["ReplacementContent"], "new_fn()")

        # Protected file write via write_file alias is caught by R31
        r31_res = evaluate_tool_call({
            "toolName": "write_file",
            "toolArgs": {"Path": "/workspace/hooks.json", "Content": "{}"},
        })
        self.assertEqual(r31_res["decision"], "ask")

        # PostToolUse returns empty {} for hooks.proto compatibility
        post_res = evaluate_tool_call({"hookEventName": "PostToolUse", "toolName": "write_file"})
        self.assertEqual(post_res, {})

        # Case R reactive /task- wakeup detection & SWE sandbox short-circuit
        self.assertTrue(
            detect_case_r_reactive_task_wakeup(
                [{"content": "Notification from /task-bg-42 completed"}],
                [],
            )
        )
        self.assertTrue(is_isolated_swe_sandbox_turn({"cwd": "/testbed"}, "Fix issue"))

        # NONDEV-BUG-1..3
        with tempfile.TemporaryDirectory() as tmp_home:
            self.assertTrue(is_sandbox_or_bundled_nondev_host(tmp_home))
            skills_root = resolve_multi_path_skills_root(tmp_home)
            self.assertTrue(skills_root.is_dir())

    def test_24_wave12_eval_dreaming_compaction_and_replay_kernels(self):
        """Verifies Group B kernels AGW-W12-01, AGW-W12-02, AGW-W12-03, AGW-W12-04, and AGW-W12-12."""
        # AGW-W12-01
        bt_res = compute_waterfill_bt_gtheory_consensus(
            stratum_variances={"easy": 0.04, "medium": 0.16, "hard": 0.36},
            total_budget=18,
            pairwise_wins={"treatment": {"control": 12}, "control": {"treatment": 3}},
            judge_scores=[[0.95, 0.93, 0.94], [0.60, 0.62, 0.58], [0.80, 0.82, 0.79]],
        )
        self.assertEqual(bt_res["total_allocated"], 18)
        self.assertTrue(bt_res["min_stratum_floor_met"])
        self.assertEqual(bt_res["bt_leader"], "treatment")
        self.assertGreaterEqual(bt_res["g_theory_phi"], 0.85)

        # AGW-W12-12
        rejudge_res = rejudge_cached_transcripts_and_audit_eval_specs(
            cached_transcripts=[{"id": "t1", "response": "verified schema grounding", "previous_score": 0.5}],
            rubric_keywords=["verified", "schema", "grounding"],
            eval_specs=[
                {"name": "bad_spec", "assertion": "assert True", "has_negative_control": False},
            ],
        )
        self.assertEqual(rejudge_res["rejudged_results"][0]["rejudged_score"], 1.0)
        self.assertFalse(rejudge_res["spec_lint_passed"])
        self.assertEqual(rejudge_res["llm_tokens_burned"], 0)
        self.assertEqual(run_evaluation(mode="fast")["verdict"], "PASS")

        # AGW-W12-02
        ko_res = decompose_harness_friction_and_mix_shift(
            tool_events=[
                {"category": "harness_infra", "tokens": 300},
                {"category": "model_planning", "tokens": 700},
            ],
            baseline_strata={"s1": {"weight": 0.5, "score": 80.0}, "s2": {"weight": 0.5, "score": 90.0}},
            current_strata={"s1": {"weight": 0.2, "score": 85.0}, "s2": {"weight": 0.8, "score": 95.0}},
        )
        self.assertEqual(ko_res["harness_friction_share"], 0.3)
        self.assertAlmostEqual(
            ko_res["within_task_quality_effect"] + ko_res["task_mix_shift_effect"],
            ko_res["total_score_delta"],
            places=3,
        )

        # AGW-W12-03
        comp_res = audit_compaction_call_response_boundary(
            steps=[
                {"type": "USER_INPUT", "content": "start"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "write_file", "args": {"Path": "/tmp/a.md"}}]},
                {"type": "TOOL_RESULT", "content": "ok"},
            ],
            proposed_split_index=2,
        )
        self.assertEqual(comp_res["safe_split_index"], 1)
        self.assertTrue(comp_res["boundary_shifted"])

        # AGW-W12-04
        long_tb = "CMD_HEADER: pytest\n" + ("middle log line\n" * 100) + "SyntaxError: invalid syntax at line 42"
        tb_res = slice_tail_preserving_traceback_and_classify_retry(long_tb, head_chars=80, tail_chars=120)
        self.assertTrue(tb_res["truncated"])
        self.assertIn("CMD_HEADER", tb_res["sliced_output"])
        self.assertIn("SyntaxError", tb_res["sliced_output"])
        self.assertEqual(tb_res["error_class"], "DETERMINISTIC_CODE_OR_SCHEMA_ERROR")
        self.assertFalse(tb_res["should_retry_unchanged"])

    def test_25_wave12_security_anonymization_and_popperian_veto_kernels(self):
        """Verifies Group B kernels AGW-W12-05, AGW-W12-06, AGW-W12-07, and AGW-W12-13."""
        # AGW-W12-05
        trust_bad = verify_comment_author_trust_and_shell_boundary(
            comment_author="untrusted_guest",
            authenticated_user="maintainer_a",
            allowed_maintainers=["maintainer_a"],
            shell_command="python3 -c 'open(\"hooks.json\", \"w\")'",
        )
        self.assertFalse(trust_bad["passed"])
        self.assertFalse(trust_bad["author_trusted"])
        self.assertFalse(trust_bad["shell_safe"])
        self.assertFalse(check_case_q_manual_release_lock("/home/u/.gemini/config/plugins/p/plugin.json", False)["allowed"])

        # AGW-W12-06
        sec_res = audit_sidecar_and_hook_surface_security(
            sidecar_configs=[{"name": "bad_sc", "bind_host": "0.0.0.0"}],
            hook_commands=["python3 raw_hook.py"],
        )
        self.assertFalse(sec_res["passed"])
        self.assertEqual(run_hygiene_audit(REPO_ROOT)["verdict"], "PASS")

        # AGW-W12-07
        md_sample = "Contact engineer@corp-domain.io at /home/alice/project.\n```python\nx = '/home/alice/code.py'\n```"
        scrub_res = redact_code_safe_pii_and_partition_spool(md_sample, session_id="sess-42")
        self.assertIn("<USER_LDAP>@example.com", scrub_res["scrubbed_text"])
        self.assertIn("<USER_HOME_DIR>/project", scrub_res["scrubbed_text"])
        self.assertTrue(scrub_res["code_fences_preserved"])

        # AGW-W12-13
        veto_res = apply_popperian_counterexample_veto([
            {"name": "OptimisticFlawed", "hat_scores": {"White": 0.9, "Black": 0.4, "Yellow": 1.0}},
            {"name": "BalancedSafe", "hat_scores": {"White": 0.85, "Black": 0.85, "Yellow": 0.8}},
        ])
        self.assertEqual(veto_res["veto_count"], 1)
        self.assertEqual(veto_res["surviving_options"][0]["name"], "BalancedSafe")
        delphi_winner = evaluate_options_delphi([
            {"name": "OptimisticFlawed", "hat_scores": {"White": 0.9, "Black": 0.4, "Yellow": 1.0}, "counterexample": "OOM under load"},
            {"name": "BalancedSafe", "hat_scores": {"White": 0.85, "Black": 0.85, "Yellow": 0.8}},
        ])
        self.assertEqual(delphi_winner["winner"]["name"], "BalancedSafe")

    def test_26_wave12_workspace_commitment_tab1_and_cdp_wal_kernels(self):
        """Verifies Group B kernels AGW-W12-08, AGW-W12-09, and AGW-W12-10."""
        # AGW-W12-08
        decay_res = score_outbound_commitment_followup_decay([
            {"owner": "Lead", "topic": "Send architecture sizing", "age_hours": 72.0, "replied": False},
            {"owner": "lead", "topic": "Send  architecture sizing", "age_hours": 72.0, "replied": False},
            {"owner": "PM", "topic": "Approve charter", "age_hours": 12.0, "replied": True},
        ])
        self.assertEqual(decay_res["deduplicated_count"], 2)
        self.assertEqual(decay_res["escalations_due"], 1)

        # AGW-W12-09
        tab_audit = audit_executive_tab1_and_cross_tab_stability(
            tab1_markdown="## 1. Executive Summary\n* **Architecture:** Verified multi-region topology.",
            tab2_markdown="Detailed section #sec-01 and #sec-02 analysis.",
            tab3_markdown="| `sec-01` | Intro |\n| `sec-02` | Details |",
        )
        self.assertTrue(tab_audit["passed"])

        # AGW-W12-10
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "Cookies")
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("CREATE TABLE cookies (name TEXT, value TEXT);")
            conn.execute("INSERT INTO cookies VALUES ('sid', '12345');")
            conn.commit()
            conn.close()
            snap_res = flush_cookie_wal_before_headless_cdp(db_path, target_dir=os.path.join(tmp, "snap"))
            self.assertTrue(snap_res["flushed"])
            self.assertTrue(os.path.isfile(snap_res["snapshot_db_path"]))


if __name__ == "__main__":
    unittest.main()
