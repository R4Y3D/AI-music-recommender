"""
Guardrails for the Music Recommender.

Two responsibilities:
  1. Input validation  — sanitize user preferences before scoring
  2. Output validation — flag low-diversity recommendation sets

Design intent: pure functions, no side effects, no external state.
"""

from collections import Counter
from difflib import get_close_matches
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────
#  Input guardrail
# ─────────────────────────────────────────────────────────────
def validate_user_prefs(
    user_prefs: Dict,
    songs: List[Dict],
) -> Tuple[Dict, List[str]]:
    """
    Sanitize user preferences against the catalog.

    Returns:
        (sanitized_prefs, warnings)
        - sanitized_prefs is always safe to pass to the scorer
        - warnings is a list of human-readable strings for the UI

    Behaviour:
        - genre / mood: if not an exact match in the catalog, attempt fuzzy
          match via difflib; if no close match, fall back to the most common
          value in the catalog.
        - energy: clamped to [0.0, 1.0]; non-numeric → 0.5
        - likes_acoustic: coerced to bool
    """
    warnings: List[str] = []

    available_genres = sorted({s["genre"] for s in songs})
    available_moods  = sorted({s["mood"]  for s in songs})

    # --- Genre ---
    raw_genre = (user_prefs.get("genre") or "").strip()
    genre = _resolve_label(
        raw_genre, available_genres, songs, key="genre", warnings=warnings,
        kind="Genre",
    )

    # --- Mood ---
    raw_mood = (user_prefs.get("mood") or "").strip()
    mood = _resolve_label(
        raw_mood, available_moods, songs, key="mood", warnings=warnings,
        kind="Mood",
    )

    # --- Energy ---
    raw_energy = user_prefs.get("energy", 0.5)
    try:
        energy = float(raw_energy)
        if energy < 0.0:
            warnings.append(f"Energy {energy:.2f} is below 0.0; clamping to 0.0.")
            energy = 0.0
        elif energy > 1.0:
            warnings.append(f"Energy {energy:.2f} is above 1.0; clamping to 1.0.")
            energy = 1.0
    except (TypeError, ValueError):
        warnings.append(f"Energy value {raw_energy!r} is not numeric; defaulting to 0.5.")
        energy = 0.5

    # --- Acoustic ---
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    return (
        {
            "genre": genre,
            "mood": mood,
            "energy": energy,
            "likes_acoustic": likes_acoustic,
        },
        warnings,
    )


def _resolve_label(
    raw: str,
    available: List[str],
    songs: List[Dict],
    key: str,
    warnings: List[str],
    kind: str,
) -> str:
    """
    Resolve a user-supplied label to a real catalog value.
    Exact match → fuzzy match (case-insensitive) → most common fallback.
    """
    if raw in available:
        return raw

    # Case-insensitive map: lowercased → real label in catalog
    lower_map = {a.lower(): a for a in available}
    if raw.lower() in lower_map:
        canonical = lower_map[raw.lower()]
        warnings.append(f"{kind} '{raw}' matched to '{canonical}' (case-insensitive).")
        return canonical

    # Fuzzy match against the lowercased keys
    matches = get_close_matches(raw.lower(), list(lower_map.keys()), n=1, cutoff=0.6)
    if matches:
        canonical = lower_map[matches[0]]
        warnings.append(f"{kind} '{raw}' not found; using closest match '{canonical}'.")
        return canonical

    # Fallback: most common value in the catalog
    counter = Counter(s[key] for s in songs)
    fallback = counter.most_common(1)[0][0]
    warnings.append(
        f"{kind} '{raw}' not found and no close match; defaulting to "
        f"'{fallback}' (most common in catalog)."
    )
    return fallback


# ─────────────────────────────────────────────────────────────
#  Output guardrail
# ─────────────────────────────────────────────────────────────
def check_diversity(results: List[Dict]) -> Optional[str]:
    """
    Inspect the top-k recommendation set and return a warning string
    if it lacks diversity. Returns None when the set is healthy.

    Heuristics (any one triggers a warning):
      - All results share the same genre
      - All results share the same mood
    """
    if len(results) < 2:
        return None

    genres = {r.get("genre") for r in results}
    moods  = {r.get("mood")  for r in results}

    if len(genres) == 1:
        only = next(iter(genres))
        return (
            f"Low genre diversity: all top {len(results)} results are '{only}'. "
            f"Try a different mood or energy to broaden the mix."
        )

    if len(moods) == 1:
        only = next(iter(moods))
        return (
            f"Low mood diversity: all top {len(results)} results are '{only}'. "
            f"Try a different genre or energy to broaden the mix."
        )

    return None
