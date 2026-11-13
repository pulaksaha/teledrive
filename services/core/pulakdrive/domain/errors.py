"""
pulakdrive.domain.errors — Typed domain error hierarchy.

All errors carry an error_code for stable API response mapping.
Error messages are caller-safe (no secrets, no raw paths, no stack traces).

Error classes are grouped by subsystem:
  - ConfigError: application configuration problems.
  - VaultError: vault lifecycle and state machine violations.
  - DatabaseError: SQLite connection and migration problems (Milestone 4).
  - ApiError: local API request/response problems (Milestone 5, blocked).
  - JobError: durable job state machine violations (Milestone 3+).
"""
from __future__ import annotations


class PulakDriveError(Exception):
    """Base class for all PulakDrive domain errors."""

    error_code: str = "PULAKDRIVE_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"{type(self).__name__}(error_code={self.error_code!r}, message={self.message!r})"


# ---------------------------------------------------------------------------
# Configuration errors
# ---------------------------------------------------------------------------

class ConfigError(PulakDriveError):
    """Application configuration is invalid or missing."""
    error_code = "CONFIG_ERROR"


class InvalidConfigFieldError(ConfigError):
    """A specific configuration field has an invalid value."""
    error_code = "CONFIG_INVALID_FIELD"

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"Configuration field '{field}' is invalid: {reason}")
        self.field = field
        self.reason = reason


# ---------------------------------------------------------------------------
# Vault errors
# ---------------------------------------------------------------------------

class VaultError(PulakDriveError):
    """Base class for vault lifecycle and state errors."""
    error_code = "VAULT_ERROR"


class VaultNotFoundError(VaultError):
    """No vault exists at the expected location."""
    error_code = "VAULT_NOT_FOUND"


class VaultStateError(VaultError):
    """An operation was attempted in an invalid vault state."""
    error_code = "VAULT_INVALID_STATE"

    def __init__(self, operation: str, current_state: str) -> None:
        super().__init__(
            f"Cannot perform '{operation}' when vault is in state '{current_state}'"
        )
        self.operation = operation
        self.current_state = current_state


# ---------------------------------------------------------------------------
# Database errors (Milestone 4)
# ---------------------------------------------------------------------------

class DatabaseError(PulakDriveError):
    """Base class for database infrastructure errors."""
    error_code = "DATABASE_ERROR"


class MigrationError(DatabaseError):
    """A schema migration failed or produced an unexpected checksum."""
    error_code = "DATABASE_MIGRATION_ERROR"


class IntegrityError(DatabaseError):
    """Database integrity check failed on startup."""
    error_code = "DATABASE_INTEGRITY_ERROR"


# ---------------------------------------------------------------------------
# API errors (Milestone 5, blocked)
# ---------------------------------------------------------------------------

class ApiError(PulakDriveError):
    """Base class for local API errors."""
    error_code = "API_ERROR"


class AuthenticationError(ApiError):
    """Request authentication failed."""
    error_code = "API_AUTH_ERROR"


class InvalidRequestError(ApiError):
    """Request schema or size validation failed."""
    error_code = "API_INVALID_REQUEST"


# ---------------------------------------------------------------------------
# Job errors (Milestone 3+)
# ---------------------------------------------------------------------------

class JobError(PulakDriveError):
    """Base class for durable job state machine errors."""
    error_code = "JOB_ERROR"


class InvalidJobTransitionError(JobError):
    """An invalid state transition was attempted."""
    error_code = "JOB_INVALID_TRANSITION"

    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid job state transition: '{from_state}' -> '{to_state}'"
        )
        self.from_state = from_state
        self.to_state = to_state

