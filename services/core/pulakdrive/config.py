"""
pulakdrive.config — Application configuration model.

Configuration is loaded from environment variables or a file; it is never stored
in SQLite, logs, or source code. Secrets (bearer token, encryption keys) are NOT
part of this model — they remain in Keychain (blocked until security review).

This module contains no production cryptographic material.
"""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ServiceConfig(BaseModel):
    """
    Immutable runtime configuration for the PulakDrive core service.

    All fields are non-secret. Secret material (bearer token, VMK) is not
    stored here and must never appear in logs, environment variables, or config files.
    """

    # Application data directory (macOS: ~/Library/Application Support/PulakDrive)
    # Must be an absolute path owned by the current user.
    app_data_dir: Path = Field(
        default_factory=lambda: Path.home() / "Library" / "Application Support" / "PulakDrive"
    )

    # Protocol version for local API compatibility negotiation.
    # Increment major on breaking changes; minor on additive changes.
    api_protocol_major: int = Field(default=1, ge=1)
    api_protocol_minor: int = Field(default=0, ge=0)

    # Service log level. Never log secrets regardless of level.
    log_level: str = Field(default="INFO")

    # Loopback port range for the local API (blocked; not bound in Milestone 1).
    # Actual port selection occurs at runtime from an available port in this range.
    api_port_min: int = Field(default=49200, ge=1024, le=65535)
    api_port_max: int = Field(default=49299, ge=1024, le=65535)

    # Maximum body size for local API requests (bytes).
    api_max_body_bytes: int = Field(default=1_048_576, ge=1024)  # 1 MiB default

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = v.upper()
        if normalized not in allowed:
            raise ValueError(f"log_level must be one of {sorted(allowed)}, got {v!r}")
        return normalized

    @field_validator("app_data_dir")
    @classmethod
    def validate_app_data_dir(cls, v: Path) -> Path:
        if not v.is_absolute():
            raise ValueError(f"app_data_dir must be absolute, got {v!r}")
        return v

    @field_validator("api_port_max")
    @classmethod
    def validate_port_range(cls, v: int, info: object) -> int:
        # Access field data via info.data for cross-field validation.
        data = getattr(info, "data", {})
        min_port = data.get("api_port_min")
        if min_port is not None and v < min_port:
            raise ValueError(
                f"api_port_max ({v}) must be >= api_port_min ({min_port})"
            )
        return v

    @classmethod
    def from_environment(cls) -> ServiceConfig:
        """
        Construct configuration from environment variables.

        Environment variable names follow the pattern PULAKDRIVE_<FIELD_NAME_UPPER>.
        Unset variables use the field defaults.

        Never reads secrets from environment (they must come from Keychain).
        """
        kwargs: dict = {}

        if val := os.environ.get("PULAKDRIVE_APP_DATA_DIR"):
            kwargs["app_data_dir"] = Path(val)
        if val := os.environ.get("PULAKDRIVE_LOG_LEVEL"):
            kwargs["log_level"] = val
        if val := os.environ.get("PULAKDRIVE_API_PORT_MIN"):
            kwargs["api_port_min"] = int(val)
        if val := os.environ.get("PULAKDRIVE_API_PORT_MAX"):
            kwargs["api_port_max"] = int(val)
        if val := os.environ.get("PULAKDRIVE_API_MAX_BODY_BYTES"):
            kwargs["api_max_body_bytes"] = int(val)

        return cls(**kwargs)

    model_config = {"frozen": True}
