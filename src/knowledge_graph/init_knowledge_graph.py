#!/usr/bin/env python3
"""
Role: Knowledge Graph Memory Initializer for Antigravity Customizations & Web Hub (v1.4.0 / v3.8.0).
Purpose: Bootstraps initial long-term memory graph schema, seeds foundational reference documentation
  entities and core architectural nodes, compiles OKF v0.2 kb/ dossiers, and warms the shared-memory
  caches (/dev/shm/kg_warm_cache.json and /dev/shm/agw_kg_warm_cache.json).
How It Is Used: Invoked by scripts/install.sh, start_hub.sh, and scripts/run_ab_benchmark.py.
"""

import os
import sys
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DEFAULT_KB_ROOT = os.path.join(REPO_ROOT, "kb")

DEFAULT_OUTPUT_PATH = os.path.expanduser(os.environ.get("KG_JSON_PATH", "/mnt/data/knowledge_graph.json"))
FALLBACK_OUTPUT_PATH = os.path.expanduser("~/.gemini/antigravity/knowledge_graph.json")
WARM_CACHE_PATH = os.environ.get("KG_WARM_CACHE_PATH", "/dev/shm/kg_warm_cache.json")
AGW_WARM_CACHE_PATH = "/dev/shm/agw_kg_warm_cache.json"

CORE_ENTITIES = [
    ("doc:antigravity_web_hub", "Antigravity Web Hub v3.8.0 Self-Documentation", "documentation", "4-plane runtime architecture: Nginx reverse proxy (:8080 + bootstrap.js), headless Go language_server v2.24.0 (:8081), 8-Model Vertex AI ADC router (:8083), and FastMCP servers (:8084)."),
    ("doc:antigravity_cli_sdk", "Antigravity CLI v1.4.0 & Python SDK (google-antigravity)", "documentation", "Companion CLI (/usr/local/bin/antigravity v1.4.0) and programmatic Python SDK (google-antigravity LocalAgentConfig().eval(), ATIF-v1.7 trajectories, hooks.json lifecycle contract)."),
    ("doc:google_adk", "Google Agent Development Kit (ADK / google-adk) & A2A Protocol", "documentation", "Open-source Python agent framework (pip install google-adk): LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, FunctionTool, McpToolset, Runner, and Agent2Agent (A2A) JSON-RPC protocol."),
    ("doc:agents_cli", "Google Agents CLI (agents-cli / google-agents-cli)", "documentation", "Developer CLI for scaffolding, inspecting, and running ADK agent projects (`uv tool install google-agents-cli`)."),
    ("doc:gemini_vertex_models", "Gemini & Vertex AI Model Catalog & API Parameter Contracts", "documentation", "8-Model GA catalog (Gemini 4 Argon enum 354, Gemini 3.8/3.7/3.6/3.5 Flash enums 352/350/348/330, Claude Opus/Sonnet 5.5 enums 290/333, Claude Fable 5 enum 340)."),
    ("doc:autonomy_hooks_and_skills", "14-Pillar Clean-Room Autonomy Engine, 3 Hooks & 21 PD-Q Skills", "documentation", "Three deterministic hooks (PreInvocation kg_pre_invocation_hook.py, PreToolUse sentinel_dispatch.py, Stop agent_stop_black_hat_gate.py), 21 PD-Q skills, and 5 subagents."),
    ("okf:google-adk-and-a2a-protocol", "Google ADK & A2A Protocol OKF Dossier", "okf_dossier", "Verified Open Knowledge Format v0.2 reference dossier covering Google ADK multi-agent orchestration and A2A JSON-RPC message framing."),
    ("okf:antigravity-hub", "Antigravity Web Hub Architecture OKF Dossier", "okf_dossier", "Verified Open Knowledge Format v0.2 architecture dossier for Antigravity Web Hub and Dark Factory custom harness."),
    ("okf:autonomy-lifecycle", "Autonomy Engine & Nightly Dreaming OKF Dossier", "okf_dossier", "Verified Open Knowledge Format v0.2 guide covering the 4-Pillar Dark Factory lifecycle, P0/P1 circuit breakers, and Nightly Dreaming consolidation."),
    ("infra:n4_compute_vm", "Google Cloud N4 VM", "infrastructure", "5th Gen Intel Xeon Emerald Rapids compute engine hosting Antigravity Web Hub."),
    ("infra:hyperdisk_balanced", "Hyperdisk Balanced", "infrastructure", "High-performance block storage backend attached to N4 compute instance."),
    ("infra:classic_https_lb", "GCP Classic HTTPS Load Balancer", "infrastructure", "Public ingress load balancer terminating SSL and enforcing IAP zero-trust authentication."),
    ("model:gemini_4_argon", "Gemini 4 Argon", "model", "Flagship 1M-context GA reasoning model (proto enum 354 -> gemini-4-argon) served via Vertex AI."),
    ("model:gemini_3_8_flash", "Gemini 3.8 Flash", "model", "Recommended default production multimodal reasoning, agentic coding, and tool-dispatch model on Vertex AI (proto enum 352)."),
    ("model:gemini_3_6_flash", "Gemini 3.6 Flash", "model", "Ultra-fast default reasoning model served via Vertex AI streaming SSE (proto enum 348)."),
    ("model:gemini_3_5_flash_lite", "Gemini 3.5 Flash Lite", "model", "High-throughput lightweight reasoning model for instant inline completions (proto enum 330)."),
    ("model:gemini_3_5_flash", "Gemini 3.5 Flash", "model", "Low-latency reasoning model served via Vertex AI streaming SSE."),
    ("model:gemini_3_1_pro", "Gemini 3.1 Pro", "model", "Deep reasoning model for multi-stage research and complex architectural analysis."),
    ("mcp:autonomy_engine", "14-Pillar Autonomy Engine FastMCP Server", "mcp_server", "FastMCP server exposing P0/P1 circuit-breakers, 6-field BM25F + Graph-RAG polyphonic retrieval, Bayesian Self-Grill, and Six Thinking Hats Delphi routing."),
    ("mcp:knowledge_graph", "Knowledge Graph Long-Term Memory", "mcp_server", "FastMCP memory engine providing 0ms shared-memory reads and graph context injection."),
    ("mcp:deep_research", "On-Demand Deep Research", "mcp_server", "FastMCP server executing multi-agent research loops over internal and external docs."),
    ("mcp:google_workspace", "Google Workspace MCP", "mcp_server", "Native Node.js MCP server connecting Drive, Docs, Sheets, and Gmail.")
]

CORE_EDGES = [
    ("doc:antigravity_web_hub", "doc:antigravity_cli_sdk", "DOCUMENTS_RUNTIME", 1.0),
    ("doc:antigravity_web_hub", "doc:gemini_vertex_models", "ROUTES_MODELS", 1.0),
    ("doc:antigravity_web_hub", "doc:autonomy_hooks_and_skills", "ENFORCES_GOVERNANCE", 1.0),
    ("doc:antigravity_web_hub", "mcp:knowledge_graph", "HOSTS_MCP_SERVER", 1.0),
    ("doc:antigravity_web_hub", "mcp:autonomy_engine", "HOSTS_MCP_SERVER", 1.0),
    ("doc:google_adk", "doc:agents_cli", "SCAFFOLDED_BY", 1.0),
    ("doc:google_adk", "okf:google-adk-and-a2a-protocol", "DOCUMENTED_IN_OKF", 1.0),
    ("infra:n4_compute_vm", "infra:hyperdisk_balanced", "attaches_storage", 1.0),
    ("infra:classic_https_lb", "infra:n4_compute_vm", "routes_traffic_to", 1.0),
    ("infra:n4_compute_vm", "model:gemini_3_8_flash", "streams_inference_from", 1.0),
    ("infra:n4_compute_vm", "model:gemini_3_6_flash", "streams_inference_from", 1.0),
    ("infra:n4_compute_vm", "model:gemini_3_5_flash_lite", "streams_inference_from", 1.0),
    ("infra:n4_compute_vm", "mcp:knowledge_graph", "executes_module", 1.0),
    ("infra:n4_compute_vm", "mcp:deep_research", "executes_module", 1.0),
    ("infra:n4_compute_vm", "mcp:google_workspace", "executes_module", 1.0)
]


def init_knowledge_graph(target_path=None, force=False, seed_demo=True, warm_cache_path=None, empty=False, kb_root=None):
    if not target_path:
        target_path = DEFAULT_OUTPUT_PATH if os.path.exists(os.path.dirname(DEFAULT_OUTPUT_PATH)) else FALLBACK_OUTPUT_PATH

    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    if os.path.exists(target_path) and not force:
        print(f"[KG] Knowledge graph already exists at {target_path}. Skipping initialization.")
        return target_path

    force_empty = bool(empty or os.environ.get("AGW_EMPTY_KG") == "1" or (seed_demo is False))
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    nodes = []
    edges = []
    if not force_empty:
        for nid, label, ntype, desc in CORE_ENTITIES:
            nodes.append({
                "id": nid,
                "label": label,
                "type": ntype,
                "description": desc,
                "aliases": [label.lower(), nid.split(":")[-1].replace("_", " ")],
                "properties": {"created_by": "bootstrap", "confidence": 1.0, "base_confidence": 1.0},
                "updated_at": now_iso,
            })

        for src, dst, rel, w in CORE_EDGES:
            edges.append({
                "source": src,
                "target": dst,
                "relation": rel,
                "weight": w,
            })

    payload = {
        "version": "2.0-OKF-v0.2",
        "initialized_at": now_iso,
        "nodes": nodes,
        "edges": edges,
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
    if not force_empty and os.path.isdir(active_kb):
        try:
            from src.knowledge_graph.okf_knowledge_compiler import sync_kb_to_graph
            sync_kb_to_graph(kb_root=active_kb, graph_path=target_path)
            with open(target_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception:
            pass

    print(
        f"[KG] Successfully initialized Knowledge Graph at {target_path} "
        f"({len(payload.get('nodes', []))} nodes, {len(payload.get('edges', []))} edges)."
    )

    # Warm shared memory caches (/dev/shm/kg_warm_cache.json and /dev/shm/agw_kg_warm_cache.json)
    cache_targets = [warm_cache_path] if warm_cache_path else [WARM_CACHE_PATH, AGW_WARM_CACHE_PATH]
    for cache_dest in cache_targets:
        if not cache_dest:
            continue
        try:
            cache_dir = os.path.dirname(os.path.abspath(cache_dest))
            if os.path.exists(cache_dir) and os.access(cache_dir, os.W_OK):
                with open(cache_dest, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
                print(f"[KG] Shared-memory cache pre-warmed at {cache_dest}.")
        except Exception as e:
            print(f"[KG] Warning: could not write /dev/shm cache: {e}")

    return target_path


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    empty_flag = "--empty" in sys.argv
    init_knowledge_graph(force=force_flag, seed_demo=not empty_flag, empty=empty_flag)
