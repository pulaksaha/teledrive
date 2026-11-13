/**
 * PulakDrive — Shared Service & Status Contracts
 *
 * Mirrors `pulakdrive.domain.models.ServiceState`, `JobState`, and `ServiceStatus`.
 */

import { VaultState } from "./vault.js";

/**
 * Observable lifecycle state of the PulakDrive Python background service.
 */
export enum ServiceState {
  NOT_CONFIGURED = "not_configured",
  INITIALIZING = "initializing",
  READY = "ready",
  PAUSED = "paused",
  DEGRADED = "degraded",
  NEEDS_ATTENTION = "needs_attention",
  SERVICE_UNAVAILABLE = "service_unavailable",
}

/**
 * State machine states for durable background transfer jobs.
 */
export enum JobState {
  PENDING = "pending",
  RUNNING = "running",
  PAUSED = "paused",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

/**
 * Serialized `ServiceStatus` snapshot using the Python model's field names.
 *
 * Every property is present in a serialized response. The backup timestamp is
 * required but nullable: `null` means that no backup has completed.
 */
export interface ServiceStatus {
  /** Current state of the service daemon. */
  service_state: ServiceState;
  /** Current state of the local vault. */
  vault_state: VaultState;
  /** Major protocol changes are incompatible. */
  api_protocol_major: number;
  /** Minor protocol changes remain compatible within the same major version. */
  api_protocol_minor: number;
  /** ISO 8601 timestamp, or `null` when no backup has completed. */
  last_successful_backup_at: string | null;
  /** Number of local files indexed by the scanner. */
  files_indexed: number;
  /** Number of currently pending jobs. */
  pending_jobs: number;
  /** Number of failed jobs requiring attention or retry. */
  failed_jobs: number;
}

