#!/usr/bin/env python3
"""
Unified Plugin + Host-Companion Reconciler (`lazy_plugin_bootstrap.py` v1.4.0)
for the Customer-Facing Antigravity Customizations Suite.

Triggered automatically in two ways (Single Install / Update Flow):
1. Zero-Touch Turn-1 / Version-Bump `PreInvocation` Hook (`<plugin_root>/hooks.json`):
   - Fast path (`version == bootstrapped_version.json` and warm cache exists): `< 1 ms` exit.
   - Cold start or version bump:
     * Seeds `knowledge_graph.json` and `/dev/shm/kg_warm_cache.json` from
       `resources/knowledge_graph.seed.json` + `kb/` (`OKF v0.2`).
     * Backs up duplicate standalone loose rules (`~/.gemini/config/rules/{GEMINI,AGENTS,no-bullshit}.md`)
       into `${PLUGIN_DATA}/legacy_standalone_backup/` (`R1`).
     * Provisions `~/.gemini/config/projects/automations.json` (`id: "automations"`,
       display name `"Automations"`) so scheduled sidecars share one workspace (`R5`).
2. Explicit CLI Invocation (`python3 lazy_plugin_bootstrap.py --full-host-reconcile [--home <dir>]`):
   - Invoked by `scripts/install.sh` or verification suites.
"""

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import sys
import time

sys.dont_write_bytecode = True

HOOK_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HOOK_DIR.parent.parent
MANAGED_RULES = ("GEMINI.md", "AGENTS.md", "no-bullshit.md")
MANAGED_HOOK_KEYS = (
    "sentinel-policy-guard",
    "knowledge-graph-grounding",
    "black-hat-completion-gate",
)
MANAGED_MCP_KEYS = (
    "autonomy_engine",
    "knowledge_graph",
    "diagram_renderer",
    "deep_research",
    "google_workspace",
    "playwright_scraper",
    "six_hats_evaluator",
)
MANAGED_AGENTS = (
    "black-hat-goldfish",
    "black-hat-judge",
    "black-hat-critic",
    "dreaming-improvement-reasoner",
    "workspace-housekeeper",
)
MANAGED_SIDECARS = (
    "autonomy-dashboard",
    "daily-nightly-dreaming-engine",
    "kg_cdc_watcher",
)
MANAGED_PLUGIN_PREFIXES = (
    "antigravity-customizations/",
    "agy-knowledge-graph/",
    "enterprise-cloud-architect/",
)


def _read_plugin_version(repo_root: pathlib.Path) -> str:
    ver_file = repo_root / "VERSION"
    if ver_file.is_file():
        return ver_file.read_text(encoding="utf-8").strip()
    return "1.4.0"


def is_sandbox_or_bundled_nondev_host(home_dir: str) -> bool:
    """
    NONDEV-BUG-1: Detects when the plugin is running on a non-developer adopter host
    or inside a container/sandbox where legacy dev-only repo paths do not exist.
    """
    home = pathlib.Path(home_dir).resolve()
    if str(home).startswith("/testbed") or os.environ.get("ANTIGRAVITY_SWE_SANDBOX") == "1":
        return True
    dev_projects_dir = home / "Projects"
    return not dev_projects_dir.is_dir()


def resolve_multi_path_skills_root(home_dir: str) -> pathlib.Path:
    """
    NONDEV-BUG-2..3: Resolves the active skills directory across bundled plugin,
    ~/.gemini/config/plugins/antigravity-customizations/skills, and ~/.gemini/antigravity/skills.
    """
    home = pathlib.Path(home_dir).resolve()
    candidates = [
        REPO_ROOT / "skills",
        home / ".gemini" / "config" / "plugins" / "antigravity-customizations" / "skills",
        home / ".gemini" / "antigravity" / "skills",
        home / ".gemini" / "config" / "skills",
    ]
    for cand in candidates:
        if cand.is_dir():
            return cand
    return REPO_ROOT / "skills"


def _resolve_paths(home_dir: str) -> dict:
    home = pathlib.Path(home_dir).resolve()
    plugin_data_env = os.environ.get("PLUGIN_DATA", "")
    if plugin_data_env and home == pathlib.Path.home().resolve():
        plugin_data = pathlib.Path(plugin_data_env)
    else:
        plugin_data = home / ".gemini" / "antigravity" / "plugin_data" / "antigravity-customizations"
    shm_root = pathlib.Path("/dev/shm") if os.path.isdir("/dev/shm") and home == pathlib.Path.home().resolve() else (plugin_data / "shm")
    return {
        "home": home,
        "plugin_data": plugin_data,
        "stamp": plugin_data / "bootstrapped_version.json",
        "backup_dir": plugin_data / "legacy_standalone_backup",
        "review_json": plugin_data / "legacy_customizations_review.json",
        "review_md": plugin_data / "LEGACY_CUSTOMIZATIONS_REVIEW.md",
        "kg_json": home / ".gemini" / "antigravity" / "knowledge_graph.json",
        "warm_cache": shm_root / "kg_warm_cache.json",
        "config_json": home / ".gemini" / "config" / "config.json",
        "projects_dir": home / ".gemini" / "config" / "projects",
        "automations_proj": home / ".gemini" / "config" / "projects" / "automations.json",
    }


def _sha256_file(path: pathlib.Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _managed_skill_names() -> set:
    sfile = REPO_ROOT / "skills.json"
    if sfile.is_file():
        try:
            data = json.loads(sfile.read_text(encoding="utf-8"))
            return {pathlib.Path(p).parts[1] for p in data.get("skills", []) if len(pathlib.Path(p).parts) >= 2}
        except Exception:
            pass
    return {d.name for d in (REPO_ROOT / "skills").iterdir() if d.is_dir()} if (REPO_ROOT / "skills").is_dir() else set()


def backup_and_audit_existing_customizations(home_dir: str) -> dict:
    """
    Snapshots pre-existing user customizations before/during plugin installation into
    legacy_standalone_backup/ and writes legacy_customizations_review.json +
    LEGACY_CUSTOMIZATIONS_REVIEW.md with side-by-side coexistence and merge guidance.
    """
    paths = _resolve_paths(home_dir)
    home = paths["home"]
    backup_dir = paths["backup_dir"]
    files_backup_root = backup_dir / "files"
    paths["plugin_data"].mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    existing_items_by_key = {}
    if paths["review_json"].is_file():
        try:
            prev = json.loads(paths["review_json"].read_text(encoding="utf-8"))
            for it in prev.get("discovered_items", []):
                k = f"{it.get('category')}:{it.get('original_path')}:{it.get('name')}"
                existing_items_by_key[k] = it
        except Exception:
            pass

    def _record(item: dict) -> None:
        k = f"{item.get('category')}:{item.get('original_path')}:{item.get('name')}"
        existing_items_by_key[k] = item

    # 1. Pre-existing Rules (.gemini/config/rules/*.md, .claude/CLAUDE.md, .cursorrules)
    rules_dir = home / ".gemini" / "config" / "rules"
    if rules_dir.is_dir():
        for rfile in sorted(rules_dir.glob("*.md")):
            if rfile.is_symlink():
                continue
            rel = str(rfile.relative_to(home))
            if rfile.name in MANAGED_RULES:
                repo_rule = REPO_ROOT / "rules" / rfile.name
                if _sha256_file(rfile) != _sha256_file(repo_rule):
                    top_bkp = backup_dir / rfile.name
                    rel_bkp = files_backup_root / rel
                    rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                    if not top_bkp.is_file():
                        shutil.copy2(rfile, top_bkp)
                    if not rel_bkp.is_file():
                        shutil.copy2(rfile, rel_bkp)
                    _record({
                        "category": "rule",
                        "name": rfile.name,
                        "original_path": rel,
                        "backup_path": str(top_bkp.relative_to(home)),
                        "status": "BACKED_UP_FOR_MERGE",
                        "integration_strategy": (
                            "Backed up before v1.4.0 rule deployment. Run "
                            "`python3 src/hooks/lazy_plugin_bootstrap.py --merge-legacy` "
                            "to consolidate your custom rules into `~/.gemini/config/rules/legacy-user-customizations.md` "
                            "so they load alongside the 3 Arm B Sentinel rules without file collision."
                        ),
                    })
            elif rfile.name != "legacy-user-customizations.md":
                rel_bkp = files_backup_root / rel
                rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rfile, rel_bkp)
                _record({
                    "category": "rule",
                    "name": rfile.name,
                    "original_path": rel,
                    "backup_path": str(rel_bkp.relative_to(home)),
                    "status": "AUTO_COEXISTING",
                    "integration_strategy": (
                        "Preserved in `~/.gemini/config/rules/` and automatically active "
                        "alongside the 3 Arm B Sentinel rules."
                    ),
                })

    for extra_rule_rel, repo_equiv in ((".claude/CLAUDE.md", "CLAUDE.md"), (".cursorrules", ".cursorrules")):
        cand = home / extra_rule_rel
        if cand.is_file() and _sha256_file(cand) != _sha256_file(REPO_ROOT / repo_equiv):
            rel_bkp = files_backup_root / extra_rule_rel
            rel_bkp.parent.mkdir(parents=True, exist_ok=True)
            if not rel_bkp.is_file():
                shutil.copy2(cand, rel_bkp)
            _record({
                "category": "rule",
                "name": extra_rule_rel,
                "original_path": extra_rule_rel,
                "backup_path": str(rel_bkp.relative_to(home)),
                "status": "BACKED_UP_FOR_MERGE",
                "integration_strategy": (
                    f"Backed up `{extra_rule_rel}`. Append custom project instructions as a dedicated "
                    f"bottom section in `{extra_rule_rel}` or `~/.gemini/config/rules/legacy-user-customizations.md`."
                ),
            })

    # 2. Pre-existing Skills (.gemini/config/skills/*, .gemini/skills/*)
    suite_skills = _managed_skill_names()
    for sroot_rel in (".gemini/config/skills", ".gemini/skills"):
        sroot = home / sroot_rel
        if not sroot.is_dir():
            continue
        for sdir in sorted(sroot.iterdir()):
            if not sdir.is_dir():
                continue
            rel = str(sdir.relative_to(home))
            if sdir.name not in suite_skills:
                rel_bkp = files_backup_root / rel
                if not rel_bkp.exists():
                    rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(sdir, rel_bkp)
                _record({
                    "category": "skill",
                    "name": sdir.name,
                    "original_path": rel,
                    "backup_path": str(rel_bkp.relative_to(home)),
                    "status": "AUTO_COEXISTING",
                    "integration_strategy": (
                        f"Custom skill `{sdir.name}` is preserved on disk alongside the 20 PD-Q suite skills. "
                        "Optionally add it to `skills.json` `include_only` if Tier-1 preloading is desired."
                    ),
                })
            else:
                user_skill_md = sdir / "SKILL.md"
                repo_skill_md = REPO_ROOT / "skills" / sdir.name / "SKILL.md"
                if user_skill_md.is_file() and _sha256_file(user_skill_md) != _sha256_file(repo_skill_md):
                    rel_bkp = files_backup_root / rel
                    if not rel_bkp.exists():
                        rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(sdir, rel_bkp)
                    _record({
                        "category": "skill",
                        "name": sdir.name,
                        "original_path": rel,
                        "backup_path": str(rel_bkp.relative_to(home)),
                        "status": "BACKED_UP_FOR_MERGE",
                        "integration_strategy": (
                            f"Pre-existing customized skill `{sdir.name}` backed up before v1.4.0 update. "
                            "Port custom workflows into `references/` or a companion custom skill."
                        ),
                    })

    # 3. Pre-existing Subagents (.gemini/config/agents/*, .claude/agents/*.md)
    for aroot_rel in (".gemini/config/agents", ".gemini/agents", ".claude/agents"):
        aroot = home / aroot_rel
        if not aroot.is_dir():
            continue
        for entry in sorted(aroot.iterdir()):
            stem = entry.stem if entry.is_file() else entry.name
            if stem not in MANAGED_AGENTS:
                rel = str(entry.relative_to(home))
                rel_bkp = files_backup_root / rel
                rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                if entry.is_dir() and not rel_bkp.exists():
                    shutil.copytree(entry, rel_bkp)
                elif entry.is_file() and not rel_bkp.is_file():
                    shutil.copy2(entry, rel_bkp)
                _record({
                    "category": "subagent",
                    "name": stem,
                    "original_path": rel,
                    "backup_path": str(rel_bkp.relative_to(home)),
                    "status": "AUTO_COEXISTING",
                    "integration_strategy": (
                        f"Custom subagent `{stem}` is preserved in `{aroot_rel}` and remains directly "
                        "invokable via `invoke_subagent` alongside the 5 suite subagents."
                    ),
                })

    # 4. Pre-existing Lifecycle Hooks (.gemini/config/hooks.json)
    hooks_file = home / ".gemini" / "config" / "hooks.json"
    if hooks_file.is_file():
        try:
            hdata = json.loads(hooks_file.read_text(encoding="utf-8"))
            if isinstance(hdata, dict):
                custom_hook_keys = [k for k in hdata.keys() if k not in MANAGED_HOOK_KEYS]
                if custom_hook_keys:
                    rel_bkp = files_backup_root / ".gemini/config/hooks.json"
                    rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                    if not rel_bkp.is_file():
                        shutil.copy2(hooks_file, rel_bkp)
                    for hk in custom_hook_keys:
                        _record({
                            "category": "hook",
                            "name": hk,
                            "original_path": ".gemini/config/hooks.json",
                            "backup_path": str(rel_bkp.relative_to(home)),
                            "status": "BACKED_UP_FOR_MERGE",
                            "integration_strategy": (
                                f"Custom hook `{hk}` backed up. Run `python3 src/hooks/lazy_plugin_bootstrap.py "
                                f"--merge-legacy` to merge `{hk}` into `~/.gemini/config/hooks.json` alongside "
                                "the 3 suite lifecycle hooks."
                            ),
                        })
        except Exception:
            pass

    # 5. Pre-existing MCP Servers (.gemini/config/mcp_config.json, .cursor/mcp.json)
    for mcp_rel in (".gemini/config/mcp_config.json", ".cursor/mcp.json"):
        mfile = home / mcp_rel
        if not mfile.is_file():
            continue
        try:
            mdata = json.loads(mfile.read_text(encoding="utf-8"))
            servers = (mdata.get("mcpServers") or {}) if isinstance(mdata, dict) else {}
            custom_mcps = [k for k in servers.keys() if k not in MANAGED_MCP_KEYS]
            if custom_mcps:
                rel_bkp = files_backup_root / mcp_rel
                rel_bkp.parent.mkdir(parents=True, exist_ok=True)
                if not rel_bkp.is_file():
                    shutil.copy2(mfile, rel_bkp)
                for mk in custom_mcps:
                    _record({
                        "category": "mcp_server",
                        "name": mk,
                        "original_path": mcp_rel,
                        "backup_path": str(rel_bkp.relative_to(home)),
                        "status": "BACKED_UP_FOR_MERGE",
                        "integration_strategy": (
                            f"Custom MCP server `{mk}` backed up from `{mcp_rel}`. Run "
                            "`python3 src/hooks/lazy_plugin_bootstrap.py --merge-legacy` to merge "
                            f"`{mk}` into `mcp_config.json` alongside the 7 eager suite MCP servers."
                        ),
                    })
        except Exception:
            pass

    items_list = list(existing_items_by_key.values())
    auto_count = sum(1 for x in items_list if x.get("status") == "AUTO_COEXISTING")
    merge_count = sum(1 for x in items_list if x.get("status") == "BACKED_UP_FOR_MERGE")

    review_payload = {
        "version": _read_plugin_version(REPO_ROOT),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "backup_root": str(backup_dir),
        "discovered_count": len(items_list),
        "auto_coexisting_count": auto_count,
        "backed_up_for_merge_count": merge_count,
        "merge_command": f"python3 {REPO_ROOT}/src/hooks/lazy_plugin_bootstrap.py --merge-legacy --home {home}",
        "discovered_items": items_list,
    }
    paths["review_json"].write_text(json.dumps(review_payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Pre-Existing Customizations Backup & Integration Review (`v1.4.0`)",
        "",
        f"- **Backup Directory**: `{backup_dir}`",
        f"- **Total Pre-Existing Customizations Detected**: `{len(items_list)}` (`{auto_count}` Auto-Coexisting, `{merge_count}` Backed Up for Merge)",
        f"- **One-Command Non-Destructive Merge**: `python3 {REPO_ROOT}/src/hooks/lazy_plugin_bootstrap.py --merge-legacy --home {home}`",
        "",
        "| Target | Behavior & Outcome | Status |",
        "| :--- | :--- | :--- |",
    ]
    if not items_list:
        md_lines.append("| Clean Vanilla Environment | Zero pre-existing customizations detected prior to v1.4.0 install | ✅ |")
    else:
        for it in items_list:
            md_lines.append(
                f"| `{it['name']}` (`{it['category']}`) | Backed up to `{it['backup_path']}`; {it['integration_strategy']} | "
                f"{'✅ Coexisting' if it['status'] == 'AUTO_COEXISTING' else '🔄 Ready to Merge'} |"
            )
    paths["review_md"].write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return review_payload


def merge_legacy_customizations(home_dir: str) -> dict:
    """
    Non-destructively integrates backed-up user customizations alongside the deployed v1.4.0 suite:
    1. Consolidates backed-up colliding rules into ~/.gemini/config/rules/legacy-user-customizations.md.
    2. Merges non-colliding custom top-level hook keys from backed-up hooks.json into live hooks.json.
    3. Merges non-colliding custom mcpServers from backed-up mcp_config.json / .cursor/mcp.json into live configs.
    """
    paths = _resolve_paths(home_dir)
    home = paths["home"]
    backup_dir = paths["backup_dir"]
    files_backup_root = backup_dir / "files"
    merged_summary = {"merged_rules": [], "merged_hooks": [], "merged_mcp_servers": []}

    # 1. Consolidate backed-up colliding rules into ~/.gemini/config/rules/legacy-user-customizations.md
    rule_sections = []
    for rname in MANAGED_RULES:
        bkp_rule = backup_dir / rname
        if bkp_rule.is_file() and _sha256_file(bkp_rule) != _sha256_file(REPO_ROOT / "rules" / rname):
            content = bkp_rule.read_text(encoding="utf-8").strip()
            if content:
                rule_sections.append(f"## Backed-Up User Rule: `{rname}`\n\n{content}")
                merged_summary["merged_rules"].append(rname)
    if rule_sections:
        target_custom_rule = home / ".gemini" / "config" / "rules" / "legacy-user-customizations.md"
        target_custom_rule.parent.mkdir(parents=True, exist_ok=True)
        header = "# Integrated User Custom Rules (Preserved Alongside Antigravity v1.4.0)\n\n"
        target_custom_rule.write_text(header + "\n\n---\n\n".join(rule_sections) + "\n", encoding="utf-8")

    # 2. Merge custom top-level hooks into ~/.gemini/config/hooks.json & ~/.gemini/antigravity/hooks.json
    bkp_hooks = files_backup_root / ".gemini/config/hooks.json"
    if bkp_hooks.is_file():
        try:
            old_h = json.loads(bkp_hooks.read_text(encoding="utf-8"))
            if isinstance(old_h, dict):
                for dest_h in (home / ".gemini/config/hooks.json", home / ".gemini/antigravity/hooks.json"):
                    if dest_h.is_file():
                        cur_h = json.loads(dest_h.read_text(encoding="utf-8"))
                        for k, v in old_h.items():
                            if k not in MANAGED_HOOK_KEYS and k != "hooks" and isinstance(v, dict):
                                cur_h[k] = v
                                if k not in merged_summary["merged_hooks"]:
                                    merged_summary["merged_hooks"].append(k)
                        dest_h.write_text(json.dumps(cur_h, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    # 3. Merge custom mcpServers into ~/.gemini/config/mcp_config.json, ~/.gemini/antigravity/mcp_config.json, & ~/.cursor/mcp.json
    for mcp_rel, live_targets in (
        (".gemini/config/mcp_config.json", [home / ".gemini/config/mcp_config.json", home / ".gemini/antigravity/mcp_config.json"]),
        (".cursor/mcp.json", [home / ".cursor/mcp.json"]),
    ):
        bkp_m = files_backup_root / mcp_rel
        if not bkp_m.is_file():
            continue
        try:
            old_m = json.loads(bkp_m.read_text(encoding="utf-8"))
            old_servers = (old_m.get("mcpServers") or {}) if isinstance(old_m, dict) else {}
            for dest_m in live_targets:
                if dest_m.is_file():
                    cur_m = json.loads(dest_m.read_text(encoding="utf-8"))
                    cur_servers = cur_m.setdefault("mcpServers", {})
                    for sk, sv in old_servers.items():
                        if sk not in MANAGED_MCP_KEYS:
                            cur_servers[sk] = sv
                            if sk not in merged_summary["merged_mcp_servers"]:
                                merged_summary["merged_mcp_servers"].append(sk)
                    dest_m.write_text(json.dumps(cur_m, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    if paths["review_json"].is_file():
        try:
            rev = json.loads(paths["review_json"].read_text(encoding="utf-8"))
            for it in rev.get("discovered_items", []):
                if it.get("status") == "BACKED_UP_FOR_MERGE":
                    it["status"] = "INTEGRATED_ALONGSIDE_SUITE"
            rev["merged_summary"] = merged_summary
            paths["review_json"].write_text(json.dumps(rev, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    return {"status": "merged", "home": str(home), **merged_summary}


def _is_managed_sidecar_project_name(pname: str) -> bool:
    if not pname:
        return False
    if pname in MANAGED_SIDECARS or pname == "swarm/swarm_board":
        return True
    if any(pname.startswith(pfx) for pfx in MANAGED_PLUGIN_PREFIXES):
        return True
    bare = pname.split("/", 1)[1] if "/" in pname else pname
    return bare in MANAGED_SIDECARS


def _has_unbound_sidecar_projects(paths: dict) -> bool:
    cfg_file = paths["config_json"]
    if not cfg_file.is_file():
        return True
    try:
        cfg_data = json.loads(cfg_file.read_text(encoding="utf-8")) or {}
        sc_map = cfg_data.get("sidecars") or {}
        for sc_id in MANAGED_SIDECARS:
            for key_id in (
                sc_id,
                f"antigravity-customizations/{sc_id}",
                f"agy-knowledge-graph/{sc_id}",
            ):
                entry = sc_map.get(key_id)
                if not isinstance(entry, dict) or entry.get("projectId") != "automations" or entry.get("schemaVersion") != 1:
                    return True
    except Exception:
        return True
    proj_dir = paths["projects_dir"]
    if proj_dir.is_dir():
        for pfile in proj_dir.glob("*.json"):
            if pfile.name == "automations.json":
                continue
            try:
                pdata = json.loads(pfile.read_text(encoding="utf-8")) or {}
                pname = str(pdata.get("name") or "").strip()
                if _is_managed_sidecar_project_name(pname):
                    return True
            except Exception:
                continue
    return False


def _bind_sidecars_and_prune_projects(paths: dict) -> int:
    cfg_file = paths["config_json"]
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    cfg_data = {}
    if cfg_file.is_file():
        try:
            loaded = json.loads(cfg_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                cfg_data = loaded
        except Exception:
            cfg_data = {}
    sc_map = cfg_data.setdefault("sidecars", {})
    for sc_id in MANAGED_SIDECARS:
        for key_id in (
            sc_id,
            f"antigravity-customizations/{sc_id}",
            f"agy-knowledge-graph/{sc_id}",
        ):
            cur = sc_map.get(key_id)
            if not isinstance(cur, dict):
                sc_map[key_id] = {"enabled": True, "projectId": "automations", "schemaVersion": 1}
            else:
                cur.setdefault("enabled", True)
                cur["projectId"] = "automations"
                cur["schemaVersion"] = 1
                cur.pop("allProjects", None)
    for existing_k, existing_v in list(sc_map.items()):
        if isinstance(existing_v, dict) and _is_managed_sidecar_project_name(existing_k):
            existing_v["projectId"] = "automations"
            existing_v["schemaVersion"] = 1
            existing_v.pop("allProjects", None)
    cfg_file.write_text(json.dumps(cfg_data, indent=2) + "\n", encoding="utf-8")

    # Prune any orphaned auto-spawned <plugin>/<sidecar> UUID projects and migrate conversations
    proj_dir = paths["projects_dir"]
    auto_file = paths["automations_proj"]
    pruned = 0
    if not proj_dir.is_dir():
        return 0
    auto_data = {}
    if auto_file.is_file():
        try:
            auto_data = json.loads(auto_file.read_text(encoding="utf-8")) or {}
        except Exception:
            auto_data = {}
    raw_pc = auto_data.get("projectConversations")
    convs = list(raw_pc.get("conversations", []) if isinstance(raw_pc, dict) else (raw_pc if isinstance(raw_pc, list) else []))
    seen_cids = {c.get("conversationId") for c in convs if isinstance(c, dict) and c.get("conversationId")}
    convs_changed = False
    for pfile in sorted(proj_dir.glob("*.json")):
        if pfile.name == "automations.json":
            continue
        try:
            pdata = json.loads(pfile.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        pname = str(pdata.get("name") or "").strip()
        pid = str(pdata.get("id") or "").strip()
        if pid != "automations" and _is_managed_sidecar_project_name(pname):
            p_pc = pdata.get("projectConversations")
            p_convs = p_pc.get("conversations", []) if isinstance(p_pc, dict) else (p_pc if isinstance(p_pc, list) else [])
            for c in p_convs:
                if isinstance(c, dict) and c.get("conversationId") and c["conversationId"] not in seen_cids:
                    convs.append(c)
                    seen_cids.add(c["conversationId"])
                    convs_changed = True
            try:
                pfile.unlink()
                pruned += 1
            except OSError:
                pass
    if convs_changed and auto_data:
        auto_data["projectConversations"] = {"conversations": convs}
        auto_file.write_text(json.dumps(auto_data, indent=2) + "\n", encoding="utf-8")
    return pruned


def reconcile_host_environment(home_dir: str, force: bool = False) -> dict:
    """Executes idempotent Turn-1 / version-bump host reconciliation."""
    t0 = time.monotonic()
    version = _read_plugin_version(REPO_ROOT)
    paths = _resolve_paths(home_dir)

    if (
        not force
        and paths["stamp"].is_file()
        and paths["warm_cache"].is_file()
        and paths["automations_proj"].is_file()
        and not _has_unbound_sidecar_projects(paths)
    ):
        stamp_data = json.loads(paths["stamp"].read_text(encoding="utf-8"))
        if stamp_data.get("version") == version:
            return {
                "decision": "allow",
                "status": "fast_path_cached",
                "version": version,
                "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 3),
            }

    paths["plugin_data"].mkdir(parents=True, exist_ok=True)
    paths["kg_json"].parent.mkdir(parents=True, exist_ok=True)
    paths["warm_cache"].parent.mkdir(parents=True, exist_ok=True)
    paths["automations_proj"].parent.mkdir(parents=True, exist_ok=True)

    # 1. Seed Bitemporal Knowledge Graph from resources/knowledge_graph.seed.json
    seed_path = REPO_ROOT / "resources" / "knowledge_graph.seed.json"
    if seed_path.is_file() and not paths["kg_json"].is_file():
        shutil.copyfile(seed_path, paths["kg_json"])
    if paths["kg_json"].is_file():
        shutil.copyfile(paths["kg_json"], paths["warm_cache"])
    elif seed_path.is_file():
        shutil.copyfile(seed_path, paths["warm_cache"])

    # 2. Audit and back up pre-existing user customizations into legacy_standalone_backup/ (R1)
    review_summary = backup_and_audit_existing_customizations(home_dir)
    backed_up = [
        it["name"]
        for it in review_summary.get("discovered_items", [])
        if it.get("category") == "rule"
    ]

    # 3. Provision single 'automations' workspace project (R5) and bind all plugin sidecars in config.json
    if not paths["automations_proj"].is_file():
        auto_payload = {
            "id": "automations",
            "name": "Automations",
            "displayName": "Automations",
            "projectConversations": {"conversations": []},
        }
        paths["automations_proj"].write_text(json.dumps(auto_payload, indent=2) + "\n", encoding="utf-8")
    pruned_projects = _bind_sidecars_and_prune_projects(paths)

    # 4. Write version stamp
    stamp_payload = {
        "version": version,
        "bootstrapped_at": time.time(),
        "backed_up_rules": backed_up,
        "discovered_legacy_customizations": review_summary.get("discovered_count", 0),
        "review_manifest_path": str(paths["review_json"]),
        "pruned_sidecar_projects": pruned_projects,
    }
    paths["stamp"].write_text(json.dumps(stamp_payload, indent=2) + "\n", encoding="utf-8")

    return {
        "decision": "allow",
        "status": "bootstrapped",
        "version": version,
        "kg_seeded": paths["warm_cache"].is_file(),
        "automations_project": paths["automations_proj"].is_file(),
        "discovered_legacy_customizations": review_summary.get("discovered_count", 0),
        "review_manifest_path": str(paths["review_json"]),
        "pruned_sidecar_projects": pruned_projects,
        "nondev_sandbox_host": is_sandbox_or_bundled_nondev_host(home_dir),
        "skills_root": str(resolve_multi_path_skills_root(home_dir)),
        "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lazy Plugin Bootstrap Reconciler")
    parser.add_argument("--full-host-reconcile", action="store_true", help="Force full reconciliation")
    parser.add_argument("--backup-existing", action="store_true", help="Pre-install backup and audit of existing customizations")
    parser.add_argument("--merge-legacy", action="store_true", help="Non-destructively merge backed-up rules, hooks, and MCP servers")
    parser.add_argument("--home", default=os.path.expanduser("~"), help="Target HOME directory")
    parser.add_argument("--self-test", action="store_true", help="Run hermetic self-test in temp dir")
    args = parser.parse_args()

    if args.self_test:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            r1 = reconcile_host_environment(tmp, force=True)
            r2 = reconcile_host_environment(tmp, force=False)
            ok = r1["status"] == "bootstrapped" and r2["status"] == "fast_path_cached" and r1["kg_seeded"]
            print(json.dumps({"verdict": "PASS" if ok else "FAIL", "cold": r1, "warm": r2}))
            return 0 if ok else 1

    if args.backup_existing:
        print(json.dumps(backup_and_audit_existing_customizations(args.home)))
        return 0

    if args.merge_legacy:
        print(json.dumps(merge_legacy_customizations(args.home)))
        return 0

    res = reconcile_host_environment(args.home, force=args.full_host_reconcile)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
