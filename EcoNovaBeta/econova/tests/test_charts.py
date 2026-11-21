"""Chart maths (exact 85% / 15%) and Plotly interactivity configuration."""
import pytest

from src import charts


def test_baseline_is_exact_85_15():
    assert charts.OCEAN_SHARE_PCT == 85
    assert charts.OTHER_SHARE_PCT == 15
    assert charts.OCEAN_SHARE_PCT + charts.OTHER_SHARE_PCT == 100


@pytest.mark.parametrize("total", [1, 5, 10, 25, 50])
def test_heat_split_keeps_share_at_any_timeframe(total):
    ocean, other = charts.heat_split(total)
    assert ocean == pytest.approx(total * 0.85)
    assert other == pytest.approx(total * 0.15)
    assert ocean + other == pytest.approx(total)


@pytest.mark.parametrize("years", charts.HEAT_TIMEFRAMES)
def test_donut_never_changes_with_slider(years):
    pie = charts.build_heat_figure(years).data[0]
    assert list(pie.values) == [85, 15]


def test_every_figure_supports_box_zoom():
    for fig in (charts.build_heat_figure(), charts.build_paris_figure(), charts.build_survey_placeholder_figure()):
        assert fig.layout.dragmode == "zoom"
    assert charts.PLOTLY_CONFIG["doubleClick"] == "reset"
    assert "zoom2d" in charts.PLOTLY_CONFIG["modeBarButtonsToAdd"]


def test_paris_categories_add_up_to_unfccc_total():
    fig = charts.build_paris_figure()
    assert sum(trace.y[0] for trace in fig.data) == charts.UNFCCC_PARTIES == 198
    assert len(fig.data) == 3  # one trace each, so the legend can filter


def test_survey_panel_has_no_fabricated_data():
    assert len(charts.build_survey_placeholder_figure().data) == 0
