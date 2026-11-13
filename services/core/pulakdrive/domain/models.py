"""
pulakdrive.domain.models — Core domain value objects and entities.

Phase 1 Milestone 1: foundation. These are plain Python data classes with no
database, network, or cryptographic dependencies.

BLOCKED (not implemented here):
- Encryption-key fields: blocked until crypto review complete.
- VMK / DEK / recovery material: blocked.
- Keychain references: blocked.
- Telegram / remote object fields: Phase 3+.
- SQLite-backed persistence: Milestone 4.
"""
from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ServiceState(str, enum.Enum):
    """Observable lifecycle state of the PulakDrive Python service."""
    NOT_CONFIGURED = "not_configured"
    INITIALIZING = "initializing"
    READY = "ready"
    PAUSED = "paused"
    DEGRADED = "degraded"
    NEEDS_ATTENTION = "needs_attention"
    SERVICE_UNAVAILABLE = "service_unavailable"


class VaultState(str, enum.Enum):
    """Observable lifecycle state of the local vault."""
    NO_VAULT = "no_vault"
    INITIALIZING = "initializing"
    READY = "ready"
    LOCKED = "locked"
    DEGRADED = "degraded"


class JobState(str, enum.Enum):
    """
    State machine for durable jobs.

    Transitions (Phase 2+):
      PENDING -> RUNNING -> COMPLETED
                         -> FAILED -> PENDING (retry)
                         -> CANCELLED
      RUNNING -> PAUSED -> RUNNING
    """
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceStatus(BaseModel):
    """
    Top-level service health and status snapshot.

    Returned by the future health endpoint (Milestone 5+).
    Contains no secret material.
    """
    service_state: ServiceState
    vault_state: VaultState
    api_protocol_major: int = Field(ge=1)
    api_protocol_minor: int = Field(ge=0)
    # ISO 8601 timestamp of the last confirmed successful backup.
    # None means no backup has been completed.
    last_successful_backup_at: datetime | None = None
    files_indexed: int = Field(default=0, ge=0)
    pending_jobs: int = Field(default=0, ge=0)
    failed_jobs: int = Field(default=0, ge=0)

    model_config = {"frozen": True}

    @classmethod
    def mock_not_configured(cls) -> ServiceStatus:
        """
        A safe mock status for tests and UI development.

        Does NOT claim any backup has succeeded — an unconfigured service has
        no backup history.
        """
        return cls(
            service_state=ServiceState.NOT_CONFIGURED,
            vault_state=VaultState.NO_VAULT,
            api_protocol_major=1,
            api_protocol_minor=0,
            last_successful_backup_at=None,
        )


class VaultInfo(BaseModel):
    """
    Minimal non-secret vault identification.

    Cryptographic material (VMK, DEK, recovery secret) is not stored here.
    Those fields are blocked until the crypto review gate is satisfied.
    """
    vault_id: UUID
    display_name: str = Field(min_length=1, max_length=200)
    created_at: datetime
    state: VaultState

    model_config = {"frozen": True}
