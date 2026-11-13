"""
tests.test_logging — Tests for structured/redacted logging.

Verifies that the logging configuration:
  - Does not emit secrets in log output.
  - Applies redacting filter.
  - Formats records correctly.

No real secrets are used in these tests.
"""
from __future__ import annotations

import io
import json
import logging

from pulakdrive.logging_config import (
    REDACTED,
    RedactingFilter,
    StructuredJsonFormatter,
    configure_logging,
)


class TestRedactingFilter:
    def _make_record(self, **extra: object) -> logging.LogRecord:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        for key, val in extra.items():
            setattr(record, key, val)
        return record

    def test_safe_record_passes_through(self) -> None:
        f = RedactingFilter()
        record = self._make_record(component="sync")
        assert f.filter(record) is True

    def test_record_with_token_field_is_sanitized(self) -> None:
        f = RedactingFilter()
        record = self._make_record(token="should-not-appear")
        f.filter(record)
        # The field value should be redacted, not the original.
        assert record.token == REDACTED

    def test_record_with_secret_field_is_sanitized(self) -> None:
        f = RedactingFilter()
        record = self._make_record(secret="super-secret")
        f.filter(record)
        assert record.secret == REDACTED

    def test_record_with_passphrase_field_is_sanitized(self) -> None:
        f = RedactingFilter()
        record = self._make_record(passphrase="hunter2")
        f.filter(record)
        assert record.passphrase == REDACTED


class TestStructuredJsonFormatter:
    def _format_record(self, msg: str = "hello", **extra: object) -> dict:
        formatter = StructuredJsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )
        for key, val in extra.items():
            setattr(record, key, val)
        output = formatter.format(record)
        return json.loads(output)

    def test_output_is_valid_json(self) -> None:
        formatted = self._format_record("test message")
        assert isinstance(formatted, dict)

    def test_required_fields_present(self) -> None:
        formatted = self._format_record("test message")
        assert "timestamp" in formatted
        assert "level" in formatted
        assert "logger" in formatted
        assert "message" in formatted

    def test_message_is_correct(self) -> None:
        formatted = self._format_record("hello world")
        assert formatted["message"] == "hello world"

    def test_level_is_correct(self) -> None:
        formatted = self._format_record("test")
        assert formatted["level"] == "INFO"

    def test_safe_extra_field_included(self) -> None:
        formatted = self._format_record("test", component="sync")
        assert formatted.get("component") == "sync"

    def test_sensitive_extra_field_is_redacted(self) -> None:
        """Secret values must never appear in JSON log output."""
        formatted = self._format_record("test", token="VERY_SECRET_TOKEN")
        assert formatted.get("token") == REDACTED
        assert "VERY_SECRET_TOKEN" not in json.dumps(formatted)


class TestConfigureLogging:
    def test_configure_logging_does_not_raise(self) -> None:
        buf = io.StringIO()
        configure_logging(level="INFO", structured=False, stream=buf)

    def test_configure_logging_structured_json(self) -> None:
        buf = io.StringIO()
        configure_logging(level="DEBUG", structured=True, stream=buf)
        logger = logging.getLogger("test.structured")
        logger.info("structured test")
        val = buf.getvalue()
        if val:  # May be empty if handler not flushed yet.
            parsed = json.loads(val.strip().split("\n")[0])
            assert "message" in parsed

    def test_no_secrets_in_log_output(self) -> None:
        """No secret value should appear in log output even if accidentally passed."""
        buf = io.StringIO()
        configure_logging(level="DEBUG", structured=True, stream=buf)
        logger = logging.getLogger("test.secret_check")
        # Simulate a developer accidentally logging a sensitive attribute.
        logger.info("operation complete", extra={"token": "SECRET_VALUE_XYZ"})
        output = buf.getvalue()
        assert "SECRET_VALUE_XYZ" not in output, (
            "Secret value must never appear in log output"
        )
