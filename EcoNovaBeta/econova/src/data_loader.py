"""Excel ingestion for EcoNova: row filtering, validation and verbatim loading."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import ContentBlock

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "BASE_DE_DATOS_ODS_4_y_13.xlsx"
SHEET_NAME = "Hoja1"
EXPECTED_COLUMNS = ("ID", "Seccion", "Tema", "Información", "Fuente", "Enlace")
TEMPLATE_ROW_ID = 1  # internal template instructions, never publishable
REQUIRED_IDS = (2, 3, 4, 5, 6, 7)


class ContentLoadError(RuntimeError):
    """Raised when the content database cannot be read or is malformed."""


def _clean(value: object) -> str:
    """Return the cell as text, or "" for NaN/None. Text is never altered."""
    if value is None or (isinstance(value, float) and pd.isna(value)) or pd.isna(value):
        return ""
    return str(value)


def load_content_blocks(path: Path | str = DEFAULT_DATA_PATH) -> list[ContentBlock]:
    """Load publishable rows: skips ID 1 and any row without ``Información``."""
    path = Path(path)
    if not path.exists():
        raise ContentLoadError(f"Content database not found: {path}")
    try:
        frame = pd.read_excel(path, sheet_name=SHEET_NAME, engine="openpyxl", dtype=object)
    except ValueError as exc:  # missing sheet
        raise ContentLoadError(f"Sheet '{SHEET_NAME}' could not be read: {exc}") from exc

    missing = [col for col in EXPECTED_COLUMNS if col not in frame.columns]
    if missing:
        raise ContentLoadError(f"Missing expected columns: {', '.join(missing)}")

    blocks: list[ContentBlock] = []
    for _, row in frame.iterrows():
        raw_id = pd.to_numeric(row["ID"], errors="coerce")
        if pd.isna(raw_id):
            continue
        row_id = int(raw_id)
        if row_id == TEMPLATE_ROW_ID:
            continue
        information = _clean(row["Información"])
        if not information.strip():
            continue  # incomplete rows (e.g. ID 8, 9, 10) are never rendered
        blocks.append(
            ContentBlock(
                id=row_id,
                section=_clean(row["Seccion"]),
                topic=_clean(row["Tema"]),
                information=information,
                source=_clean(row["Fuente"]),
                link=_clean(row["Enlace"]),
            )
        )
    return blocks


def blocks_by_id(blocks: list[ContentBlock]) -> dict[int, ContentBlock]:
    return {block.id: block for block in blocks}


def missing_required_ids(blocks: list[ContentBlock]) -> list[int]:
    present = {block.id for block in blocks}
    return [i for i in REQUIRED_IDS if i not in present]
