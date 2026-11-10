#!/usr/bin/env python3
"""
Role: Empty Skeleton Initializer for the Bitemporal Knowledge Graph (`init_knowledge_graph.py` v1.5.0).
Purpose: Bootstraps an empty long-term Knowledge Graph schema skeleton (`0` pre-loaded nodes, `0` pre-loaded
  entities, `0` pre-loaded edges) at `~/.gemini/antigravity/knowledge_graph.json` (or `KG_JSON_PATH`) and
  pre-warms the shared-memory serving caches (`/dev/shm/agw_kg_warm_cache.json` and `/dev/shm/kg_warm_cache.json`)
  without injecting any pre-loaded domain or documentation entities. Optionally synchronizes user-created
  Open Knowledge Format (`OKF v0.2`) dossiers from `kb/` only when `--sync-kb` (`sync_kb=True`) is explicitly passed.
How It Is Used: Invoked by `scripts/install.sh`, `scripts/run_ab_benchmark.py`, and MCP/hook bootstrap.
"""

import json
import os
import sys
import time

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_KB_ROOT = os.path.join(REPO_ROOT, "kb")

DEFAULT_OUTPUT_PATH = os.path.expanduser(os.environ.get("KG_JSON_PATH", "/mnt/data/knowledge_graph.json"))
FALLBACK_OUTPUT_PATH = os.path.expanduser("~/.gemini/antigravity/knowledge_graph.json")
WARM_CACHE_PATH = os.environ.get("KG_WARM_CACHE_PATH", "/dev/shm/agw_kg_warm_cache.json")
LEGACY_WARM_CACHE_PATH = "/dev/shm/kg_warm_cache.json"

# Zero pre-loaded entities or edges: the suite ships strictly an empty Knowledge Graph skeleton.
FOUNDATIONAL_ENTITIES = []
CORE_ENTITIES = FOUNDATIONAL_ENTITIES
FOUNDATIONAL_EDGES = []
CORE_EDGES = FOUNDATIONAL_EDGES


def init_knowledge_graph(
    target_path=None,
    force=False,
    seed_demo=False,
    warm_cache_path=None,
    empty=True,
    kb_root=None,
    sync_kb=False,
):
    """Initializes an empty Bitemporal Knowledge Graph skeleton (`0` nodes, `0` edges) and warms shared-memory caches."""
    if not target_path:
        target_path = DEFAULT_OUTPUT_PATH if os.path.exists(os.path.dirname(DEFAULT_OUTPUT_PATH)) else FALLBACK_OUTPUT_PATH

    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    if os.path.exists(target_path) and not force:
        print(f"[KG] Knowledge graph already exists at {target_path}. Skipping initialization.")
        return target_path

    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = {
        "version": "2.1-OKF-v0.2",
        "initialized_at": now_iso,
        "metadata": {
            "schema_version": "okf-v0.2",
            "package_version": "1.5.0",
            "description": "Empty Bitemporal Knowledge Graph skeleton for the Antigravity Customizations Suite.",
        },
        "nodes": [],
        "entities": {},
        "edges": [],
    }

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except PermissionError:
        target_path = FALLBACK_OUTPUT_PATH
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    active_kb = kb_root or DEFAULT_KB_ROOT
    if sync_kb and not empty and os.path.isdir(active_kb):
        try:
            from src.knowledge_graph.okf_knowledge_compiler import sync_kb_to_graph
        except ImportError:
            try:
                from knowledge_graph.okf_knowledge_compiler import sync_kb_to_graph
            except ImportError:
                sync_kb_to_graph = None
        if sync_kb_to_graph is not None:
            try:
                sync_kb_to_graph(kb_root=active_kb, graph_path=target_path, cache_path=warm_cache_path)
            except Exception:
                pass
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except Exception:
                pass

    print(
        f"[KG] Initialized empty Knowledge Graph skeleton at {target_path} "
        f"({len(payload.get('nodes', []))} nodes, {len(payload.get('edges', []))} edges)."
    )

    cache_targets = [warm_cache_path] if warm_cache_path else [WARM_CACHE_PATH, LEGACY_WARM_CACHE_PATH]
    seen_caches = set()
    for cache_dest in cache_targets:
        if not cache_dest or cache_dest in seen_caches:
            continue
        seen_caches.add(cache_dest)
        try:
            cache_dir = os.path.dirname(os.path.abspath(cache_dest))
            if os.path.exists(cache_dir) and os.access(cache_dir, os.W_OK):
                with open(cache_dest, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
                print(f"[KG] Shared-memory cache pre-warmed at {cache_dest}.")
        except Exception as e:
            print(f"[KG] Warning: could not write shared-memory cache: {e}")

    return target_path


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    sync_kb_flag = "--sync-kb" in sys.argv
    init_knowledge_graph(
        force=force_flag,
        seed_demo=False,
        empty=not sync_kb_flag,
        sync_kb=sync_kb_flag,
    )
