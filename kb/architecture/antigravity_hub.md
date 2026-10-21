---
okf_version: "0.2"
id: antigravity-web-hub-architecture
title: "Antigravity Customizations Architecture & Multi-Model Routing"
summary: "Clean-room enterprise customization architecture with 7-model Vertex AI routing, FastMCP servers, and SQLite-WAL persistence."
type: architecture
status: verified
confidence: 0.99
last_verified: "2026-09-30"
tags: [antigravity, vertex-ai, fastmcp, nginx, iap, architecture]
aliases: [antigravity-customizations, multi-model-router, language-server]
related_concepts: [autonomy-lifecycle-governance]
sources:
  - id: src-model-router
    type: code_repo
    title: "src/autonomy_engine/unified_eval_router.py — Allowlisted Multi-Model Tier Catalog"
    URI: "src/autonomy_engine/unified_eval_router.py"
    fetched_at: "2026-09-30"
---

# Antigravity Customizations Architecture & Multi-Model Routing

## Summary

Antigravity Customizations configures standalone AI coding harnesses (`agy`, `claude`, Cursor, Windsurf) with multi-model Vertex AI routing, FastMCP STDIO servers, and Bitemporal Knowledge Graph persistence [^src-model-router].

## Core Facts & Allowlisted Model Catalog

* **Default Serving Model**: `Gemini 3.8 Flash` (`gemini-3.8-flash`) [^src-model-router].
* **High-Throughput Tier**: `Gemini 3.5 Flash Lite` (`gemini-3.5-flash-lite`) [^src-model-router].
* **Deep Reasoning Partner Tier**: `Claude Opus 5 (Vertex AI)` (`claude-opus-5`) and `Claude Sonnet 5 (Vertex AI)` (`claude-sonnet-5`) [^src-model-router].
* **FastMCP STDIO Servers**: `knowledge_graph`, `autonomy_engine`, `deep_research`, and `google_workspace` [^src-model-router].

[^src-model-router]: Verified in `src/autonomy_engine/unified_eval_router.py` and `scripts/install.sh` (`v1.4.0`).
