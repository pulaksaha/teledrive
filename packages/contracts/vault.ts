/**
 * PulakDrive — Shared Vault Contracts
 *
 * Mirrors `pulakdrive.domain.models.VaultState` and `VaultInfo`.
 *
 * Note: No cryptographic fields (VMK, DEK, recovery secrets) are exposed here.
 * Those remain strictly blocked pending cryptographic review.
 */

/**
 * Observable lifecycle state of the local vault.
 */
export enum VaultState {
  NO_VAULT = "no_vault",
  INITIALIZING = "initializing",
  READY = "ready",
  LOCKED = "locked",
  DEGRADED = "degraded",
}

/**
 * Serialized `VaultInfo` using the Python model's field names.
 *
 * All properties are required and non-nullable.
 */
export interface VaultInfo {
  /** Canonical UUID string representation of the vault. */
  vault_id: string;
  /** User-facing display name. */
  display_name: string;
  /** ISO 8601 timestamp string of vault creation. */
  created_at: string;
  /** Current vault lifecycle state. */
  state: VaultState;
}

