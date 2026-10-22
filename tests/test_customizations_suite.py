#!/usr/bin/env python3
"""
Comprehensive Clean-Room Verification Suite for Antigravity Customizations Suite (v1.4.0).
Verifies:
1. Zero Web Hub / external proxy / bootstrap.js / Nginx / Terraform bloat.
2. Native Antigravity CLI (agy) & Antigravity 2.0 plugin manifests (v1.4.0 + 20 keywords/tags).
3. Native Claude Code (.claude/settings.json, .claude/agents/*.md, .claude/commands/*.md, CLAUDE.md, .mcp.json) compatibility.
4. Native Cursor / Windsurf / Cloud Code (AGENTS.md, GEMINI.md, .cursorrules, .mcp.json) compatibility.
5. Universal Multi-Harness Hook Adapter (PreToolUse, UserPromptSubmit/PreInvocation, Stop + rootConversationId + --event flag).
6. All 14 Autonomy Engine pillars, Bitemporal Knowledge Graph (OKF v0.2), 20 PD-Q skills, 5 subagents, and 7 MCP servers.
7. Zero binary files and zero internal Google codenames, personal identities, or internal project IDs across working tree and git log -p.
8. AuxPane UI Plugin Sidecar + CDC Watcher + Scheduled Nightly Dreaming Sidecars (with PluginNeedsSetup == false).
9. Four Modular Domain Sub-Plugins (plugins/agy-*), jsonhook.ParseHooks() hooks.json schema, subagent-scoped hooks.json (R3),
   Zero-Touch Turn-1 Reconciler (lazy_plugin_bootstrap.py + knowledge_graph.seed.json), Role Bundle (bundle.schema.json),
   Full Install -> Bootstrap -> Uninstall Clean-Slate Lifecycle, E2E 6-Scenario Dreaming & Anti-Overfitting Lifecycle (Issue #1),
   and Clean-Room Runtime Livelock & 24 GiB OOM Guards.
"""

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, os.path.join(SRC_DIR, "hooks"))

from autonomy_engine.p0_quality_first_engine import run_self_test as run_p0_self_test
from autonomy_engine.p1_quality_first_engine import run_self_test as run_p1_self_test
from autonomy_engine.anti_overfitting_gate import AntiOverfittingGate
from hooks.black_hat_analyzer import scan_target
from hooks.multi_harness_hook_adapter import (
    adapt_pre_tool_use,
    adapt_pre_invocation,
    adapt_stop,
    apply_child_rlimit_as,
    _resolve_event_mode,
)
from hooks.sentinel_dispatch import (
    check_schedule_cron_daemon_guard,
    check_own_session_transcript_access,
    normalize_dual_tool_schema_payload,
    evaluate_tool_call,
)
from hooks.agent_stop_black_hat_gate import (
    detect_orphaned_background_tasks,
    format_compact_subagent_wakeup,
    detect_case_r_reactive_task_wakeup,
    is_isolated_swe_sandbox_turn,
)
from hooks.execution_mode_router import classify_execution_mode, strip_turn0_metadata
from hooks.kg_pre_invocation_hook import (
    extract_negated_terms,
    deduplicate_turn0_ephemeral_kernel,
    sanitize_pre_invocation_hook_result,
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
)
from autonomy_engine.resilient_steer_harvester import audit_compaction_call_response_boundary
from autonomy_engine.single_turn_replay import slice_tail_preserving_traceback_and_classify_retry
from autonomy_engine.workspace_hygiene_gate import audit_sidecar_and_hook_surface_security
from autonomy_engine.delphi_six_hats_task_router import apply_popperian_counterexample_veto
from mcp_google_workspace.agent_ssot_formatter import (
    score_outbound_commitment_followup_decay,
    audit_executive_tab1_and_cross_tab_stability,
)
from playwright_scraper.cdp_navigator import flush_cookie_wal_before_headless_cdp
from knowledge_graph.dreaming_engine import (
    run_dreaming_pipeline,
    decompose_harness_friction_and_mix_shift,
)
from knowledge_graph.validate_okf import validate_kb_bundle


ALLOWED_PLUGIN_JSON_KEYS = {
    "name",
    "displayName",
    "description",
    "version",
    "logo",
    "keywords",
    "suggestedPrompts",
    "disabled",
}

ALLOWED_BUNDLE_SCHEMA_KEYS = {
    "$schema",
    "title",
    "description",
    "logo",
    "contact_email",
    "issue_tracker_id",
    "access_group",
    "plugins",
}


class TestAntigravityCustomizationsSuite(unittest.TestCase):
    def test_01_zero_web_hub_or_external_proxy_bloat(self):
        """Asserts that Web Hub server files (proxy_gateway.py, bootstrap.js, nginx.conf, start_hub.sh, terraform/) are absent."""
        forbidden_paths = [
            "src/proxy_gateway.py",
            "src/bootstrap.js",
            "src/start_hub.sh",
            "config/nginx.conf",
            "config/start_hub.sh",
            "config/antigravity-web.service",
            "terraform",
        ]
        for rel in forbidden_paths:
            self.assertFalse(
                os.path.exists(os.path.join(REPO_ROOT, rel)),
                f"Web Hub infrastructure path must not exist in standalone customizations project: {rel}",
            )

    def test_02_antigravity_cli_and_2_0_plugin_manifests(self):
        """Verifies plugin.json schema (v1.4.0), 20 keywords (zero deprecated duplicate tags), logo, suggestedPrompts, agents.json, skills.json, rules.json, plugins.json, sidecars.json."""
        ver = pathlib.Path(REPO_ROOT, "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(ver, "1.4.0")
        self.assertTrue(pathlib.Path(REPO_ROOT, "assets", "logo.svg").is_file())

        for rel in ["plugin.json", ".antigravity-plugin/plugin.json", ".gemini-plugin/plugin.json", ".claude-plugin/plugin.json"]:
            p = pathlib.Path(REPO_ROOT, rel)
            self.assertTrue(p.is_file(), f"Missing {rel}")
            data = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], "antigravity-customizations")
            self.assertEqual(data["version"], "1.4.0")
            self.assertTrue(set(data.keys()).issubset(ALLOWED_PLUGIN_JSON_KEYS), f"Unexpected keys in {rel}: {set(data.keys())}")
            self.assertNotIn("tags", data, f"Deprecated duplicate 'tags' key must be absent in {rel}")
            self.assertEqual(len(data["suggestedPrompts"]), 3)
            self.assertEqual(len(data["keywords"]), 20)

        agents_data = json.loads(pathlib.Path(REPO_ROOT, "agents.json").read_text(encoding="utf-8"))
        self.assertEqual(len(agents_data["agents"]), 5)
        skills_data = json.loads(pathlib.Path(REPO_ROOT, "skills.json").read_text(encoding="utf-8"))
        self.assertEqual(len(skills_data["skills"]), 20)
        self.assertEqual(len(skills_data["entries"][0]["include_only"]), 7)
        rules_data = json.loads(pathlib.Path(REPO_ROOT, "rules.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rules_data["rules"]), 3)
        plugins_data = json.loads(pathlib.Path(REPO_ROOT, "plugins.json").read_text(encoding="utf-8"))
        self.assertEqual(plugins_data["entries"][0]["path"], "plugins")
        sidecars_data = json.loads(pathlib.Path(REPO_ROOT, "sidecars.json").read_text(encoding="utf-8"))
        self.assertEqual(sidecars_data["entries"][0]["path"], "sidecars")

    def test_03_claude_code_non_google_harness_manifests(self):
        """Verifies CLAUDE.md, .claude/settings.json, 5 .claude/agents/*.md, 20 .claude/commands/*.md, and .mcp.json."""
        self.assertTrue(pathlib.Path(REPO_ROOT, "CLAUDE.md").is_file())
        settings = json.loads(pathlib.Path(REPO_ROOT, ".claude", "settings.json").read_text(encoding="utf-8"))
        self.assertIn("UserPromptSubmit", settings["hooks"])
        self.assertIn("PreToolUse", settings["hooks"])
        self.assertIn("Stop", settings["hooks"])

        claude_agents = list(pathlib.Path(REPO_ROOT, ".claude", "agents").glob("*.md"))
        self.assertEqual(len(claude_agents), 5)
        claude_cmds = list(pathlib.Path(REPO_ROOT, ".claude", "commands").glob("*.md"))
        self.assertEqual(len(claude_cmds), 20)

    def test_04_cursor_windsurf_cloud_code_manifests(self):
        """Verifies AGENTS.md, GEMINI.md, .cursorrules, and .mcp.json for Cursor/Windsurf/Cloud Code."""
        for fn in ("AGENTS.md", "GEMINI.md", ".cursorrules", ".mcp.json"):
            self.assertTrue(pathlib.Path(REPO_ROOT, fn).is_file(), f"Missing {fn}")
        mcp_data = json.loads(pathlib.Path(REPO_ROOT, ".mcp.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mcp_data["mcpServers"]), 7)

    def test_05_multi_harness_hook_adapter_pre_tool_use(self):
        """Verifies multi_harness_hook_adapter translates Claude Code Bash/PreToolUse payloads and blocks destructive commands."""
        bad_res = adapt_pre_tool_use({
            "session_id": "claude-sess-1",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
        })
        self.assertEqual(bad_res["decision"], "ask")
        self.assertEqual(bad_res["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertEqual(bad_res["rootConversationId"], "claude-sess-1")

        good_res = adapt_pre_tool_use({
            "rootConversationId": "agy-root-1",
            "toolName": "run_command",
            "toolArgs": {"CommandLine": "echo ok"},
        })
        self.assertEqual(good_res["decision"], "allow")
        self.assertEqual(good_res["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_06_multi_harness_hook_adapter_pre_invocation_and_stop(self):
        """Verifies multi_harness_hook_adapter UserPromptSubmit/PreInvocation skill matching and Stop gate."""
        pre_res = adapt_pre_invocation({
            "rootConversationId": "root-999",
            "prompt": "Design a multi-region GKE and Cloud Spanner architecture using universal-solution-architect",
        })
        self.assertEqual(pre_res["decision"], "allow")
        self.assertEqual(pre_res["rootConversationId"], "root-999")
        self.assertGreaterEqual(len(pre_res["matched_skills"]), 1)
        self.assertIn("hookSpecificOutput", pre_res)

        stop_res = adapt_stop({"stop_hook_active": True, "session_id": "s1"})
        self.assertEqual(stop_res["decision"], "allow")

    def test_07_eager_mcp_loading_and_native_plugin_root_env(self):
        """Verifies _meta: {'antigravity/alwaysLoad': true} and native ${PLUGIN_ROOT}/${PLUGIN_DATA} env across MCP configs."""
        from knowledge_graph.kg_mcp_server import EAGER_TOOL_META
        self.assertTrue(EAGER_TOOL_META.get("antigravity/alwaysLoad"))
        mcp_cfg = json.loads(pathlib.Path(REPO_ROOT, "mcp_config.json").read_text(encoding="utf-8"))
        for srv_name, srv_cfg in mcp_cfg["mcpServers"].items():
            self.assertTrue(srv_cfg.get("_meta", {}).get("antigravity/alwaysLoad"), f"Missing alwaysLoad on {srv_name}")
            self.assertIs(srv_cfg.get("disabled"), False)
            self.assertEqual(srv_cfg.get("env", {}).get("PLUGIN_ROOT"), "${PLUGIN_ROOT}")
            self.assertEqual(srv_cfg.get("env", {}).get("PLUGIN_DATA"), "${PLUGIN_DATA}")

    def test_08_subagent_skills_and_preload_skills_frontmatter(self):
        """Verifies all 5 custom subagents include both native 'skills:' and 'preloadSkills:' frontmatter keys."""
        nested_agents = list(pathlib.Path(REPO_ROOT, "agents").glob("*/agent.md"))
        flat_agents = list(pathlib.Path(REPO_ROOT, "agents").glob("*.md"))
        self.assertEqual(len(nested_agents), 5)
        self.assertEqual(len(flat_agents), 5)
        for ag_md in nested_agents + flat_agents:
            txt = ag_md.read_text(encoding="utf-8")
            self.assertIn("preloadSkills:", txt, f"Missing preloadSkills in {ag_md}")
            self.assertIn("\nskills:\n", txt, f"Missing native skills: key in {ag_md}")

    def test_09_p0_p1_quality_engines_and_saboteur_benchmark(self):
        """Verifies P0 (CB-1..CB-7), P1 (P1-CB-1..P1-CB-7), and 8-Mutant Saboteur self-tests."""
        self.assertEqual(run_p0_self_test()["verdict"], "PASS")
        self.assertEqual(run_p1_self_test()["verdict"], "PASS")
        self.assertEqual(AntiOverfittingGate().run_saboteur_benchmark()["verdict"], "PASS")

    def test_10_okf_v02_bundle_and_20_pdq_skills(self):
        """Verifies Open Knowledge Format (OKF v0.2) kb/ dossiers and all 20 PD-Q skills."""
        val_res = validate_kb_bundle(os.path.join(REPO_ROOT, "kb"))
        self.assertTrue(val_res["valid"])
        manifest = json.loads(pathlib.Path(REPO_ROOT, "skills", "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["skill_count"], 20)

    def test_11_installer_dry_run_and_temp_home_install(self):
        """Verifies scripts/install.sh installs native plugin bundle and 4 modular plugins cleanly into a temp HOME."""
        tmp_home = tempfile.mkdtemp()
        try:
            res = subprocess.run(
                ["bash", os.path.join(REPO_ROOT, "scripts", "install.sh"), "--target", "all", "--home", tmp_home],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("v1.4.0 installed successfully", res.stdout)
            self.assertTrue(os.path.isfile(os.path.join(tmp_home, ".gemini", "config", "hooks.json")))
            self.assertTrue(os.path.isfile(os.path.join(tmp_home, ".gemini", "config", "plugins", "antigravity-customizations", "plugin.json")))
            self.assertTrue(os.path.isfile(os.path.join(tmp_home, ".gemini", "config", "plugins", "agy-core-governance", "plugin.json")))
            self.assertTrue(os.path.isfile(os.path.join(tmp_home, ".claude", "settings.json")))
            self.assertTrue(os.path.isfile(os.path.join(tmp_home, ".cursor", "mcp.json")))
        finally:
            shutil.rmtree(tmp_home, ignore_errors=True)

    def test_12_customer_distribution_zero_google_ip_or_binaries(self):
        """Certifies 0 binaries, 0 zip bundles, and 0 internal Google codenames, personal emails, or test project IDs."""
        from hooks.black_hat_analyzer import PROHIBITED_TOKEN_SHA256, PROHIBITED_LEAK_PATTERNS
        scan_res = scan_target(REPO_ROOT)
        self.assertEqual(scan_res["verdict"], "PASS", f"Static analyzer failed: {scan_res}")

        repo_path = pathlib.Path(REPO_ROOT)
        binary_files = []
        violations = []
        runtime_skip_dirs = {".git", "__pycache__", "node_modules"}
        for p in sorted(repo_path.rglob("*")):
            if (runtime_skip_dirs & set(p.parts)) or not p.is_file():
                continue
            rel = str(p.relative_to(repo_path))
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                binary_files.append(rel)
                continue
            for token in set(re.findall(r"[A-Za-z0-9_-]{4,}", content)):
                h = hashlib.sha256(token.lower().encode("utf-8")).hexdigest()
                if h in PROHIBITED_TOKEN_SHA256:
                    violations.append(f"{rel}: token '{token}'")

        self.assertEqual(binary_files, [], f"Binary files found: {binary_files}")
        self.assertEqual(violations, [], f"Internal IP / personal identifier violations found: {violations}")

        if (
            os.path.isdir(os.path.join(REPO_ROOT, ".git"))
            and subprocess.run(
                ["git", "-C", REPO_ROOT, "rev-parse", "--verify", "HEAD"],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        ):
            git_log_out = subprocess.check_output(
                ["git", "-C", REPO_ROOT, "log", "-p"], text=True
            )
            history_violations = []
            for token in set(re.findall(r"[A-Za-z0-9_-]{4,}", git_log_out)):
                h = hashlib.sha256(token.lower().encode("utf-8")).hexdigest()
                if h in PROHIBITED_TOKEN_SHA256:
                    history_violations.append(token)
            for pat, desc in PROHIBITED_LEAK_PATTERNS:
                if re.search(pat, git_log_out):
                    history_violations.append(desc)
            self.assertEqual(history_violations, [], f"Git commit history contains internal tokens: {history_violations}")

    def test_13_ui_plugin_sidecar_aux_pane_and_theme_tokens(self):
        """Verifies sidecars/autonomy-dashboard/sidecar.json, /preload.js, modern CSS tokens, and server.py --self-test."""
        sc_dir = pathlib.Path(REPO_ROOT, "sidecars", "autonomy-dashboard")
        sc_json = json.loads((sc_dir / "sidecar.json").read_text(encoding="utf-8"))
        self.assertTrue(sc_json["has_web_ui"])
        self.assertEqual(sc_json["ui_config"]["views"][0]["entrypoint"], "SIDECAR_UI_ENTRYPOINT_AUX_PANE")

        html = (sc_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn('<script src="/preload.js"></script>', html)
        self.assertIn("window.sidecar", html)

        css = (sc_dir / "styles.css").read_text(encoding="utf-8")
        self.assertIn("var(--background", css)
        self.assertIn("var(--foreground", css)
        self.assertIn("var(--card", css)
        self.assertNotIn("--vscode-", css)

        res = subprocess.run(
            ["python3", "-B", str(sc_dir / "server.py"), "--self-test"],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(res.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["version"], "1.4.0")
        self.assertEqual(payload["skill_count"], 20)
        self.assertEqual(payload["plugin_packs"], 4)

    def test_14_four_modular_domain_plugins(self):
        """Verifies the 4 modular domain plugins under plugins/ partition all 20 skills, 5 subagents, and 7 MCP servers."""
        expected_dirs = {
            "agy-core-governance",
            "agy-knowledge-graph",
            "agy-cloud-architect",
            "agy-workspace-automation",
        }
        plugins_root = pathlib.Path(REPO_ROOT, "plugins")
        found_dirs = {p.name for p in plugins_root.iterdir() if p.is_dir()}
        self.assertEqual(found_dirs, expected_dirs)

        all_skills = set()
        all_agents = set()
        all_mcp = set()
        for d in expected_dirs:
            pdir = plugins_root / d
            pjson = json.loads((pdir / "plugin.json").read_text(encoding="utf-8"))
            self.assertTrue(set(pjson.keys()).issubset(ALLOWED_PLUGIN_JSON_KEYS))
            self.assertNotIn("tags", pjson)
            self.assertEqual(pjson["version"], "1.4.0")
            if (pdir / "skills.json").is_file():
                sjson = json.loads((pdir / "skills.json").read_text(encoding="utf-8"))
                all_skills.update(sjson["entries"][0]["include_only"])
            if (pdir / "agents.json").is_file():
                ajson = json.loads((pdir / "agents.json").read_text(encoding="utf-8"))
                all_agents.update(ajson["entries"][0]["include_only"])
            if (pdir / "mcp_config.json").is_file():
                mjson = json.loads((pdir / "mcp_config.json").read_text(encoding="utf-8"))
                all_mcp.update(mjson["mcpServers"].keys())

        self.assertEqual(len(all_skills), 20)
        self.assertEqual(len(all_agents), 5)
        self.assertEqual(len(all_mcp), 7)

    def test_15_parsehooks_schema_and_cwd_relative_execution(self):
        """Verifies hooks.json uses jsonhook.ParseHooks() map[string]JSONHookSpec schema and executes cleanly from REPO_ROOT."""
        hooks_cfg = json.loads(pathlib.Path(REPO_ROOT, "hooks.json").read_text(encoding="utf-8"))
        self.assertNotIn("hooks", hooks_cfg, "hooks.json must use top-level named hooks (map[string]JSONHookSpec), not an outer 'hooks' wrapper")
        self.assertIn("sentinel-policy-guard", hooks_cfg)
        self.assertIn("knowledge-graph-grounding", hooks_cfg)
        self.assertIn("black-hat-completion-gate", hooks_cfg)
        self.assertNotIn("PostToolUse", json.dumps(hooks_cfg))

        # PreToolUse is grouped (matcher + hooks); PreInvocation and Stop are flat handler arrays
        pre_tool_group = hooks_cfg["sentinel-policy-guard"]["PreToolUse"][0]
        self.assertIn("matcher", pre_tool_group)
        self.assertIn("hooks", pre_tool_group)
        pre_inv_list = hooks_cfg["knowledge-graph-grounding"]["PreInvocation"]
        self.assertEqual(len(pre_inv_list), 2)
        self.assertIn("command", pre_inv_list[0])
        stop_list = hooks_cfg["black-hat-completion-gate"]["Stop"]
        self.assertIn("command", stop_list[0])

        env = {k: v for k, v in os.environ.items() if k != "PLUGIN_ROOT"}
        for cmd in [
            pre_tool_group["hooks"][0]["command"],
            pre_inv_list[1]["command"],
            stop_list[0]["command"],
        ]:
            res = subprocess.run(
                cmd,
                shell=True,
                cwd=REPO_ROOT,
                env=env,
                input=json.dumps({"rootConversationId": "test-cid", "prompt": "test", "stop_hook_active": True}),
                capture_output=True,
                text=True,
                check=True,
            )
            out = json.loads(res.stdout)
            self.assertIn("decision", out)

    def test_16_subagent_scoped_hooks_and_lazy_plugin_bootstrap(self):
        """Verifies subagent-scoped agents/black-hat-{goldfish,judge}/hooks.json (R3), seed KG, and lazy_plugin_bootstrap.py."""
        for ag in ("black-hat-goldfish", "black-hat-judge"):
            hpath = pathlib.Path(REPO_ROOT, "agents", ag, "hooks.json")
            self.assertTrue(hpath.is_file(), f"Missing subagent hooks.json for {ag}")
            hdata = json.loads(hpath.read_text(encoding="utf-8"))
            self.assertIn("black-hat-subagent-pre-tool-sentinel", hdata)
            self.assertIn("black-hat-subagent-return-gate", hdata)

        seed_kg = json.loads(pathlib.Path(REPO_ROOT, "resources", "knowledge_graph.seed.json").read_text(encoding="utf-8"))
        self.assertEqual(seed_kg["metadata"]["package_version"], "1.4.0")
        self.assertGreaterEqual(len(seed_kg["entities"]), 4)

        res = subprocess.run(
            ["python3", "-B", os.path.join(REPO_ROOT, "src", "hooks", "lazy_plugin_bootstrap.py"), "--self-test"],
            capture_output=True,
            text=True,
            check=True,
        )
        out = json.loads(res.stdout)
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["cold"]["status"], "bootstrapped")
        self.assertEqual(out["warm"]["status"], "fast_path_cached")

    def test_17_role_bundle_schema_and_three_zero_permission_sidecars(self):
        """Verifies bundle.schema.json compliance, AGENT_DIRECTORY.md/WORKFLOW_DIRECTORY.md, and 3 zero-permission sidecars."""
        bundle_path = pathlib.Path(REPO_ROOT, "_agents", "bundles", "enterprise_architect", "bundle-antigravity-customizations.json")
        self.assertTrue(bundle_path.is_file())
        bdata = json.loads(bundle_path.read_text(encoding="utf-8"))
        self.assertEqual(set(bdata.keys()), ALLOWED_BUNDLE_SCHEMA_KEYS)
        self.assertEqual(bdata["$schema"], "https://schemas.example.com/antigravity/schemas/v1/bundle.schema.json")
        self.assertEqual(len(bdata["plugins"]), 5)

        self.assertTrue(pathlib.Path(REPO_ROOT, "AGENT_DIRECTORY.md").is_file())
        self.assertTrue(pathlib.Path(REPO_ROOT, "WORKFLOW_DIRECTORY.md").is_file())

        sidecar_dirs = {p.name for p in pathlib.Path(REPO_ROOT, "sidecars").iterdir() if p.is_dir()}
        self.assertEqual(sidecar_dirs, {"autonomy-dashboard", "kg_cdc_watcher", "daily-nightly-dreaming-engine"})
        for sname in sidecar_dirs:
            sjson = json.loads(pathlib.Path(REPO_ROOT, "sidecars", sname, "sidecar.json").read_text(encoding="utf-8"))
            self.assertNotIn("arguments", sjson)
            self.assertNotIn("agent_permissions", sjson)
            self.assertNotIn("access_grants", sjson)

        watcher_res = subprocess.run(
            ["python3", "-B", os.path.join(REPO_ROOT, "sidecars", "kg_cdc_watcher", "watcher.py"), "--self-test"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(watcher_res.stdout)["status"], "ok")

    def test_18_full_lifecycle_install_bootstrap_uninstall_clean_slate(self):
        """Verifies the 4-stage lifecycle: Install -> PreInvocation Bootstrap -> Rule Backup Restore -> Clean-Slate Uninstall."""
        tmp_home = tempfile.mkdtemp()
        try:
            user_rules_dir = pathlib.Path(tmp_home, ".gemini", "config", "rules")
            user_rules_dir.mkdir(parents=True, exist_ok=True)
            (user_rules_dir / "AGENTS.md").write_text("# Pre-existing User Rule\n", encoding="utf-8")

            subprocess.run(
                ["bash", os.path.join(REPO_ROOT, "scripts", "install.sh"), "--target", "agy", "--home", tmp_home],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue(pathlib.Path(tmp_home, ".gemini", "config", "plugins", "antigravity-customizations", "plugin.json").is_file())
            self.assertTrue(pathlib.Path(tmp_home, ".gemini", "config", "projects", "automations.json").is_file())

            un_res = subprocess.run(
                ["bash", os.path.join(REPO_ROOT, "scripts", "uninstall.sh"), "--home", tmp_home],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("vanilla clean slate verified", un_res.stdout)
            self.assertFalse(pathlib.Path(tmp_home, ".gemini", "config", "plugins", "antigravity-customizations").exists())
            self.assertFalse(pathlib.Path(tmp_home, ".gemini", "antigravity", "plugin_data", "antigravity-customizations").exists())
        finally:
            shutil.rmtree(tmp_home, ignore_errors=True)

    def test_19_dreaming_pipeline_e2e_6_scenarios(self):
        """Verifies GitHub Issue #1 6-scenario E2E Dreaming & Anti-Overfitting lifecycle on synthetic session transcripts."""
        tmp_dir = tempfile.mkdtemp()
        try:
            graph_path = os.path.join(tmp_dir, "knowledge_graph.json")
            warm_path = os.path.join(tmp_dir, "kg_warm_cache.json")
            plan_path = os.path.join(tmp_dir, "dreaming_reasoned_implementation_plan.json")
            traces_dir = os.path.join(tmp_dir, "traces")
            os.makedirs(traces_dir, exist_ok=True)

            # Seed graph with:
            # 1) A legacy steer:auto_old node
            # 2) An expired steer:expired0001 node from 2025-01-01 (decayed_confidence < 0.15)
            # 3) An ACTIVE steer:unhelpful01 node absorbed 10 days ago with baseline_quality_score=99.9
            initial_graph = {
                "version": "2.0-OKF-v0.2",
                "nodes": [
                    {
                        "id": "steer:auto_legacy",
                        "label": "Legacy auto steer",
                        "type": "UserPreference",
                        "description": "Always use legacy flag",
                        "properties": {"confidence": 0.95},
                        "updated_at": "2026-10-01T00:00:00Z",
                    },
                    {
                        "id": "steer:expired0001",
                        "label": "Expired steer rule",
                        "type": "UserPreference",
                        "description": "Always run old linter before build",
                        "properties": {"confidence": 0.95},
                        "updated_at": "2025-01-01T00:00:00Z",
                    },
                    {
                        "id": "steer:unhelpful01",
                        "label": "Unhelpful active rule",
                        "type": "UserPreference",
                        "description": "Always force verbose debug logging on every query",
                        "properties": {
                            "confidence": 0.95,
                            "decayed_confidence": 0.90,
                            "status": "ACTIVE",
                            "active": True,
                            "absorbed_at": "2026-10-01T00:00:00Z",
                            "baseline_quality_score": 99.9,
                        },
                        "updated_at": "2026-10-18T00:00:00Z",
                    },
                ],
                "edges": [],
            }
            with open(graph_path, "w", encoding="utf-8") as f:
                json.dump(initial_graph, f)

            # Synthetic transcripts:
            # - Trace 1 (Session A, Day 2026-10-18):
            #   * Recurring clean rule R_clean: "Always verify CLI flags via --help before invoking external tools."
            #   * Single-session rule R_single: "Always run unit tests before committing database migrations."
            #   * Token-bloated rule R_bloat (28 words > 10% of 250-token budget when max_token_growth_pct=5.0)
            #   * Includes 1 ERROR step so session quality score is 96.0 (< 99.9 baseline of steer:unhelpful01)
            trace1_path = os.path.join(traces_dir, "trace_sess_a.jsonl")
            trace1_steps = [
                {
                    "session_id": "sess-alpha",
                    "created_at": "2026-10-18T10:00:00Z",
                    "type": "USER_INPUT",
                    "content": (
                        "Always verify CLI flags via --help before invoking external tools.\n"
                        "Always run unit tests before committing database migrations.\n"
                        "Always validate schema migrations across staging replicas and check foreign key indexes "
                        "and verify rollback scripts and inspect query plans and audit table locks before deployment."
                    ),
                },
                {
                    "session_id": "sess-alpha",
                    "created_at": "2026-10-18T10:01:00Z",
                    "type": "TOOL_RESULT",
                    "status": "ERROR",
                    "toolAction": "run_command",
                },
            ]
            with open(trace1_path, "w", encoding="utf-8") as f:
                for st in trace1_steps:
                    f.write(json.dumps(st) + "\n")

            # - Trace 2 (Session B, Day 2026-10-19):
            #   * Recurring clean rule R_clean again in a second session on a second day!
            trace2_path = os.path.join(traces_dir, "trace_sess_b.jsonl")
            trace2_steps = [
                {
                    "session_id": "sess-beta",
                    "created_at": "2026-10-19T14:00:00Z",
                    "type": "USER_INPUT",
                    "content": "Always verify CLI flags via --help before invoking external tools.",
                },
            ]
            with open(trace2_path, "w", encoding="utf-8") as f:
                for st in trace2_steps:
                    f.write(json.dumps(st) + "\n")

            # Reasoner implementation plan with READY_FOR_AB_VALIDATION
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "REASONING_VERDICT": "READY_FOR_AB_VALIDATION",
                        "candidate_patches": [
                            {
                                "rule": "Always check exit codes after running container builds.",
                                "confidence": 0.95,
                                "observed_sessions": ["sess-r1", "sess-r2"],
                                "observed_days": ["2026-10-18", "2026-10-19"],
                            }
                        ],
                    },
                    f,
                )

            # Use a strict 6.0% max_token_growth_pct gate so 10-word rules (4.0% growth) pass evaluate_patch()
            # while the 26-word bloated rule (10.4% growth) is rejected by evaluate_patch()!
            strict_gate = AntiOverfittingGate(max_token_growth_pct=6.0)
            res = run_dreaming_pipeline(
                lookback_hours=48,
                graph_path=graph_path,
                trace_dirs=[traces_dir],
                sdt_gate=strict_gate,
                min_recurrence_sessions=2,
                min_recurrence_days=2,
                now_ts=1792497600.0,  # 2026-10-20T12:00:00Z
                reasoner_plan_path=plan_path,
                warm_cache_path=warm_path,
            )

            self.assertEqual(res["status"], "ok")
            # Scenario (c): bloated rule rejected by evaluate_patch()
            self.assertGreaterEqual(res["rejected_by_patch_gate_count"], 1)
            # Scenario (e): steer:auto_legacy and steer:expired0001 evicted
            self.assertGreaterEqual(res["evicted_decayed_count"], 2)
            # Scenario (f): steer:unhelpful01 evicted due to 7-day negative quality delta (avg_score < 99.9)
            self.assertEqual(res["evicted_unhelpful_count"], 1)
            # Scenario (a) + Reasoner plan: 2 active steers (R_clean + reasoner patch)
            self.assertEqual(res["activated_steers_count"], 2)
            # Scenario (b): 1 provisional single-session steer (R_single)
            self.assertEqual(res["provisional_steers_count"], 1)

            g_after = json.loads(pathlib.Path(graph_path).read_text(encoding="utf-8"))
            steer_nodes = {
                n["description"]: n for n in g_after["nodes"] if str(n.get("id", "")).startswith("steer:")
            }
            self.assertIn("Always verify CLI flags via --help before invoking external tools", steer_nodes)
            clean_node = steer_nodes["Always verify CLI flags via --help before invoking external tools"]
            self.assertEqual(clean_node["properties"]["status"], "ACTIVE")
            self.assertTrue(clean_node["properties"]["active"])
            self.assertEqual(len(clean_node["properties"]["observed_sessions"]), 2)
            self.assertEqual(len(clean_node["properties"]["observed_days"]), 2)

            self.assertIn("Always run unit tests before committing database migrations", steer_nodes)
            single_node = steer_nodes["Always run unit tests before committing database migrations"]
            self.assertEqual(single_node["properties"]["status"], "PROVISIONAL")
            self.assertFalse(single_node["properties"]["active"])

            # Verify warm serving cache excludes PROVISIONAL and evicted steers
            warm_data = json.loads(pathlib.Path(warm_path).read_text(encoding="utf-8"))
            warm_descriptions = {
                n.get("description") for n in warm_data["nodes"] if str(n.get("id", "")).startswith("steer:")
            }
            self.assertIn("Always verify CLI flags via --help before invoking external tools", warm_descriptions)
            self.assertIn("Always check exit codes after running container builds.", warm_descriptions)
            self.assertNotIn("Always run unit tests before committing database migrations", warm_descriptions)
            self.assertNotIn("Always run old linter before build", warm_descriptions)
            self.assertNotIn("Always force verbose debug logging on every query", warm_descriptions)

            # Scenario (d): Fail-closed saboteur self-test blocks all rule absorption
            class BrokenSaboteurGate(AntiOverfittingGate):
                def run_saboteur_benchmark(self):
                    return {"verdict": "FAIL", "mutants_caught": 0, "mutants_total": 8, "saboteur_recall_pct": 0.0}

            blocked_graph_path = os.path.join(tmp_dir, "blocked_graph.json")
            with open(blocked_graph_path, "w", encoding="utf-8") as f:
                json.dump({"version": "2.0-OKF-v0.2", "nodes": [], "edges": []}, f)

            blocked_res = run_dreaming_pipeline(
                lookback_hours=48,
                graph_path=blocked_graph_path,
                trace_dirs=[traces_dir],
                sdt_gate=BrokenSaboteurGate(),
                warm_cache_path=warm_path,
            )
            self.assertEqual(blocked_res["status"], "blocked_by_saboteur")
            self.assertEqual(blocked_res["steers_harvested_count"], 0)
            self.assertEqual(blocked_res["activated_steers_count"], 0)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_20_clean_room_runtime_livelock_and_oom_guards(self):
        """Verifies --event CLI flag parsing, 24 GiB RLIMIT_AS child guard, cron daemon guard, and C14f/C14g subagent guards."""
        self.assertEqual(_resolve_event_mode(["prog", "--event", "PreToolUse"]), "PreToolUse")
        self.assertEqual(_resolve_event_mode(["prog", "--event=PreInvocation"]), "PreInvocation")
        self.assertEqual(_resolve_event_mode(["prog", "Stop"]), "Stop")
        self.assertTrue(apply_child_rlimit_as())

        # Unbounded cron without IsDaemon=True or MaxIterations is denied
        cron_block = check_schedule_cron_daemon_guard(
            "schedule", {"CronExpression": "*/5 * * * *", "Prompt": "poll status"}
        )
        self.assertIsNotNone(cron_block)
        self.assertEqual(cron_block["decision"], "deny")

        # Cron with IsDaemon=True is allowed
        cron_ok = check_schedule_cron_daemon_guard(
            "schedule", {"CronExpression": "*/5 * * * *", "IsDaemon": True, "Prompt": "standing job"}
        )
        self.assertIsNone(cron_ok)

        # Own-session transcript read is explicitly allowed
        own_ok = check_own_session_transcript_access(
            "view_file",
            {"AbsolutePath": "/tmp/brain/cid-1234/.system_generated/logs/transcript.jsonl"},
            root_conversation_id="cid-1234",
        )
        self.assertEqual(own_ok["decision"], "allow")

        # C14f orphaned background task detection
        orphan_res = detect_orphaned_background_tasks([
            {
                "tool_calls": [
                    {"name": "run_command", "args": {"CommandLine": "python3 worker.py", "WaitMsBeforeAsync": 500}},
                    {"name": "schedule", "args": {"CronExpression": "*/5 * * * *", "Prompt": "check"}},
                ]
            }
        ])
        self.assertFalse(orphan_res["passed"])
        self.assertEqual(orphan_res["active_orphans"], 2)

        # C14g compact subagent wakeup (<800B)
        long_msg = "Detailed forensic evidence row " * 40
        wakeup = format_compact_subagent_wakeup(long_msg, detail_path="/tmp/dossier.md", max_bytes=800)
        self.assertTrue(wakeup["passed"])
        self.assertTrue(wakeup["truncated"])
        self.assertLessEqual(wakeup["byte_length"], 800)

    def test_20b_copy_paste_deploy_prompt_and_install_verify_flag(self):
        """Verifies DEPLOY_PROMPT.md, README.md copy-paste deployment prompt, and ./scripts/install.sh --verify."""
        deploy_md = pathlib.Path(REPO_ROOT, "DEPLOY_PROMPT.md")
        readme_md = pathlib.Path(REPO_ROOT, "README.md")
        self.assertTrue(deploy_md.is_file(), "Missing DEPLOY_PROMPT.md in repo root")
        deploy_txt = deploy_md.read_text(encoding="utf-8")
        readme_txt = readme_md.read_text(encoding="utf-8")

        for doc_name, txt in (("DEPLOY_PROMPT.md", deploy_txt), ("README.md", readme_txt)):
            self.assertIn("https://github.com/gmilen-sketch/antigravity-customizations.git", txt, f"Missing repo URL in {doc_name}")
            self.assertIn("./scripts/install.sh --target all --verify", txt, f"Missing --verify install command in {doc_name}")
            self.assertIn("GetAllSkills", txt, f"Missing Hub LanguageServer verification probe in {doc_name}")

        tmp_home = tempfile.mkdtemp()
        try:
            res = subprocess.run(
                ["bash", os.path.join(REPO_ROOT, "scripts", "install.sh"), "--target", "all", "--home", tmp_home, "--verify"],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "AGY_INSTALL_VERIFY_IN_PROGRESS": "1"},
                check=True,
            )
            self.assertIn('"verdict": "PASS"', res.stdout)
            self.assertIn('"primitives_verified": "7/7"', res.stdout)
        finally:
            shutil.rmtree(tmp_home, ignore_errors=True)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_v140_wave12_and_hooks import TestV140Wave12AndHookHardening  # noqa: F401
    unittest.main()
