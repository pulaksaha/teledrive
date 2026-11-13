import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Dashboard } from "@/features/dashboard/Dashboard";
import { DEFAULT_MOCK_STATUS, MockServiceClient } from "@/services/mockService";

async function renderDashboard(): Promise<void> {
  render(<Dashboard />);
  await waitFor(() => {
    expect(screen.queryByTestId("dashboard-loading")).not.toBeInTheDocument();
  });
}

describe("Dashboard", () => {
  it("shows the service and vault as unconfigured", async () => {
    await renderDashboard();

    expect(screen.getByTestId("service-status-badge")).toHaveTextContent(
      "Not Configured"
    );
    expect(screen.getByTestId("vault-status-badge")).toHaveTextContent(
      "No Vault Created"
    );
  });

  it("does not falsely report a successful backup", async () => {
    await renderDashboard();

    expect(screen.getByTestId("last-backup-indicator")).toHaveTextContent(
      "No backup recorded yet"
    );
    expect(screen.getByText("No backup has occurred")).toBeInTheDocument();
    expect(screen.queryByText("Confirmed backup timestamp")).not.toBeInTheDocument();
  });

  it("displays a useful empty vault state", async () => {
    await renderDashboard();

    expect(screen.getByTestId("empty-vault-state")).toHaveTextContent(
      "No Local Vault Configured"
    );
    expect(screen.getByTestId("empty-vault-state")).toHaveTextContent(
      "No files have been backed up"
    );
  });

  it("uses the serialized Python contract field names", async () => {
    const status = await new MockServiceClient().getStatus();

    expect(status).toEqual(DEFAULT_MOCK_STATUS);
    expect(Object.keys(status)).toEqual([
      "service_state",
      "vault_state",
      "api_protocol_major",
      "api_protocol_minor",
      "last_successful_backup_at",
      "files_indexed",
      "pending_jobs",
      "failed_jobs",
    ]);
  });
});
