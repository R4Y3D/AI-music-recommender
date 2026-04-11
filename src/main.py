"""
Command line runner for the Music Recommender Simulation.

Runs multiple user profiles - including standard and adversarial edge cases -
to evaluate scoring behaviour across different preference combinations.
"""

from src.recommender import load_songs, recommend_songs


PROFILES = [
    # --- Standard profiles ---
    {
        "label":  "High-Energy Pop",
        "genre":  "pop",
        "mood":   "happy",
        "energy": 0.85,
    },
    {
        "label":  "Chill Lofi",
        "genre":  "lofi",
        "mood":   "chill",
        "energy": 0.38,
    },
    {
        "label":  "Deep Intense Rock",
        "genre":  "rock",
        "mood":   "intense",
        "energy": 0.92,
    },
    # --- Adversarial / edge-case profiles ---
    {
        "label":  "EDGE: High Energy + Chill Mood (conflicting)",
        "genre":  "lofi",
        "mood":   "chill",
        "energy": 0.95,   # chill mood but wants maximum energy
    },
    {
        "label":  "EDGE: Rare Genre (country - only 1 song in catalog)",
        "genre":  "country",
        "mood":   "nostalgic",
        "energy": 0.44,
    },
    {
        "label":  "EDGE: Dead-Center Energy (everything scores similarly)",
        "genre":  "ambient",
        "mood":   "focused",
        "energy": 0.50,   # equidistant from most songs - weak tiebreaker
    },
]


def print_profile(label, user_prefs, recommendations):
    width = 58
    print()
    print("=" * width)
    print(f"  {label}")
    print("=" * width)
    print(f"  genre={user_prefs['genre']}  "
          f"mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}")
    print("-" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Score  : {score:.2f} / 4.00")
        print(f"       Genre  : {song['genre']}   "
              f"Mood: {song['mood']}   "
              f"Energy: {song['energy']}")
        reasons = explanation.split(", ")
        print(f"       Reasons: {reasons[0]}")
        for reason in reasons[1:]:
            print(f"                {reason}")

    print()
    print("=" * width)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile in PROFILES:
        user_prefs = {k: v for k, v in profile.items() if k != "label"}
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_profile(profile["label"], user_prefs, recommendations)


if __name__ == "__main__":
    main()
