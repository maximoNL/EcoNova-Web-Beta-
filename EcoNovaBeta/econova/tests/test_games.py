"""Sanity checks for the embedded HTML5 games (content, structure, safety)."""
import re

from src.games import eco_school_quest as quest
from src.games import trash_platformer as runner


def test_runner_has_ten_levels_and_all_waste_items():
    html = runner.get_trash_platformer_html()
    assert runner.LEVELS == 10 and "<canvas" in html
    for name in ("Newspaper", "Plastic Bottle", "Glass Jar", "Banana Peel",
                 "Cardboard Box", "Plastic Cup", "Glass Bottle", "Apple Core"):
        assert name in html
    for label in ("Paper/Cardboard", "Plastic", "Glass", "Organic"):
        assert label in html
    assert "Secret SDG 13 Climate Action Message" in html


def test_runner_items_map_to_real_bins():
    bins = {b["id"] for b in runner.BINS}
    assert all(item["bin"] in bins for item in runner.WASTE_ITEMS)


def test_quest_has_seven_notebooks_with_three_questions_each():
    assert quest.NOTEBOOKS == 7 and len(quest.QUIZ) == 7
    for notebook in quest.QUIZ:
        assert len(notebook) == 3
        for item in notebook:
            assert len(item["o"]) == 4 and 0 <= item["a"] < 4 and item["hint"]
    assert quest.SECONDS_PER_QUESTION == 20


def test_games_have_no_external_assets_or_scary_content():
    for html in (runner.get_trash_platformer_html(), quest.get_eco_school_quest_html()):
        assert not re.search(r"(src|href)=[\"']https?://", html)
        assert "AudioContext" not in html and "<audio" not in html
        assert "__CONFIG__" not in html
