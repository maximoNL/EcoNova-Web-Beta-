"""Email payload formatting, CSV logging and mocked SMTP dispatch."""
import csv
import smtplib
from datetime import datetime

from src import email_service as es
from src.models import FeedbackSubmission

CONFIGURED = es.SmtpSettings(sender="me@gmail.com", password="abcdabcdabcdabcd")
UNCONFIGURED = es.SmtpSettings(sender="", password=es.PLACEHOLDER_PASSWORD)


def _sub(**kw):
    base = dict(message="Loved the games.\nMore levels please!", visited_before="Yes", rating=5,
                name="Ana", submitted_at=datetime(2026, 11, 20, 10, 30))
    base.update(kw)
    return FeedbackSubmission(**base)


def test_defaults_and_normalisation():
    sub = FeedbackSubmission(message=" hi ", name="  \n ", rating=99)
    assert sub.name == "Anonymous" and sub.rating == 5 and sub.message == "hi"


def test_email_has_plain_and_html_parts_and_recipient():
    msg = es.build_email(_sub(), CONFIGURED)
    assert msg["To"] == "empresa.econova@gmail.com"
    assert "5/5" in msg["Subject"]
    plain = msg.get_body(("plain",)).get_content()
    assert "RESPONDENT" in plain and "- Name: Ana" in plain and "Loved the games." in plain
    html_part = msg.get_body(("html",)).get_content()
    assert "<h2" in html_part and "Loved the games.<br>More levels" in html_part


def test_html_is_escaped_and_name_cannot_inject_headers():
    sub = _sub(message="<script>alert(1)</script>", name="Eve\r\nBcc: x@y.z")
    msg = es.build_email(sub, CONFIGURED)
    assert "<script>" not in msg.get_body(("html",)).get_content()
    assert "\n" not in sub.name and msg["Bcc"] is None


def test_csv_backup_header_rows_and_formula_guard(tmp_path):
    path = tmp_path / "fb.csv"
    es.append_to_csv(_sub(), "sent", path)
    es.append_to_csv(_sub(message="=HYPERLINK(1)"), "saved", path)
    rows = list(csv.reader(path.open(encoding="utf-8")))
    assert tuple(rows[0]) == es.CSV_FIELDS and len(rows) == 3
    assert rows[2][4].startswith("'=")


def test_not_configured_saves_locally(tmp_path):
    path = tmp_path / "fb.csv"
    result = es.submit_feedback(_sub(), UNCONFIGURED, path)
    assert result.status == "saved_locally" and not result.emailed and path.exists()


def test_successful_send_uses_smtp_ssl(tmp_path, monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, **kwargs):
            calls["init"] = (host, port)
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            return False
        def login(self, user, password):
            calls["login"] = (user, password)
        def send_message(self, msg):
            calls["sent"] = msg

    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTP)
    path = tmp_path / "fb.csv"
    result = es.submit_feedback(_sub(), CONFIGURED, path)
    assert result.emailed and calls["init"] == ("smtp.gmail.com", 465)
    assert calls["login"] == ("me@gmail.com", "abcdabcdabcdabcd")
    assert calls["sent"]["To"] == "empresa.econova@gmail.com"
    assert "sent_via_gmail_smtp" in path.read_text(encoding="utf-8")


def test_smtp_failure_falls_back_to_csv(tmp_path, monkeypatch):
    def boom(*args, **kwargs):
        raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(smtplib, "SMTP_SSL", boom)
    path = tmp_path / "fb.csv"
    result = es.submit_feedback(_sub(), CONFIGURED, path)
    assert result.status == "smtp_error" and path.exists()
