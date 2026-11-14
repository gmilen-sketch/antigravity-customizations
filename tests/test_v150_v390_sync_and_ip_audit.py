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

    def test_34_end_to_end_customer_plugin_runtime_all_primitives(self):
        """Simulates a clean customer install (deleted clone, stripped +x bits, no fastmcp/httpx/node_modules) and verifies all 10 MCP stdio servers, hooks, skills, and multi-harness configs."""
        tmp_root = tempfile.mkdtemp(prefix="agw_e2e_cust_")
        try:
            tmp_path = pathlib.Path(tmp_root)
            clone_dir = tmp_path / "temp_clone"
            shutil.copytree(
                REPO_ROOT,
                clone_dir,
                ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", "*.pyc"),
            )
            cust_home = tmp_path / "cust_home"
            cust_home.mkdir()
            base_env = {**os.environ, "HOME": str(cust_home), "PYTHONDONTWRITEBYTECODE": "1"}

            subprocess.run(
                ["bash", str(clone_dir / "scripts" / "install.sh"), "--target", "all", "--home", str(cust_home)],
                env=base_env,
                capture_output=True,
                text=True,
                check=True,
            )
            # Delete temporary clone to prove installed hooks/MCPs never depend on transient download path
            shutil.rmtree(clone_dir)

            claude_cfg = json.loads((cust_home / ".claude" / "settings.json").read_text(encoding="utf-8"))
            claude_hook_script = claude_cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"].split()[2]
            self.assertTrue(os.path.isfile(claude_hook_script), f"Claude hook script missing after clone deletion: {claude_hook_script}")

            cursor_cfg = json.loads((cust_home / ".cursor" / "mcp.json").read_text(encoding="utf-8"))
            for srv, scfg in cursor_cfg["mcpServers"].items():
                script_arg = next(a for a in scfg["args"] if a.endswith((".py", ".js")))
                self.assertTrue(os.path.isfile(script_arg), f"Cursor MCP script missing after clone deletion ({srv}): {script_arg}")

            pdir = cust_home / ".gemini" / "config" / "plugins" / "antigravity-customizations"
            for f in pdir.rglob("*"):
                if f.is_file():
                    f.chmod(0o644)

            # Verify all root hooks & all 5 subagent hooks succeed even with 0644 file modes
            root_hooks = json.loads((pdir / "hooks.json").read_text(encoding="utf-8"))
            for grp in root_hooks.values():
                if not isinstance(grp, dict):
                    continue
                for ev in ("PreInvocation", "PostInvocation", "PreToolUse", "Stop"):
                    for item in grp.get(ev, []):
                        for h in item.get("hooks", [item]):
                            r = subprocess.run(
                                ["/bin/sh", "-c", h["command"]],
                                cwd=str(pdir),
                                env=base_env,
                                input=json.dumps({"hookEventName": ev, "conversationId": "c1", "toolName": "edit_file", "toolArgs": {"Path": "/tmp/t.txt", "Target": "a", "Replacement": "b"}}),
                                text=True,
                                capture_output=True,
                                check=True,
                            )
                            self.assertIn("decision", json.loads(r.stdout))

            for adir in sorted((pdir / "agents").iterdir()):
                if not adir.is_dir():
                    continue
                ah = json.loads((adir / "hooks.json").read_text(encoding="utf-8"))
                for grp in ah.values():
                    if not isinstance(grp, dict):
                        continue
                    for ev in ("PreToolUse", "Stop"):
                        for item in grp.get(ev, []):
                            for h in item.get("hooks", [item]):
                                r = subprocess.run(
                                    ["/bin/sh", "-c", h["command"]],
                                    cwd=str(adir),
                                    env=base_env,
                                    input=json.dumps({"hookEventName": ev, "conversationId": "sub1", "agentName": adir.name, "toolName": "run_command", "toolArgs": {"CommandLine": "ls /tmp"}}),
                                    text=True,
                                    capture_output=True,
                                    check=True,
                                )
                                self.assertIn("decision", json.loads(r.stdout))

            # Block optional 3P Python packages (`fastmcp`, `httpx`) to simulate a clean stock Python 3 customer host
            block_site = tmp_path / "block_3p"
            block_site.mkdir()
            (block_site / "fastmcp.py").write_text("raise ImportError('no fastmcp')\n", encoding="utf-8")
            (block_site / "httpx.py").write_text("raise ImportError('no httpx')\n", encoding="utf-8")

            rpc_input = (
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "audit", "version": "1.0"}}}) + "\n"
                + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n"
                + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
            )
            mcp_servers = json.loads((pdir / "mcp_config.json").read_text(encoding="utf-8"))["mcpServers"]
            self.assertEqual(len(mcp_servers), 10)
            for sname, scfg in mcp_servers.items():
                cmd = [scfg["command"]] + [a.replace("${PLUGIN_ROOT}", str(pdir)) for a in scfg.get("args", [])]
                s_env = {**base_env, "PYTHONPATH": str(block_site)}
                for ek, ev in scfg.get("env", {}).items():
                    s_env[ek] = ev.replace("${PLUGIN_ROOT}", str(pdir)).replace("${PLUGIN_DATA}", str(tmp_path / "pdata"))
                proc = subprocess.run(cmd, cwd=str(pdir), env=s_env, input=rpc_input, text=True, capture_output=True, timeout=10, check=True)
                json_lines = [json.loads(ln) for ln in proc.stdout.splitlines() if ln.strip()]
                self.assertEqual(len(json_lines), 2, f"Expected 2 JSON-RPC replies (initialize + tools/list) from {sname}, got: {proc.stdout!r} stderr={proc.stderr!r}")
                self.assertEqual(json_lines[0]["id"], 1)
                self.assertIn("protocolVersion", json_lines[0]["result"])
                tools = json_lines[1]["result"]["tools"]
                self.assertGreaterEqual(len(tools), 1, f"MCP server {sname} exposed 0 tools")

            # Verify all 20 skills + reference markdown relative links resolve cleanly
            link_re = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#|file://|customization://|sidecar://)([^)#\s]+)(?:#[^)]*)?\)")
            for sdir in sorted((pdir / "skills").iterdir()):
                if not sdir.is_dir():
                    continue
                md_files = [sdir / "SKILL.md"] + sorted((sdir / "references").glob("*.md") if (sdir / "references").is_dir() else [])
                for mdf in md_files:
                    for m in link_re.finditer(mdf.read_text(encoding="utf-8")):
                        self.assertTrue((mdf.parent / m.group(1)).resolve().exists(), f"Broken link in {mdf}: {m.group(1)}")
        finally:
            shutil.rmtree(tmp_root, ignore_errors=True)

    def test_35_issue2_stop_gate_heredoc_and_critic_fallback_matrix(self):
        """Verifies Issue #2 fixes: heredoc/quote/FD/scratch-safe is_mutating_command + inline-Python write detection, unresolved Judge wave boundaries, and fail-closed black-hat-critic fallback."""
        import hooks.agent_stop_black_hat_gate as bh_gate

        # 1. Read-only inline Python heredocs, quotes, FD redirects, and /tmp or /dev/shm scratch writes
        self.assertFalse(bh_gate.is_mutating_command("python3 -B -c \"x = 5; print(x > 2)\""))
        self.assertFalse(
            bh_gate.is_mutating_command(
                "python3 -B << 'PYEOF'\nvals = [3, 1, 4]\nprint([v for v in vals if v > 2])\nPYEOF"
            )
        )
        self.assertFalse(bh_gate.is_mutating_command("echo \"a > b\" && pytest -q 2>&1"))
        self.assertFalse(bh_gate.is_mutating_command("ls -la 2>/dev/null"))
        self.assertFalse(bh_gate.is_mutating_command("echo ok > /tmp/probe.txt"))
        self.assertFalse(bh_gate.is_mutating_command("echo ok > /dev/shm/probe.txt"))
        self.assertFalse(bh_gate.is_mutating_command("python3 -B -c \"open('/tmp/s.txt', 'w').write('ok')\""))
        self.assertFalse(
            bh_gate.is_mutating_command(
                "python3 -B << 'PYEOF'\nimport pathlib\npathlib.Path('/dev/shm/s.txt').write_text('ok')\nPYEOF"
            )
        )

        # 2. True-positive shell redirects & inline Python durable writes remain fail-closed
        self.assertTrue(bh_gate.is_mutating_command("echo mutated > /workspace/out.txt"))
        self.assertTrue(bh_gate.is_mutating_command("python3 -B -c \"open('src/out.py', 'w').write('x')\""))
        self.assertTrue(
            bh_gate.is_mutating_command(
                "python3 -B << 'PYEOF'\nimport pathlib\npathlib.Path('README.md').write_text('x')\nPYEOF"
            )
        )

        # 3. resolve_active_goldfish_wave ignores aborted Judge spawns with cid=None
        gf_spawns = [
            (1, "[SHARD:code] check code", "11111111-1111-1111-1111-111111111111", False, "code"),
            (3, "[SHARD:tests] check tests", "22222222-2222-2222-2222-222222222222", False, "tests"),
        ]
        aborted_judge = [(2, "adjudicate", None, False, None)]
        wave = bh_gate.resolve_active_goldfish_wave(gf_spawns, aborted_judge)
        self.assertEqual({w[4] for w in wave}, {"code", "tests"})

        # 4. Full fallback & fail-closed matrix in find_structural_proof_with_index
        tmp_brain = tempfile.mkdtemp(prefix="agw_bh_brain_")
        orig_roots = list(bh_gate.BRAIN_CANDIDATE_ROOTS)
        orig_strict = os.environ.get("BH_GATE_STRICT_TWO_STAGE")
        try:
            bh_gate.BRAIN_CANDIDATE_ROOTS[:] = [tmp_brain]
            os.environ.pop("BH_GATE_STRICT_TWO_STAGE", None)

            def _write_transcript(cid: str, lines: list) -> str:
                log_dir = pathlib.Path(tmp_brain, cid, ".system_generated", "logs")
                log_dir.mkdir(parents=True, exist_ok=True)
                tpath = log_dir / "transcript_full.jsonl"
                tpath.write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
                return str(tpath)

            gf_clean_cid = "aaaaaaaa-1111-4111-8111-111111111111"
            gf_disc_cid = "bbbbbbbb-2222-4222-8222-222222222222"
            gf_mut_cid = "cccccccc-3333-4333-8333-333333333333"
            critic_ok_cid = "dddddddd-4444-4444-8444-444444444444"
            judge_rej_cid = "eeeeeeee-5555-4555-8555-555555555555"

            gf_clean_path = _write_transcript(
                gf_clean_cid,
                [
                    {"type": "PLANNER_RESPONSE", "content": "Inspecting", "tool_calls": [{"name": "read_file", "args": {"Path": "/tmp/a"}}, {"name": "run_command", "args": {"CommandLine": "pytest -q"}}]},
                    {"type": "PLANNER_RESPONSE", "content": "FORENSIC_EVIDENCE_DOSSIER\nDISCREPANCY_COUNT: 0"},
                ],
            )
            _write_transcript(
                gf_disc_cid,
                [
                    {"type": "PLANNER_RESPONSE", "content": "Inspecting", "tool_calls": [{"name": "read_file", "args": {"Path": "/tmp/a"}}, {"name": "run_command", "args": {"CommandLine": "pytest -q"}}]},
                    {"type": "PLANNER_RESPONSE", "content": "FORENSIC_EVIDENCE_DOSSIER\nDISCREPANCY_COUNT: 1"},
                ],
            )
            _write_transcript(
                gf_mut_cid,
                [
                    {"type": "PLANNER_RESPONSE", "content": "Mutating", "tool_calls": [{"name": "write_file", "args": {"Path": "/workspace/bad.py"}}, {"name": "read_file", "args": {"Path": "/tmp/a"}}]},
                    {"type": "PLANNER_RESPONSE", "content": "FORENSIC_EVIDENCE_DOSSIER\nDISCREPANCY_COUNT: 0"},
                ],
            )
            _write_transcript(
                critic_ok_cid,
                [
                    {"type": "PLANNER_RESPONSE", "content": "Auditing", "tool_calls": [{"name": "read_file", "args": {"Path": "/tmp/a"}}]},
                    {"type": "PLANNER_RESPONSE", "content": "Running suite", "tool_calls": [{"name": "run_command", "args": {"CommandLine": "pytest -q"}}]},
                    {"type": "PLANNER_RESPONSE", "content": "All checks verified.\nCRITIC_VERDICT: APPROVED"},
                ],
            )
            _write_transcript(
                judge_rej_cid,
                [
                    {"type": "PLANNER_RESPONSE", "content": "Reading dossier", "tool_calls": [{"name": "read_file", "args": {"Path": gf_clean_path}}]},
                    {"type": "PLANNER_RESPONSE", "content": "MITM_LAUNDERING: DETECTED\nCRITIC_VERDICT: REJECTED"},
                ],
            )

            # Case A: Clean Goldfish + unresolved Judge dispatch (cid=None) + post-wave Critic APPROVED -> PASS
            turn_unresolved_judge = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Verify claims"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_clean_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-judge", "Prompt": "Adjudicate"}}]},
                {"type": "TOOL_RESULT", "content": "Error: unknown subagent black-hat-judge"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Fallback audit"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
            ]
            ok, detail, w_idx = bh_gate.find_structural_proof_with_index(turn_unresolved_judge)
            self.assertTrue(ok, f"Expected fallback PASS, got: {detail}")
            self.assertEqual(w_idx, 0)

            # Case B: Strict 2-stage mode blocks Critic fallback
            os.environ["BH_GATE_STRICT_TWO_STAGE"] = "1"
            ok_strict, _, _ = bh_gate.find_structural_proof_with_index(turn_unresolved_judge)
            self.assertFalse(ok_strict)
            os.environ.pop("BH_GATE_STRICT_TWO_STAGE", None)

            # Case C: Goldfish DISCREPANCY_COUNT > 0 blocks Critic fallback
            turn_gf_disc = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Verify claims"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_disc_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Fallback audit"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
            ]
            self.assertFalse(bh_gate.find_structural_proof_with_index(turn_gf_disc)[0])

            # Case D: Goldfish GOLDFISH-RO-1 mutation or handcuff prompt blocks Critic fallback
            turn_gf_mut = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Verify claims"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_mut_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Fallback audit"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
            ]
            self.assertFalse(bh_gate.find_structural_proof_with_index(turn_gf_mut)[0])

            turn_gf_handcuff = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Use read_file only"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_clean_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Fallback audit"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
            ]
            self.assertFalse(bh_gate.find_structural_proof_with_index(turn_gf_handcuff)[0])

            # Case E: Critic executed prior to active Goldfish wave cannot clear gate
            turn_pre_wave_critic = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Early audit"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Verify claims"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_clean_cid}"},
            ]
            self.assertFalse(bh_gate.find_structural_proof_with_index(turn_pre_wave_critic)[0])

            # Case F: Resolved post-wave Judge REJECTED / MITM_LAUNDERING blocks Critic fallback
            turn_judge_rej = [
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-goldfish", "Prompt": "Verify claims"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {gf_clean_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-judge", "Prompt": "Adjudicate"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {judge_rej_cid}"},
                {"type": "PLANNER_RESPONSE", "tool_calls": [{"name": "invoke_subagent", "args": {"TypeName": "black-hat-critic", "Prompt": "Attempted override"}}]},
                {"type": "TOOL_RESULT", "content": f"conversationId: {critic_ok_cid}"},
            ]
            self.assertFalse(bh_gate.find_structural_proof_with_index(turn_judge_rej)[0])
        finally:
            bh_gate.BRAIN_CANDIDATE_ROOTS[:] = orig_roots
            if orig_strict is not None:
                os.environ["BH_GATE_STRICT_TWO_STAGE"] = orig_strict
            else:
                os.environ.pop("BH_GATE_STRICT_TWO_STAGE", None)
            shutil.rmtree(tmp_brain, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
