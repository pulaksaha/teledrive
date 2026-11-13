"""
tests.test_domain — Tests for domain models and error types.

All tests use synthetic data only. No real paths, secrets, or credentials.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from pulakdrive.domain.errors import (
    InvalidJobTransitionError,
    PulakDriveError,
    VaultNotFoundError,
    VaultStateError,
)
from pulakdrive.domain.models import (
    JobState,
    ServiceState,
    ServiceStatus,
    VaultInfo,
    VaultState,
)


class TestServiceState:
    def test_all_cases_have_non_empty_values(self) -> None:
        for state in ServiceState:
            assert state.value, f"ServiceState.{state.name} has empty value"

    def test_not_configured_is_initial_state(self) -> None:
        assert ServiceState.NOT_CONFIGURED.value == "not_configured"


class TestVaultState:
    def test_all_cases_have_non_empty_values(self) -> None:
        for state in VaultState:
            assert state.value, f"VaultState.{state.name} has empty value"


class TestJobState:
    def test_all_cases_have_non_empty_values(self) -> None:
        for state in JobState:
            assert state.value, f"JobState.{state.name} has empty value"


class TestServiceStatus:
    def test_mock_not_configured_no_false_success(self) -> None:
        """mock_not_configured must never claim a backup succeeded."""
        status = ServiceStatus.mock_not_configured()
        assert status.service_state == ServiceState.NOT_CONFIGURED
        assert status.vault_state == VaultState.NO_VAULT
        assert status.last_successful_backup_at is None, (
            "Unconfigured service must not report a successful backup"
        )

    def test_mock_not_configured_zero_counts(self) -> None:
        status = ServiceStatus.mock_not_configured()
        assert status.files_indexed == 0
        assert status.pending_jobs == 0
        assert status.failed_jobs == 0

    def test_status_is_frozen(self) -> None:
        status = ServiceStatus.mock_not_configured()
        with pytest.raises(ValidationError):
            status.service_state = ServiceState.READY  # type: ignore[misc]

    def test_status_full_construction(self) -> None:
        ts = datetime(2026, 11, 12, 0, 0, 0, tzinfo=UTC)
        status = ServiceStatus(
            service_state=ServiceState.READY,
            vault_state=VaultState.READY,
            api_protocol_major=1,
            api_protocol_minor=0,
            last_successful_backup_at=ts,
            files_indexed=10,
            pending_jobs=2,
            failed_jobs=0,
        )
        assert status.last_successful_backup_at == ts
        assert status.files_indexed == 10

    def test_negative_files_indexed_raises(self) -> None:
        with pytest.raises(ValidationError):
            ServiceStatus(
                service_state=ServiceState.READY,
                vault_state=VaultState.READY,
                api_protocol_major=1,
                api_protocol_minor=0,
                files_indexed=-1,
            )


class TestVaultInfo:
    def test_construction_with_valid_data(self) -> None:
        vault = VaultInfo(
            vault_id=uuid4(),
            display_name="My Test Vault",
            created_at=datetime.now(tz=UTC),
            state=VaultState.READY,
        )
        assert vault.display_name == "My Test Vault"

    def test_empty_display_name_raises(self) -> None:
        with pytest.raises(ValidationError):
            VaultInfo(
                vault_id=uuid4(),
                display_name="",
                created_at=datetime.now(tz=UTC),
                state=VaultState.READY,
            )

    def test_vault_info_is_frozen(self) -> None:
        vault = VaultInfo(
            vault_id=uuid4(),
            display_name="My Test Vault",
            created_at=datetime.now(tz=UTC),
            state=VaultState.READY,
        )
        with pytest.raises(ValidationError):
            vault.state = VaultState.LOCKED  # type: ignore[misc]


class TestErrors:
    def test_base_error_has_message(self) -> None:
        err = PulakDriveError("test message")
        assert str(err) == "test message"
        assert err.message == "test message"
        assert err.error_code == "PULAKDRIVE_ERROR"

    def test_vault_not_found_error_code(self) -> None:
        err = VaultNotFoundError("vault missing")
        assert err.error_code == "VAULT_NOT_FOUND"

    def test_vault_state_error_includes_context(self) -> None:
        err = VaultStateError("backup", "locked")
        assert "backup" in str(err)
        assert "locked" in str(err)
        assert err.error_code == "VAULT_INVALID_STATE"

    def test_invalid_job_transition_error_code(self) -> None:
        err = InvalidJobTransitionError("pending", "completed")
        assert err.error_code == "JOB_INVALID_TRANSITION"
        assert "pending" in str(err)
        assert "completed" in str(err)

    def test_errors_are_exceptions(self) -> None:
        with pytest.raises(VaultNotFoundError):
            raise VaultNotFoundError("not found")
