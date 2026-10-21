# Antigravity Customizations Suite — Two-Tier Skill & Subagent Routing Directory (`v1.3.0`)

## 1. Two-Tier Skill Activation Architecture (`R2` `-58%` Context Footprint)
To minimize baseline prompt token consumption while keeping all `20` `PD-Q` enterprise skills immediately accessible:
- **Tier 1 (7 Core Always-Active Skills in `skills.json` `include_only`)**: Injected into `<skills>` on Turn 1.
- **Tier 2 (13 On-Demand Domain Skills in `skills/`)**: Automatically matched and activated on demand by `src/hooks/kg_pre_invocation_hook.py` (`multi_harness_hook_adapter.py --event PreInvocation`) or read directly from `skills/<name>/SKILL.md`.

### Tier 1 — Core Always-Active Skills (7)
| # | Skill Name | Skill Path | Primary Use Cases |
| :--- | :--- | :--- | :--- |
| 1 | `black-hat-analysis` | `skills/black-hat-analysis/SKILL.md` | 2-Stage Stateless Goldfish -> Isolated Judge forensic completion verification |
| 2 | `diagram-renderer` | `skills/diagram-renderer/SKILL.md` | High-resolution Mermaid (`.mmd`), Cloud Draw (`.clouddraw`), and BENTO card compilation |
| 3 | `finops-focus-auditor` | `skills/finops-focus-auditor/SKILL.md` | FOCUS v1.3 cloud billing, CUD utilization, and Net Effective Savings Rate audits |
| 4 | `open-deep-researcher` | `skills/open-deep-researcher/SKILL.md` | Multi-source technical research with Six Thinking Hats pre-screening |
| 5 | `p0-quality-first-engine` | `skills/p0-quality-first-engine/SKILL.md` | 7 P0 execution circuit breakers (`CB-1..CB-7`) |
| 6 | `self-grill` | `skills/self-grill/SKILL.md` | Bayesian Hunter-MM / Elo pre-execution design and UI geometry self-interrogation |
| 7 | `universal-solution-architect` | `skills/universal-solution-architect/SKILL.md` | 6-Pillar enterprise cloud architecture design & tradeoff matrices |

### Tier 2 — On-Demand Domain Skills (13)
| # | Skill Name | Skill Path | Primary Use Cases |
| :--- | :--- | :--- | :--- |
| 8 | `antigravity-web-builder` | `skills/antigravity-web-builder/SKILL.md` | Full-stack web application and AuxPane UI plugin engineering |
| 9 | `first-principles-brainstormer` | `skills/first-principles-brainstormer/SKILL.md` | Axiom decomposition and first-principles architectural synthesis |
| 10 | `golden-ab-testing` | `skills/golden-ab-testing/SKILL.md` | 5D Golden Reference A/B evaluation (`R_fact`, `P_faith`, `F_cite`, `S_sem`, `C_struct`) |
| 11 | `idea-evaluator` | `skills/idea-evaluator/SKILL.md` | Multi-gate candidate feature and architecture enhancement scoring |
| 12 | `issue-tracker-manager` | `skills/issue-tracker-manager/SKILL.md` | Issue triage, SLA tracking, and root-cause dossier linkage |
| 13 | `migration-center-architect` | `skills/migration-center-architect/SKILL.md` | Legacy-to-cloud workload assessment, TCO modeling, and wave planning |
| 14 | `p1-quality-first-engine` | `skills/p1-quality-first-engine/SKILL.md` | 8 P1 quality & prompt-injection circuit breakers (`P1-CB-1..P1-CB-8`) |
| 15 | `parallel-task-orchestrator` | `skills/parallel-task-orchestrator/SKILL.md` | Native multi-agent `/swarm` and `run_workflow` DAG orchestration |
| 16 | `playwright-agent-browser` | `skills/playwright-agent-browser/SKILL.md` | Headless Chromium DOM extraction and authenticated SPA verification |
| 17 | `six-hats-evaluator` | `skills/six-hats-evaluator/SKILL.md` | Parallel 6-Hats (`White`, `Red`, `Black`, `Yellow`, `Green`, `Blue`) decision matrices |
| 18 | `universal-task-sync` | `skills/universal-task-sync/SKILL.md` | Portfolio task ledger synchronization and 3-Row Staging Diff generation |
| 19 | `workspace-docs-publisher` | `skills/workspace-docs-publisher/SKILL.md` | 3-Tab `Arm E` executive technical documentation publishing |
| 20 | `workspace-slides-generator` | `skills/workspace-slides-generator/SKILL.md` | 4-Card executive presentation deck generation |

---

## 2. Custom Subagents (`agents/`)
| Subagent Name | Definition Path | Subagent Hooks | Role |
| :--- | :--- | :--- | :--- |
| `black-hat-goldfish` | `agents/black-hat-goldfish.md` | `agents/black-hat-goldfish/hooks.json` | Stage 1 Stateless Forensic Investigator (`DISCREPANCY_COUNT`) |
| `black-hat-judge` | `agents/black-hat-judge.md` | `agents/black-hat-judge/hooks.json` | Stage 2 Isolated Forensic Adjudicator (`CRITIC_VERDICT`) |
| `black-hat-critic` | `agents/black-hat-critic.md` | Inherited | Single-stage adversarial deliverable verifier |
| `dreaming-improvement-reasoner` | `agents/dreaming-improvement-reasoner.md` | Inherited | Nightly Dreaming Pareto error-cluster causal synthesizer |
| `workspace-housekeeper` | `agents/workspace-housekeeper.md` | Inherited | Post-dreaming workspace hygiene and mirror synchronization |
