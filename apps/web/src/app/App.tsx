import React from "react";
import { Dashboard } from "@/features/dashboard/Dashboard";

export const App: React.FC = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="app-title">
          <span>PulakDrive</span>
          <span className="app-badge">Phase 1 Foundation</span>
        </div>
        <div style={{ fontSize: "0.8125rem", color: "var(--text-secondary)" }}>
          macOS Personal Backup Foundation
        </div>
      </header>

      <main className="main-content">
        <Dashboard />
      </main>
    </div>
  );
};

