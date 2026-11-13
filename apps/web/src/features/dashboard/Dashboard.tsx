import React, { useState, useEffect } from "react";
import type { ServiceStatus, VaultInfo } from "@pulakdrive/contracts";
import { StatusBadge } from "@/components/StatusBadge";
import { mockService, DEFAULT_MOCK_STATUS } from "@/services/mockService";

export const Dashboard: React.FC = () => {
  const [status, setStatus] = useState<ServiceStatus>(DEFAULT_MOCK_STATUS);
  const [vaults, setVaults] = useState<VaultInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    const [fetchedStatus, fetchedVaults] = await Promise.all([
      mockService.getStatus(),
      mockService.listVaults(),
    ]);
    setStatus(fetchedStatus);
    setVaults(fetchedVaults);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="card" data-testid="dashboard-loading">
        <p className="card-subtitle">Loading PulakDrive status...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Safety Notice regarding Phase 1 Mock State */}
      <div className="notice-box" role="status">
        <div className="notice-title">Phase 1 Foundation Milestone</div>
        <div>
          This interface is running on synthetic data. Real cryptographic key
          derivation, Telegram remote transport, and background scanning are not
          active.
        </div>
      </div>

      {/* Operational Metrics Grid */}
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-title">Service Daemon</div>
          <div className="card-value">
            <StatusBadge type="service" state={status.service_state} />
          </div>
          <div className="card-subtitle">
            Protocol v{status.api_protocol_major}.{status.api_protocol_minor}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Local Vault</div>
          <div className="card-value">
            <StatusBadge type="vault" state={status.vault_state} />
          </div>
          <div className="card-subtitle">
            {vaults.length === 0
              ? "No vault created"
              : `${vaults.length} local ${vaults.length === 1 ? "vault" : "vaults"} configured`}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Last Confirmed Backup</div>
          <div
            className="card-value"
            style={{ fontSize: "1.125rem", marginTop: "0.5rem" }}
            data-testid="last-backup-indicator"
          >
            {status.last_successful_backup_at ? (
              new Date(status.last_successful_backup_at).toLocaleString()
            ) : (
              <span style={{ color: "var(--text-secondary)" }}>
                No backup recorded yet
              </span>
            )}
          </div>
          <div className="card-subtitle">
            {status.last_successful_backup_at
              ? "Confirmed backup timestamp"
              : "No backup has occurred"}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Indexed Files</div>
          <div className="card-value">{status.files_indexed}</div>
          <div className="card-subtitle">Pending jobs: {status.pending_jobs}</div>
        </div>
      </div>

      {/* Vault List / Empty State */}
      <div className="card" style={{ marginTop: "1rem" }}>
        <h3 style={{ marginBottom: "1rem", fontSize: "1.125rem" }}>Vault Overview</h3>
        {vaults.length === 0 ? (
          <div className="empty-state" data-testid="empty-vault-state">
            <div className="empty-title">No Local Vault Configured</div>
            <div className="empty-description">
              Vault setup and backup operations are not available in this
              foundation milestone. No files have been backed up.
            </div>
          </div>
        ) : (
          <div>
            {vaults.map((vault) => (
              <div
                key={vault.vault_id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0.75rem 0",
                  borderBottom: "1px solid var(--border-color)",
                }}
              >
                <div>
                  <strong>{vault.display_name}</strong>
                  <div className="card-subtitle" style={{ fontSize: "0.75rem" }}>
                    ID: {vault.vault_id}
                  </div>
                </div>
                <StatusBadge type="vault" state={vault.state} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

