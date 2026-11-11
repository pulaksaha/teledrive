# Codex Prompt 00 — Read-only Phase 0 review

You are the architecture reviewer for PulakDrive. Read `AGENTS.md` and all files under `docs/` and `docs/adr/`.

Current authorization: **Phase 0 documentation and analysis only**. Do not create application code, executable scaffolding, install dependencies, access Telegram, or touch real user files or credentials.

Tasks:
1. Identify contradictions, missing decisions, ambiguous requirements, and unsupported assumptions.
2. Review the Swift shell / React UI / Python service boundaries and single-process ownership.
3. Review crypto envelope, recovery-kit independence, nonce/AAD rules, and metadata exposure.
4. Review SQLite model, state machines, commit protocol, crash recovery, tombstones, indefinite retention, and purge semantics.
5. Review the local API/IPC security requirements.
6. Identify Telegram-specific feasibility questions that can be answered from official public documentation only.
7. Produce a prioritized risk register with severity, impact, likelihood, mitigation, owner/phase, and validation evidence needed.
8. Map every finding to a document and proposed edit.

Output:
- Executive assessment.
- Blocking findings.
- Non-blocking findings.
- Missing decisions.
- Recommended document changes.
- Explicit confirmation that no application code or Telegram operation was performed.

Do not edit files in this pass. Do not claim a design is secure merely because it uses AES-GCM or Argon2id.
