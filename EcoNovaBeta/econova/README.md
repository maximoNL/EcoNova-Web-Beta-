# EcoNova (Kipling Institute · SDG 4 & SDG 13)

Interactive Streamlit app with Plotly charts and two HTML5 Canvas games.

## Run it (VS Code)
1. `python -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in the Gmail app password (optional: without it, feedback is saved to `data/feedback_submissions.csv`)
4. `streamlit run app.py`, or press F5 with the "EcoNova: streamlit run app.py" launch configuration
5. Tests: `pytest`

## Notes
- Page text comes from `data/BASE_DE_DATOS_ODS_4_y_13.xlsx` (rows ID 2-7), shown verbatim. Row ID 1 and incomplete rows are skipped.
- The Paris Agreement counts (194 of 198 UNFCCC Parties) are not in the Excel file. They are global UN context in `src/charts.py`; re-check them before publishing.
- The school survey is in its validation phase, so no survey results are shown.
