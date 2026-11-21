"""Interactive Plotly figures for the Eco Impact view.

Only verified figures are used:
* ID=7 (database): roughly 85% of the excess heat from global warming is absorbed
  by the oceans. The remaining 15% is the derived complement.
* Paris Agreement participation (UNFCCC, November 2026): 198 UNFCCC Parties, of
  which 194 (193 countries + the European Union) are in the Paris Agreement.
  These counts are NOT in the Excel file; they are global UN context supplied by
  the EcoNova team, so re-check them before publishing.

No Kipling Institute survey results are ever generated here (ID=3: the survey is
still in its collection and validation phase).
"""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

FOREST = "#1B4332"
LEAF = "#2D6A4F"
MINT = "#D8F3DC"
OFFWHITE = "#F8FAF9"
CHARCOAL = "#1E293B"
OCEAN_BLUE = "#2B7A9B"
WARM = "#E9A23B"
MUTED = "#94A3B8"

# --- Verified baselines -----------------------------------------------------
OCEAN_SHARE_PCT = 85
OTHER_SHARE_PCT = 100 - OCEAN_SHARE_PCT  # 15

PARIS_PARTIES = 194            # 193 countries + the European Union
PARIS_SIGNED_NOT_RATIFIED = 3  # Iran, Libya, Yemen
PARIS_WITHDRAWN = 1            # United States (effective 27 January 2026)
UNFCCC_PARTIES = 198
PARIS_SOURCE_NOTE = (
    "UNFCCC Paris Agreement status, November 2026. Global UN context supplied by the "
    "EcoNova team (not part of the Excel database)."
)

# Illustrative timeframes (years) for the scenario slider.
HEAT_TIMEFRAMES = (1, 5, 10, 25, 50)

# Interactive behaviour for every chart: drag to zoom, pan, reset on double-click.
PLOTLY_CONFIG = {
    "displaylogo": False,
    "displayModeBar": True,
    "scrollZoom": False,
    "doubleClick": "reset",
    "modeBarButtonsToAdd": ["zoom2d", "pan2d", "select2d", "lasso2d", "resetScale2d"],
}


def apply_interactive_layout(fig: go.Figure, title: str) -> go.Figure:
    """Shared EcoNova styling plus full mouse interactivity (box zoom by default)."""
    fig.update_layout(
        title={"text": title, "x": 0.01, "font": {"size": 18, "color": FOREST}},
        dragmode="zoom",
        hovermode="closest",
        paper_bgcolor=OFFWHITE,
        plot_bgcolor="white",
        font={"color": CHARCOAL, "family": "Source Sans 3, Segoe UI, Arial, sans-serif"},
        margin={"l": 50, "r": 30, "t": 70, "b": 50},
        legend={"orientation": "h", "y": -0.15},
    )
    return fig


def heat_split(total_units: float) -> tuple[float, float]:
    """Split ``total_units`` into (ocean, other) with the exact 85/15 baseline."""
    ocean = total_units * OCEAN_SHARE_PCT / 100
    return ocean, total_units - ocean


def build_heat_figure(years: int = 10) -> go.Figure:
    """Chart 1: donut of the 85/15 split + stacked bars for the selected timeframe.

    The bars assume a constant, illustrative rate (1 relative unit per year), so
    only the totals scale with the slider; the 85/15 split never changes.
    """
    shown = [y for y in HEAT_TIMEFRAMES if y <= years] or [HEAT_TIMEFRAMES[0]]
    ocean_vals, other_vals = zip(*(heat_split(float(y)) for y in shown))
    labels = [f"{y} yr" for y in shown]

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.42, 0.58],
        specs=[[{"type": "domain"}, {"type": "xy"}]],
        subplot_titles=("Where the excess heat goes", f"Illustrative cumulative heat (up to {shown[-1]} yr)"),
    )
    fig.add_trace(
        go.Pie(
            labels=["Oceans (roughly 85%)", "Atmosphere, land & ice"],
            values=[OCEAN_SHARE_PCT, OTHER_SHARE_PCT],
            hole=0.55, sort=False, direction="clockwise",
            marker={"colors": [OCEAN_BLUE, WARM], "line": {"color": "white", "width": 2}},
            textinfo="label+percent", hovertemplate="%{label}: %{value}%<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=labels, y=list(ocean_vals), name="Oceans", marker_color=OCEAN_BLUE,
               hovertemplate="%{x}<br>Oceans: %{y:.2f} units (85%)<extra></extra>"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Bar(x=labels, y=list(other_vals), name="Atmosphere, land & ice", marker_color=WARM,
               hovertemplate="%{x}<br>Atmosphere, land & ice: %{y:.2f} units (15%)<extra></extra>"),
        row=1, col=2,
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Relative heat units (illustrative)", row=1, col=2)
    fig.add_annotation(text="85%<br>oceans", x=0.17, y=0.5, showarrow=False,
                       font={"size": 16, "color": FOREST}, xref="paper", yref="paper")
    return apply_interactive_layout(fig, "Where excess global warming heat goes (Gapminder / UN SDG 13)")


def build_paris_figure() -> go.Figure:
    """Chart 2: Paris Agreement participation. One trace per category so the legend filters."""
    categories = [
        ("In the Paris Agreement (193 countries + EU)", PARIS_PARTIES, LEAF),
        ("Signed, not ratified (Iran, Libya, Yemen)", PARIS_SIGNED_NOT_RATIFIED, WARM),
        ("Withdrew, effective 27 Jan 2026 (United States)", PARIS_WITHDRAWN, MUTED),
    ]
    fig = go.Figure()
    for label, count, color in categories:
        fig.add_trace(
            go.Bar(x=[label.split(" (")[0]], y=[count], name=label, marker_color=color,
                   text=[count], textposition="outside",
                   hovertemplate=f"{label}<br>%{{y}} of {UNFCCC_PARTIES} UNFCCC Parties<extra></extra>")
        )
    fig.update_yaxes(title_text="UNFCCC Parties", range=[0, 225])
    fig.update_layout(showlegend=True, barmode="group")
    return apply_interactive_layout(
        fig, f"Global climate cooperation: {PARIS_PARTIES} of {UNFCCC_PARTIES} UNFCCC Parties are in the Paris Agreement"
    )


# Survey areas only describe the *structure* of the dashboard. They hold no data.
SURVEY_PLANNED_AREAS = (
    "Climate awareness",
    "Recycling habits at school",
    "Energy-saving habits",
    "Pollution concerns",
)


def build_survey_placeholder_figure() -> go.Figure:
    """Panel 3: an intentionally empty chart (no traces, no numbers)."""
    fig = go.Figure()
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.add_annotation(
        text="Collection & Validation Phase: no validated survey results yet",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
        font={"size": 15, "color": MUTED},
    )
    return apply_interactive_layout(fig, "Kipling Institute school survey (pending validation)")
