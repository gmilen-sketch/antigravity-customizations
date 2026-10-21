#!/usr/bin/env python3
"""
Delphi Consensus & Six Thinking Hats Multi-Criteria Task Router v2.0 (Clean-Room Edition).
Evaluates architectural options across 6 orthogonal lenses (White, Red, Black, Yellow, Green, Blue)
with iterative Delphi convergence.
"""

from typing import Dict, Any, List

SIX_HATS_LENSES = {
    "White": "Verified primary telemetry, empirical latency/throughput bounds, and schema ground truth",
    "Red": "Operator UX friction, cognitive load, and alert fatigue risks",
    "Black": "Adversarial failure modes, CWE/SSRF surfaces, quota exhaustion, and single points of failure",
    "Yellow": "Quantified normalized gain, TCO savings, and KV-cache prefix stability",
    "Green": "Clean-room open-source alternatives and zero-dependency lateral simplifications",
    "Blue": "Execution sequencing, rollback checkpoints, and deterministic completion gates",
}


def apply_popperian_counterexample_veto(
    options: List[Dict[str, Any]],
    black_hat_floor: float = 0.60,
    white_hat_floor: float = 0.60,
) -> Dict[str, Any]:
    """
    AGW-W12-13: Popperian Falsification & Black-Hat / White-Hat Counterexample Veto Gate.
    Applies a hard falsification veto to any candidate option that either has a verified
    critical counterexample (`falsified_by_counterexample=True`) or falls below the minimum
    Black-Hat safety floor (`0.60`) or White-Hat primary evidence floor (`0.60`), preventing
    high Yellow-Hat optimism scores from masking fatal architectural defects.
    """
    surviving = []
    vetoed = []
    for opt in options or []:
        scores = opt.get("hat_scores", {})
        bh = float(scores.get("Black", 1.0))
        wh = float(scores.get("White", 1.0))
        counterexample = str(opt.get("counterexample") or "").strip()
        falsified = bool(opt.get("falsified_by_counterexample", False) or counterexample)
        if falsified or bh < black_hat_floor or wh < white_hat_floor:
            vetoed.append({
                "name": opt.get("name", "Option"),
                "reason": counterexample or f"Floor violation (Black={bh}, White={wh})",
            })
        else:
            surviving.append(opt)
    return {
        "surviving_options": surviving,
        "vetoed_options": vetoed,
        "veto_count": len(vetoed),
    }


def evaluate_options_delphi(options: List[Dict[str, Any]], weights: Dict[str, float] = None) -> Dict[str, Any]:
    weights = weights or {"White": 0.25, "Black": 0.25, "Yellow": 0.20, "Green": 0.10, "Red": 0.10, "Blue": 0.10}
    veto_res = apply_popperian_counterexample_veto(options, black_hat_floor=0.0, white_hat_floor=0.0)
    active_pool = veto_res["surviving_options"] if veto_res["surviving_options"] else options
    ranked = []
    for opt in active_pool:
        scores = opt.get("hat_scores", {})
        total = sum(float(scores.get(h, 0.0)) * w for h, w in weights.items())
        ranked.append({"name": opt.get("name", "Option"), "weighted_score": round(total, 4), "hat_scores": scores})
    ranked.sort(key=lambda x: x["weighted_score"], reverse=True)
    return {
        "winner": ranked[0] if ranked else None,
        "ranking": ranked,
        "vetoed": veto_res["vetoed_options"],
        "lenses": SIX_HATS_LENSES,
    }
