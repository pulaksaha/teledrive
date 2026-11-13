"""
tests.test_config — Tests for pulakdrive.config.ServiceConfig.

All tests use synthetic values only. No real paths, secrets, or credentials.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from pulakdrive.config import ServiceConfig


class TestServiceConfigDefaults:
    def test_default_app_data_dir_is_absolute(self) -> None:
        cfg = ServiceConfig()
        assert cfg.app_data_dir.is_absolute(), (
            "Default app_data_dir must be an absolute path"
        )

    def test_default_log_level_is_info(self) -> None:
        cfg = ServiceConfig()
        assert cfg.log_level == "INFO"

    def test_default_protocol_versions_are_positive(self) -> None:
        cfg = ServiceConfig()
        assert cfg.api_protocol_major >= 1
        assert cfg.api_protocol_minor >= 0

    def test_default_port_range_is_valid(self) -> None:
        cfg = ServiceConfig()
        assert cfg.api_port_min < cfg.api_port_max
        assert 1024 <= cfg.api_port_min <= 65535
        assert 1024 <= cfg.api_port_max <= 65535

    def test_config_is_frozen(self) -> None:
        cfg = ServiceConfig()
        with pytest.raises(ValidationError):
            cfg.log_level = "DEBUG"  # type: ignore[misc]


class TestServiceConfigValidation:
    def test_invalid_log_level_raises(self) -> None:
        with pytest.raises(ValidationError):
            ServiceConfig(log_level="VERBOSE")

    def test_log_level_normalized_to_uppercase(self) -> None:
        cfg = ServiceConfig(log_level="debug")
        assert cfg.log_level == "DEBUG"

    def test_relative_app_data_dir_raises(self) -> None:
        with pytest.raises(ValidationError):
            ServiceConfig(app_data_dir=Path("relative/path"))

    def test_port_max_less_than_min_raises(self) -> None:
        with pytest.raises(ValidationError):
            ServiceConfig(api_port_min=49290, api_port_max=49200)

    def test_negative_port_raises(self) -> None:
        with pytest.raises(ValidationError):
            ServiceConfig(api_port_min=-1)

    def test_valid_all_log_levels(self) -> None:
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            cfg = ServiceConfig(log_level=level)
            assert cfg.log_level == level


class TestServiceConfigFromEnvironment:
    def test_from_environment_uses_defaults_when_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("PULAKDRIVE_APP_DATA_DIR", raising=False)
        monkeypatch.delenv("PULAKDRIVE_LOG_LEVEL", raising=False)
        cfg = ServiceConfig.from_environment()
        assert cfg.log_level == "INFO"
        assert cfg.app_data_dir.is_absolute()

    def test_from_environment_reads_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("PULAKDRIVE_LOG_LEVEL", "DEBUG")
        cfg = ServiceConfig.from_environment()
        assert cfg.log_level == "DEBUG"

    def test_from_environment_reads_app_data_dir(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("PULAKDRIVE_APP_DATA_DIR", str(tmp_path))
        cfg = ServiceConfig.from_environment()
        assert cfg.app_data_dir == tmp_path

    def test_no_secret_fields_in_config(self) -> None:
        """ServiceConfig must not have any field for secrets or bearer tokens."""
        cfg = ServiceConfig()
        field_names = set(cfg.model_fields.keys())
        forbidden = {"token", "bearer", "secret", "passphrase", "key", "keychain", "password"}
        overlap = field_names & forbidden
        assert not overlap, (
            f"ServiceConfig must not contain secret fields: {overlap}"
        )

