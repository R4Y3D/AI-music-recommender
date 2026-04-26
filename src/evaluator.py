"""
Evaluation Harness for the Music Recommender.

Runs a fixed suite of test profiles through the recommender and asserts
expected behaviour. Reports a PASS/FAIL summary and an overall confidence
score (passed / total).

Usage:
    CLI:    python -m src.evaluator
    Code:   from src.evaluator import run_evaluation, format_report
"""

import sys
import os
from typing import Callable, Dict, List

# Allow `python src/evaluator.py` as well as `python -m src.evaluator`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import load_songs, recommend_songs_detailed


# ─────────────────────────────────────────────────────────────
#  Test definitions
# ─────────────────────────────────────────────────────────────
# Each test is (name, user_prefs, assertion_fn).
#   assertion_fn(results) -> (passed: bool, detail: str)
#
# Tests are deterministic and depend only on data/songs.csv.

def _t1_pop_top_genre(results: List[Dict]) -> tuple:
    if not results:
        return False, "no results returned"
    top = results[0]
    return (
        top["genre"] == "Pop",
        f"top result genre is '{top['genre']}' ({top['title']})",
    )


def _t2_acoustic_preference(results: List[Dict]) -> tuple:
    if not results:
        return False, "no results returned"
    top = results[0]
    return (
        top["acousticness"] >= 0.5,
        f"top result acousticness is {top['acousticness']:.2f} "
        f"({top['title']} by {top['artist']})",
    )


def _t3_high_energy_match(results: List[Dict]) -> tuple:
    if not results:
        return False, "no results returned"
    top = results[0]
    return (
        top["energy"] >= 0.85,
        f"top result energy is {top['energy']:.2f} ({top['title']})",
    )


def _t4_genre_alignment(results: List[Dict]) -> tuple:
    hip_hop_count = sum(1 for r in results if r["genre"] == "Hip-Hop")
    return (
        hip_hop_count >= 3,
        f"{hip_hop_count} of {len(results)} top results are Hip-Hop",
    )


def _t5_score_bounds(results: List[Dict]) -> tuple:
    if not results:
        return False, "no results to check"
    out_of_range = [r for r in results if not (0.0 <= r["score"] <= 4.5)]
    if out_of_range:
        return False, f"{len(out_of_range)} score(s) outside [0.0, 4.5]"
    return True, f"all {len(results)} scores in [0.00, 4.50]"


def _t6_determinism(results_a: List[Dict], results_b: List[Dict]) -> tuple:
    titles_a = [r["title"] for r in results_a]
    titles_b = [r["title"] for r in results_b]
    return (
        titles_a == titles_b,
        f"two identical runs produced {'matching' if titles_a == titles_b else 'different'} ordering",
    )


# ─────────────────────────────────────────────────────────────
#  Test suite
# ─────────────────────────────────────────────────────────────
TEST_SUITE = [
    {
        "name": "Genre alignment - Pop top match",
        "prefs": {"genre": "Pop", "mood": "Happy", "energy": 0.75, "likes_acoustic": False},
        "assertion": _t1_pop_top_genre,
        "rationale": "A Pop/Happy/0.75 user must get a Pop song at #1.",
    },
    {
        "name": "Acoustic preference is honoured",
        "prefs": {"genre": "Pop", "mood": "Sad", "energy": 0.4, "likes_acoustic": True},
        "assertion": _t2_acoustic_preference,
        "rationale": "When likes_acoustic=True, top result should be on the acoustic side (>=0.5).",
    },
    {
        "name": "High-energy request returns high-energy track",
        "prefs": {"genre": "EDM", "mood": "Energetic", "energy": 0.95, "likes_acoustic": False},
        "assertion": _t3_high_energy_match,
        "rationale": "Target energy 0.95 should yield a top result with energy >= 0.85.",
    },
    {
        "name": "Hip-Hop preference dominates top-5",
        "prefs": {"genre": "Hip-Hop", "mood": "Confident", "energy": 0.7, "likes_acoustic": False},
        "assertion": _t4_genre_alignment,
        "rationale": ">=3 of the top 5 should be Hip-Hop given the catalog has multiple Hip-Hop entries.",
    },
    {
        "name": "Score bounds are respected",
        "prefs": {"genre": "Pop", "mood": "Happy", "energy": 0.5, "likes_acoustic": True},
        "assertion": _t5_score_bounds,
        "rationale": "No score should exceed the documented max of 4.5 or fall below 0.0.",
    },
    # Test 6 (determinism) is special-cased in run_evaluation since it needs two runs.
]


# ─────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────
def run_evaluation(songs: List[Dict]) -> Dict:
    """
    Execute the full test suite against the provided song catalog.

    Returns:
        {
          "tests":      [{"name": str, "passed": bool, "detail": str, "rationale": str}, ...],
          "passed":     int,
          "total":      int,
          "confidence": float,   # passed / total, in [0.0, 1.0]
        }
    """
    test_records: List[Dict] = []

    # Standard tests
    for spec in TEST_SUITE:
        results = recommend_songs_detailed(spec["prefs"], songs, k=5)
        passed, detail = spec["assertion"](results)
        test_records.append({
            "name":      spec["name"],
            "passed":    passed,
            "detail":    detail,
            "rationale": spec["rationale"],
        })

    # Determinism test - run twice with the same prefs and compare
    det_prefs = {"genre": "Pop", "mood": "Happy", "energy": 0.6, "likes_acoustic": False}
    run_a = recommend_songs_detailed(det_prefs, songs, k=5)
    run_b = recommend_songs_detailed(det_prefs, songs, k=5)
    det_passed, det_detail = _t6_determinism(run_a, run_b)
    test_records.append({
        "name":      "Determinism - same input -> same output",
        "passed":    det_passed,
        "detail":    det_detail,
        "rationale": "A rule-based system must be deterministic for trustworthy explanation.",
    })

    passed = sum(1 for t in test_records if t["passed"])
    total  = len(test_records)
    return {
        "tests":      test_records,
        "passed":     passed,
        "total":      total,
        "confidence": passed / total if total else 0.0,
    }


def format_report(results: Dict) -> str:
    """Plain-text PASS/FAIL summary suitable for CLI or Streamlit st.code()."""
    lines: List[str] = []
    lines.append("=" * 64)
    lines.append("  VIBECIPHER - SYSTEM RELIABILITY EVALUATION")
    lines.append("=" * 64)
    for i, t in enumerate(results["tests"], start=1):
        marker = "PASS" if t["passed"] else "FAIL"
        lines.append(f"")
        lines.append(f"  [{marker}]  Test {i}: {t['name']}")
        lines.append(f"          -> {t['detail']}")
        lines.append(f"          why: {t['rationale']}")

    lines.append("")
    lines.append("-" * 64)
    lines.append(
        f"  Overall: {results['passed']} / {results['total']}   "
        f"Confidence: {results['confidence']:.0%}"
    )
    lines.append("=" * 64)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────
def main() -> int:
    """Run the evaluator from the command line. Returns exit code."""
    songs = load_songs("data/songs.csv")
    results = run_evaluation(songs)
    print(format_report(results))
    # Non-zero exit if any test failed (so this can gate CI later)
    return 0 if results["passed"] == results["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
