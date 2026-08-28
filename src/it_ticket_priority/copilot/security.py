"""Deterministic input controls for PII, secrets, and prompt injection."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from .models import GuardrailReport, RedactionEvent

MAX_PROMPT_TEXT_LENGTH = 4_000

_SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "email",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "<REDACTED_EMAIL>",
    ),
    (
        "phone",
        re.compile(r"(?<!\w)(?:\+?\d[\d .()/-]{7,}\d)(?!\w)"),
        "<REDACTED_PHONE>",
    ),
    (
        "employee_identifier",
        re.compile(
            r"(?i)\b(?:employee|emp|user)[ _-]?id\s*[:=#-]?\s*[A-Z0-9][A-Z0-9_-]{3,}\b"
        ),
        "<REDACTED_EMPLOYEE_ID>",
    ),
    (
        "secret",
        re.compile(
            r"(?i)\b(?:api[ _-]?key|access[ _-]?token|bearer[ _-]?token|password|passwd|secret)"
            r"\s*[:=]\s*[^\s,;]+"
        ),
        "<REDACTED_SECRET>",
    ),
)

_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_previous_instructions",
        re.compile(r"(?i)\bignore\b.{0,40}\b(?:previous|prior|all)\b.{0,30}\binstructions?\b"),
    ),
    (
        "disregard_policy",
        re.compile(r"(?i)\bdisregard\b.{0,50}\b(?:instructions?|rules?|policy|guardrails?)\b"),
    ),
    (
        "reveal_hidden_prompt",
        re.compile(
            r"(?i)\b(?:reveal|show|print|leak|expose)\b.{0,60}"
            r"\b(?:system prompt|developer message|hidden instructions?)\b"
        ),
    ),
    (
        "override_guardrails",
        re.compile(r"(?i)\b(?:override|bypass|disable)\b.{0,40}\b(?:safety|policy|guardrails?)\b"),
    ),
    (
        "role_hijack",
        re.compile(
            r"(?i)\b(?:you are now|act as)\b.{0,50}"
            r"\b(?:unrestricted|developer|system|admin)\b"
        ),
    ),
    (
        "follow_instead",
        re.compile(
            r"(?i)\bfollow\b.{0,30}\b(?:these|my)\b.{0,20}"
            r"\binstructions?\b.{0,20}\binstead\b"
        ),
    ),
)


def normalize_untrusted_text(text: str) -> str:
    """Normalize Unicode and strip control characters without changing meaning."""

    normalized = unicodedata.normalize("NFKC", text).replace("\x00", " ")
    return " ".join(normalized.split())


def detect_prompt_injection(text: str) -> list[str]:
    """Return named signals; this is a conservative detector, not a classifier."""

    normalized = normalize_untrusted_text(text)
    return [name for name, pattern in _INJECTION_PATTERNS if pattern.search(normalized)]


def redact_sensitive_data(text: str) -> tuple[str, list[RedactionEvent]]:
    """Mask common personal identifiers and credential-like values."""

    redacted = normalize_untrusted_text(text)
    events: list[RedactionEvent] = []
    for kind, pattern, replacement in _SENSITIVE_PATTERNS:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            events.append(RedactionEvent(kind=kind, count=count))
    return redacted, events


def sanitize_ticket_text(text: str) -> tuple[str, GuardrailReport]:
    """Create the exact text allowed to enter retrieval and prompt construction."""

    normalized = normalize_untrusted_text(text)
    injection_signals = detect_prompt_injection(normalized)
    redacted, redactions = redact_sensitive_data(normalized)
    truncated = len(redacted) > MAX_PROMPT_TEXT_LENGTH
    safe_text = redacted[:MAX_PROMPT_TEXT_LENGTH]

    notes = [
        "Ticket text is treated as untrusted data, never as an instruction.",
        "The portfolio copilot is advisory and cannot execute system changes.",
    ]
    if injection_signals:
        notes.append("Potential prompt injection detected; mandatory human review is enabled.")
    if redactions:
        notes.append("Sensitive values were masked before retrieval and prompt construction.")

    return safe_text, GuardrailReport(
        injection_detected=bool(injection_signals),
        injection_signals=injection_signals,
        redactions=redactions,
        input_truncated=truncated,
        automation_allowed=False,
        notes=notes,
    )


def scan_context_for_injection(chunks: Iterable[tuple[str, str]]) -> list[str]:
    """Detect instruction-like text in retrieved context to reduce indirect injection risk."""

    signals: list[str] = []
    for evidence_id, text in chunks:
        for signal in detect_prompt_injection(text):
            signals.append(f"{evidence_id}:{signal}")
    return signals
