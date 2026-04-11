"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("=" * 52)
    print("  Music Recommender - Top 5 Results")
    print("=" * 52)
    print(f"  Profile : genre={user_prefs['genre']}  "
          f"mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}")
    print("=" * 52)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Score  : {score:.2f} / 4.00")
        print(f"       Genre  : {song['genre']}   Mood: {song['mood']}   Energy: {song['energy']}")
        reasons = explanation.split(", ")
        print(f"       Reasons: {reasons[0]}")
        for reason in reasons[1:]:
            print(f"                {reason}")

    print()
    print("=" * 52)


if __name__ == "__main__":
    main()
