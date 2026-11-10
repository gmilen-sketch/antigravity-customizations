#!/usr/bin/env python3
"""
Role: Clean-Room Verification & Google IP Audit Suite for v1.5.0 / Web Hub v3.9.0 Sync (`test_v150_v390_sync_and_ip_audit.py`).
Purpose: Verifies all net-new v1.5.0 capabilities synchronized from the public Antigravity Web Hub v3.9.0 release
  and runs exhaustive clean-room Google Intellectual Property (IP), corporate token, retired model, and binary checks:
  1. `PostInvocation` UX verification banner, `<artifact>.metadata.json` `userFacing` holdback/restore, and subagent `Role` rewriter.
  2. `GOLDFISH-RO-1` read-only subagent command enforcement (`enforce_goldfish_readonly_command`), `BUG-14` heredoc literal stripper,
     and `Stop` `C3b` transcript mutation detector (`detect_goldfish_transcript_mutations`).
  3. `v4.18` Adaptive `K=1..3` `[SHARD:<id>]` Multi-Goldfish wave resolver (`resolve_active_goldfish_wave`) and Holistic Judge
     `C6-Multi` / `C6-Holistic` union & seam enforcement.
  4. `force_ask` destructive command & R31 control-plane guards, `/tmp` & `/dev/shm` scratch `rm -rf` exemption, and `L3` anti-spin.
  5. 3 new eager FastMCP servers (`browser_cdp_mcp`, `cloud_telemetry_mcp`, `workspace_docs_mcp`).
  6. Empty OKF v0.2 & Knowledge Graph skeleton (`validate_kb_bundle`, `init_knowledge_graph` with `0` pre-loaded nodes/edges), and `verify_skill_patch_ttl_window`.
  7. Turnkey Paired A/B Benchmark Orchestrator (`scripts/run_ab_benchmark.py --self-test`).
  8. 95-digest SHA-256 + corporate regex + UTF-8/binary + `.pyc` + `git log -p` Google IP clean-room certification.
How It Is Used: Executed via `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p "test_*.py" -v`.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.dont_write_bytecode = True

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
for _p in (REPO_ROOT, SRC_DIR, os.path.join(SRC_DIR, "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hooks.black_hat_in_progress_ux_hook import (
    evaluate_post_invocation,
    stage_deliverable_artifact_cards,
    restore_deliverable_artifact_cards,
    rewrite_black_hat_subagent_role,
)
from hooks.multi_harness_hook_adapter import adapt_post_invocation, adapt_pre_invocation
from hooks.sentinel_dispatch import (
    enforce_goldfish_readonly_command,
    strip_heredoc_and_quoted_literals,
    check_identical_command_anti_spin,
    evaluate_tool_call,
)
from hooks.agent_stop_black_hat_gate import (
    _extract_subagent_spawns,
    resolve_active_goldfish_wave,
    detect_goldfish_transcript_mutations,
    check_chat_bottom_up_tldr_structure,
)
from hooks.kg_pre_invocation_hook import enforce_strict_pre_invocation_schema
from hooks.black_hat_analyzer import (
    PROHIBITED_TOKEN_SHA256,
    PROHIBITED_LEAK_PATTERNS,
    PROHIBITED_BINARY_EXTENSIONS,
    scan_target,
)
from knowledge_graph.init_knowledge_graph import init_knowledge_graph
from knowledge_graph.validate_okf import validate_kb_bundle
from knowledge_graph.dreaming_engine import verify_skill_patch_ttl_window
from mcp_servers.browser_cdp_mcp import (
    audit_web_ui_geometry,
    cdp_shadow_dom_snapshot,
    EAGER_TOOL_META as CDP_META,
)
from mcp_servers.cloud_telemetry_mcp import _parse_bq_rows, EAGER_TOOL_META as CLOUD_META
from mcp_servers.workspace_docs_mcp import (
    build_agent_ssot_v1_tab3,
    build_cloudstyle_4card_slide,
    build_3row_sheet_staging_diff,
    EAGER_TOOL_META as DOCS_META,
)


class TestV150V390SyncAndIpAudit(unittest.TestCase):
    def test_27_post_invocation_ux_holdback_and_role_rewriter(self):
        """Verifies PostInvocation [!WARNING] banner, artifact userFacing holdback/restore, and subagent Role rewriter."""
        tmp_dir = tempfile.mkdtemp()
        try:
            brain_dir = os.path.join(tmp_dir, "cid-ux-1")
            os.makedirs(brain_dir, exist_ok=True)
            art_path = os.path.join(brain_dir, "report.md")
            meta_path = os.path.join(brain_dir, "report.md.metadata.json")
            with open(art_path, "w", encoding="utf-8") as f:
                f.write("# Architecture Report\n")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump({"summary": "Architecture Report", "userFacing": True}, f)

            held_count, already_notified = stage_deliverable_artifact_cards(
                brain_dir, subagent_cid="sub-1", stage_num=1
            )
            self.assertEqual(held_count, 1)
            self.assertFalse(already_notified)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.assertIs(json.load(f)["userFacing"], False)

            restored = restore_deliverable_artifact_cards(brain_dir)
            self.assertEqual(restored, ["report.md"])
            with open(meta_path, "r", encoding="utf-8") as f:
                self.assertIs(json.load(f)["userFacing"], True)

            rewritten = rewrite_black_hat_subagent_role({
                "TypeName": "black-hat-goldfish",
                "Role": "[SHARD:backend] Forensic Verifier",
            })
            self.assertIsNotNone(rewritten)
            self.assertEqual(rewritten["decision"], "allow")
            self.assertIn("[SHARD:backend]", rewritten["overwrite"]["Role"])
            self.assertIn("⏳ Checking Results (1/2):", rewritten["overwrite"]["Role"])

            post_out = adapt_post_invocation({"rootConversationId": "cid-ux-clean"})
            self.assertEqual(post_out["decision"], "allow")
            eval_clean = evaluate_post_invocation({"rootConversationId": "cid-ux-clean"})
            self.assertEqual(eval_clean, {})
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_28_goldfish_ro1_and_heredoc_stripper_and_transcript_mutation_detector(self):
        """Verifies GOLDFISH-RO-1 PreToolUse guard, BUG-14 heredoc literal stripper, and Stop C3b mutation detector."""
        stripped = strip_heredoc_and_quoted_literals(
            "python3 -B << 'PYEOF'\nmsg = 'rm -rf /important'\nprint('ok')\nPYEOF"
        )
        self.assertNotIn("rm -rf /important", stripped)

        ro_block = enforce_goldfish_readonly_command(
            "run_command",
            {"CommandLine": "echo hacked > repo_file.txt"},
            agent_name="black-hat-goldfish",
            conversation_id="cid-gf-1",
        )
        self.assertIsNotNone(ro_block)
        self.assertEqual(ro_block["decision"], "deny")

        ro_shm_ok = enforce_goldfish_readonly_command(
            "run_command",
            {"CommandLine": "python3 -B -c 'print(1)' > /dev/shm/gf_123/out.txt"},
            agent_name="black-hat-goldfish",
            conversation_id="cid-gf-1",
        )
        self.assertIsNone(ro_shm_ok)

        entries = [
            {
                "tool_calls": [
                    {"name": "write_file", "args": {"Path": "/repo/leak.py", "Content": "x=1"}}
                ]
            }
        ]
        mut_err = detect_goldfish_transcript_mutations(entries, "cid-gf-1")
        self.assertIsNotNone(mut_err)
        self.assertIn("write_file", mut_err)

    def test_29_v418_multi_goldfish_wave_and_hook_system_message_and_tldr(self):
        """Verifies v4.18 [SHARD:<id>] wave grouping, HookSystemMessage schema, and backtick-safe TL;DR checker."""
        c1, c2, c2_fix = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
        turn = [
            {
                "tool_calls": [
                    {"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "[SHARD:code] C1"}},
                    {"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "[SHARD:docs] C2"}},
                ]
            },
            {"type": "TOOL_RESULT", "content": json.dumps([{"conversationId": c1}, {"conversationId": c2}])},
            {
                "tool_calls": [
                    {"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "[SHARD:docs] Retry C2"}},
                ]
            },
            {"type": "TOOL_RESULT", "content": json.dumps({"conversationId": c2_fix})},
        ]
        gf_spawns = _extract_subagent_spawns(turn, "black-hat-goldfish")
        wave = resolve_active_goldfish_wave(gf_spawns, [])
        wave_cids = [g[2] for g in wave]
        self.assertEqual(wave_cids, [c1, c2_fix])

        strict_pre = enforce_strict_pre_invocation_schema(
            {"injectSteps": [{"ephemeralMessage": "grounding-ctx"}], "decision": "allow"}
        )
        self.assertEqual(
            strict_pre,
            {"injectSteps": [{"systemMessage": {"systemMessage": "grounding-ctx"}}]},
        )
        adapted_pre = adapt_pre_invocation({
            "rootConversationId": "cid-sysmsg-1",
            "prompt": "Use universal-solution-architect to design GKE topology",
        })
        if "injectSteps" in adapted_pre:
            self.assertIn("systemMessage", adapted_pre["injectSteps"][0])

        good_chat = (
            "<details><summary><strong>📊 Verification Matrix (Click to Expand)</strong></summary>\n\n"
            "| Target | Behavior & Outcome | Status |\n"
            "| :--- | :--- | :--- |\n"
            "| [run_ab_benchmark.py](file:///repo/scripts/run_ab_benchmark.py) | Passed `--self-test` (`|A| == |B|`) | ✅ |\n\n"
            "</details>\n\n"
            "### 📋 Summary of Approved Response & Deliverables\n"
            "- Updated clean-room hooks and MCP servers.\n\n"
            "### ⚡ TL;DR\n"
            "All 33 tests pass (`|delta| == 0`).\n\n"
            "CRITIC_VERDICT: APPROVED | GCS = 1.000 | 10/10 Checks Passed"
        )
        tldr_res = check_chat_bottom_up_tldr_structure(good_chat)
        self.assertTrue(tldr_res["passed"], f"TL;DR check failed: {tldr_res}")

    def test_30_force_ask_scratch_rm_exemption_and_l3_anti_spin(self):
        """Verifies force_ask destructive mediation, /tmp scratch rm -rf exemption, retired gemini-3.5-pro block, and L3 anti-spin."""
        scratch_ok = evaluate_tool_call({
            "toolName": "run_command",
            "toolArgs": {"CommandLine": "rm -rf /tmp/test_scratch_dir_123"},
        })
        self.assertEqual(scratch_ok["decision"], "allow")

        prod_rm = evaluate_tool_call({
            "toolName": "run_command",
            "toolArgs": {"CommandLine": "rm -rf /var/lib/production_data"},
        })
        self.assertEqual(prod_rm["decision"], "force_ask")

        dep_mod = evaluate_tool_call({
            "toolName": "write_file",
            "toolArgs": {"Path": "/tmp/client.py", "Content": 'MODEL = "gemini-3.5-pro"\n'},
        })
        self.assertEqual(dep_mod["decision"], "deny")

        spin_steps = [
            {"tool_calls": [{"name": "run_command", "args": {"CommandLine": "pytest tests/unit"}}]},
            {"tool_calls": [{"name": "run_command", "args": {"CommandLine": "pytest tests/unit"}}]},
            {"tool_calls": [{"name": "run_command", "args": {"CommandLine": "pytest tests/unit"}}]},
        ]
        spin3 = check_identical_command_anti_spin(
            "run_command", {"CommandLine": "pytest tests/unit"}, transcript_steps=spin_steps
        )
        self.assertIsNotNone(spin3)
        self.assertEqual(spin3["decision"], "deny")

    def test_31_three_new_fastmcp_servers_and_empty_kg_skeleton_and_benchmark_selftest(self):
        """Verifies browser_cdp_mcp, cloud_telemetry_mcp, workspace_docs_mcp, empty OKF/KG skeleton (0 pre-loaded nodes/edges), and run_ab_benchmark.py --self-test."""
        self.assertTrue(CDP_META.get("antigravity/alwaysLoad"))
        self.assertTrue(CLOUD_META.get("antigravity/alwaysLoad"))
        self.assertTrue(DOCS_META.get("antigravity/alwaysLoad"))

        cdp_geom = json.loads(audit_web_ui_geometry("http://127.0.0.1:59999/"))
        self.assertIn("issueCount", cdp_geom)
        cdp_snap = json.loads(cdp_shadow_dom_snapshot("#upload"))
        self.assertEqual(cdp_snap["status"], "OK")

        cols, parsed_rows = _parse_bq_rows({
            "schema": {"fields": [{"name": "service", "type": "STRING"}, {"name": "net_cost", "type": "FLOAT64"}]},
            "rows": [{"f": [{"v": "Compute Engine"}, {"v": "42.50"}]}],
        })
        self.assertEqual(cols, ["service", "net_cost"])
        self.assertEqual(parsed_rows, [{"service": "Compute Engine", "net_cost": 42.5}])

        tab3 = build_agent_ssot_v1_tab3("Architecture Doc", json.dumps([{"id": "sec-1", "title": "Overview", "lines": "L1-L10"}]))
        self.assertIn("AGENT-SSOT-v1", tab3)
        slide = json.loads(build_cloudstyle_4card_slide("slide_01", json.dumps([{"title": "C1", "body": "B1"}])))
        self.assertIsInstance(slide, list)
        self.assertGreater(len(slide), 0)
        diff_res = json.loads(build_3row_sheet_staging_diff(json.dumps({"Spend": 100}), json.dumps({"Spend": 120})))
        self.assertIsInstance(diff_res, dict)

        kb_val = validate_kb_bundle(os.path.join(REPO_ROOT, "kb"))
        self.assertTrue(kb_val["valid"])
        self.assertEqual(kb_val["files_checked"], 2)  # kb/index.md + kb/log.md empty skeleton only

        seed_kg = json.loads(pathlib.Path(REPO_ROOT, "resources", "knowledge_graph.seed.json").read_text(encoding="utf-8"))
        self.assertEqual(seed_kg["nodes"], [])
        self.assertEqual(seed_kg["entities"], {})
        self.assertEqual(seed_kg["edges"], [])

        tmp_kg_dir = tempfile.mkdtemp()
        try:
            kg_out = os.path.join(tmp_kg_dir, "kg.json")
            warm_out = os.path.join(tmp_kg_dir, "warm.json")
            init_knowledge_graph(target_path=kg_out, force=True, warm_cache_path=warm_out, kb_root=os.path.join(REPO_ROOT, "kb"))
            kg_data = json.loads(pathlib.Path(kg_out).read_text(encoding="utf-8"))
            self.assertEqual(kg_data["nodes"], [])
            self.assertEqual(kg_data.get("entities", {}), {})
            self.assertEqual(kg_data["edges"], [])

            comp_cli = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    os.path.join(REPO_ROOT, "src", "knowledge_graph", "okf_knowledge_compiler.py"),
                    "--kb-root",
                    os.path.join(REPO_ROOT, "kb"),
                ],
                env={
                    **{k: v for k, v in os.environ.items() if k != "KG_JSON_PATH"},
                    "HOME": tmp_kg_dir,
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "KG_WARM_CACHE_PATH": warm_out,
                },
                capture_output=True,
                text=True,
                check=True,
            )
            comp_json = json.loads(comp_cli.stdout)
            self.assertEqual(comp_json["synced_dossiers"], 0)
            self.assertEqual(comp_json["total_graph_nodes"], 0)
            self.assertEqual(comp_json["total_graph_edges"], 0)
        finally:
            shutil.rmtree(tmp_kg_dir, ignore_errors=True)

        ttl_ok = verify_skill_patch_ttl_window({"absorbed_epoch": 1000.0, "baseline_score": 85.0}, 88.0, now_ts=1000.0 + 8 * 86400)
        self.assertIn("GRADUATED", str(ttl_ok.get("disposition", "")).upper())
        ttl_rev = verify_skill_patch_ttl_window({"absorbed_epoch": 1000.0, "baseline_score": 85.0}, 80.0, now_ts=1000.0 + 2 * 86400)
        self.assertIn("REVERT", str(ttl_rev.get("disposition", "")).upper())

        bench_res = subprocess.run(
            [sys.executable, "-B", os.path.join(REPO_ROOT, "scripts", "run_ab_benchmark.py"), "--self-test"],
            capture_output=True,
            text=True,
            check=True,
        )
        bench_json = json.loads(bench_res.stdout.splitlines()[0] if bench_res.stdout.startswith("{") else bench_res.stdout[bench_res.stdout.index("{"):])
        self.assertEqual(bench_json["verdict"], "PASS")
        self.assertEqual(bench_json["total_tasks"], 28)

    def test_32_exhaustive_95_digest_google_ip_and_zero_pyc_audit(self):
        """Certifies >= 95 SHA-256 digests, 0 Google IP/internal links/mounts/models, 0 binaries, and 0 .pyc files."""
        self.assertGreaterEqual(len(PROHIBITED_TOKEN_SHA256), 95)
        scan_res = scan_target(REPO_ROOT)
        self.assertEqual(scan_res["verdict"], "PASS", f"Clean-room IP analyzer failed: {scan_res}")

        repo_path = pathlib.Path(REPO_ROOT)
        pyc_files = [str(p.relative_to(repo_path)) for p in repo_path.rglob("*.pyc")]
        self.assertEqual(pyc_files, [], f"Bytecode .pyc files must not exist: {pyc_files}")

        for p in sorted(repo_path.rglob("*")):
            if ".git" in p.parts or not p.is_file():
                continue
            rel = str(p.relative_to(repo_path))
            self.assertNotIn(p.suffix.lower(), PROHIBITED_BINARY_EXTENSIONS, f"Prohibited binary extension: {rel}")
            text = p.read_text(encoding="utf-8")
            for pat, desc in PROHIBITED_LEAK_PATTERNS:
                self.assertIsNone(re.search(pat, text), f"{rel} matched prohibited pattern ({desc})")

    def test_33_native_plugin_deployment_and_self_contained_packs(self):
        """Verifies valid subagent commandExecutionPolicy, rule trigger frontmatter, local plugin logos, and --plugin-only self-contained install."""
        judge_md = pathlib.Path(REPO_ROOT, "agents", "black-hat-judge", "agent.md").read_text(encoding="utf-8")
        self.assertIn("commandExecutionPolicy: off", judge_md)
        self.assertNotIn("commandExecutionPolicy: deny", judge_md)
        self.assertEqual(list(pathlib.Path(REPO_ROOT, "agents").glob("*.md")), [])

        nb_rule = pathlib.Path(REPO_ROOT, "rules", "no-bullshit.md").read_text(encoding="utf-8")
        self.assertTrue(nb_rule.startswith("---\ntrigger: always_on\n"), "rules/no-bullshit.md requires trigger: always_on YAML frontmatter")

        for mod in ("agy-core-governance", "agy-knowledge-graph", "agy-cloud-architect", "agy-workspace-automation"):
            pdir = pathlib.Path(REPO_ROOT, "plugins", mod)
            pjson = json.loads((pdir / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(pjson["logo"], "assets/logo.svg")
            self.assertIs(pjson["disabled"], True)
            self.assertTrue((pdir / "assets" / "logo.svg").is_file())
            mcp_json = json.loads((pdir / "mcp_config.json").read_text(encoding="utf-8"))
            for srv, cfg in mcp_json["mcpServers"].items():
                script_args = [a for a in cfg["args"] if "${PLUGIN_ROOT}" in a]
                self.assertGreaterEqual(len(script_args), 1, f"Missing PLUGIN_ROOT script arg on {mod}/{srv}")
                resolved = pathlib.Path(script_args[0].replace("${PLUGIN_ROOT}", str(pdir))).resolve()
                self.assertTrue(resolved.is_file(), f"Broken in-repo MCP path for {mod}/{srv}: {resolved}")

        tmp_home = tempfile.mkdtemp()
        try:
            res = subprocess.run(
                [
                    "bash",
                    os.path.join(REPO_ROOT, "scripts", "install.sh"),
                    "--target",
                    "agy",
                    "--plugin-only",
                    "--home",
                    tmp_home,
                    "--verify",
                ],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "AGY_INSTALL_VERIFY_IN_PROGRESS": "1"},
                check=True,
            )
            self.assertIn('"verdict": "PASS"', res.stdout)
            self.assertFalse(pathlib.Path(tmp_home, ".gemini", "config", "hooks.json").exists())
            self.assertFalse(pathlib.Path(tmp_home, ".gemini", "config", "mcp_config.json").exists())

            plugins_dir = pathlib.Path(tmp_home, ".gemini", "config", "plugins")
            for pname in ("antigravity-customizations", "agy-core-governance", "agy-knowledge-graph", "agy-cloud-architect", "agy-workspace-automation"):
                inst = plugins_dir / pname
                self.assertTrue((inst / "plugin.json").is_file())
                self.assertTrue((inst / "assets" / "logo.svg").is_file())
                for jf in inst.glob("*.json"):
                    self.assertNotIn("../../", jf.read_text(encoding="utf-8"), f"Escaped relative path in installed {pname}/{jf.name}")
                if (inst / "mcp_config.json").is_file():
                    mdata = json.loads((inst / "mcp_config.json").read_text(encoding="utf-8"))
                    for srv, cfg in mdata["mcpServers"].items():
                        for arg in cfg["args"]:
                            if "${PLUGIN_ROOT}" in arg:
                                target_script = pathlib.Path(arg.replace("${PLUGIN_ROOT}", str(inst)))
                                self.assertTrue(target_script.is_file(), f"Missing installed MCP script {target_script} in {pname}/{srv}")
        finally:
            shutil.rmtree(tmp_home, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
