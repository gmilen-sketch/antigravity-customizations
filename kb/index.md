---
okf_version: "0.2"
id: antigravity-kb-index
title: "Open Knowledge Format (OKF v0.2) Empty Knowledge Bundle Skeleton"
summary: "Empty Open Knowledge Format (OKF v0.2) root skeleton with zero pre-loaded dossiers; populated organically by user-authored Markdown dossiers and Nightly Dreaming consolidation."
type: overview
status: verified
confidence: 1.0
last_verified: "2026-11-10"
tags: [okf, skeleton, knowledge-graph]
---

# Open Knowledge Format (`OKF v0.2`) Empty Knowledge Bundle Skeleton

This directory ships as an **empty `OKF v0.2` skeleton** (`0` pre-loaded dossiers, `0` pre-loaded Knowledge Graph entities or edges) conforming to the public [Open Knowledge Format (`OKF v0.2`)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) schema.

## Populating Your Own Knowledge Base

* Drop project-specific Markdown dossiers with `okf_version: "0.2"` YAML frontmatter under `kb/` (for example `kb/architecture/`, `kb/guides/`, or `kb/reference/`), or let the Nightly Dreaming engine consolidate verified user preferences from your own sessions.
* Run `python3 -B src/knowledge_graph/validate_okf.py --kb-root kb` to validate frontmatter and `python3 -B src/knowledge_graph/okf_knowledge_compiler.py --kb-root kb` to synchronize user-created dossiers into `knowledge_graph.json`.
