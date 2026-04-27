"""
evaluate.py
-----------
Test harness and evaluation script for the Game Glitch Investigator v2.

Usage:
    python evaluate.py
    python evaluate.py --verbose
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass

from ai_investigator import GlitchInvestigator


@dataclass
class EvalCase:
    id: str
    description: str
    expected_bug_id: str
    expect_valid: bool
    min_confidence: float
    tags: list[str]


EVAL_CASES: list[EvalCase] = [
    EvalCase("TC-01", "Every time I guess a number higher than the secret, the game says 'Too Low'. It's completely backwards.", "inverted_comparison", True, 0.50, ["logic", "hints"]),
    EvalCase("TC-02", "The score is always 0 no matter how quickly I guess the number. Even if I get it in 2 tries, it still shows 0 points.", "integer_division_score", True, 0.45, ["logic", "score"]),
    EvalCase("TC-03", "The game crashes immediately when I type letters in the input box. I see a ValueError traceback.", "unhandled_non_numeric_input", True, 0.45, ["crash", "input"]),
    EvalCase("TC-04", "It seems like 100 can never be the secret number. I've played hundreds of games and the secret is always 99 or below.", "off_by_one_range", True, 0.40, ["logic", "range"]),
    EvalCase("TC-05", "When I refresh the page in Streamlit, the game resets but my previous score disappears and sometimes a KeyError appears.", "session_state_not_initialised", True, 0.40, ["state", "streamlit"]),
    EvalCase("TC-06", "After winning the game, I can still keep clicking Guess and it keeps counting attempts even though I already got 'Correct!'.", "guess_accepted_after_game_over", True, 0.38, ["logic", "game-over"]),
    EvalCase("TC-07", "hi", "", False, 0.0, ["guardrail", "too-short"]),
    EvalCase("TC-08", "What is the capital of France?", "", False, 0.0, ["guardrail", "off-topic"]),
    EvalCase("TC-09", "The hint message shows up even before I make my first guess, which is confusing.", "hint_shown_before_first_guess", True, 0.35, ["display"]),
    EvalCase("TC-10", "When I start a new game the score from the previous game is still showing and my attempt counter never resets.", "score_not_reset_on_new_game", True, 0.38, ["state", "reset"]),
]


@dataclass
class EvalResult:
    case: EvalCase
    passed: bool
    top_bug_id: str
    actual_confidence: float
    guardrail_passed: bool
    elapsed: float
    failure_reason: str = ""


def run_evaluation(verbose: bool = False) -> list[EvalResult]:
    agent = GlitchInvestigator(verbose=False)
    results: list[EvalResult] = []

    print("\n" + "=" * 65)
    print("  GAME GLITCH INVESTIGATOR — EVALUATION HARNESS")
    print("=" * 65)
    print(f"  Running {len(EVAL_CASES)} test cases …\n")

    for case in EVAL_CASES:
        t0 = time.time()
        report = agent.investigate(case.description)
        elapsed = round(time.time() - t0, 2)

        guardrail_correct = (len(report.warnings) == 0) == case.expect_valid
        top_id = report.retrieved_bugs[0]["id"] if report.retrieved_bugs else ""
        retrieval_ok = (top_id == case.expected_bug_id if case.expected_bug_id else True)
        conf_ok = report.confidence >= case.min_confidence
        passed = guardrail_correct and retrieval_ok and conf_ok

        reason = ""
        if not guardrail_correct:
            reason += f"Guardrail: expected {'pass' if case.expect_valid else 'fail'}, got {'pass' if len(report.warnings)==0 else 'fail'}. "
        if not retrieval_ok:
            reason += f"Retrieval: expected '{case.expected_bug_id}', got '{top_id}'. "
        if not conf_ok:
            reason += f"Confidence: expected ≥{case.min_confidence:.0%}, got {report.confidence:.0%}. "

        result = EvalResult(case=case, passed=passed, top_bug_id=top_id,
                            actual_confidence=report.confidence, guardrail_passed=guardrail_correct,
                            elapsed=elapsed, failure_reason=reason.strip())
        results.append(result)

        status = "✓ PASS" if passed else "✗ FAIL"
        tags = ", ".join(case.tags)
        print(f"  [{status}] {case.id} | conf={report.confidence:.0%} | {elapsed:.2f}s | tags=[{tags}]")
        if not passed:
            print(f"           ↳ {reason}")
        if verbose:
            print(f"           ↳ Top bug: {top_id!r}")
            print(f"           ↳ Diagnosis: {report.diagnosis[:80]}…")

    return results


def print_summary(results: list[EvalResult]) -> int:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    avg_conf = sum(r.actual_confidence for r in results) / max(total, 1)
    avg_time = sum(r.elapsed for r in results) / max(total, 1)

    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Tests passed  : {passed}/{total}")
    print(f"  Tests failed  : {total - passed}/{total}")
    print(f"  Avg confidence: {avg_conf:.0%}")
    print(f"  Avg time/case : {avg_time:.2f}s")

    by_tag: dict[str, list[bool]] = {}
    for r in results:
        for tag in r.case.tags:
            by_tag.setdefault(tag, []).append(r.passed)
    print("\n  By category:")
    for tag, outcomes in sorted(by_tag.items()):
        p = sum(outcomes)
        t = len(outcomes)
        bar = "█" * p + "░" * (t - p)
        print(f"    {tag:<20} {bar}  {p}/{t}")

    print("=" * 65)
    if passed == total:
        print("  🎉  All tests passed!")
    else:
        print(f"  ⚠   {total - passed} test(s) failed. See details above.")
    print("=" * 65 + "\n")
    return 0 if passed == total else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation harness for Game Glitch Investigator v2.")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    results = run_evaluation(verbose=args.verbose)
    exit_code = print_summary(results)
    sys.exit(exit_code)
