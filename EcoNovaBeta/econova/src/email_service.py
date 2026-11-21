"""Feedback delivery: Gmail SMTP (SMTP_SSL) with a local CSV backup."""
from __future__ import annotations

import csv
import html
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

from .models import FeedbackSubmission

DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "feedback_submissions.csv"
CSV_FIELDS = ("submitted_at", "name", "visited_before", "rating", "message", "delivery_status")
PLACEHOLDER_PASSWORD = "your_16_char_gmail_app_password"
DEFAULT_RECIPIENT = "empresa.econova@gmail.com"


@dataclass(frozen=True)
class SmtpSettings:
    host: str = "smtp.gmail.com"
    port: int = 465
    sender: str = ""
    password: str = ""
    recipient: str = DEFAULT_RECIPIENT

    @property
    def is_configured(self) -> bool:
        return bool(self.sender and self.password and self.password != PLACEHOLDER_PASSWORD)


@dataclass(frozen=True)
class DeliveryResult:
    status: str  # "sent" | "saved_locally" | "smtp_error"
    message: str

    @property
    def emailed(self) -> bool:
        return self.status == "sent"


def load_smtp_settings() -> SmtpSettings:
    load_dotenv()
    return SmtpSettings(
        host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        port=int(os.getenv("SMTP_PORT", "465")),
        sender=os.getenv("SMTP_SENDER_EMAIL", ""),
        password=os.getenv("SMTP_APP_PASSWORD", ""),
        recipient=os.getenv("ECONOVA_RECIPIENT_EMAIL", DEFAULT_RECIPIENT),
    )


def build_plain_text(sub: FeedbackSubmission) -> str:
    """Structured plain text so Gmail's AI summary can pull out clear action items."""
    return "\n".join([
        "ECONOVA FEEDBACK",
        "Task: summarize this feedback and list concrete CODE improvements and UX improvements.",
        "",
        "RESPONDENT",
        f"- Name: {sub.name}",
        f"- Visited EcoNova before: {sub.visited_before}",
        f"- Submitted at: {sub.submitted_at:%Y-%m-%d %H:%M}",
        "",
        "RATING",
        f"- Platform usefulness: {sub.rating}/5",
        "",
        "FEEDBACK (what they learned about SDG 4 & 13, habit they will adopt, how to improve)",
        sub.message,
        "",
        "TRIAGE (to fill in)",
        "- Code improvements:",
        "- UX improvements:",
        "- Content improvements:",
    ])


def build_html(sub: FeedbackSubmission) -> str:
    esc = html.escape
    message = esc(sub.message).replace("\n", "<br>")
    return (
        "<html><body style='font-family:Arial,sans-serif;color:#1E293B'>"
        "<h2 style='color:#1B4332'>EcoNova feedback</h2>"
        "<p><em>Task: summarize this feedback and list concrete code improvements and UX improvements.</em></p>"
        "<h3>Respondent</h3><ul>"
        f"<li><b>Name:</b> {esc(sub.name)}</li>"
        f"<li><b>Visited EcoNova before:</b> {esc(sub.visited_before)}</li>"
        f"<li><b>Submitted at:</b> {sub.submitted_at:%Y-%m-%d %H:%M}</li></ul>"
        f"<h3>Rating</h3><p><b>Platform usefulness:</b> {sub.rating}/5</p>"
        "<h3>Feedback</h3>"
        f"<blockquote style='border-left:4px solid #2D6A4F;margin:0;padding:6px 12px;background:#D8F3DC'>{message}</blockquote>"
        "<h3>Triage (to fill in)</h3><ul><li>Code improvements:</li><li>UX improvements:</li><li>Content improvements:</li></ul>"
        "</body></html>"
    )


def build_email(sub: FeedbackSubmission, settings: SmtpSettings) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"EcoNova feedback: {sub.rating}/5 usefulness"
    msg["From"] = settings.sender
    msg["To"] = settings.recipient
    msg.set_content(build_plain_text(sub))
    msg.add_alternative(build_html(sub), subtype="html")
    return msg


def _csv_safe(value: object) -> str:
    """Neutralise spreadsheet formula injection in the backup CSV."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text


def append_to_csv(sub: FeedbackSubmission, status: str, path: Path | str = DEFAULT_CSV_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if is_new:
            writer.writerow(CSV_FIELDS)
        writer.writerow([
            sub.submitted_at.isoformat(timespec="seconds"),
            _csv_safe(sub.name), sub.visited_before, sub.rating, _csv_safe(sub.message), status,
        ])
    return path


def send_via_smtp(msg: EmailMessage, settings: SmtpSettings) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.host, settings.port, context=context, timeout=20) as server:
        server.login(settings.sender, settings.password)
        server.send_message(msg)


def submit_feedback(
    sub: FeedbackSubmission,
    settings: SmtpSettings | None = None,
    csv_path: Path | str = DEFAULT_CSV_PATH,
) -> DeliveryResult:
    """Email the feedback through Gmail SMTP and always keep a local CSV copy."""
    settings = settings or load_smtp_settings()
    if not settings.is_configured:
        append_to_csv(sub, "saved_locally_smtp_not_configured", csv_path)
        return DeliveryResult(
            "saved_locally",
            "Saved locally in data/feedback_submissions.csv. Gmail SMTP is not configured yet "
            "(add SMTP_SENDER_EMAIL and SMTP_APP_PASSWORD to .env to send emails).",
        )
    try:
        send_via_smtp(build_email(sub, settings), settings)
    except (smtplib.SMTPException, OSError) as exc:
        append_to_csv(sub, f"smtp_error:{type(exc).__name__}", csv_path)
        return DeliveryResult(
            "smtp_error",
            f"The email could not be sent ({type(exc).__name__}). Your feedback was saved locally instead.",
        )
    append_to_csv(sub, "sent_via_gmail_smtp", csv_path)
    return DeliveryResult("sent", f"Thank you! Your feedback was sent to {settings.recipient} via Gmail SMTP.")
