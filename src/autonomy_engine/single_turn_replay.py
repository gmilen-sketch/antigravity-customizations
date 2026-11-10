"""Single-Turn Replay Engine & Tail-Preserving Traceback Slicer (`AGW-W12-04`)."""
import time
import json
from typing import Dict, Any, List, Optional, Callable


def slice_tail_preserving_traceback_and_classify_retry(
    raw_output: str,
    head_chars: int = 300,
    tail_chars: int = 700,
) -> Dict[str, Any]:
    """
    AGW-W12-04: Tail-Preserving Traceback Slicer (30% Head / 70% Tail) & Deterministic vs. Transient Error Classifier.
    Preserves both the command invocation header (30% head) and the bottom Python/compiler exception root cause
    (70% tail) while classifying whether the error is transient (retryable with backoff) or deterministic (requires code fix).
    """
    text = raw_output or ""
    total_budget = max(100, int(head_chars) + int(tail_chars))
    if len(text) <= total_budget:
        sliced = text
        truncated = False
    else:
        sliced = f"{text[:head_chars]}\n...[TRUNCATED MIDDLE]...\n{text[-tail_chars:]}"
        truncated = True

    lower = text.lower()
    transient_markers = ("429", "rate limit", "deadline exceeded", "503", "connection reset", "temporarily unavailable")
    deterministic_markers = ("syntaxerror", "typeerror", "nameerror", "keyerror", "importerror", "assertionerror", "filenotfounderror")

    if any(m in lower for m in deterministic_markers):
        error_class = "DETERMINISTIC_CODE_OR_SCHEMA_ERROR"
        should_retry_unchanged = False
    elif any(m in lower for m in transient_markers):
        error_class = "TRANSIENT_INFRA_ERROR"
        should_retry_unchanged = True
    else:
        error_class = "CLEAN_OR_UNKNOWN"
        should_retry_unchanged = False

    return {
        "sliced_output": sliced,
        "truncated": truncated,
        "error_class": error_class,
        "should_retry_unchanged": should_retry_unchanged,
    }


class SingleTurnReplayEngine:
    def __init__(self, inference_fn: Optional[Callable[[List[Dict[str, str]]], str]] = None):
        self.inference_fn = inference_fn or self._default_mock_inference

    @staticmethod
    def _default_mock_inference(messages: List[Dict[str, str]]) -> str:
        # Standard mock inference validating fast execution
        return "I will use the verified tool and follow strict schema constraints."

    def replay_turn(self, frozen_context: List[Dict[str, str]], candidate_prompt_patch: str, oracle_validator: Optional[Callable[[str], bool]] = None) -> Dict[str, Any]:
        start_t = time.time()
        
        # Inject candidate patch as system instruction
        augmented_context = [
            {"role": "system", "content": candidate_prompt_patch}
        ] + frozen_context

        # Execute 1-turn inference
        response_text = self.inference_fn(augmented_context)
        latency_ms = (time.time() - start_t) * 1000.0
        diag = slice_tail_preserving_traceback_and_classify_retry(response_text)

        is_valid = True
        if oracle_validator:
            is_valid = oracle_validator(response_text)

        return {
            "passed": is_valid,
            "latency_ms": round(latency_ms, 2),
            "response": response_text,
            "diagnostics": diag,
            "fast_turn_pass": latency_ms < 2000.0 # Assert sub-2 second turnaround
        }
