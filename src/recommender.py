import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_song(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """
    Scores a single song against a user profile.

    EXPERIMENT — Weight Shift: energy doubled, genre halved.
    Original:   genre +2.0, mood +1.0, energy ×1.0  (max 4.0)
    Experiment: genre +1.0, mood +1.0, energy ×2.0  (max 4.0)

    Math check: 1.0 + 1.0 + 2.0×(0.0–1.0) = 0.0 to 4.0  [valid, same ceiling]

    Returns:
        (score, reasons) — numeric total and a list of human-readable reason strings.
    """
    score = 0.0
    reasons = []

    if song.genre == user.favorite_genre:
        score += 1.0                          # was 2.0 — halved
        reasons.append(f"genre match (+1.0)")

    if song.mood == user.favorite_mood:
        score += 1.0
        reasons.append(f"mood match (+1.0)")

    energy_points = round(2.0 * (1.0 - abs(song.energy - user.target_energy)), 2)
    score += energy_points                    # was ×1.0 — doubled
    reasons.append(f"energy proximity (+{energy_points})")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the song catalog for scoring and ranking."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score every song against the user profile and return the top k sorted by score."""
        scored = sorted(self.songs, key=lambda s: _score_song(user, s)[0], reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a comma-separated string of reasons why this song was recommended."""
        _, reasons = _score_song(user, song)
        return ", ".join(reasons) if reasons else "Recommended based on overall similarity"


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file using Python's built-in csv module.
    Converts numerical fields to the correct types for math operations.
    Required by src/main.py
    """
    INT_FIELDS   = {"id", "tempo_bpm"}
    FLOAT_FIELDS = {"energy", "valence", "danceability", "acousticness"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in INT_FIELDS:
                if field in row:
                    row[field] = int(float(row[field]))
            for field in FLOAT_FIELDS:
                if field in row:
                    row[field] = float(row[field])
            songs.append(row)

    print(f"Loaded songs: {len(songs)}")
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional bridge used by src/main.py.

    For every song in the catalog, _score_song() acts as a judge and produces
    a numeric score. sorted() then ranks all (song, score, reasons) triples
    from highest to lowest without touching the original list. [:k] slices
    the top results.
    """
    song_objects = [
        Song(
            id=s["id"],
            title=s["title"],
            artist=s["artist"],
            genre=s["genre"],
            mood=s["mood"],
            energy=s["energy"],
            tempo_bpm=s["tempo_bpm"],
            valence=s["valence"],
            danceability=s["danceability"],
            acousticness=s["acousticness"],
        )
        for s in songs
    ]

    user = UserProfile(
        favorite_genre=user_prefs["genre"],
        favorite_mood=user_prefs["mood"],
        target_energy=user_prefs["energy"],
        likes_acoustic=user_prefs.get("likes_acoustic", False),
    )

    # Score every song — _score_song is the "judge" called once per song
    scored = [(song, score, reasons) for song, (score, reasons) in
              ((song, _score_song(user, song)) for song in song_objects)]

    # sorted() ranks without modifying the original catalog; key= picks the score
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    # Slice the top k and pair each Song back with its original dict
    song_dict_by_id = {s["id"]: s for s in songs}
    return [
        (song_dict_by_id[song.id], score, ", ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]
