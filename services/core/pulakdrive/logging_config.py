"""
pulakdrive.logging_config — Structured, redacted logging configuration.

Logging rules (enforced by convention; not the only defense):
  - NEVER log bearer tokens, Keychain contents, or encryption keys.
  - NEVER log passphrases, recovery secrets, OTP/2FA, or session material.
  - NEVER log plaintext file content or sensitive file paths.
  - NEVER log Telegram credentials or session strings.
  - Use REDACTED sentinel for any value that should not appear in logs.

Structured logging uses Python's standard `logging` module with a JSON
formatter for machine-readable output in production and a human-readable
formatter for development.

No third-party logging library is added in Milestone 1.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

# Sentinel string for redacted fields — never the actual secret value.
REDACTED = "[REDACTED]"


class RedactingFilter(logging.Filter):
    """
    Log filter that rejects records containing known secret-shaped substrings.

    This is a defense-in-depth check, not a comprehensive sanitizer.
    The primary defense is never passing secret values to the logger in the first place.
    """

    # Keywords whose presence as a record attribute name triggers redaction.
    _SENSITIVE_ATTRIBUTE_NAMES: frozenset[str] = frozenset({
        "token", "bearer", "secret", "passphrase", "key", "keychain",
        "password", "credential", "session", "otp", "recovery",
    })

    def filter(self, record: logging.LogRecord) -> bool:
        # Reject records with sensitive attribute names in extra fields.
        for attr in list(vars(record).keys()):
            if attr.lower() in self._SENSITIVE_ATTRIBUTE_NAMES:
                record.msg = f"[LOG RECORD REJECTED: possible secret field '{attr}']"
                record.__dict__[attr] = REDACTED
        return True


class StructuredJsonFormatter(logging.Formatter):
    """
    Format log records as JSON lines for structured log processing.

    Fields included: timestamp, level, logger, message, plus any extra fields
    attached via LogRecord. Sensitive fields are replaced by REDACTED.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include safe extra fields; skip internal logging attributes and sensitive names.
        _skip = frozenset({
            "args", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "message",
            "module", "msecs", "msg", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "thread", "threadName",
        })
        for key, val in vars(record).items():
            if key in _skip or key.startswith("_"):
                continue
            # Redact by name as a safety net.
            if key.lower() in RedactingFilter._SENSITIVE_ATTRIBUTE_NAMES:
                log_entry[key] = REDACTED
            else:
                log_entry[key] = val

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development/terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=UTC).strftime("%H:%M:%S.%f")[:-3]
        return f"[{ts}] {record.levelname:8s} {record.name}: {record.getMessage()}"


def configure_logging(
    level: str = "INFO",
    structured: bool = False,
    stream: Any = None,
) -> None:
    """
    Configure root logger for the PulakDrive service.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        structured: If True, use JSON formatter; otherwise use human-readable.
        stream: Output stream (defaults to sys.stderr).
    """
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Remove any existing handlers to avoid duplicate output.
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setLevel(level.upper())
    handler.addFilter(RedactingFilter())

    if structured:
        handler.setFormatter(StructuredJsonFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())

    root.addHandler(handler)

    # Suppress noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
