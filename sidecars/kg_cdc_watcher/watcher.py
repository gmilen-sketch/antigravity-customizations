#!/usr/bin/env python3
"""
Clean-Room Streaming CDC File Event Watcher Sidecar Daemon (`kg_cdc_watcher`).
Monitors workspace and skill file modifications and appends structured
change-data-capture events to the Bitemporal Knowledge Graph event stream.
"""

import argparse
import json
import os
import pathlib
import sys
import time

sys.dont_write_bytecode = True

SIDECAR_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = SIDECAR_DIR.parent.parent

IGNORED_DIRS = {
    "node_modules", "venv", ".venv", "env", "__pycache__",
    "cache", "brain", "site-packages", "dist", "build", "target", ".git"
}

IGNORED_FILES = {
    "knowledge_graph.json", "manifest.json", ".skills_state.json", "bootstrapped_version.json"
}


def scan_once(watch_dirs: list, seen_mtimes: dict, cdc_log_path: pathlib.Path) -> int:
    """Scans watch_dirs once and emits CDC events for modified files."""
    events_emitted = 0
    for wdir in watch_dirs:
        if not os.path.exists(wdir):
            continue
        for root, dirs, files in os.walk(wdir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORED_DIRS]
            for fname in files:
                if fname.startswith(".") or fname in IGNORED_FILES:
                    continue
                if not fname.endswith((".py", ".json", ".md", ".sh")):
                    continue
                fpath = os.path.join(root, fname)
                if not os.path.isfile(fpath):
                    continue
                mtime = os.path.getmtime(fpath)
                if fpath in seen_mtimes and mtime > seen_mtimes[fpath]:
                    seen_mtimes[fpath] = mtime
                    slug = fpath.replace("/", "_").replace(".", "_")[-40:]
                    edge_payload = {
                        "source": f"file:{slug}",
                        "target": "proj:antigravity_workspace",
                        "relation": "MODIFIED_IN_SESSION",
                        "description": f"Real-time CDC detected edit to {fname}",
                        "timestamp": time.time(),
                    }
                    cdc_log_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(cdc_log_path, "a", encoding="utf-8") as cf:
                        cf.write(json.dumps(edge_payload) + "\n")
                    events_emitted += 1
                else:
                    seen_mtimes[fpath] = mtime
    return events_emitted


def main() -> int:
    parser = argparse.ArgumentParser(description="Knowledge Graph CDC Watcher Sidecar")
    parser.add_argument("--self-test", action="store_true", help="Run hermetic self-test and exit")
    args = parser.parse_args()

    if args.self_test:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tfile = pathlib.Path(tmp) / "sample.py"
            cdc_log = pathlib.Path(tmp) / "kg_cdc_events.jsonl"
            tfile.write_text("x = 1\n", encoding="utf-8")
            seen = {}
            scan_once([tmp], seen, cdc_log)
            seen[str(tfile)] -= 5.0
            count = scan_once([tmp], seen, cdc_log)
            print(json.dumps({"status": "ok", "events_emitted": count}))
            return 0 if count == 1 and cdc_log.is_file() else 1

    watch_dirs = [
        str(REPO_ROOT / "skills"),
        str(REPO_ROOT / "src"),
        os.path.expanduser("~/.gemini/config/skills"),
    ]
    cdc_log = pathlib.Path("/dev/shm/kg_cdc_events.jsonl") if os.path.isdir("/dev/shm") else (REPO_ROOT / "kg_cdc_events.jsonl")
    seen_mtimes: dict = {}
    sys.stderr.write("[kg_cdc_watcher] Running real-time CDC watcher...\n")
    while True:
        scan_once(watch_dirs, seen_mtimes, cdc_log)
        time.sleep(30)


if __name__ == "__main__":
    raise SystemExit(main())
