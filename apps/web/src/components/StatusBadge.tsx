import React from "react";
import { ServiceState, VaultState } from "@pulakdrive/contracts";

interface StatusBadgeProps {
  type: "service" | "vault";
  state: ServiceState | VaultState;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, state }) => {
  let styleClass = "status-neutral";
  let label = String(state);

  if (type === "service") {
    switch (state) {
      case ServiceState.READY:
        styleClass = "status-ready";
        label = "Ready";
        break;
      case ServiceState.INITIALIZING:
        styleClass = "status-warning";
        label = "Initializing";
        break;
      case ServiceState.PAUSED:
        styleClass = "status-neutral";
        label = "Paused";
        break;
      case ServiceState.DEGRADED:
        styleClass = "status-warning";
        label = "Degraded";
        break;
      case ServiceState.NEEDS_ATTENTION:
        styleClass = "status-danger";
        label = "Needs Attention";
        break;
      case ServiceState.SERVICE_UNAVAILABLE:
        styleClass = "status-danger";
        label = "Unavailable";
        break;
      case ServiceState.NOT_CONFIGURED:
      default:
        styleClass = "status-neutral";
        label = "Not Configured";
        break;
    }
  } else {
    switch (state) {
      case VaultState.READY:
        styleClass = "status-ready";
        label = "Active & Ready";
        break;
      case VaultState.INITIALIZING:
        styleClass = "status-warning";
        label = "Initializing";
        break;
      case VaultState.LOCKED:
        styleClass = "status-warning";
        label = "Locked";
        break;
      case VaultState.DEGRADED:
        styleClass = "status-danger";
        label = "Degraded";
        break;
      case VaultState.NO_VAULT:
      default:
        styleClass = "status-neutral";
        label = "No Vault Created";
        break;
    }
  }

  return (
    <span
      className={`status-badge ${styleClass}`}
      data-testid={`${type}-status-badge`}
    >
      <span aria-hidden="true">•</span>
      {label}
    </span>
  );
};

