"""
pulakdrive.repositories.mock_repository — In-memory mock repository.

Used exclusively for Milestone 1 testing and UI development.
No persistence, no SQLite, no Telegram.

This implementation satisfies the same interface that the production SQLite
repository will implement in Milestone 4. It allows tests and the mock
service application layer to work without any blocked infrastructure.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pulakdrive.domain.errors import VaultNotFoundError
from pulakdrive.domain.models import ServiceStatus, VaultInfo, VaultState


class MockStatusRepository:
    """
    In-memory mock implementation of the service status repository.

    Returns safe, synthetic data. Never reports a successful backup unless
    one is explicitly staged for testing.
    """

    def __init__(self) -> None:
        self._status: ServiceStatus = ServiceStatus.mock_not_configured()

    def get_status(self) -> ServiceStatus:
        """Return the current mock status snapshot."""
        return self._status

    def set_status_for_testing(self, status: ServiceStatus) -> None:
        """
        Override the mock status for a test scenario.

        Not part of the production interface. Used only in test code.
        """
        self._status = status


class MockVaultRepository:
    """
    In-memory mock implementation of the vault repository.

    Vaults are stored in a dict keyed by vault_id.
    No data is persisted to disk or SQLite.
    """

    def __init__(self) -> None:
        self._vaults: dict[UUID, VaultInfo] = {}

    def find_vault(self, vault_id: UUID) -> VaultInfo:
        """
        Return vault info by ID.

        Raises VaultNotFoundError if the vault does not exist.
        """
        if vault_id not in self._vaults:
            raise VaultNotFoundError(
                f"Vault not found (id={vault_id})"
            )
        return self._vaults[vault_id]

    def list_vaults(self) -> list[VaultInfo]:
        """Return all known vaults."""
        return list(self._vaults.values())

    def create_vault_for_testing(
        self,
        display_name: str = "Test Vault",
        state: VaultState = VaultState.READY,
    ) -> VaultInfo:
        """
        Create a synthetic vault for use in tests.

        The vault ID is a random UUID. No encryption keys or secrets are created.
        Not part of the production interface.
        """
        vault = VaultInfo(
            vault_id=uuid4(),
            display_name=display_name,
            created_at=datetime.now(tz=UTC),
            state=state,
        )
        self._vaults[vault.vault_id] = vault
        return vault
