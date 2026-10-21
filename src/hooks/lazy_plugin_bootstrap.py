#!/usr/bin/env python3
"""
Unified Plugin + Host-Companion Reconciler (`lazy_plugin_bootstrap.py` v1.3.0)
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
        "kg_json": home / ".gemini" / "antigravity" / "knowledge_graph.json",
        "warm_cache": shm_root / "kg_warm_cache.json",
        "config_json": home / ".gemini" / "config" / "config.json",
        "projects_dir": home / ".gemini" / "config" / "projects",
        "automations_proj": home / ".gemini" / "config" / "projects" / "automations.json",
    }


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

    # 2. Deduplicate legacy standalone rules in ~/.gemini/config/rules/ (R1)
    # Only when plugin is installed inside ~/.gemini/config/plugins/antigravity-customizations
    plugin_install_dir = paths["home"] / ".gemini" / "config" / "plugins" / "antigravity-customizations"
    rules_dir = paths["home"] / ".gemini" / "config" / "rules"
    backed_up = []
    if (plugin_install_dir / "plugin.json").is_file() and rules_dir.is_dir():
        paths["backup_dir"].mkdir(parents=True, exist_ok=True)
        for rname in MANAGED_RULES:
            cand = rules_dir / rname
            if cand.is_file() and not cand.is_symlink():
                shutil.copy2(cand, paths["backup_dir"] / rname)
                backed_up.append(rname)

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
        "pruned_sidecar_projects": pruned_projects,
    }
    paths["stamp"].write_text(json.dumps(stamp_payload, indent=2) + "\n", encoding="utf-8")

    return {
        "decision": "allow",
        "status": "bootstrapped",
        "version": version,
        "kg_seeded": paths["warm_cache"].is_file(),
        "automations_project": paths["automations_proj"].is_file(),
        "pruned_sidecar_projects": pruned_projects,
        "nondev_sandbox_host": is_sandbox_or_bundled_nondev_host(home_dir),
        "skills_root": str(resolve_multi_path_skills_root(home_dir)),
        "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lazy Plugin Bootstrap Reconciler")
    parser.add_argument("--full-host-reconcile", action="store_true", help="Force full reconciliation")
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

    res = reconcile_host_environment(args.home, force=args.full_host_reconcile)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
