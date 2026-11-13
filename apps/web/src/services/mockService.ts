/**
 * Synthetic service data for the Milestone 1 dashboard.
 *
 * This client performs no network, filesystem, credential, or backup work.
 */

import {
  ServiceState,
  VaultState,
  type ServiceStatus,
  type VaultInfo,
} from "@pulakdrive/contracts";

export const DEFAULT_MOCK_STATUS = {
  service_state: ServiceState.NOT_CONFIGURED,
  vault_state: VaultState.NO_VAULT,
  api_protocol_major: 1,
  api_protocol_minor: 0,
  last_successful_backup_at: null,
  files_indexed: 0,
  pending_jobs: 0,
  failed_jobs: 0,
} satisfies ServiceStatus;

export class MockServiceClient {
  async getStatus(): Promise<ServiceStatus> {
    return Promise.resolve({ ...DEFAULT_MOCK_STATUS });
  }

  async listVaults(): Promise<VaultInfo[]> {
    return Promise.resolve([]);
  }
}

export const mockService = new MockServiceClient();
