"""
Streamlit UI — Frutiger Aero / Skeuomorphism Edition
Run:  streamlit run src/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.recommender import load_songs, recommend_songs_detailed

MAX_SCORE = 4.5

AERO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

/* ═══════════════════════════════════════════
   BASE
═══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Nunito', 'Trebuchet MS', 'Arial Rounded MT Bold', sans-serif !important;
    color: #1a2d40;
}

/* Sky-blue Aero gradient background */
.stApp {
    background: linear-gradient(175deg,
        #8ec8f0 0%,
        #b0d9f5 20%,
        #cce8f8 45%,
        #def3fc 70%,
        #edf8ff 100%) !important;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

/* Soft radial cloud highlights */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse at 15% 25%, rgba(255,255,255,0.4) 0%, transparent 45%),
        radial-gradient(ellipse at 85% 10%, rgba(255,255,255,0.3) 0%, transparent 40%),
        radial-gradient(ellipse at 50% 90%, rgba(180,225,250,0.2) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ═══════════════════════════════════════════
   HIDE CHROME — keep header for sidebar toggle
═══════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; box-shadow: none !important; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; }

/* Sidebar expand button — always visible */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display:    flex !important;
    opacity:    1   !important;
    background: linear-gradient(180deg, #ffffff 0%, #ddf0fb 100%) !important;
    border:     1px solid rgba(120, 185, 230, 0.6) !important;
    border-left: none !important;
    border-radius: 0 10px 10px 0 !important;
    box-shadow: 3px 0 10px rgba(80,150,210,0.2) !important;
    color: #3388cc !important;
}

/* ═══════════════════════════════════════════
   TITLE
═══════════════════════════════════════════ */
.aero-title {
    font-size: 2.2rem;
    font-weight: 800;
    font-style: italic;
    letter-spacing: 1px;
    color: #1177cc;
    text-shadow:
        0 2px 8px  rgba(60,140,220,0.25),
        0 1px 0    rgba(255,255,255,0.9);
    margin-bottom: 3px;
}

.aero-subtitle {
    font-size: 0.82rem;
    font-weight: 600;
    color: #4488aa;
    letter-spacing: 0.5px;
    margin-bottom: 1.6rem;
}

/* ═══════════════════════════════════════════
   DIVIDER — aqua line with fade
═══════════════════════════════════════════ */
.aero-divider {
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg,
        transparent 0%,
        #66bbee 30%,
        #88ddff 55%,
        #66bbee 80%,
        transparent 100%);
    margin: 1.2rem 0;
    opacity: 0.7;
}

/* ═══════════════════════════════════════════
   SECTION LABEL
═══════════════════════════════════════════ */
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3388aa;
    margin-bottom: 0.8rem;
}

/* ═══════════════════════════════════════════
   PROFILE TAGS — aqua pill badges
═══════════════════════════════════════════ */
.profile-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 0.4rem;
}

.profile-tag {
    background: linear-gradient(180deg,
        rgba(255,255,255,0.95) 0%,
        rgba(210,238,255,0.85) 100%);
    border: 1px solid rgba(130,195,240,0.6);
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #2a5580;
    box-shadow:
        0 2px 6px  rgba(80,160,220,0.15),
        0 1px 0    rgba(255,255,255,0.9) inset;
}

.profile-tag b { color: #0d77cc; }

/* ═══════════════════════════════════════════
   SONG CARDS — white gloss panel (skeuomorphic)
═══════════════════════════════════════════ */
.aero-card {
    background: linear-gradient(180deg, #ffffff 0%, #eef7ff 100%);
    border: 1px solid rgba(130, 200, 240, 0.5);
    border-radius: 14px;
    padding: 18px 20px 16px 24px;
    margin-bottom: 12px;
    box-shadow:
        0 5px 18px  rgba(70, 145, 210, 0.18),
        0 1px 0     rgba(255,255,255,1) inset,
        0 -1px 0    rgba(130,200,240,0.2) inset;
    position: relative;
    overflow: hidden;
}

/* Top gloss sheen */
.aero-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 46%;
    background: linear-gradient(180deg,
        rgba(255,255,255,0.65) 0%,
        rgba(255,255,255,0.0)  100%);
    border-radius: 14px 14px 0 0;
    pointer-events: none;
}

/* Left aqua accent bar */
.aero-card::before {
    content: '';
    position: absolute;
    top: 14px; left: 0;
    width: 4px;
    height: calc(100% - 28px);
    background: linear-gradient(180deg, #44ccff, #1199dd);
    border-radius: 0 4px 4px 0;
    box-shadow: 0 0 6px rgba(40,170,240,0.4);
}

.rank-badge {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #55aad4;
    margin-bottom: 2px;
}

.song-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #0f1e30;
    margin-bottom: 1px;
}

.song-artist {
    font-size: 0.8rem;
    font-weight: 600;
    color: #4a6a88;
    letter-spacing: 0.3px;
    margin-bottom: 10px;
}

.song-meta {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}

.meta-chip {
    font-size: 0.68rem;
    font-weight: 700;
    color: #2a5577;
    background: linear-gradient(180deg, #e4f4ff 0%, #cce8f8 100%);
    border: 1px solid rgba(120,195,235,0.4);
    border-radius: 20px;
    padding: 2px 11px;
    box-shadow: 0 1px 3px rgba(80,160,215,0.12);
}

/* ═══════════════════════════════════════════
   TOTAL SCORE ROW
═══════════════════════════════════════════ */
.score-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}

.score-value {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0d77cc;
    min-width: 62px;
    text-shadow: 0 1px 4px rgba(0,100,200,0.2);
}

.score-denom {
    font-size: 0.7rem;
    font-weight: 600;
    color: #7aaac4;
    white-space: nowrap;
}

.total-bar-bg {
    flex: 1;
    height: 11px;
    background: rgba(180, 225, 248, 0.35);
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid rgba(130,200,240,0.3);
    box-shadow: inset 0 1px 3px rgba(80,155,215,0.2);
}

.total-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #29aaea 0%, #66d4ff 60%, #3bbfee 100%);
    box-shadow: 0 1px 5px rgba(30,160,235,0.4);
    position: relative;
}

/* Gloss on total bar */
.total-bar-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 50%;
    background: rgba(255,255,255,0.35);
    border-radius: 99px 99px 0 0;
}

/* ═══════════════════════════════════════════
   BREAKDOWN GRID
═══════════════════════════════════════════ */
.breakdown-grid {
    display: grid;
    grid-template-columns: 52px 1fr 48px;
    row-gap: 8px;
    align-items: center;
}

.bar-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6699bb;
    text-align: right;
    padding-right: 10px;
}

.bar-track {
    height: 9px;
    background: rgba(180,225,248,0.28);
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid rgba(130,200,240,0.22);
    box-shadow: inset 0 1px 2px rgba(80,155,215,0.15);
}

/* Each breakdown bar colour — all in the sky-blue / aqua / teal family */
.bar-genre {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #0d99dd, #44ccff);
    box-shadow: 0 1px 3px rgba(15,150,225,0.35);
}

.bar-mood {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #1a88cc, #55bbee);
    box-shadow: 0 1px 3px rgba(25,140,210,0.35);
}

.bar-energy {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #22aacc, #55ddee);
    box-shadow: 0 1px 3px rgba(30,175,215,0.35);
}

.bar-acoustic {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #33aa77, #66dd99);
    box-shadow: 0 1px 3px rgba(40,170,120,0.35);
}

.bar-pts {
    font-size: 0.68rem;
    font-weight: 700;
    color: #3377aa;
    text-align: right;
    padding-left: 8px;
    font-variant-numeric: tabular-nums;
}

/* ═══════════════════════════════════════════
   SIDEBAR — light Aero glass panel
═══════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        rgba(205, 235, 255, 0.96) 0%,
        rgba(185, 225, 252, 0.96) 100%) !important;
    border-right: 1px solid rgba(130, 195, 240, 0.45) !important;
    box-shadow: 4px 0 18px rgba(80,150,215,0.12) !important;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #0d77cc !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.5px !important;
}

section[data-testid="stSidebar"] label {
    color: #1a4466 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
}

/* Dropdown inputs */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(130,195,240,0.6) !important;
    border-radius: 8px !important;
    color: #1a2d40 !important;
}

/* Glossy aqua primary button */
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(180deg,
        #66d0f5 0%,
        #22aaee 45%,
        #0088cc 100%) !important;
    border: 1px solid #0099dd !important;
    border-bottom: 2px solid #0077bb !important;
    color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0,60,120,0.4) !important;
    border-radius: 22px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    box-shadow:
        0 3px 10px rgba(0,130,220,0.35),
        0 1px 0    rgba(255,255,255,0.35) inset !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(180deg,
        #88deff 0%,
        #33bbff 45%,
        #1199dd 100%) !important;
    box-shadow:
        0 5px 16px rgba(0,130,220,0.45),
        0 1px 0    rgba(255,255,255,0.35) inset !important;
    transform: translateY(-1px) !important;
}

/* ═══════════════════════════════════════════
   WELCOME STATE
═══════════════════════════════════════════ */
.welcome-state {
    margin-top: 4rem;
    text-align: center;
}

.welcome-glyph {
    font-size: 4rem;
    display: block;
    margin-bottom: 0.8rem;
    color: #33aadd;
    text-shadow:
        0 4px 16px rgba(30,155,225,0.35),
        0 2px 0    rgba(255,255,255,0.7);
}

.welcome-text {
    color: #4477aa;
    font-size: 0.88rem;
    font-weight: 600;
    line-height: 2;
}
</style>
"""


@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")


def _bar_row(label: str, pts: float, max_pts: float, bar_class: str) -> str:
    pct = (pts / max_pts * 100) if max_pts > 0 else 0
    return (
        f'<div class="bar-label">{label}</div>'
        f'<div class="bar-track">'
        f'<div class="{bar_class}" style="width:{pct:.1f}%"></div>'
        f'</div>'
        f'<div class="bar-pts">+{pts:.2f}</div>'
    )


def _song_card(rank: int, result: dict, likes_acoustic: bool) -> str:
    b = result["breakdown"]
    total_pct = min(result["score"] / MAX_SCORE * 100, 100)
    acoustic_row = (
        _bar_row("ACST", b["acoustic"], 0.5, "bar-acoustic")
        if likes_acoustic else ""
    )
    return f"""
<div class="aero-card">
  <div class="rank-badge">★ Rank {rank:02d}</div>
  <div class="song-title">{result['title']}</div>
  <div class="song-artist">{result['artist']}</div>
  <div class="song-meta">
    <span class="meta-chip">{result['genre']}</span>
    <span class="meta-chip">{result['mood']}</span>
    <span class="meta-chip">Energy {result['energy']:.2f}</span>
    <span class="meta-chip">Acoustic {result['acousticness']:.2f}</span>
  </div>
  <div class="score-row">
    <div class="score-value">{result['score']:.2f}</div>
    <div class="score-denom">/ {MAX_SCORE:.1f} pts</div>
    <div class="total-bar-bg">
      <div class="total-bar-fill" style="width:{total_pct:.1f}%"></div>
    </div>
  </div>
  <div class="breakdown-grid">
    {_bar_row('Genre',  b['genre'],  2.0, 'bar-genre')}
    {_bar_row('Mood',   b['mood'],   1.0, 'bar-mood')}
    {_bar_row('Energy', b['energy'], 1.0, 'bar-energy')}
    {acoustic_row}
  </div>
</div>
"""


def main():
    st.set_page_config(page_title="VibeCipher", page_icon="🎵", layout="wide")
    st.markdown(AERO_CSS, unsafe_allow_html=True)

    songs  = get_songs()
    genres = sorted({s["genre"] for s in songs})
    moods  = sorted({s["mood"]  for s in songs})

    # ── Sidebar ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🎵 Taste Profile")
        genre          = st.selectbox("Genre", genres)
        mood           = st.selectbox("Mood", moods)
        energy         = st.slider("Energy Level", 0.0, 1.0, 0.5, step=0.05,
                                   help="0.0 = very calm  ·  1.0 = maximum energy")
        likes_acoustic = st.checkbox("I like acoustic songs", value=False)
        st.markdown("<br>", unsafe_allow_html=True)
        find_btn = st.button("► Find My Songs", use_container_width=True)

    # ── Page header ───────────────────────────────────────────
    st.markdown('<div class="aero-title">♫ VibeCipher</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="aero-subtitle">'
        'AI Music Recommender &nbsp;·&nbsp; Rule-Based Scoring Engine'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Welcome state ─────────────────────────────────────────
    if not find_btn:
        st.markdown("""
        <div class="welcome-state">
          <span class="welcome-glyph">♫</span>
          <div class="welcome-text">
            Choose your genre, mood, and energy level in the sidebar,<br>
            then click <strong>Find My Songs</strong> to get recommendations.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Active profile ────────────────────────────────────────
    st.markdown('<div class="aero-divider"></div>', unsafe_allow_html=True)
    acoustic_tag = (
        '<div class="profile-tag">Acoustic &nbsp;<b>On</b></div>'
        if likes_acoustic else ""
    )
    st.markdown(f"""
    <div class="section-label">Your Taste Profile</div>
    <div class="profile-row">
      <div class="profile-tag">Genre &nbsp;<b>{genre}</b></div>
      <div class="profile-tag">Mood &nbsp;<b>{mood}</b></div>
      <div class="profile-tag">Energy &nbsp;<b>{energy:.2f}</b></div>
      {acoustic_tag}
    </div>
    """, unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────
    st.markdown('<div class="aero-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-label">Top Matches &nbsp;·&nbsp; Score Breakdown</div>',
        unsafe_allow_html=True,
    )

    user_prefs = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
    }
    results = recommend_songs_detailed(user_prefs, songs, k=5)

    for rank, result in enumerate(results, start=1):
        st.markdown(_song_card(rank, result, likes_acoustic), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
