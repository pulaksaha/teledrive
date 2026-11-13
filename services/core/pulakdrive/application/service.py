"""
pulakdrive.application.service — Application service layer.

Coordinates domain operations through injected repositories.
No network access, no Telegram, no production crypto in Milestone 1.

Dependency injection: repositories are passed to the constructor.
This makes the service testable with mock implementations.
"""
from __future__ import annotations

import logging
from uuid import UUID

from pulakdrive.domain.models import ServiceStatus, VaultInfo

logger = logging.getLogger(__name__)


class PulakDriveService:
    """
    Application service layer for PulakDrive.

    Owns business-logic orchestration. All I/O goes through injected
    repositories; this class has no direct SQLite, network, or crypto imports.

    Phase 1: status retrieval and vault lifecycle stubs only.
    Backup/restore/job operations are deferred to later milestones.
    """

    def __init__(
        self,
        status_repo: object,  # StatusRepository protocol (typed in Milestone 4)
        vault_repo: object,   # VaultRepository protocol (typed in Milestone 4)
    ) -> None:
        # Repositories are stored by duck-typed interface.
        # Formal Protocol types will be introduced in Milestone 4.
        self._status_repo = status_repo
        self._vault_repo = vault_repo
        logger.info("PulakDriveService initialized", extra={"milestone": "1"})

    def get_service_status(self) -> ServiceStatus:
        """
        Return the current service health and status snapshot.

        Never returns a status that falsely claims backup success.
        """
        status: ServiceStatus = self._status_repo.get_status()
        logger.debug("Status requested", extra={"state": status.service_state.value})
        return status

    def list_vaults(self) -> list[VaultInfo]:
        """Return all known vaults (mock data in Milestone 1)."""
        vaults: list[VaultInfo] = self._vault_repo.list_vaults()
        logger.debug("Vault list requested", extra={"count": len(vaults)})
        return vaults

    def get_vault(self, vault_id_str: str) -> VaultInfo:
        """
        Return vault info by string ID.

        Raises VaultNotFoundError if the vault does not exist.
        """
        vault_id = UUID(vault_id_str)
        return self._vault_repo.find_vault(vault_id)

    # NOTE: backup_start, restore_request, purge_request are deferred.
    # They require: SQLite persistence (M4), job queue (M3+), crypto (blocked), API (M5).
