"""Content loading: ID=1 and incomplete rows are ignored, ID=2..7 load verbatim."""
import openpyxl
import pytest

from src.data_loader import (
    DEFAULT_DATA_PATH, ContentLoadError, blocks_by_id, load_content_blocks, missing_required_ids,
)
from src.models import is_valid_http_url

HEADERS = ["ID", "Seccion", "Tema", "Información", "Fuente", "Enlace"]


def _workbook(tmp_path, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hoja1"
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    path = tmp_path / "db.xlsx"
    wb.save(path)
    return path


def test_real_database_loads_only_ids_2_to_7():
    blocks = load_content_blocks(DEFAULT_DATA_PATH)
    assert [b.id for b in blocks] == [2, 3, 4, 5, 6, 7]
    assert missing_required_ids(blocks) == []


def test_information_is_verbatim():
    ws = openpyxl.load_workbook(DEFAULT_DATA_PATH)["Hoja1"]
    raw = {row[0].value: row[3].value for row in ws.iter_rows(min_row=2) if row[0].value}
    for block in load_content_blocks(DEFAULT_DATA_PATH):
        assert block.information == raw[block.id]


def test_template_and_empty_rows_are_ignored(tmp_path):
    path = _workbook(tmp_path, [
        [1, "Template", "Instructions", "internal notes", "x", "x"],
        [2, "Home", "Intro", "Real text", "Source", "https://example.org"],
        [8, "Green Action", "Pending", None, None, None],
        [9, "About us", "Pending", "   ", None, None],
        [10, None, None, None, None, None],
    ])
    assert [b.id for b in load_content_blocks(path)] == [2]


def test_link_validation():
    assert is_valid_http_url("https://www.un.org/")
    assert is_valid_http_url("http://example.org/a")
    assert not is_valid_http_url("No hay")
    assert not is_valid_http_url("")
    assert not is_valid_http_url(None)
    assert not is_valid_http_url("ftp://example.org")


def test_about_us_has_no_source_button():
    blocks = blocks_by_id(load_content_blocks(DEFAULT_DATA_PATH))
    assert blocks[6].link == "No hay"
    assert not blocks[6].has_valid_link
    assert blocks[2].has_valid_link


def test_gapminder_block_mentions_85_percent():
    assert "85%" in blocks_by_id(load_content_blocks(DEFAULT_DATA_PATH))[7].information


def test_missing_file_raises(tmp_path):
    with pytest.raises(ContentLoadError):
        load_content_blocks(tmp_path / "nope.xlsx")
