"""
tests.test_service — Tests for the application service layer.

Uses mock repositories; no real SQLite, network, or crypto.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from pulakdrive.application.service import PulakDriveService
from pulakdrive.domain.errors import VaultNotFoundError
from pulakdrive.domain.models import ServiceState, ServiceStatus, VaultState
from pulakdrive.repositories.mock_repository import (
    MockStatusRepository,
    MockVaultRepository,
)


def _make_service() -> tuple[PulakDriveService, MockStatusRepository, MockVaultRepository]:
    status_repo = MockStatusRepository()
    vault_repo = MockVaultRepository()
    svc = PulakDriveService(status_repo=status_repo, vault_repo=vault_repo)
    return svc, status_repo, vault_repo


class TestServiceStatus:
    def test_initial_status_is_not_configured(self) -> None:
        svc, _, _ = _make_service()
        status = svc.get_service_status()
        assert status.service_state == ServiceState.NOT_CONFIGURED

    def test_status_has_no_false_backup_success(self) -> None:
        svc, _, _ = _make_service()
        status = svc.get_service_status()
        assert status.last_successful_backup_at is None, (
            "Service must not report backup success before any backup has completed"
        )

    def test_status_reflects_mock_override(self) -> None:
        svc, status_repo, _ = _make_service()
        new_status = ServiceStatus(
            service_state=ServiceState.READY,
            vault_state=VaultState.READY,
            api_protocol_major=1,
            api_protocol_minor=0,
        )
        status_repo.set_status_for_testing(new_status)
        result = svc.get_service_status()
        assert result.service_state == ServiceState.READY


class TestVaultListing:
    def test_empty_vault_list(self) -> None:
        svc, _, _ = _make_service()
        assert svc.list_vaults() == []

    def test_vault_appears_after_creation(self) -> None:
        svc, _, vault_repo = _make_service()
        vault = vault_repo.create_vault_for_testing(display_name="Test Vault")
        vaults = svc.list_vaults()
        assert len(vaults) == 1
        assert vaults[0].vault_id == vault.vault_id

    def test_get_vault_by_id(self) -> None:
        svc, _, vault_repo = _make_service()
        vault = vault_repo.create_vault_for_testing()
        result = svc.get_vault(str(vault.vault_id))
        assert result.vault_id == vault.vault_id

    def test_get_nonexistent_vault_raises(self) -> None:
        svc, _, _ = _make_service()
        with pytest.raises(VaultNotFoundError):
            svc.get_vault(str(uuid4()))
