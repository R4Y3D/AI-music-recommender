from src.recommender import Song, UserProfile, Recommender
from src.guardrails import validate_user_prefs, check_diversity

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_acoustic_preference_boosts_acoustic_song():
    songs = [
        Song(
            id=10,
            title="Electric Banger",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.8,
            danceability=0.8,
            acousticness=0.1,  # low acousticness
        ),
        Song(
            id=11,
            title="Wooden Guitar Ballad",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.8,
            danceability=0.8,
            acousticness=0.9,  # high acousticness
        ),
    ]
    rec = Recommender(songs)
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=True,
    )
    results = rec.recommend(user, k=2)
    # The acoustic song should rank first when user likes acoustic
    assert results[0].title == "Wooden Guitar Ballad"


# ─────────────────────────────────────────────────────────────
#  Guardrail tests
# ─────────────────────────────────────────────────────────────
def _sample_catalog():
    """Tiny catalog used to drive guardrail tests."""
    return [
        {"id": 1, "title": "A", "artist": "X", "genre": "Pop",     "mood": "Happy",
         "energy": 0.8, "tempo_bpm": 120, "valence": 0.8, "danceability": 0.7, "acousticness": 0.1},
        {"id": 2, "title": "B", "artist": "X", "genre": "Pop",     "mood": "Sad",
         "energy": 0.4, "tempo_bpm": 90,  "valence": 0.3, "danceability": 0.5, "acousticness": 0.6},
        {"id": 3, "title": "C", "artist": "X", "genre": "Hip-Hop", "mood": "Happy",
         "energy": 0.7, "tempo_bpm": 100, "valence": 0.7, "danceability": 0.8, "acousticness": 0.05},
    ]


def test_validate_user_prefs_clamps_energy():
    """Out-of-bounds energy is clamped to [0.0, 1.0] with a warning."""
    songs = _sample_catalog()
    sanitized, warnings = validate_user_prefs(
        {"genre": "Pop", "mood": "Happy", "energy": 1.7, "likes_acoustic": False},
        songs,
    )
    assert sanitized["energy"] == 1.0
    assert any("clamp" in w.lower() for w in warnings)


def test_validate_user_prefs_fuzzy_matches_genre():
    """Lower-case 'pop' should resolve to canonical 'Pop' with a warning."""
    songs = _sample_catalog()
    sanitized, warnings = validate_user_prefs(
        {"genre": "pop", "mood": "Happy", "energy": 0.5, "likes_acoustic": False},
        songs,
    )
    assert sanitized["genre"] == "Pop"
    assert any("Pop" in w for w in warnings)


def test_check_diversity_flags_single_genre_set():
    """When all results share a genre, a warning is returned."""
    results = [
        {"genre": "Pop", "mood": "Happy"},
        {"genre": "Pop", "mood": "Sad"},
        {"genre": "Pop", "mood": "Energetic"},
    ]
    warning = check_diversity(results)
    assert warning is not None
    assert "Pop" in warning


def test_check_diversity_passes_diverse_set():
    """A varied result set returns None."""
    results = [
        {"genre": "Pop", "mood": "Happy"},
        {"genre": "Hip-Hop", "mood": "Energetic"},
        {"genre": "R&B", "mood": "Chill"},
    ]
    assert check_diversity(results) is None
