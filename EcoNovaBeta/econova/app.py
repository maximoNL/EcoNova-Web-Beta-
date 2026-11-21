"""EcoNova - Kipling Institute | SDG 4 (Quality Education) & SDG 13 (Climate Action).

Streamlit entry point and navigation router. Run with: streamlit run app.py
"""
from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from src.charts import (
    HEAT_TIMEFRAMES, PARIS_PARTIES, PARIS_SIGNED_NOT_RATIFIED, PARIS_SOURCE_NOTE, PARIS_WITHDRAWN,
    PLOTLY_CONFIG, SURVEY_PLANNED_AREAS, UNFCCC_PARTIES, build_heat_figure, build_paris_figure,
    build_survey_placeholder_figure,
)
from src.data_loader import ContentLoadError, load_content_blocks, missing_required_ids
from src.email_service import submit_feedback
from src.games.eco_school_quest import get_eco_school_quest_html
from src.games.trash_platformer import get_trash_platformer_html
from src.models import ContentBlock, FeedbackSubmission

st.set_page_config(page_title="EcoNova | Kipling Institute", page_icon="🌱", layout="wide")

esc = html.escape

# --------------------------------------------------------------------------- constants
NAV_HOME, NAV_IMPACT, NAV_ACTIONS, NAV_PLAY, NAV_ABOUT = (
    "01 / Home", "02 / Eco Impact", "03 / Green Actions", "04 / Eco-Play Zone", "05 / About Us",
)
NAV_ITEMS = [NAV_HOME, NAV_IMPACT, NAV_ACTIONS, NAV_PLAY, NAV_ABOUT]

# English card headings. Content comes from the database by ID, never by Seccion text.
CARD_HEADINGS = {
    2: "Our mission",
    3: "Environmental reality and our school survey",
    4: "Small habits, real climate action",
    5: "Learn by playing",
    6: "The EcoNova team",
    7: "Climate facts from Gapminder",
}

DAILY_TIPS = [
    "Use both sides of paper",
    "Carry reusable bags or containers",
    "Take only the food you will eat",
    "Walk or share rides to cut transport emissions",
    "Teach a peer a green habit",
]

CORE_HABITS = [
    ("bottle", "Reusable Water Bottle", "Cuts the emissions from producing single-use plastic."),
    ("bin", "Proper Waste Separation", "Reduces the methane that landfills release."),
    ("bulb", "Energy Saving", "Turn off unused lights and unplug chargers."),
]

CHALLENGES = [
    ("Bottle Buddy", ["Bring a reusable water bottle to school.", "Refill it instead of buying single-use bottles.", "Tell a friend why it matters."]),
    ("Bin Detective", ["Check how your school separates waste.", "Sort your own waste into the right bins for a whole day.", "Spot one item in the wrong bin and move it."]),
    ("Lights Out", ["Turn off lights when you leave an empty room.", "Unplug chargers once devices are full.", "Remind one person to do the same."]),
    ("No-Waste Lunch", ["Pack your lunch in reusable containers.", "Take only the food you will eat.", "Bring leftovers home instead of throwing them away."]),
    ("Share the Page", ["Use both sides of the paper for notes.", "Share one handout with a classmate instead of printing two.", "Reuse scrap paper for drafts."]),
    ("Walk & Notice", ["Walk or share a ride for one trip this week.", "On the way, notice three things about nature or pollution around you.", "Tell a peer what you noticed."]),
]

TEAMS = [
    ("UX/UI", "User research and interface design"),
    ("Developers", "Building the interactive web platform"),
    ("Marketing", "Climate communication"),
    ("Advertising", "Visual resources"),
]

DEMO_LEADERBOARD = [("Green Panda", 1850), ("Leafy Fox", 1620), ("Wave Rider", 1475), ("Solar Owl", 1310), ("Recycle Bear", 1190)]

ICONS = {
    "globe": "<svg viewBox='0 0 48 48' width='46' height='46'><circle cx='24' cy='24' r='18' fill='#D8F3DC' stroke='#1B4332' stroke-width='2.5'/><path d='M7 24h34M24 6c-8 9-8 27 0 36M24 6c8 9 8 27 0 36' fill='none' stroke='#2D6A4F' stroke-width='2'/></svg>",
    "sprout": "<svg viewBox='0 0 48 48' width='46' height='46'><path d='M24 43V22' stroke='#1B4332' stroke-width='3' stroke-linecap='round'/><path d='M24 25C24 14 16 9 7 9c0 10 7 16 17 16z' fill='#2D6A4F'/><path d='M24 30c0-8 6-13 17-13 0 10-7 15-17 15z' fill='#74c69d'/></svg>",
    "gamepad": "<svg viewBox='0 0 48 48' width='46' height='46'><rect x='4' y='14' width='40' height='22' rx='11' fill='#D8F3DC' stroke='#1B4332' stroke-width='2.5'/><path d='M15 20v10M10 25h10' stroke='#2D6A4F' stroke-width='3' stroke-linecap='round'/><circle cx='32' cy='22' r='2.6' fill='#2D6A4F'/><circle cx='37' cy='28' r='2.6' fill='#1B4332'/></svg>",
    "bottle": "<svg viewBox='0 0 48 48' width='46' height='46'><rect x='19' y='4' width='10' height='6' rx='2' fill='#2D6A4F'/><path d='M20 10h8v6c5 3 7 6 7 11v13a3 3 0 0 1-3 3H16a3 3 0 0 1-3-3V27c0-5 2-8 7-11z' fill='#D8F3DC' stroke='#1B4332' stroke-width='2.5'/><rect x='13' y='28' width='22' height='8' fill='#74c69d'/></svg>",
    "bin": "<svg viewBox='0 0 48 48' width='46' height='46'><rect x='8' y='9' width='32' height='6' rx='2' fill='#1B4332'/><path d='M11 15h26l-2 26a3 3 0 0 1-3 3H16a3 3 0 0 1-3-3z' fill='#D8F3DC' stroke='#1B4332' stroke-width='2.5'/><path d='M20 24l4-4 4 4M28 32l-4 4-4-4' fill='none' stroke='#2D6A4F' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "bulb": "<svg viewBox='0 0 48 48' width='46' height='46'><path d='M24 5a14 14 0 0 0-8 25c2 2 2 4 2 6h12c0-2 0-4 2-6A14 14 0 0 0 24 5z' fill='#D8F3DC' stroke='#1B4332' stroke-width='2.5'/><path d='M18 41h12M20 45h8' stroke='#1B4332' stroke-width='3' stroke-linecap='round'/><path d='M24 14l-4 8h8l-4 8' fill='none' stroke='#2D6A4F' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/></svg>",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=Source+Sans+3:wght@400;600;700&display=swap');
html, body, .stApp, [class*="st-"] { font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif; }
h1, h2, h3, .en-hero h1 { font-family: 'Bricolage Grotesque', 'Segoe UI', Arial, sans-serif !important; color: #1B4332; letter-spacing: -0.01em; }
.en-hero { display: flex; align-items: center; justify-content: space-between; gap: 24px; background: linear-gradient(120deg, #1B4332 0%, #2D6A4F 70%); color: #F8FAF9; border-radius: 22px; padding: 38px 44px; margin-bottom: 18px; }
.en-hero h1 { color: #F8FAF9 !important; font-size: clamp(2.4rem, 6vw, 4.2rem); margin: 0 0 6px 0; padding: 0; line-height: 1.0; }
.en-hero p { margin: 0; font-size: 1.2rem; color: #D8F3DC; max-width: 34ch; }
.en-card { background: #fff; border: 1px solid #cfe5d6; border-left: 6px solid #2D6A4F; border-radius: 14px; padding: 16px 22px; margin: 10px 0 6px 0; color: #1E293B; }
.en-card h3 { margin: 0 0 6px 0; font-size: 1.25rem; }
.en-info { font-size: 1.05rem; line-height: 1.55; margin: 0 0 8px 0; max-width: 78ch; }
.en-source { font-size: 0.85rem; color: #475569; margin: 0; }
.en-tile { background: #D8F3DC; border-radius: 14px; padding: 16px 18px; min-height: 140px; color: #1E293B; }
.en-tile h4 { margin: 8px 0 4px 0; color: #1B4332; font-family: 'Bricolage Grotesque', sans-serif; }
.en-tile p { margin: 0; font-size: 0.95rem; }
.en-badge { display: inline-block; background: #FFF3CD; color: #7a5200; border: 1px solid #f0c75e; border-radius: 999px; padding: 4px 14px; font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; }
.en-badge.ok { background: #D8F3DC; color: #1B4332; border-color: #74c69d; }
.en-demo { background: #fff; border: 2px dashed #2D6A4F; border-radius: 14px; padding: 12px 16px; }
.en-demo table { width: 100%; border-collapse: collapse; }
.en-demo td { padding: 5px 2px; border-bottom: 1px solid #e2efe6; }
.en-demo td:last-child { text-align: right; font-weight: 700; color: #1B4332; }
section[data-testid="stSidebar"] { border-right: 1px solid #b7e4c7; }
</style>
"""

# --------------------------------------------------------------------------- state & helpers
def init_state() -> None:
    st.session_state.setdefault("nav", NAV_HOME)
    st.session_state.setdefault("tips_done", set())
    st.session_state.setdefault("challenges_done", set())


def go_to(view: str) -> None:
    """Button callback: jump to a view (runs before the next render)."""
    st.session_state["nav"] = view


def go_to_explore_choice() -> None:
    st.session_state["nav"] = st.session_state["explore_choice"]


def eco_progress() -> tuple[int, int]:
    done = len(st.session_state["tips_done"]) + len(st.session_state["challenges_done"])
    return done, len(DAILY_TIPS) + len(CHALLENGES)


@st.cache_data(show_spinner=False)
def get_blocks() -> dict[int, ContentBlock]:
    return {block.id: block for block in load_content_blocks()}


def render_content_card(block: ContentBlock) -> None:
    """Show database text verbatim, its source, and a View Source button only for real URLs."""
    parts = [f'<div class="en-card"><h3>{esc(CARD_HEADINGS.get(block.id, ""))}</h3>']
    parts.append(f'<p class="en-info">{esc(block.information).replace(chr(10), "<br>")}</p>')
    if block.source:
        parts.append(f'<p class="en-source"><strong>Source:</strong> {esc(block.source)}</p>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
    if block.has_valid_link:
        st.link_button("View Source", block.link)


def icon_tile(icon: str, title: str, text: str) -> str:
    return f'<div class="en-tile">{ICONS[icon]}<h4>{esc(title)}</h4><p>{esc(text)}</p></div>'


def render_tracker() -> None:
    done, total = eco_progress()
    st.markdown("**Your eco-progress**")
    st.progress(done / total, text=f"{done} of {total} actions completed")
    finished = [c for i, (c, _) in enumerate(CHALLENGES) if i in st.session_state["challenges_done"]]
    if finished:
        st.caption("Challenges done: " + ", ".join(finished))


# --------------------------------------------------------------------------- views
def view_home(blocks: dict[int, ContentBlock]) -> None:
    st.markdown(
        '<div class="en-hero"><div><h1>EcoNova</h1><p>A greener future starts with us — Kipling Institute · SDG 4 &amp; SDG 13</p></div>'
        "<svg viewBox='0 0 120 120' width='120' height='120' aria-hidden='true'><circle cx='60' cy='60' r='50' fill='none' stroke='#74c69d' stroke-width='3'/>"
        "<circle cx='60' cy='60' r='34' fill='#D8F3DC'/><path d='M60 96V56' stroke='#1B4332' stroke-width='5' stroke-linecap='round'/>"
        "<path d='M60 60C60 40 46 32 28 32c0 18 12 28 32 28z' fill='#2D6A4F'/><path d='M60 70c0-14 10-22 30-22 0 18-12 26-30 26z' fill='#40916c'/></svg></div>",
        unsafe_allow_html=True,
    )
    render_content_card(blocks[2])
    st.markdown("### Where would you like to start?")
    cols = st.columns(3)
    quick = [
        ("globe", "Understand the Impact", "See verified climate facts and explore interactive charts.", NAV_IMPACT),
        ("sprout", "Try a Green Action", "Build daily habits and complete six green challenges.", NAV_ACTIONS),
        ("gamepad", "Learn Through Play", "Play two games and test what you know.", NAV_PLAY),
    ]
    for col, (icon, title, text, target) in zip(cols, quick):
        with col:
            st.markdown(icon_tile(icon, title, text), unsafe_allow_html=True)
            st.button(title, key=f"quick_{target}", on_click=go_to, args=(target,))
    with st.expander("Explore Actions"):
        st.selectbox("Jump to a section", NAV_ITEMS[1:], key="explore_choice")
        st.button("Go to section", key="explore_go", on_click=go_to_explore_choice)


def view_impact(blocks: dict[int, ContentBlock]) -> None:
    st.title("Eco Impact")
    render_content_card(blocks[3])
    render_content_card(blocks[7])

    st.markdown("### Chart 1: Where excess global warming heat goes")
    st.markdown('<span class="en-badge ok">Verified: Gapminder / UN SDG 13</span>', unsafe_allow_html=True)
    years = st.select_slider(
        "Scenario timeframe (illustrative)", options=list(HEAT_TIMEFRAMES), value=10, key="heat_years",
        format_func=lambda y: f"{y} year" + ("" if y == 1 else "s"),
    )
    st.plotly_chart(build_heat_figure(years), config=PLOTLY_CONFIG, theme=None)
    st.caption(
        "Only the split is verified: roughly 85% of the excess heat goes to the oceans, and the rest "
        "(about 15%) to the atmosphere, land and ice. The bars assume a constant rate to show how totals "
        "could grow over time. The slider never changes the 85% baseline. Drag to zoom, double-click to reset."
    )

    st.markdown("### Chart 2: Global climate cooperation (Paris Agreement)")
    st.markdown('<span class="en-badge ok">Verified global UN context</span>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("In the Paris Agreement", f"{PARIS_PARTIES} of {UNFCCC_PARTIES}")
    m2.metric("Signed, not ratified", PARIS_SIGNED_NOT_RATIFIED)
    m3.metric("Withdrew", PARIS_WITHDRAWN)
    st.plotly_chart(build_paris_figure(), config=PLOTLY_CONFIG, theme=None)
    st.caption(PARIS_SOURCE_NOTE + " Click a legend entry to hide or show a category.")

    st.markdown("### Panel 3: Kipling Institute school survey dashboard")
    st.markdown('<span class="en-badge">Collection &amp; Validation Phase — Pending Review</span>', unsafe_allow_html=True)
    st.info("No survey results are shown yet. Results will appear here only after the data has been collected and validated.")
    cols = st.columns(len(SURVEY_PLANNED_AREAS))
    for col, area in zip(cols, SURVEY_PLANNED_AREAS):
        col.metric(area, "Pending")
    st.plotly_chart(build_survey_placeholder_figure(), config=PLOTLY_CONFIG, theme=None)


def view_actions(blocks: dict[int, ContentBlock]) -> None:
    st.title("Green Actions")
    render_content_card(blocks[4])

    st.markdown("### Three core habits")
    for col, (icon, title, text) in zip(st.columns(3), CORE_HABITS):
        with col:
            st.markdown(icon_tile(icon, title, text), unsafe_allow_html=True)

    st.markdown("### Daily tips checklist")
    bar = st.empty()
    done = st.session_state["tips_done"]
    for i, tip in enumerate(DAILY_TIPS):
        checked = st.checkbox(tip, value=i in done, key=f"tip_{i}")
        (done.add if checked else done.discard)(i)
    pct = round(len(done) / len(DAILY_TIPS) * 100)
    bar.progress(pct / 100, text=f"{pct}% of today's tips completed")

    st.markdown("### Six green challenges")
    finished = st.session_state["challenges_done"]
    cols = st.columns(2)
    for i, (title, steps) in enumerate(CHALLENGES):
        with cols[i % 2]:
            with st.expander(title):
                st.markdown("\n".join(f"{n}. {step}" for n, step in enumerate(steps, 1)))
                on = st.toggle("Mark Challenge Completed", value=i in finished, key=f"challenge_{i}")
                (finished.add if on else finished.discard)(i)
                if on:
                    st.success("Challenge completed. Great work!")


def view_play(blocks: dict[int, ContentBlock]) -> None:
    st.title("Eco-Play Zone")
    render_content_card(blocks[5])
    game_a = "Game A: Eco-Runner (Trash Collect & Sort)"
    game_b = "Game B: Eco-School Quiz Quest"
    game_col, board_col = st.columns([3, 1])
    with game_col:
        choice = st.radio("Choose a game", [game_a, game_b], horizontal=True, key="game_choice", label_visibility="collapsed")
        if choice == game_a:
            components.html(get_trash_platformer_html(), height=620)
        else:
            components.html(get_eco_school_quest_html(), height=620)
        st.caption("Click inside the game once so it can read your keyboard.")
    with board_col:
        rows = "".join(f"<tr><td>{i}. {esc(name)}</td><td>{score}</td></tr>" for i, (name, score) in enumerate(DEMO_LEADERBOARD, 1))
        st.markdown(
            f'<div class="en-demo"><h3 style="margin-top:0">Top Eco-Friends (Demo Example)</h3><table>{rows}</table></div>',
            unsafe_allow_html=True,
        )
        st.caption("Visual example — placeholder names until live student scores are connected")


def view_about(blocks: dict[int, ContentBlock]) -> None:
    st.title("About Us")
    render_content_card(blocks[6])
    st.markdown("### Student teams")
    for col, (team, role) in zip(st.columns(4), TEAMS):
        with col:
            st.markdown(f'<div class="en-tile"><h4>{esc(team)}</h4><p>{esc(role)}</p></div>', unsafe_allow_html=True)

    st.markdown("### Share your feedback")
    with st.form("feedback_form"):
        name = st.text_input("Student/Teacher name (optional)", placeholder="Anonymous")
        visited = st.radio("Have you visited EcoNova before?", ["Yes", "No"], index=1, horizontal=True)
        message = st.text_area(
            "What did you learn about SDG 4 & SDG 13, what climate habit will you adopt, and how can we improve EcoNova?",
            height=160,
        )
        rating = st.select_slider("Platform usefulness rating", options=[1, 2, 3, 4, 5], value=4, format_func=lambda n: "★" * n)
        submitted = st.form_submit_button("Send feedback")
    if submitted:
        if not message.strip():
            st.error("Please answer the question about what you learned, your climate habit, and how we can improve.")
            return
        result = submit_feedback(FeedbackSubmission(message=message, visited_before=visited, rating=rating, name=name or "Anonymous"))
        (st.success if result.emailed else st.warning)(result.message)


VIEWS = {NAV_HOME: view_home, NAV_IMPACT: view_impact, NAV_ACTIONS: view_actions, NAV_PLAY: view_play, NAV_ABOUT: view_about}


def main() -> None:
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("## 🌱 EcoNova")
        st.caption("Kipling Institute · SDG 4 & SDG 13")
        st.radio("Navigate", NAV_ITEMS, key="nav", label_visibility="collapsed")
        st.divider()
        tracker_slot = st.empty()  # filled at the end so it never lags behind the page

    try:
        blocks = get_blocks()
    except ContentLoadError as exc:
        st.error(f"The content database could not be loaded: {exc}")
        st.stop()
    missing = missing_required_ids(list(blocks.values()))
    if missing:
        st.error(f"The content database is missing required rows: {missing}")
        st.stop()

    VIEWS[st.session_state["nav"]](blocks)
    with tracker_slot.container():
        render_tracker()


main()
