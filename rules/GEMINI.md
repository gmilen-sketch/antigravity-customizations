# Enterprise Cloud Architecture & Autonomy Sentinel Rules (`Arm B` High-Density Hybrid)

## 🛡️ Global Sentinel Rules
1. **Skill Activation (`Rule #1`)**: Read the matched skill's `SKILL.md` (`read_file` / `view_file`) before running its scripts or modifying domain artifacts.
2. **6-Pillar Architecture Scope (`Rule #10`)**: Evaluate enterprise cloud architectures across all 6 pillars: **AI/ML**, **Data Analytics**, **App Modernization**, **Security & Zero-Trust**, **Multicloud & Hybrid**, and **Sovereign Cloud**.
3. **3-Row Staging Diff (`Rule #9`)**: Before mutating shared ledgers or portfolio trackers, present a 3-Row Staging Diff (`Row 2: Current Baseline`, `Row 3: Planned Target`, `Row 4: Variance Delta`) and wait for explicit confirmation.
4. **Clean-Room Anonymization (`Rule #11`)**: Never commit raw workstation home paths, credentials, or customer-identifiable tokens into shared repositories; use `<USER_HOME_DIR>` and `<TARGET_CUSTOMER_NAME>`.
5. **Active Model Catalog (`Rule #28`)**: Default to `gemini-3.8-flash` (general production), `gemini-3.5-flash-lite` (high-throughput), and `gemini-3.5-pro` / `claude-opus-5` / `claude-sonnet-5` (deep reasoning). Reject legacy Gemini 1.x/2.0/2.5 and Claude 1–4.x models.
6. **Bitemporal Knowledge Graph SSOT (`Rule #20`)**: Anchor project facts, architecture decisions, and temporal validity windows in `knowledge_graph.json` (`/dev/shm/kg_warm_cache.json`) and Open Knowledge Format (`OKF v0.2`) dossiers under `kb/`.
7. **2-Stage Black-Hat Goldfish → Judge Completion Gate**: When `mutations > 0`, verify all deliverables on disk (`DISCREPANCY_COUNT: 0`) via `black-hat-goldfish` followed by `black-hat-judge` adjudication before declaring completion.
