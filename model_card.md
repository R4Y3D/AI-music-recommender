# 🎧 Model Card — VibeCipher (Applied AI Music Recommender)

## 1. Model Name

**VibeCipher** *(formerly CLaudeVibeMaster — renamed for the applied-AI extension)*

---

## 2. Intended Use

VibeCipher suggests songs from a 70-track catalogue based on a user's stated genre, mood, energy level, and acoustic preference. It is built for **classroom exploration and demo** as part of CodePath AI110. It is **not** intended for real users, public deployment, or any production use case.

It assumes a single user, a single session, no login, no taste history beyond what the user types in, and no listening telemetry. Every recommendation is fully explainable and reproducible from the inputs alone.

---

## 3. How the Model Works

Every song in the catalogue gets a score based on how well it matches the user's favourite genre (worth +2.0 points if it's an exact match), preferred mood (+1.0), target energy level (up to +1.0 the closer the song is to the requested energy), and — if the user opts in — how acoustic the track is (up to +0.5). The five highest-scoring songs are returned with a coloured bar for each component so the user can see exactly which signal contributed what. Every recommendation comes with a plain-English explanation, and identical inputs always produce identical outputs.

The applied-AI extension layers three additional behaviours on top of that base scoring rule:
- **Guardrails** clean up bad input (typos, out-of-range numbers) and flag low-diversity result sets.
- **An evaluation harness** runs six fixed test scenarios against the recommender and produces a confidence percentage.
- **A feedback loop** lets the user click 👍 / 👎 on any result to nudge the scoring weights for the rest of the session.

---

## 4. Data

The catalogue contains **70 real songs** by 30+ contemporary artists (The Weeknd, Taylor Swift, Dua Lipa, Olivia Rodrigo, SZA, Drake, Billie Eilish, Harry Styles, Ariana Grande, Adele, Beyoncé, and others). Genres represented: Pop (heavy majority), Hip-Hop, R&B, Indie, EDM, Afrobeats. Moods: Energetic, Happy, Chill, Sad, Melancholic, Reflective, Confident, Empowering, Dark, Angry, Dynamic, Playful, Nostalgic, Romantic, and others.

This dataset replaced the 18 placeholder rows from the original starter to make the demo feel realistic. The catalogue is intentionally small enough to inspect by hand, which makes the scoring engine debuggable in a way a 100K-song catalogue would not be.

**What's missing from the data:** anything outside the contemporary Pop / Hip-Hop / R&B sphere — no classical, no jazz, no metal, no global pop in non-English languages, no music older than ~10 years. Listeners with those tastes will get poor recommendations regardless of how the algorithm is tuned.

---

## 5. Strengths

The system works best when a user has clear, specific taste — for example a "Pop / Happy / 0.75" listener gets near-perfect matches at the top every time. Every recommendation comes with visible reasons via the four breakdown bars, making it easy to understand and trust the output. Because the system is purely rule-based, it's also fully reproducible: identical inputs produce identical outputs, which the determinism test in the evaluation harness verifies on every run.

The applied-AI additions also surface trustworthiness explicitly: the user can click "Run System Diagnostics" and see *empirical evidence* that the system behaves correctly, not just the developer's promise.

---

## 6. Limitations and Bias

- **Genre and mood are exact string matches.** `Indie` and `Indie Pop` are treated as completely different. A real product would need a taxonomy or fuzzy clustering. The input guardrail's fuzzy matcher only saves the user from typos — it doesn't unify genuinely related labels.
- **Catalogue is heavily Pop-weighted.** Of 70 songs, the majority are Pop. Niche taste profiles (Country, Afrobeats, Indie) get fewer high-quality matches and may trip the diversity guardrail.
- **Genre weight (+2.0) dominates.** A user who wants "sad songs across any genre" is poorly served because the rule-based engine cannot learn that mood matters more than genre for that user — unless they explicitly upvote sad-but-off-genre songs to push the mood weight up.
- **Mood labels are subjective.** Whether *Anti-Hero* is `Reflective` or `Sad` is one human's call, and that label propagates through every recommendation.
- **The feedback loop only persists in-session.** Refreshing the page resets everything. This is intentional for demo reproducibility, but a real product would persist taste profiles per user.

---

## 7. Misuse Risks

Even a small classroom recommender raises real ethics questions. The ones most relevant to this system:

- **Filter-bubble amplification.** The feedback loop nudges weights toward whatever the user already liked. Pushed to its clamp ceilings, the genre weight could grow until the system *only* recommends one genre — a textbook reinforcement-loop failure mode. The clamps and the "Reset Weights" button are the mitigation, but they're a soft mitigation, not a hard guarantee.
- **Taste profiling without informed consent.** If this system were deployed publicly, the inputs (genre, mood, energy, acoustic) would constitute a low-grade psychographic profile. Even though the data never leaves the session, a real deployment would need a clear consent flow explaining what's being collected and why.
- **Misleading "AI" branding.** The system is a four-line scoring rule, not machine learning. Calling it an "AI music recommender" risks overstating what it does and what users can expect. The README and model card both name the system as rule-based to mitigate this.
- **Catalogue bias as a curatorial decision.** The choice to include certain artists and genres is itself an editorial act. If this were used to recommend "the best new music" it would systematically privilege the music I happened to add and silence everything I didn't — without telling the user that's happening.

These risks would all be *more* serious if the system used a deep model whose internal logic couldn't be inspected. Keeping VibeCipher rule-based is itself a mitigation: anyone can read 30 lines of Python and see exactly what's happening.

---

## 8. Evaluation

The system is evaluated two ways:

- **Unit tests** (`pytest`): 7 tests covering core scoring behaviour, the acoustic bonus, fuzzy genre resolution, energy clamping, and the diversity check. All 7 pass.
- **Evaluation harness** (`python -m src.evaluator`): 6 scenario tests that assert expected behaviour for representative user profiles plus determinism and score-bound checks. **All 6 pass at 100% confidence** on the current catalogue.

The harness is the project's "AI feature" deliverable — it's how the system proves it actually does what its documentation says.

---

## 9. AI Collaboration

This project was built in collaboration with an AI coding assistant. Two specific moments are worth recording:

**Helpful suggestion (took it):**
When I described the input guardrail, the AI suggested using Python's stdlib `difflib.get_close_matches` for fuzzy genre matching with a cutoff of 0.6, falling back to the catalogue's most common value when no match is found. This was better than my initial idea (a hand-coded Levenshtein distance loop) because `difflib` is already on the standard library, has been battle-tested, and matched my "no new dependencies" constraint. I kept this design as written.

**Flawed suggestion (rejected):**
When I added the feedback loop, the AI initially proposed putting `st.rerun()` inside the button click handlers to force the page to re-render with new weights. I tried this and the demo broke — every click triggered an extra rerun cycle that made the UI feel laggy and occasionally caused a button-press to be lost between renders. I replaced it with `on_click` callbacks (which Streamlit invokes *before* the script body re-runs, so the new weights are already in effect when scoring happens), and the issue went away. The lesson: AI suggestions need to be evaluated against actual run-time behaviour, not just whether they look correct in isolation.

---

## 10. What Surprised Me During Reliability Testing

The biggest surprise from building the evaluation harness was how *useful* writing assertions in plain English forced me to be specific. I'd been carrying assumptions like "a Pop user obviously gets Pop at the top" without ever testing it — and writing the test caught a real bug. While I was tuning weights mid-development, a stale experiment had silently inverted the genre and energy multipliers (genre +1.0, energy ×2.0 instead of the documented +2.0 / ×1.0). Three of the six harness tests started failing immediately and pointed me right at the broken function. I would not have caught this from manual demo flows alone — the visual top-5 still looked plausible because energy proximity is correlated enough with the user's other choices to mask the weight bug for many profiles. The harness is what made the failure observable.

The second surprise: the determinism test. I assumed determinism was trivially true for a pure-function rule-based system, and the test was almost a placeholder. But it actually catches a real failure mode — if anyone introduces randomness during ranking (`random.shuffle` for tie-breaking, for example), the test fires immediately. It's a cheap regression net for a property the system *promises* in its documentation.

---

## 11. Future Work

- **Mood clustering.** Treat `Sad` / `Melancholic` / `Reflective` as related rather than completely independent.
- **More genres and more songs per genre.** Especially Country, Jazz, Classical, global Pop. The catalogue's Pop dominance is the biggest single limit on result quality.
- **Persistent taste profile.** Save the session weights to disk per user so feedback survives a refresh.
- **Negative preferences.** Let the user say "I never want Hip-Hop" and zero out that genre's score for them. Currently the only way to express a negative is to keep clicking 👎 until the system adapts.
- **Confidence-per-recommendation.** Right now the score is the confidence; in a richer system there's an argument for a separate "we're sure / we're guessing" indicator that reflects, e.g., how thin the catalogue is for the requested genre.
